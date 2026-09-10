"""Deixa o pacote `assistente` visível para os testes e cria um banco temporário."""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assistente import db, servicos  # noqa: E402
from assistente.config import Config  # noqa: E402

SP = ZoneInfo("America/Sao_Paulo")


TABELAS = ("usuarios", "compromissos", "lembretes", "notas", "mensagens", "configuracao")


def bancos_para_testar():
    """SQLite sempre; Postgres também, se DATABASE_URL_TESTE apontar para um."""
    bancos = ["sqlite"]
    if os.environ.get("DATABASE_URL_TESTE"):
        bancos.append("postgres")
    return bancos


@pytest.fixture(params=bancos_para_testar())
def conn(request, tmp_path):
    """A mesma bateria roda nos dois bancos — é o que garante que dá na mesma."""
    if request.param == "sqlite":
        conexao = db.conectar(tmp_path / "teste.db")
    else:
        conexao = db.conectar(os.environ["DATABASE_URL_TESTE"])
        conexao.execute(
            f"TRUNCATE {', '.join(TABELAS)} RESTART IDENTITY CASCADE"
        )
    yield conexao
    conexao.close()


@pytest.fixture()
def usuario(conn):
    return servicos.garantir_usuario(conn, chat_id=42, nome="Ana")


@pytest.fixture()
def daqui():
    """Ajuda a montar horários futuros no fuso da pessoa."""

    def _daqui(**kwargs):
        return (datetime.now(SP) + timedelta(**kwargs)).replace(second=0, microsecond=0)

    return _daqui


@pytest.fixture()
def config_falsa(tmp_path):
    """Config completa para os testes; sobrescreva o que o teste precisar."""

    def _config(**extras):
        base = dict(
            token="123456:TESTE",
            banco=str(tmp_path / "bot.db"),
            fuso_padrao="America/Sao_Paulo",
            chats_permitidos=frozenset(),
            aberto=False,
            antecedencia_padrao=30,
            hora_resumo_padrao="08:00",
            intervalo_lembretes=30,
            chave_anthropic=None,
            modelo="claude-opus-5",
            esforco="low",
            max_tokens=16000,
            usar_fallback=True,
            historico_max=20,
            porta=None,
        )
        base.update(extras)
        return Config(**base)

    return _config
