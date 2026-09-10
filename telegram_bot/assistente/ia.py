"""Conversa com o Claude, com ferramentas ligadas na agenda e nas notas.

A pessoa escreve em linguagem normal ("dentista quinta 15h", "anota que o
Wi-Fi do escritório é X", "o que eu tenho amanhã?") e o modelo decide qual
ferramenta chamar. As ferramentas são as MESMAS funções usadas pelos comandos
`/agendar`, `/notas` etc. — ou seja, a IA não tem um caminho paralelo de dados.

Se não houver ANTHROPIC_API_KEY configurada, o bot continua funcionando: o
`bot.py` cai para a interpretação offline (regex de datas em português).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

from . import servicos
from .config import Config
from .datas import NOMES_DIAS, formatar_data_hora, interpretar_quando
from .servicos import Usuario

log = logging.getLogger(__name__)

MAX_VOLTAS = 6  # no máximo 6 idas ao modelo por mensagem (evita loop infinito)

INSTRUCOES = """\
Você é a assistente pessoal de {nome} dentro do Telegram. Cuida da agenda \
dela, guarda o que ela pede para lembrar e conversa normalmente.

Contexto de agora: {dia_semana}, {data} às {hora} (fuso {fuso}).

Como agir:
- Escreva em português do Brasil, tom próximo e direto. De 1 a 3 frases, sem enrolação.
- Se a mensagem tiver qualquer coisa com data/hora ("amanhã 15h", "toda segunda"), \
registre com criar_compromisso antes de responder. Nunca diga que agendou sem ter chamado a ferramenta.
- Coisas para guardar (ideias, listas, endereços, medidas, links) vão em salvar_nota.
- Perguntas sobre a agenda ("o que tenho hoje?") se respondem com listar_compromissos; \
sobre coisas guardadas, com buscar_notas. Só fale de compromissos e notas que vieram do resultado das ferramentas.
- Faltou o horário? Assuma um razoável e diga qual assumiu. Pergunte só quando for realmente ambíguo.
- Datas nas ferramentas vão no formato AAAA-MM-DDTHH:MM, no fuso da pessoa, já resolvidas \
(nada de "amanhã": calcule a partir do contexto de agora).
- Ao confirmar um compromisso, cite o dia e a hora por extenso, e o número dele quando fizer sentido.
- Não peça dados sensíveis (senha, cartão, documento). Se ela mandar mesmo assim, guarde sem comentar.
- Texto puro, sem markdown. No máximo um emoji por mensagem.\
"""

FERRAMENTAS = [
    {
        "name": "criar_compromisso",
        "description": "Registra um compromisso na agenda e programa os lembretes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "titulo": {"type": "string", "description": "O que é, em poucas palavras."},
                "quando": {"type": "string", "description": "AAAA-MM-DDTHH:MM no fuso da pessoa."},
                "duracao_min": {"type": "integer", "description": "Duração em minutos (padrão 60)."},
                "local": {"type": "string"},
                "observacao": {"type": "string", "description": "Detalhes extras."},
                "recorrencia": {
                    "type": "string",
                    "enum": ["diaria", "semanal", "mensal"],
                    "description": "Só quando se repete.",
                },
                "antecedencia_min": {
                    "type": "integer",
                    "description": "Minutos de antecedência do aviso (padrão: preferência da pessoa).",
                },
            },
            "required": ["titulo", "quando"],
        },
    },
    {
        "name": "listar_compromissos",
        "description": "Consulta a agenda em um período.",
        "input_schema": {
            "type": "object",
            "properties": {
                "periodo": {
                    "type": "string",
                    "enum": ["hoje", "amanha", "semana", "mes", "proximos", "passados"],
                },
                "termo": {"type": "string", "description": "Filtro por palavra no título."},
            },
            "required": ["periodo"],
        },
    },
    {
        "name": "atualizar_compromisso",
        "description": "Muda dados de um compromisso existente (inclusive remarcar).",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "titulo": {"type": "string"},
                "quando": {"type": "string", "description": "AAAA-MM-DDTHH:MM."},
                "local": {"type": "string"},
                "observacao": {"type": "string"},
                "recorrencia": {"type": "string", "enum": ["diaria", "semanal", "mensal", "nenhuma"]},
                "antecedencia_min": {"type": "integer"},
            },
            "required": ["id"],
        },
    },
    {
        "name": "mudar_status_compromisso",
        "description": "Marca um compromisso como concluído, cancelado ou de volta para ativo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "status": {"type": "string", "enum": ["concluido", "cancelado", "ativo"]},
            },
            "required": ["id", "status"],
        },
    },
    {
        "name": "criar_lembrete",
        "description": "Lembrete solto, sem virar compromisso na agenda (ex.: tomar remédio às 22h).",
        "input_schema": {
            "type": "object",
            "properties": {
                "texto": {"type": "string"},
                "quando": {"type": "string", "description": "AAAA-MM-DDTHH:MM."},
            },
            "required": ["texto", "quando"],
        },
    },
    {
        "name": "salvar_nota",
        "description": "Guarda uma informação para consultar depois.",
        "input_schema": {
            "type": "object",
            "properties": {
                "texto": {"type": "string"},
                "etiquetas": {"type": "string", "description": "Palavras-chave separadas por vírgula."},
            },
            "required": ["texto"],
        },
    },
    {
        "name": "buscar_notas",
        "description": "Procura nas notas guardadas. Sem termo, devolve as mais recentes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "termo": {"type": "string"},
                "limite": {"type": "integer"},
            },
        },
    },
    {
        "name": "apagar_nota",
        "description": "Apaga uma nota pelo número.",
        "input_schema": {
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
        },
    },
    {
        "name": "ajustar_preferencias",
        "description": "Muda fuso horário, horário do resumo diário ou antecedência padrão dos avisos.",
        "input_schema": {
            "type": "object",
            "properties": {
                "fuso": {"type": "string", "description": "Ex.: America/Sao_Paulo."},
                "hora_resumo": {"type": "string", "description": "HH:MM do resumo da manhã."},
                "desligar_resumo": {"type": "boolean"},
                "antecedencia_min": {"type": "integer"},
            },
        },
    },
]


class Assistente:
    """Camada de conversa. Sem chave da API, `ativo` é False e o bot usa o modo offline."""

    def __init__(self, conn, config: Config):
        self.conn = conn
        self.config = config
        self._cliente = None
        self._fallback = config.usar_fallback
        if config.ia_ativa:
            from anthropic import AsyncAnthropic  # importado só quando há chave

            self._cliente = AsyncAnthropic(api_key=config.chave_anthropic)

    @property
    def ativo(self) -> bool:
        return self._cliente is not None

    async def responder(self, usuario: Usuario, texto: str) -> str:
        if self._cliente is None:
            raise RuntimeError("Assistente sem chave da API configurada")

        servicos.salvar_mensagem(self.conn, usuario.chat_id, "user", texto)
        mensagens: list[dict] = servicos.historico(
            self.conn, usuario.chat_id, self.config.historico_max
        )

        resposta_final = ""
        for _ in range(MAX_VOLTAS):
            resposta = await self._chamar(usuario, mensagens)

            if resposta.stop_reason == "refusal":
                return "Não consigo ajudar com isso. Quer tentar de outro jeito?"

            texto_blocos = [b.text for b in resposta.content if b.type == "text" and b.text.strip()]
            usos = [b for b in resposta.content if b.type == "tool_use"]
            if texto_blocos:
                resposta_final = "\n\n".join(texto_blocos).strip()

            if not usos:
                break

            mensagens.append({"role": "assistant", "content": resposta.content})
            resultados = []
            for uso in usos:
                entrada = uso.input if isinstance(uso.input, dict) else json.loads(uso.input or "{}")
                try:
                    conteudo = self._executar(usuario, uso.name, entrada)
                    erro = False
                except Exception as exc:  # a ferramenta falhou: o modelo precisa saber
                    log.exception("ferramenta %s falhou", uso.name)
                    conteudo, erro = f"Erro ao executar {uso.name}: {exc}", True
                resultados.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": uso.id,
                        "content": conteudo,
                        **({"is_error": True} if erro else {}),
                    }
                )
            mensagens.append({"role": "user", "content": resultados})
        else:
            log.warning("limite de voltas atingido para o chat %s", usuario.chat_id)

        resposta_final = resposta_final or "Feito."
        servicos.salvar_mensagem(self.conn, usuario.chat_id, "assistant", resposta_final)
        return resposta_final

    # ----------------------------------------------------------------- #

    async def _chamar(self, usuario: Usuario, mensagens: list[dict]):
        import anthropic

        agora = usuario.agora()
        sistema = INSTRUCOES.format(
            nome=usuario.nome or "sua pessoa",
            dia_semana=NOMES_DIAS[agora.weekday()],
            data=agora.strftime("%d/%m/%Y"),
            hora=agora.strftime("%H:%M"),
            fuso=usuario.fuso,
        )
        parametros = dict(
            model=self.config.modelo,
            max_tokens=self.config.max_tokens,
            system=sistema,
            messages=mensagens,
            tools=FERRAMENTAS,
            output_config={"effort": self.config.esforco},
        )
        if self._fallback:
            try:
                return await self._cliente.beta.messages.create(
                    **parametros,
                    betas=["server-side-fallback-2026-07-01"],
                    fallbacks="default",
                )
            except anthropic.BadRequestError as exc:
                # Conta sem acesso ao beta de fallback: segue sem ele.
                log.warning("fallback do servidor indisponível (%s); seguindo sem ele", exc)
                self._fallback = False
        return await self._cliente.messages.create(**parametros)

    # ----------------------------------------------------------------- #
    # Ferramentas
    # ----------------------------------------------------------------- #

    def _executar(self, usuario: Usuario, nome: str, entrada: dict) -> str:
        atual = servicos.obter_usuario(self.conn, usuario.chat_id) or usuario

        if nome == "criar_compromisso":
            quando = self._ler_data(entrada.get("quando", ""), atual)
            if quando is None:
                return "Não entendi a data. Peça o dia e o horário para a pessoa."
            compromisso = servicos.criar_compromisso(
                self.conn, atual,
                titulo=entrada.get("titulo", "Compromisso"),
                quando=quando,
                duracao_min=int(entrada.get("duracao_min") or 60),
                local=entrada.get("local"),
                observacao=entrada.get("observacao"),
                recorrencia=entrada.get("recorrencia"),
                antecedencia_min=entrada.get("antecedencia_min"),
            )
            return (
                f"Compromisso {compromisso.id} criado: {compromisso.titulo} — "
                f"{formatar_data_hora(compromisso.quando, atual.agora())}."
            )

        if nome == "listar_compromissos":
            return self._listar(atual, entrada.get("periodo", "proximos"), entrada.get("termo"))

        if nome == "atualizar_compromisso":
            id_ = int(entrada["id"])
            if "quando" in entrada and entrada["quando"]:
                quando = self._ler_data(entrada["quando"], atual)
                if quando is None:
                    return "Não entendi a nova data."
                if servicos.reagendar_compromisso(self.conn, atual, id_, quando) is None:
                    return f"Não existe compromisso {id_}."
            recorrencia = entrada.get("recorrencia")
            compromisso = servicos.editar_compromisso(
                self.conn, atual, id_,
                titulo=entrada.get("titulo"),
                local=entrada.get("local"),
                observacao=entrada.get("observacao"),
                recorrencia=None if recorrencia == "nenhuma" else recorrencia,
                antecedencia_min=entrada.get("antecedencia_min"),
            )
            if compromisso is None:
                return f"Não existe compromisso {id_}."
            return f"Atualizado: {compromisso.resumo(atual.agora())}"

        if nome == "mudar_status_compromisso":
            compromisso = servicos.mudar_status(
                self.conn, atual, int(entrada["id"]), entrada["status"]
            )
            if compromisso is None:
                return f"Não existe compromisso {entrada['id']}."
            return f"Compromisso {compromisso.id} agora está {compromisso.status}."

        if nome == "criar_lembrete":
            quando = self._ler_data(entrada.get("quando", ""), atual)
            if quando is None:
                return "Não entendi o horário do lembrete."
            servicos.criar_lembrete_avulso(self.conn, atual, entrada["texto"], quando)
            return f"Lembrete marcado para {formatar_data_hora(quando, atual.agora())}."

        if nome == "salvar_nota":
            nota = servicos.salvar_nota(
                self.conn, atual, entrada["texto"], entrada.get("etiquetas")
            )
            return f"Nota {nota.id} salva."

        if nome == "buscar_notas":
            limite = int(entrada.get("limite") or 10)
            termo = (entrada.get("termo") or "").strip()
            notas = (
                servicos.buscar_notas(self.conn, atual, termo, limite)
                if termo
                else servicos.listar_notas(self.conn, atual, limite)
            )
            if not notas:
                return "Nenhuma nota encontrada."
            return "\n".join(
                f"{n.id}. {n.texto} (salva em {n.criado_em:%d/%m/%Y})" for n in notas
            )

        if nome == "apagar_nota":
            ok = servicos.apagar_nota(self.conn, atual, int(entrada["id"]))
            return "Nota apagada." if ok else f"Não existe nota {entrada['id']}."

        if nome == "ajustar_preferencias":
            novo = servicos.atualizar_preferencias(
                self.conn, atual.chat_id,
                fuso=entrada.get("fuso"),
                hora_resumo=entrada.get("hora_resumo"),
                desligar_resumo=bool(entrada.get("desligar_resumo")),
                antecedencia_min=entrada.get("antecedencia_min"),
            )
            resumo = novo.hora_resumo or "desligado"
            return (
                f"Preferências: fuso {novo.fuso}, resumo diário {resumo}, "
                f"aviso {novo.antecedencia_min} min antes."
            )

        return f"Ferramenta desconhecida: {nome}"

    def _listar(self, usuario: Usuario, periodo: str, termo: str | None) -> str:
        agora = usuario.agora()
        inicio, fim = agora, None
        if periodo == "hoje":
            inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
            fim = inicio + timedelta(days=1)
        elif periodo == "amanha":
            inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            fim = inicio + timedelta(days=1)
        elif periodo == "semana":
            inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
            fim = inicio + timedelta(days=7)
        elif periodo == "mes":
            inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
            fim = inicio + timedelta(days=30)
        elif periodo == "passados":
            inicio, fim = agora - timedelta(days=30), agora

        compromissos = servicos.listar_compromissos(
            self.conn, usuario, inicio=inicio, fim=fim, limite=30
        )
        if termo:
            alvo = termo.lower()
            compromissos = [c for c in compromissos if alvo in c.titulo.lower()]
        if not compromissos:
            return "Nada na agenda nesse período."
        return "\n".join(
            f"{c.id}. {c.titulo} — {formatar_data_hora(c.quando, agora)}"
            + (f" — {c.local}" if c.local else "")
            + (f" — repete {c.recorrencia}" if c.recorrencia else "")
            for c in compromissos
        )

    def _ler_data(self, bruto: str, usuario: Usuario) -> datetime | None:
        """Aceita ISO (o formato pedido ao modelo) e, por segurança, texto solto."""
        bruto = (bruto or "").strip()
        if not bruto:
            return None
        for formato in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S",
                        "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"):
            try:
                return datetime.strptime(bruto, formato).replace(tzinfo=usuario.zona)
            except ValueError:
                continue
        try:
            data = datetime.strptime(bruto, "%Y-%m-%d")
            return data.replace(hour=9, tzinfo=usuario.zona)
        except ValueError:
            pass
        try:  # ISO em outros formatos (com ou sem fuso embutido)
            lido = datetime.fromisoformat(bruto)
            return (
                lido.replace(tzinfo=usuario.zona)
                if lido.tzinfo is None
                else lido.astimezone(usuario.zona)
            )
        except ValueError:
            pass
        interpretado = interpretar_quando(bruto, usuario.agora())
        return interpretado.quando if interpretado else None
