"""Deixa o pacote `assistente` visível para os testes e cria um banco temporário."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assistente import db, servicos  # noqa: E402

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
