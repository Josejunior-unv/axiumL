"""Fila de lembretes e recorrência.

Os lembretes ficam gravados no banco (tabela ``lembretes``), não em memória.
O bot varre essa fila de tempos em tempos, então nada se perde se o processo
cair e voltar — ao reiniciar, os lembretes atrasados são enviados.
"""

from __future__ import annotations

import sqlite3
from calendar import monthrange
from dataclasses import dataclass
from datetime import datetime, timedelta

from . import db, servicos
from .servicos import Compromisso, Usuario

# Lembretes muito antigos (bot desligado por dias) são descartados em vez de
# inundarem o chat quando ele voltar.
TOLERANCIA_ATRASO = timedelta(hours=6)


@dataclass
class LembreteDevido:
    id: int
    chat_id: int
    tipo: str
    texto: str | None
    compromisso_id: int | None
    disparo: datetime  # em UTC
    atrasado: bool


def lembretes_devidos(
    conn: sqlite3.Connection, agora: datetime, limite: int = 50
) -> list[LembreteDevido]:
    """Lembretes ainda não enviados cujo horário já chegou."""
    linhas = conn.execute(
        """SELECT * FROM lembretes
           WHERE enviado = 0 AND disparo_utc <= ?
           ORDER BY disparo_utc ASC LIMIT ?""",
        (db.para_texto(agora), int(limite)),
    ).fetchall()
    devidos = []
    for linha in linhas:
        disparo = datetime.strptime(linha["disparo_utc"], db.FORMATO_UTC).replace(
            tzinfo=agora.tzinfo
        )
        devidos.append(
            LembreteDevido(
                id=linha["id"],
                chat_id=linha["chat_id"],
                tipo=linha["tipo"],
                texto=linha["texto"],
                compromisso_id=linha["compromisso_id"],
                disparo=disparo,
                atrasado=(agora - disparo) > TOLERANCIA_ATRASO,
            )
        )
    return devidos


def marcar_enviado(conn: sqlite3.Connection, lembrete_id: int) -> None:
    conn.execute("UPDATE lembretes SET enviado = 1 WHERE id = ?", (lembrete_id,))
    conn.commit()


def proxima_ocorrencia(quando: datetime, recorrencia: str | None) -> datetime | None:
    """Próxima data de um compromisso que se repete."""
    if recorrencia == "diaria":
        return quando + timedelta(days=1)
    if recorrencia == "semanal":
        return quando + timedelta(days=7)
    if recorrencia == "mensal":
        ano = quando.year + (1 if quando.month == 12 else 0)
        mes = 1 if quando.month == 12 else quando.month + 1
        dia = min(quando.day, monthrange(ano, mes)[1])
        return quando.replace(year=ano, month=mes, day=dia)
    return None


def avancar_recorrencia(
    conn: sqlite3.Connection, usuario: Usuario, compromisso: Compromisso
) -> Compromisso | None:
    """Depois que um compromisso repetido acontece, joga ele para a próxima data."""
    proxima = proxima_ocorrencia(compromisso.quando, compromisso.recorrencia)
    if proxima is None:
        return None
    # Se o bot ficou fora do ar, pula as ocorrências que já passaram.
    agora = usuario.agora()
    while proxima <= agora:
        seguinte = proxima_ocorrencia(proxima, compromisso.recorrencia)
        if seguinte is None:
            break
        proxima = seguinte
    return servicos.reagendar_compromisso(conn, usuario, compromisso.id, proxima)


def resumos_pendentes(conn: sqlite3.Connection) -> list[Usuario]:
    """Usuários que já passaram do horário do resumo diário e ainda não o receberam."""
    pendentes = []
    for linha in conn.execute("SELECT * FROM usuarios WHERE hora_resumo IS NOT NULL"):
        usuario = servicos._para_usuario(linha)
        agora = usuario.agora()
        hora, minuto = (int(p) for p in usuario.hora_resumo.split(":"))
        alvo = agora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
        hoje = agora.strftime("%Y-%m-%d")
        if usuario.ultimo_resumo == hoje:
            continue
        if alvo <= agora <= alvo + TOLERANCIA_ATRASO:
            pendentes.append(usuario)
    return pendentes
