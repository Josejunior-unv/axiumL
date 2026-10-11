"""Agente que responde perguntas em português consultando o banco com SQL.

O Claude decide quais ferramentas chamar (ver o esquema, rodar consultas,
corrigir erros) até ter a resposta. O código só executa as ferramentas, sempre
pela conexão somente leitura.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field

import anthropic

from agente_sql.ferramentas import BancoSomenteLeitura, ErroConsulta

MODELO = "claude-opus-5-5"

SISTEMA = """Você é um analista de dados que responde perguntas sobre o banco SQLite de uma loja online.

Como trabalhar:
- Confira o esquema com as ferramentas antes de escrever SQL; não adivinhe nomes de tabelas ou colunas.
- O banco é somente leitura e o dialeto é SQLite. Datas são texto no formato AAAA-MM-DD: use strftime para agrupar por mês ou ano.
- Se uma consulta falhar ou trouxer algo estranho, leia o erro, corrija e rode de novo.
- Faturamento é a soma de quantidade * preco_unitario dos itens de pedidos não cancelados, a menos que o usuário defina de outro jeito.

Resposta final, em português do Brasil:
- comece pela resposta direta, com números formatados no padrão brasileiro (R$ 1.234,56);
- depois mostre a consulta SQL final em um bloco ```sql;
- termine com as suposições que você fez, se houver (por exemplo, como tratou pedidos cancelados)."""

FERRAMENTAS = [
    {
        "name": "listar_tabelas",
        "description": "Lista as tabelas do banco e quantas linhas cada uma tem.",
        "input_schema": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        "strict": True,
    },
    {
        "name": "descrever_tabela",
        "description": "Mostra as colunas, tipos, chaves e três linhas de exemplo de uma tabela.",
        "input_schema": {
            "type": "object",
            "properties": {"tabela": {"type": "string", "description": "Nome exato da tabela."}},
            "required": ["tabela"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "executar_sql",
        "description": (
            "Executa uma única consulta SQLite somente leitura (SELECT ou WITH) e devolve as "
            "colunas e até 200 linhas. Se houver mais, 'truncado' vem true: agregue ou use LIMIT."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"consulta": {"type": "string", "description": "Uma consulta SQL."}},
            "required": ["consulta"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


class ErroAgente(Exception):
    pass


@dataclass
class Resposta:
    texto: str
    consultas: list[str] = field(default_factory=list)  # SQL executado com sucesso, em ordem

    @property
    def ultima_consulta(self) -> str | None:
        return self.consultas[-1] if self.consultas else None


class AgenteSQL:
    """Mantém o histórico da conversa, então dá para fazer perguntas de seguimento
    ("e no ano anterior?"). Use `reiniciar()` para começar outra conversa."""

    def __init__(
        self,
        banco: BancoSomenteLeitura,
        cliente: anthropic.Anthropic | None = None,
        modelo: str = MODELO,
        esforco: str = "medium",
        max_passos: int = 15,
        ao_usar_ferramenta: Callable[[str, dict], None] | None = None,
    ):
        self.banco = banco
        self.cliente = cliente if cliente is not None else anthropic.Anthropic()
        self.modelo = modelo
        self.esforco = esforco
        self.max_passos = max_passos
        self.ao_usar_ferramenta = ao_usar_ferramenta
        self.mensagens: list[dict] = []

    def reiniciar(self) -> None:
        self.mensagens = []

    def perguntar(self, pergunta: str) -> Resposta:
        inicio = len(self.mensagens)
        self.mensagens.append({"role": "user", "content": pergunta})
        try:
            return self._rodar()
        except BaseException:
            # Descarta a pergunta que falhou para o histórico continuar válido
            del self.mensagens[inicio:]
            raise

    def _rodar(self) -> Resposta:
        consultas: list[str] = []
        for _ in range(self.max_passos):
            resposta = self.cliente.beta.messages.create(
                model=self.modelo,
                max_tokens=16000,
                system=SISTEMA,
                tools=FERRAMENTAS,
                messages=self.mensagens,
                output_config={"effort": self.esforco},
                cache_control={"type": "ephemeral"},
                # Se o modelo recusar por engano, a API tenta de novo no modelo reserva recomendado
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
            if resposta.stop_reason == "refusal":
                raise ErroAgente("o modelo recusou a pergunta")
            if resposta.stop_reason == "max_tokens":
                raise ErroAgente("a resposta passou do limite de tokens")

            # O conteúdo vai inteiro para o histórico, incluindo os blocos de raciocínio
            self.mensagens.append({"role": "assistant", "content": resposta.content})
            if resposta.stop_reason != "tool_use":
                texto = "\n".join(b.text for b in resposta.content if b.type == "text").strip()
                return Resposta(texto=texto, consultas=consultas)

            resultados = [
                self._executar_ferramenta(bloco, consultas)
                for bloco in resposta.content
                if bloco.type == "tool_use"
            ]
            self.mensagens.append({"role": "user", "content": resultados})
        raise ErroAgente(f"sem resposta depois de {self.max_passos} passos")

    def _executar_ferramenta(self, bloco, consultas: list[str]) -> dict:
        entrada = bloco.input
        if self.ao_usar_ferramenta:
            self.ao_usar_ferramenta(bloco.name, entrada)
        try:
            if bloco.name == "listar_tabelas":
                conteudo = self.banco.listar_tabelas()
            elif bloco.name == "descrever_tabela":
                conteudo = self.banco.descrever_tabela(entrada["tabela"])
            elif bloco.name == "executar_sql":
                resultado = self.banco.executar_sql(entrada["consulta"])
                consultas.append(entrada["consulta"])
                conteudo = json.dumps(resultado, ensure_ascii=False, default=str)
            else:
                raise ErroConsulta(f"ferramenta desconhecida: {bloco.name}")
        except (ErroConsulta, KeyError, TypeError) as erro:
            return {"type": "tool_result", "tool_use_id": bloco.id, "content": f"Erro: {erro}", "is_error": True}
        return {"type": "tool_result", "tool_use_id": bloco.id, "content": conteudo}
