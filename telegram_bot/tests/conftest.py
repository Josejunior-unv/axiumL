"""Deixa o pacote `assistente` visível para os testes e cria um banco temporário."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assistente import db, servicos  # noqa: E402
from assistente.config import Config  # noqa: E402

SP = ZoneInfo("America/Sao_Paulo")


@pytest.fixture()
def conn(tmp_path):
    conexao = db.conectar(tmp_path / "teste.db")
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
            caminho_db=tmp_path / "bot.db",
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
        )
        base.update(extras)
        return Config(**base)

    return _config
