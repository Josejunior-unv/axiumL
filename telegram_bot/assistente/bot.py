"""Camada do Telegram: comandos, conversa livre e o laço de lembretes."""

from __future__ import annotations

import logging
from datetime import timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.error import BadRequest, Forbidden
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from . import db, lembretes, servicos
from .config import Config
from .datas import formatar_data_hora, formatar_duracao, interpretar_antecedencia, interpretar_quando
from .ia import Assistente
from .servicos import Usuario

log = logging.getLogger(__name__)

LIMITE_TELEGRAM = 4000

AJUDA = """\
Pode falar comigo normalmente — eu entendo coisas como:
• "dentista quinta às 15h"
• "academia todo dia às 7h"
• "anota que o Wi-Fi do escritório é casa123"
• "o que eu tenho amanhã?"

Se preferir comandos:

Agenda
/agendar <o quê> <quando> — ex.: /agendar reunião sexta 10h
/agenda [hoje|amanha|semana|tudo] — ver o que vem
/adiar <nº> <novo horário> — ex.: /adiar 3 amanhã 9h
/concluir <nº> · /cancelar <nº>
/lembrete <o quê> <quando> — aviso solto, sem entrar na agenda

Anotações
/anotar <texto> — guardar
/notas [busca] — listar ou procurar
/apagar <nº> — apagar uma nota

Ajustes
/config — ver preferências
/fuso <ex.: America/Sao_Paulo>
/resumo <HH:MM|off> — resumo do dia de manhã
/aviso <minutos> — antecedência padrão dos lembretes
/limpar — esquecer o histórico da conversa (agenda e notas ficam)\
"""


# --------------------------------------------------------------------------- #
# Utilidades
# --------------------------------------------------------------------------- #

def _config(context: ContextTypes.DEFAULT_TYPE) -> Config:
    return context.application.bot_data["config"]


