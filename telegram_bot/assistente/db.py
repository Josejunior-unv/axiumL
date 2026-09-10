"""Banco de dados (SQLite) do assistente.

Tudo é guardado em um único arquivo `.db`, então dá para rodar o bot em
qualquer lugar (VPS, Raspberry Pi, o próprio computador) sem instalar serviço
nenhum. Basta fazer backup desse arquivo.

Datas são guardadas SEMPRE em UTC, no formato ``YYYY-MM-DD HH:MM:SS`` — assim a
comparação alfabética no SQL equivale à comparação cronológica. A conversão
para o fuso da pessoa acontece na camada de serviços.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

FORMATO_UTC = "%Y-%m-%d %H:%M:%S"

ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    chat_id           INTEGER PRIMARY KEY,
    nome              TEXT,
    fuso              TEXT    NOT NULL DEFAULT 'America/Sao_Paulo',
    hora_resumo       TEXT,                       -- 'HH:MM' ou NULL (sem resumo diário)
    antecedencia_min  INTEGER NOT NULL DEFAULT 30,
    ultimo_resumo     TEXT,                       -- 'YYYY-MM-DD' (data local do último resumo)
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
    recorrencia       TEXT,                       -- NULL | diaria | semanal | mensal
    antecedencia_min  INTEGER,
    status            TEXT    NOT NULL DEFAULT 'ativo',   -- ativo | concluido | cancelado
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
    tipo             TEXT    NOT NULL,            -- antes | na_hora | avulso
    texto            TEXT,                        -- usado pelos lembretes avulsos
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
    papel      TEXT    NOT NULL,                  -- user | assistant
    conteudo   TEXT    NOT NULL,
    criado_em  TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_mensagens_chat ON mensagens (chat_id, id DESC);
"""


def conectar(caminho: str | Path) -> sqlite3.Connection:
    """Abre (e cria, se preciso) o banco no caminho indicado."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(caminho, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(ESQUEMA)
    conn.commit()
    return conn


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
