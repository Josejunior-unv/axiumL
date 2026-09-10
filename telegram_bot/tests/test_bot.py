"""Fiação do bot e o modo offline (sem IA)."""

from telegram.ext import CommandHandler

from assistente import bot, servicos
from assistente.config import Config


def _config(tmp_path, **extras) -> Config:
    base = dict(
        token="123456:TESTE", caminho_db=tmp_path / "bot.db", fuso_padrao="America/Sao_Paulo",
        chats_permitidos=frozenset(), antecedencia_padrao=30, hora_resumo_padrao="08:00",
        intervalo_lembretes=30, chave_anthropic=None, modelo="claude-opus-5",
        esforco="low", max_tokens=16000, usar_fallback=True, historico_max=20,
    )
    base.update(extras)
    return Config(**base)


def test_montar_registra_comandos_e_o_laco_de_lembretes(tmp_path):
    aplicacao = bot.montar(_config(tmp_path))
    comandos = {
        c for h in aplicacao.handlers[0] if isinstance(h, CommandHandler) for c in h.commands
    }
    for esperado in ("start", "agendar", "agenda", "adiar", "anotar", "notas", "config", "resumo"):
        assert esperado in comandos
    assert aplicacao.job_queue is not None
    assert [j.name for j in aplicacao.job_queue.jobs()] == ["lembretes"]


def test_modo_offline_cria_compromisso_a_partir_do_texto(conn, usuario):
    compromisso = bot._criar_de_texto(conn, usuario, "dentista amanhã às 15h me avisa 1h antes")
    assert compromisso is not None
    assert compromisso.titulo == "dentista"
    assert compromisso.quando.hour == 15
    assert compromisso.antecedencia_min == 60


def test_modo_offline_sem_data_nao_cria_nada(conn, usuario):
    assert bot._criar_de_texto(conn, usuario, "o carro está na vaga 42") is None
    assert servicos.proximos_compromissos(conn, usuario) == []


class _MensagemFalsa:
    def __init__(self):
        self.enviadas = []

    async def reply_text(self, texto, **kwargs):
        self.enviadas.append(texto)


class _UpdateFalso:
    def __init__(self, mensagem):
        self.effective_message = mensagem


async def test_mensagem_gigante_e_quebrada_em_pedacos():
    mensagem = _MensagemFalsa()
    await bot._responder(_UpdateFalso(mensagem), "x" * 9000)  # sem quebras de linha
    assert len(mensagem.enviadas) == 3
    assert all(len(p) <= bot.LIMITE_TELEGRAM for p in mensagem.enviadas)
    assert "".join(mensagem.enviadas) == "x" * 9000


async def test_mensagem_longa_quebra_preferindo_a_linha():
    mensagem = _MensagemFalsa()
    texto = ("linha\n" * 900).rstrip()
    await bot._responder(_UpdateFalso(mensagem), texto)
    assert len(mensagem.enviadas) > 1
    assert mensagem.enviadas[0].endswith("linha")
