"""Banco de dados: SQLite por padrão, Postgres quando hospedado.

Local, num VPS ou num Raspberry Pi, o padrão é um arquivo SQLite — simples de
copiar e de fazer backup. Em hospedagens com disco volátil (Render e afins), o
arquivo sumiria a cada deploy, então basta apontar ``DATABASE_URL`` para um
Postgres externo e o mesmo código passa a gravar lá.

Datas são guardadas SEMPRE em UTC, como texto ``YYYY-MM-DD HH:MM:SS`` — nos dois
bancos, para a comparação alfabética no SQL equivaler à cronológica. A conversão
para o fuso da pessoa acontece na camada de serviços.
"""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Union

FORMATO_UTC = "%Y-%m-%d %H:%M:%S"

# As duas versões do esquema precisam andar juntas; o teste
# `test_esquemas_batem` compara as colunas das duas quando há Postgres à mão.
ESQUEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS usuarios (
    chat_id           INTEGER PRIMARY KEY,
    nome              TEXT,
    fuso              TEXT    NOT NULL DEFAULT 'America/Sao_Paulo',
    hora_resumo       TEXT,
    antecedencia_min  INTEGER NOT NULL DEFAULT 30,
    ultimo_resumo     TEXT,
    criado_em         TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS compromissos (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id           INTEGER NOT NULL,
    titulo            TEXT    NOT NULL,
    quando_utc        TEXT    NOT NULL,
    duracao_min       INTEGER NOT NULL DEFAULT 60,
    local             TEXT,
    observacao        TEXT,
    recorrencia       TEXT,
    antecedencia_min  INTEGER,
    status            TEXT    NOT NULL DEFAULT 'ativo',
    criado_em         TEXT    NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES usuarios (chat_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_compromissos_agenda
    ON compromissos (chat_id, status, quando_utc);

CREATE TABLE IF NOT EXISTS lembretes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    compromisso_id   INTEGER,
    chat_id          INTEGER NOT NULL,
    disparo_utc      TEXT    NOT NULL,
    tipo             TEXT    NOT NULL,
    texto            TEXT,
    enviado          INTEGER NOT NULL DEFAULT 0,
    criado_em        TEXT    NOT NULL,
    FOREIGN KEY (compromisso_id) REFERENCES compromissos (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_lembretes_fila
    ON lembretes (enviado, disparo_utc);

CREATE TABLE IF NOT EXISTS notas (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id    INTEGER NOT NULL,
    texto      TEXT    NOT NULL,
    etiquetas  TEXT,
    criado_em  TEXT    NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES usuarios (chat_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notas_chat ON notas (chat_id, criado_em DESC);

CREATE TABLE IF NOT EXISTS mensagens (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id    INTEGER NOT NULL,
    papel      TEXT    NOT NULL,
    conteudo   TEXT    NOT NULL,
    criado_em  TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_mensagens_chat ON mensagens (chat_id, id DESC);

CREATE TABLE IF NOT EXISTS configuracao (
    chave  TEXT PRIMARY KEY,
    valor  TEXT
);
"""

# BIGINT nos chat_id: id de Telegram já passa do limite de 32 bits.
ESQUEMA_POSTGRES = """
CREATE TABLE IF NOT EXISTS usuarios (
    chat_id           BIGINT PRIMARY KEY,
    nome              TEXT,
    fuso              TEXT    NOT NULL DEFAULT 'America/Sao_Paulo',
    hora_resumo       TEXT,
    antecedencia_min  INTEGER NOT NULL DEFAULT 30,
    ultimo_resumo     TEXT,
    criado_em         TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS compromissos (
    id                BIGSERIAL PRIMARY KEY,
    chat_id           BIGINT  NOT NULL,
    titulo            TEXT    NOT NULL,
    quando_utc        TEXT    NOT NULL,
    duracao_min       INTEGER NOT NULL DEFAULT 60,
    local             TEXT,
    observacao        TEXT,
    recorrencia       TEXT,
    antecedencia_min  INTEGER,
    status            TEXT    NOT NULL DEFAULT 'ativo',
    criado_em         TEXT    NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES usuarios (chat_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_compromissos_agenda
    ON compromissos (chat_id, status, quando_utc);

CREATE TABLE IF NOT EXISTS lembretes (
    id               BIGSERIAL PRIMARY KEY,
    compromisso_id   BIGINT,
    chat_id          BIGINT  NOT NULL,
    disparo_utc      TEXT    NOT NULL,
    tipo             TEXT    NOT NULL,
    texto            TEXT,
    enviado          INTEGER NOT NULL DEFAULT 0,
    criado_em        TEXT    NOT NULL,
    FOREIGN KEY (compromisso_id) REFERENCES compromissos (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_lembretes_fila
    ON lembretes (enviado, disparo_utc);

CREATE TABLE IF NOT EXISTS notas (
    id         BIGSERIAL PRIMARY KEY,
    chat_id    BIGINT NOT NULL,
    texto      TEXT   NOT NULL,
    etiquetas  TEXT,
    criado_em  TEXT   NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES usuarios (chat_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notas_chat ON notas (chat_id, criado_em DESC);

CREATE TABLE IF NOT EXISTS mensagens (
    id         BIGSERIAL PRIMARY KEY,
    chat_id    BIGINT NOT NULL,
    papel      TEXT   NOT NULL,
    conteudo   TEXT   NOT NULL,
    criado_em  TEXT   NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_mensagens_chat ON mensagens (chat_id, id DESC);

CREATE TABLE IF NOT EXISTS configuracao (
    chave  TEXT PRIMARY KEY,
    valor  TEXT
);
"""


class ConexaoPostgres:
    """Conexão Postgres com a mesma cara da do sqlite3.

    Duas diferenças do driver são resolvidas aqui: o marcador de parâmetro
    (``?`` vira ``%s``) e a queda da conexão ociosa — hospedagens gratuitas
    suspendem o banco depois de alguns minutos parado, então a consulta é
    refeita uma vez com a conexão nova.
    """

    def __init__(self, url: str):
        self.url = url
        self._conn = None
        self._abrir()
        self.executescript(ESQUEMA_POSTGRES)

    def _abrir(self) -> None:
        import psycopg
        from psycopg.rows import dict_row

        # autocommit: cada comando vale por si, sem transação pendurada
        # esperando uma conexão que pode cair a qualquer momento.
        self._conn = psycopg.connect(self.url, autocommit=True, row_factory=dict_row)

    def execute(self, sql: str, params: Iterable[Any] = ()):
        import psycopg

        consulta = sql.replace("?", "%s")
        valores = tuple(params)
        try:
            return self._conn.execute(consulta, valores)
        except (psycopg.OperationalError, psycopg.InterfaceError):
            self._abrir()  # o banco tinha suspendido; tenta de novo, uma vez só
            return self._conn.execute(consulta, valores)

    def executescript(self, script: str) -> None:
        for comando in _separar_comandos(script):
            self.execute(comando)

    def commit(self) -> None:
        pass  # já está em autocommit

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()


Conexao = Union[sqlite3.Connection, ConexaoPostgres]


def _separar_comandos(script: str) -> list[str]:
    return [c.strip() for c in script.split(";") if c.strip()]


def e_url_postgres(destino: str) -> bool:
    return bool(re.match(r"^(postgres|postgresql)(\+\w+)?://", destino.strip(), re.I))


def conectar(destino: str | Path) -> Conexao:
    """Abre o banco. Aceita caminho de arquivo (SQLite) ou URL do Postgres."""
    if e_url_postgres(str(destino)):
        return ConexaoPostgres(str(destino))

    caminho = Path(destino)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(caminho, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(ESQUEMA_SQLITE)
    conn.commit()
    return conn


def inserir(conn: Conexao, sql: str, params: Iterable[Any]) -> int:
    """INSERT que devolve o id novo nos dois bancos."""
    if isinstance(conn, ConexaoPostgres):
        linha = conn.execute(f"{sql} RETURNING id", params).fetchone()
        return int(linha["id"])
    return int(conn.execute(sql, tuple(params)).lastrowid)


def agora_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def para_texto(quando: datetime) -> str:
    """datetime com fuso -> texto UTC guardável."""
    if quando.tzinfo is None:
        raise ValueError("datetime sem fuso; use um datetime ciente do fuso")
    return quando.astimezone(timezone.utc).strftime(FORMATO_UTC)


def de_texto(texto: str, fuso) -> datetime:
    """Texto UTC do banco -> datetime no fuso da pessoa."""
    bruto = datetime.strptime(texto, FORMATO_UTC).replace(tzinfo=timezone.utc)
    return bruto.astimezone(fuso)
