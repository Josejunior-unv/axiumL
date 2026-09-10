"""Camada de banco: os dois bancos precisam se comportar igual."""

import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from assistente import db, servicos

URL_PG = os.environ.get("DATABASE_URL_TESTE")
so_com_postgres = pytest.mark.skipif(not URL_PG, reason="sem Postgres para testar")


def test_reconhece_url_de_postgres():
    assert db.e_url_postgres("postgresql://u:s@host/banco") is True
    assert db.e_url_postgres("postgres://u:s@host/banco") is True
    assert db.e_url_postgres("dados/assistente.db") is False
    assert db.e_url_postgres("/var/lib/bot/assistente.db") is False


def test_datas_vao_e_voltam_em_utc():
    sp = ZoneInfo("America/Sao_Paulo")
    momento = datetime(2026, 9, 10, 15, 30, tzinfo=sp)
    texto = db.para_texto(momento)
    assert texto == "2026-09-10 18:30:00"          # São Paulo é UTC-3
    assert db.de_texto(texto, sp) == momento
    assert db.de_texto(texto, timezone.utc).hour == 18


def test_data_sem_fuso_e_recusada():
    with pytest.raises(ValueError):
        db.para_texto(datetime(2026, 9, 10, 15, 30))


def test_ids_novos_vem_certos(conn, usuario, daqui):
    """Vale para os dois bancos: lastrowid no SQLite, RETURNING no Postgres."""
    primeiro = servicos.criar_compromisso(conn, usuario, "Um", daqui(hours=1))
    segundo = servicos.criar_compromisso(conn, usuario, "Dois", daqui(hours=2))
    assert segundo.id > primeiro.id
    assert servicos.obter_compromisso(conn, usuario, segundo.id).titulo == "Dois"


def test_busca_ignora_maiusculas(conn, usuario):
    servicos.salvar_nota(conn, usuario, "Senha do Wi-Fi: CASA123")
    assert servicos.buscar_notas(conn, usuario, "wi-fi")
    assert servicos.buscar_notas(conn, usuario, "casa123")


def test_chat_id_grande_cabe(conn):
    """Id de Telegram passa de 2^31 — precisa de coluna de 64 bits."""
    grande = 8_000_000_000
    servicos.garantir_usuario(conn, grande, "Gigante")
    assert servicos.obter_usuario(conn, grande).nome == "Gigante"


@so_com_postgres
def test_esquemas_batem(tmp_path):
    """As duas versões do esquema não podem sair de sincronia."""
    sqlite = db.conectar(tmp_path / "comparar.db")
    postgres = db.conectar(URL_PG)
    try:
        for tabela in ("usuarios", "compromissos", "lembretes", "notas",
                       "mensagens", "configuracao"):
            colunas_sqlite = {
                linha["name"] for linha in sqlite.execute(f"PRAGMA table_info({tabela})")
            }
            colunas_postgres = {
                linha["column_name"]
                for linha in postgres.execute(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = ?",
                    (tabela,),
                )
            }
            assert colunas_sqlite == colunas_postgres, f"colunas diferentes em {tabela}"
    finally:
        sqlite.close()
        postgres.close()


@so_com_postgres
def test_conexao_derrubada_se_refaz_sozinha(conn):
    """Banco grátis suspende quando fica ocioso; a próxima consulta reconecta."""
    if not isinstance(conn, db.ConexaoPostgres):
        pytest.skip("só vale para o Postgres")
    conn.execute("SELECT 1")
    conn._conn.close()                       # simula a queda
    assert conn.execute("SELECT 1 AS um").fetchone()["um"] == 1