def _conn(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["conn"]


def _assistente(context: ContextTypes.DEFAULT_TYPE) -> Assistente:
    return context.application.bot_data["assistente"]


def _permitido(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Bot de uma pessoa só: o primeiro chat vira o dono e os outros ficam de fora."""
    chat = update.effective_chat
    if chat is None:
        return False
    config = _config(context)
    return servicos.autorizar(_conn(context), chat.id, config.chats_permitidos, config.aberto)


def _info_acesso(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> str:
    config = _config(context)
    if config.aberto:
        return "aberto a qualquer pessoa (BOT_ABERTO=1)"
    if config.chats_permitidos:
        return f"restrito à lista do .env (este chat: {chat_id})"
    dono = servicos.obter_dono(_conn(context))
    if dono == chat_id:
        return f"só você (chat {chat_id})"
    return f"outro chat é o dono ({dono})"


def _usuario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Usuario:
    chat = update.effective_chat
    nome = None
    if update.effective_user:
        nome = update.effective_user.first_name or update.effective_user.username
    return servicos.garantir_usuario(
        _conn(context), chat.id, nome, _config(context).fuso_padrao
    )


async def _responder(update: Update, texto: str, **kwargs) -> None:
    """Responde quebrando mensagens longas (o Telegram corta em 4096 caracteres)."""
    alvo = update.effective_message
    if alvo is None:
        return
    while len(texto) > LIMITE_TELEGRAM:
        corte = texto.rfind("\n", 0, LIMITE_TELEGRAM)
        if corte <= 0:
            corte = LIMITE_TELEGRAM
        await alvo.reply_text(texto[:corte])
        texto = texto[corte:].lstrip()
    await alvo.reply_text(texto, **kwargs)


def _lista_compromissos(compromissos, agora, vazio: str) -> str:
    if not compromissos:
        return vazio
    linhas = []
    for c in compromissos:
        linha = f"{c.id}. {c.titulo} — 🕒 {formatar_data_hora(c.quando, agora)}"
        if c.local:
            linha += f" — 📍 {c.local}"
        if c.recorrencia:
            linha += f" — 🔁 {c.recorrencia}"
        linhas.append(linha)
    return "\n".join(linhas)


def _botoes(compromisso_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Feito", callback_data=f"feito:{compromisso_id}"),
                InlineKeyboardButton("⏰ +10 min", callback_data=f"adiar:{compromisso_id}:10"),
                InlineKeyboardButton("⏰ +1 h", callback_data=f"adiar:{compromisso_id}:60"),
            ]
        ]
    )


# --------------------------------------------------------------------------- #
# Comandos
# --------------------------------------------------------------------------- #

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config = _config(context)
    usuario = _usuario(update, context)
    if usuario.hora_resumo is None and config.hora_resumo_padrao:
        usuario = servicos.atualizar_preferencias(
            _conn(context), usuario.chat_id,
            hora_resumo=config.hora_resumo_padrao,
            antecedencia_min=config.antecedencia_padrao,
        )
    nome = usuario.nome or "oi"
    modo = "" if _assistente(context).ativo else (
        "\n\n(No momento estou sem a chave da IA, então entendo datas e guardo notas, "
        "mas converso pouco.)"
    )
    cadeado = ""
    if not _config(context).aberto:
        cadeado = "\n🔒 Este bot é seu: mais ninguém consegue usar.\n"
    await _responder(
        update,
        f"Oi, {nome}! 👋 Eu cuido da sua agenda e guardo o que você quiser lembrar.\n"
        f"{cadeado}\n"
        f"Fuso: {usuario.fuso} · resumo do dia: {usuario.hora_resumo or 'desligado'} · "
        f"aviso {usuario.antecedencia_min} min antes.\n\n" + AJUDA + modo,
    )


async def cmd_ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _responder(update, AJUDA)


async def cmd_agendar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    usuario = _usuario(update, context)
    texto = " ".join(context.args or []).strip()
    if not texto:
        await _responder(update, "Use assim: /agendar dentista quinta às 15h")
        return
    compromisso = _criar_de_texto(_conn(context), usuario, texto)
    if compromisso is None:
        await _responder(update, "Não achei uma data aí. Tente algo como “sexta às 15h”.")
        return
    await _confirmar_criacao(update, usuario, compromisso)


async def cmd_agenda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    usuario = _usuario(update, context)
    agora = usuario.agora()
    periodo = (context.args[0].lower() if context.args else "proximos")
    inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)

    if periodo in {"hoje", "hj"}:
        compromissos = servicos.listar_compromissos(
            _conn(context), usuario, inicio=inicio, fim=inicio + timedelta(days=1)
        )
        titulo, vazio = "📅 Hoje", "Hoje está livre. 🎉"
    elif periodo in {"amanha", "amanhã"}:
        base = inicio + timedelta(days=1)
        compromissos = servicos.listar_compromissos(
            _conn(context), usuario, inicio=base, fim=base + timedelta(days=1)
        )
        titulo, vazio = "📅 Amanhã", "Amanhã está livre."
    elif periodo in {"semana", "7"}:
        compromissos = servicos.listar_compromissos(
            _conn(context), usuario, inicio=inicio, fim=inicio + timedelta(days=7)
        )
        titulo, vazio = "📅 Próximos 7 dias", "Semana livre."
    elif periodo in {"tudo", "todos", "all"}:
        compromissos = servicos.listar_compromissos(_conn(context), usuario, limite=100)
        titulo, vazio = "📅 Tudo que está marcado", "Nada marcado ainda."
    else:
        compromissos = servicos.proximos_compromissos(_conn(context), usuario, limite=10)
        titulo, vazio = "📅 Próximos compromissos", "Nada marcado ainda."

    await _responder(update, f"{titulo}\n\n{_lista_compromissos(compromissos, agora, vazio)}")


async def cmd_adiar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    usuario = _usuario(update, context)
    args = context.args or []
    if len(args) < 2 or not args[0].isdigit():
        await _responder(update, "Use assim: /adiar 3 amanhã às 9h")
        return
    compromisso_id = int(args[0])
    interpretado = interpretar_quando(" ".join(args[1:]), usuario.agora())
    if interpretado is None:
        await _responder(update, "Não entendi o novo horário.")
        return
    compromisso = servicos.reagendar_compromisso(
        _conn(context), usuario, compromisso_id, interpretado.quando
    )
    if compromisso is None:
        await _responder(update, f"Não achei o compromisso {compromisso_id}.")
        return
    await _responder(
        update,
        f"Remarcado: {compromisso.titulo} → "
        f"{formatar_data_hora(compromisso.quando, usuario.agora())} ✅",
    )


async def cmd_concluir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _mudar_status(update, context, "concluido", "Marcado como feito ✅")


async def cmd_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _mudar_status(update, context, "cancelado", "Cancelado 🗑")


async def _mudar_status(
    update: Update, context: ContextTypes.DEFAULT_TYPE, status: str, mensagem: str
) -> None:
    usuario = _usuario(update, context)
    if not context.args or not context.args[0].isdigit():
        await _responder(update, "Diga o número do compromisso (veja em /agenda).")
        return
    compromisso = servicos.mudar_status(
        _conn(context), usuario, int(context.args[0]), status
    )
    if compromisso is None:
        await _responder(update, "Não achei esse compromisso.")
        return
    await _responder(update, f"{mensagem}: {compromisso.titulo}")


async def cmd_lembrete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    usuario = _usuario(update, context)
    texto = " ".join(context.args or []).strip()
    interpretado = interpretar_quando(texto, usuario.agora()) if texto else None
    if interpretado is None:
        await _responder(update, "Use assim: /lembrete tomar remédio às 22h")
        return
    conteudo = interpretado.titulo or "Lembrete"
    servicos.criar_lembrete_avulso(_conn(context), usuario, conteudo, interpretado.quando)
    await _responder(
        update,
        f"Combinado, te aviso {formatar_data_hora(interpretado.quando, usuario.agora())}: {conteudo} ⏰",
    )


async def cmd_anotar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    usuario = _usuario(update, context)
    texto = " ".join(context.args or []).strip()
    if not texto:
        await _responder(update, "Use assim: /anotar o carro está na vaga 42")
        return
    nota = servicos.salvar_nota(_conn(context), usuario, texto)
    await _responder(update, f"Guardado 📝 (nota {nota.id})")


async def cmd_notas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    usuario = _usuario(update, context)
    termo = " ".join(context.args or []).strip()
    notas = (
        servicos.buscar_notas(_conn(context), usuario, termo)
        if termo
        else servicos.listar_notas(_conn(context), usuario)
    )
    if not notas:
        await _responder(update, "Nada encontrado." if termo else "Você ainda não guardou nada.")
        return
    cabecalho = f"📝 Notas com “{termo}”" if termo else "📝 Suas notas"
    corpo = "\n".join(f"{n.id}. {n.texto}  ({n.criado_em:%d/%m})" for n in notas)
    await _responder(update, f"{cabecalho}\n\n{corpo}")


async def cmd_apagar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    usuario = _usuario(update, context)
    if not context.args or not context.args[0].isdigit():
        await _responder(update, "Diga o número da nota (veja em /notas).")
        return
    ok = servicos.apagar_nota(_conn(context), usuario, int(context.args[0]))
    await _responder(update, "Apagada 🗑" if ok else "Não achei essa nota.")


async def cmd_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    usuario = _usuario(update, context)
    ia = "ligada" if _assistente(context).ativo else "desligada (sem ANTHROPIC_API_KEY)"
    await _responder(
        update,
        "⚙️ Preferências\n\n"
        f"Fuso: {usuario.fuso}\n"
        f"Resumo do dia: {usuario.hora_resumo or 'desligado'}\n"
        f"Aviso antes dos compromissos: {formatar_duracao(usuario.antecedencia_min)}\n"
        f"Conversa com IA: {ia}\n"
        f"Acesso: {_info_acesso(context, usuario.chat_id)}\n\n"
        "Mude com /fuso, /resumo e /aviso.",
    )


async def cmd_fuso(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    usuario = _usuario(update, context)
    if not context.args:
        await _responder(update, "Use assim: /fuso America/Sao_Paulo")
        return
    novo = servicos.atualizar_preferencias(_conn(context), usuario.chat_id, fuso=context.args[0])
    await _responder(update, f"Fuso agora é {novo.fuso}. Agora aí são {novo.agora():%H:%M}. 🕒")


async def cmd_resumo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    usuario = _usuario(update, context)
    argumento = (context.args[0] if context.args else "").lower()
    if argumento in {"off", "nao", "não", "desligar", "0"}:
        servicos.atualizar_preferencias(_conn(context), usuario.chat_id, desligar_resumo=True)
        await _responder(update, "Resumo diário desligado.")
        return
    if not argumento:
        await _responder(update, "Use assim: /resumo 08:00 (ou /resumo off)")
        return
    try:
        novo = servicos.atualizar_preferencias(
            _conn(context), usuario.chat_id, hora_resumo=argumento
        )
    except (ValueError, IndexError):
        await _responder(update, "Horário inválido. Exemplo: /resumo 07:30")
        return
    await _responder(update, f"Toda manhã às {novo.hora_resumo} eu te mando o dia. ☀️")


async def cmd_aviso(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    usuario = _usuario(update, context)
    if not context.args or not context.args[0].isdigit():
        await _responder(update, "Use assim: /aviso 30 (minutos antes)")
        return
    novo = servicos.atualizar_preferencias(
        _conn(context), usuario.chat_id, antecedencia_min=int(context.args[0])
    )
    await _responder(
        update,
        f"Vou avisar {formatar_duracao(novo.antecedencia_min)} antes dos próximos compromissos.",
    )


async def cmd_limpar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    usuario = _usuario(update, context)
    servicos.limpar_historico(_conn(context), usuario.chat_id)
    await _responder(update, "Esqueci nossa conversa. Sua agenda e suas notas continuam aqui. 🧠")


# --------------------------------------------------------------------------- #
# Conversa livre
# --------------------------------------------------------------------------- #

async def conversar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _permitido(update, context):
        return
    mensagem = update.effective_message
    if mensagem is None or not mensagem.text:
        return
    usuario = _usuario(update, context)
    assistente = _assistente(context)

    if not assistente.ativo:
        await _offline(update, context, usuario, mensagem.text)
        return

    await context.bot.send_chat_action(chat_id=usuario.chat_id, action=ChatAction.TYPING)
    try:
        resposta = await assistente.responder(usuario, mensagem.text)
    except Exception:
        log.exception("falha ao falar com o modelo")
        await _offline(update, context, usuario, mensagem.text, avisar_erro=True)
        return
    await _responder(update, resposta)


async def _offline(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    usuario: Usuario,
    texto: str,
    avisar_erro: bool = False,
) -> None:
    """Sem IA: ainda dá para agendar e anotar (interpretação por regras)."""
    prefixo = "Tive um problema para pensar agora, mas resolvi no braço:\n\n" if avisar_erro else ""
    compromisso = _criar_de_texto(_conn(context), usuario, texto)
    if compromisso is not None:
        await _confirmar_criacao(update, usuario, compromisso, prefixo)
        return
    nota = servicos.salvar_nota(_conn(context), usuario, texto)
    await _responder(update, f"{prefixo}Guardei isso nas suas notas 📝 (nota {nota.id})")


def _criar_de_texto(conn, usuario: Usuario, texto: str):
    """Interpreta "dentista quinta 15h" e cria o compromisso. None se não houver data."""
    antecedencia, restante = interpretar_antecedencia(texto)
    interpretado = interpretar_quando(restante, usuario.agora())
    if interpretado is None or not interpretado.titulo:
        return None
    return servicos.criar_compromisso(
        conn, usuario,
        titulo=interpretado.titulo,
        quando=interpretado.quando,
        recorrencia=interpretado.recorrencia,
        antecedencia_min=antecedencia,
    )


async def _confirmar_criacao(update: Update, usuario: Usuario, compromisso, prefixo: str = "") -> None:
    extra = f" · repete {compromisso.recorrencia}" if compromisso.recorrencia else ""
    await _responder(
        update,
        f"{prefixo}Anotado ✅ {compromisso.titulo}\n"
        f"🕒 {formatar_data_hora(compromisso.quando, usuario.agora())}{extra}\n"
        f"(nº {compromisso.id} · te aviso antes)",
    )


async def botao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    consulta = update.callback_query
    if consulta is None or not consulta.data or not _permitido(update, context):
        return
    await consulta.answer()
    usuario = servicos.garantir_usuario(_conn(context), consulta.message.chat_id)
    partes = consulta.data.split(":")

    if partes[0] == "feito":
        compromisso = servicos.mudar_status(_conn(context), usuario, int(partes[1]), "concluido")
        texto = f"✅ {compromisso.titulo} — feito!" if compromisso else "Não achei o compromisso."
    elif partes[0] == "adiar":
        compromisso = servicos.obter_compromisso(_conn(context), usuario, int(partes[1]))
        if compromisso is None:
            texto = "Não achei o compromisso."
        else:
            novo_quando = usuario.agora() + timedelta(minutes=int(partes[2]))
            servicos.reagendar_compromisso(_conn(context), usuario, compromisso.id, novo_quando)
            texto = f"⏰ Te lembro de novo {formatar_data_hora(novo_quando, usuario.agora())}."
    else:
        texto = "Não entendi esse botão."

    await consulta.edit_message_text(f"{consulta.message.text}\n\n{texto}")


# --------------------------------------------------------------------------- #
# Laço de lembretes
# --------------------------------------------------------------------------- #

async def tique(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Roda a cada poucos segundos: dispara lembretes e resumos do dia."""
    conn = context.application.bot_data["conn"]
    agora = db.agora_utc()

    for devido in lembretes.lembretes_devidos(conn, agora):
        try:
            await _disparar(context, conn, devido)
        except (Forbidden, BadRequest) as exc:
            # Chat bloqueado ou mensagem inválida: insistir não resolve.
            log.warning("lembrete %s descartado: %s", devido.id, exc)
        except Exception:
            # Provavelmente rede: deixa na fila e tenta no próximo tique.
            log.exception("falha temporária no lembrete %s", devido.id)
            continue
        lembretes.marcar_enviado(conn, devido.id)

    for usuario in lembretes.resumos_pendentes(conn):
        try:
            await _enviar_resumo(context, conn, usuario)
        except Exception:
            log.exception("falha ao enviar resumo para %s", usuario.chat_id)


async def _disparar(context: ContextTypes.DEFAULT_TYPE, conn, devido) -> None:
    usuario = servicos.obter_usuario(conn, devido.chat_id)
    if usuario is None:
        return

    if devido.tipo == "avulso":
        if devido.atrasado:
            return
        await context.bot.send_message(usuario.chat_id, f"⏰ {devido.texto}")
        return

    compromisso = servicos.obter_compromisso(conn, usuario, devido.compromisso_id or -1)
    if compromisso is None or compromisso.status != "ativo":
        return

    if not devido.atrasado:
        if devido.tipo == "antes":
            faltam = int((compromisso.quando - usuario.agora()).total_seconds() // 60)
            quanto = formatar_duracao(max(1, faltam))
            texto = f"⏰ Em {quanto}: {compromisso.titulo}\n🕒 {compromisso.quando:%H:%M}"
        else:
            texto = f"🔔 Agora: {compromisso.titulo}"
        if compromisso.local:
            texto += f"\n📍 {compromisso.local}"
        if compromisso.observacao:
            texto += f"\n💬 {compromisso.observacao}"
        await context.bot.send_message(
            usuario.chat_id, texto, reply_markup=_botoes(compromisso.id)
        )

    if devido.tipo == "na_hora" and compromisso.recorrencia:
        lembretes.avancar_recorrencia(conn, usuario, compromisso)


async def _enviar_resumo(context: ContextTypes.DEFAULT_TYPE, conn, usuario: Usuario) -> None:
    agora = usuario.agora()
    compromissos = servicos.compromissos_do_dia(conn, usuario)
    if compromissos:
        corpo = _lista_compromissos(compromissos, agora, "")
        texto = f"☀️ Bom dia! Seu dia {agora:%d/%m}:\n\n{corpo}"
    else:
        texto = f"☀️ Bom dia! Nada marcado para hoje ({agora:%d/%m}). Dia livre. 🎉"
    await context.bot.send_message(usuario.chat_id, texto)
    servicos.registrar_resumo_enviado(conn, usuario.chat_id, agora.strftime("%Y-%m-%d"))


async def erro(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.exception("erro tratando update", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("Ops, deu ruim aqui. Tenta de novo? 🙃")
        except Exception:
            pass


# --------------------------------------------------------------------------- #
# Montagem
# --------------------------------------------------------------------------- #

def montar(config: Config) -> Application:
    conn = db.conectar(config.banco)
    aplicacao = Application.builder().token(config.token).build()
    aplicacao.bot_data.update(
        {"conn": conn, "config": config, "assistente": Assistente(conn, config)}
    )

    comandos = {
        "start": cmd_start, "ajuda": cmd_ajuda, "help": cmd_ajuda,
        "agendar": cmd_agendar, "agenda": cmd_agenda, "adiar": cmd_adiar,
        "concluir": cmd_concluir, "cancelar": cmd_cancelar, "lembrete": cmd_lembrete,
        "anotar": cmd_anotar, "nota": cmd_anotar, "notas": cmd_notas, "apagar": cmd_apagar,
        "config": cmd_config, "fuso": cmd_fuso, "resumo": cmd_resumo, "aviso": cmd_aviso,
        "limpar": cmd_limpar,
    }
    for nome, funcao in comandos.items():
        aplicacao.add_handler(CommandHandler(nome, _protegido(funcao)))

    aplicacao.add_handler(CallbackQueryHandler(botao))
    aplicacao.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, conversar))
    aplicacao.add_error_handler(erro)

    if aplicacao.job_queue is None:
        log.warning("JobQueue indisponível — instale python-telegram-bot[job-queue]")
    else:
        aplicacao.job_queue.run_repeating(
            tique, interval=config.intervalo_lembretes, first=5, name="lembretes"
        )
    return aplicacao


def _protegido(funcao):
    """Bloqueia chats fora da lista permitida (quando ela existir)."""

    async def embrulho(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not _permitido(update, context):
            await _responder(update, "Este bot é particular. 🙂")
            return
        await funcao(update, context)

    embrulho.__name__ = getattr(funcao, "__name__", "handler")
    return embrulho
