"""Regras de negócio: compromissos, lembretes, notas e preferências.

Esta camada não sabe nada sobre Telegram nem sobre IA — ela é usada tanto pelos
comandos (`/agendar`, `/agenda`, ...) quanto pelas ferramentas que o Claude
chama durante a conversa. Assim os dois caminhos escrevem exatamente os mesmos
dados no banco.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from . import db
from .datas import formatar_data_hora

RECORRENCIAS = {"diaria", "semanal", "mensal"}
STATUS_VALIDOS = {"ativo", "concluido", "cancelado"}


@dataclass
class Usuario:
    chat_id: int
    nome: str | None
    fuso: str
    hora_resumo: str | None
    antecedencia_min: int
    ultimo_resumo: str | None

    @property
    def zona(self) -> ZoneInfo:
        return zona_valida(self.fuso)

    def agora(self) -> datetime:
        return datetime.now(self.zona).replace(microsecond=0)


@dataclass
class Compromisso:
    id: int
    chat_id: int
    titulo: str
    quando: datetime          # já no fuso da pessoa
    duracao_min: int
    local: str | None
    observacao: str | None
    recorrencia: str | None
    antecedencia_min: int | None
    status: str

    def resumo(self, agora: datetime | None = None) -> str:
        partes = [f"{self.id}. {self.titulo}", f"🕒 {formatar_data_hora(self.quando, agora)}"]
        if self.local:
            partes.append(f"📍 {self.local}")
        if self.recorrencia:
            partes.append(f"🔁 {self.recorrencia}")
        return " — ".join(partes)


@dataclass
class Nota:
    id: int
    chat_id: int
    texto: str
    etiquetas: str | None
    criado_em: datetime


def zona_valida(nome: str) -> ZoneInfo:
    try:
        return ZoneInfo(nome)
    except (ZoneInfoNotFoundError, ValueError, KeyError):
        return ZoneInfo("America/Sao_Paulo")


# --------------------------------------------------------------------------- #
# Usuário / preferências
# --------------------------------------------------------------------------- #

def garantir_usuario(
    conn: sqlite3.Connection,
    chat_id: int,
    nome: str | None = None,
    fuso_padrao: str = "America/Sao_Paulo",
) -> Usuario:
    linha = conn.execute("SELECT * FROM usuarios WHERE chat_id = ?", (chat_id,)).fetchone()
    if linha is None:
        conn.execute(
            "INSERT INTO usuarios (chat_id, nome, fuso, criado_em) VALUES (?, ?, ?, ?)",
            (chat_id, nome, fuso_padrao, db.agora_utc().strftime(db.FORMATO_UTC)),
        )
        conn.commit()
        linha = conn.execute("SELECT * FROM usuarios WHERE chat_id = ?", (chat_id,)).fetchone()
    elif nome and not linha["nome"]:
        conn.execute("UPDATE usuarios SET nome = ? WHERE chat_id = ?", (nome, chat_id))
        conn.commit()
        linha = conn.execute("SELECT * FROM usuarios WHERE chat_id = ?", (chat_id,)).fetchone()
    return _para_usuario(linha)


def obter_usuario(conn: sqlite3.Connection, chat_id: int) -> Usuario | None:
    linha = conn.execute("SELECT * FROM usuarios WHERE chat_id = ?", (chat_id,)).fetchone()
    return _para_usuario(linha) if linha else None


def atualizar_preferencias(
    conn: sqlite3.Connection,
    chat_id: int,
    *,
    nome: str | None = None,
    fuso: str | None = None,
    hora_resumo: str | None = None,
    desligar_resumo: bool = False,
    antecedencia_min: int | None = None,
) -> Usuario:
    campos, valores = [], []
    if nome is not None:
        campos.append("nome = ?"); valores.append(nome)
    if fuso is not None:
        campos.append("fuso = ?"); valores.append(str(zona_valida(fuso)))
    if desligar_resumo:
        campos.append("hora_resumo = NULL")
    elif hora_resumo is not None:
        campos.append("hora_resumo = ?"); valores.append(_hora_valida(hora_resumo))
    if antecedencia_min is not None:
        campos.append("antecedencia_min = ?"); valores.append(max(0, int(antecedencia_min)))
    if campos:
        valores.append(chat_id)
        conn.execute(f"UPDATE usuarios SET {', '.join(campos)} WHERE chat_id = ?", valores)
        conn.commit()
    usuario = obter_usuario(conn, chat_id)
    assert usuario is not None
    return usuario


def _hora_valida(bruto: str) -> str:
    bruto = bruto.strip().replace("h", ":").rstrip(":")
    partes = bruto.split(":")
    hora = int(partes[0])
    minuto = int(partes[1]) if len(partes) > 1 and partes[1] else 0
    return f"{time(hora, minuto):%H:%M}"


def _para_usuario(linha: sqlite3.Row) -> Usuario:
    return Usuario(
        chat_id=linha["chat_id"],
        nome=linha["nome"],
        fuso=linha["fuso"],
        hora_resumo=linha["hora_resumo"],
        antecedencia_min=linha["antecedencia_min"],
        ultimo_resumo=linha["ultimo_resumo"],
    )


# --------------------------------------------------------------------------- #
# Compromissos
# --------------------------------------------------------------------------- #

def criar_compromisso(
    conn: sqlite3.Connection,
    usuario: Usuario,
    titulo: str,
    quando: datetime,
    *,
    duracao_min: int = 60,
    local: str | None = None,
    observacao: str | None = None,
    recorrencia: str | None = None,
    antecedencia_min: int | None = None,
) -> Compromisso:
    if not titulo.strip():
        titulo = "Compromisso"
    if recorrencia and recorrencia not in RECORRENCIAS:
        recorrencia = None
    if quando.tzinfo is None:
        quando = quando.replace(tzinfo=usuario.zona)

    cur = conn.execute(
        """INSERT INTO compromissos
           (chat_id, titulo, quando_utc, duracao_min, local, observacao,
            recorrencia, antecedencia_min, status, criado_em)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ativo', ?)""",
        (
            usuario.chat_id, titulo.strip(), db.para_texto(quando), int(duracao_min),
            local, observacao, recorrencia, antecedencia_min,
            db.agora_utc().strftime(db.FORMATO_UTC),
        ),
    )
    compromisso_id = int(cur.lastrowid)
    _agendar_lembretes(conn, usuario, compromisso_id, quando, antecedencia_min)
    conn.commit()
    obtido = obter_compromisso(conn, usuario, compromisso_id)
    assert obtido is not None
    return obtido


def obter_compromisso(
    conn: sqlite3.Connection, usuario: Usuario, compromisso_id: int
) -> Compromisso | None:
    linha = conn.execute(
        "SELECT * FROM compromissos WHERE id = ? AND chat_id = ?",
        (compromisso_id, usuario.chat_id),
    ).fetchone()
    return _para_compromisso(linha, usuario) if linha else None


def listar_compromissos(
    conn: sqlite3.Connection,
    usuario: Usuario,
    *,
    inicio: datetime | None = None,
    fim: datetime | None = None,
    status: str | None = "ativo",
    limite: int = 50,
) -> list[Compromisso]:
    sql = "SELECT * FROM compromissos WHERE chat_id = ?"
    params: list = [usuario.chat_id]
    if status:
        sql += " AND status = ?"
        params.append(status)
    if inicio is not None:
        sql += " AND quando_utc >= ?"
        params.append(db.para_texto(inicio))
    if fim is not None:
        sql += " AND quando_utc <= ?"
        params.append(db.para_texto(fim))
    sql += " ORDER BY quando_utc ASC LIMIT ?"
    params.append(int(limite))
    return [_para_compromisso(l, usuario) for l in conn.execute(sql, params)]


def compromissos_do_dia(
    conn: sqlite3.Connection, usuario: Usuario, dia: datetime | None = None
) -> list[Compromisso]:
    base = dia or usuario.agora()
    inicio = base.replace(hour=0, minute=0, second=0, microsecond=0)
    return listar_compromissos(conn, usuario, inicio=inicio, fim=inicio + timedelta(days=1))


def proximos_compromissos(
    conn: sqlite3.Connection, usuario: Usuario, limite: int = 10
) -> list[Compromisso]:
    return listar_compromissos(conn, usuario, inicio=usuario.agora(), limite=limite)


def reagendar_compromisso(
    conn: sqlite3.Connection, usuario: Usuario, compromisso_id: int, novo_quando: datetime
) -> Compromisso | None:
    compromisso = obter_compromisso(conn, usuario, compromisso_id)
    if compromisso is None:
        return None
    if novo_quando.tzinfo is None:
        novo_quando = novo_quando.replace(tzinfo=usuario.zona)
    conn.execute(
        "UPDATE compromissos SET quando_utc = ?, status = 'ativo' WHERE id = ? AND chat_id = ?",
        (db.para_texto(novo_quando), compromisso_id, usuario.chat_id),
    )
    _limpar_lembretes(conn, compromisso_id)
    _agendar_lembretes(conn, usuario, compromisso_id, novo_quando, compromisso.antecedencia_min)
    conn.commit()
    return obter_compromisso(conn, usuario, compromisso_id)


def editar_compromisso(
    conn: sqlite3.Connection,
    usuario: Usuario,
    compromisso_id: int,
    *,
    titulo: str | None = None,
    local: str | None = None,
    observacao: str | None = None,
    recorrencia: str | None = None,
    antecedencia_min: int | None = None,
) -> Compromisso | None:
    compromisso = obter_compromisso(conn, usuario, compromisso_id)
    if compromisso is None:
        return None
    campos, valores = [], []
    if titulo:
        campos.append("titulo = ?"); valores.append(titulo.strip())
    if local is not None:
        campos.append("local = ?"); valores.append(local or None)
    if observacao is not None:
        campos.append("observacao = ?"); valores.append(observacao or None)
    if recorrencia is not None:
        campos.append("recorrencia = ?")
        valores.append(recorrencia if recorrencia in RECORRENCIAS else None)
    if antecedencia_min is not None:
        campos.append("antecedencia_min = ?"); valores.append(max(0, int(antecedencia_min)))
    if campos:
        valores += [compromisso_id, usuario.chat_id]
        conn.execute(
            f"UPDATE compromissos SET {', '.join(campos)} WHERE id = ? AND chat_id = ?", valores
        )
        if antecedencia_min is not None:
            atual = obter_compromisso(conn, usuario, compromisso_id)
            if atual is not None:
                _limpar_lembretes(conn, compromisso_id)
                _agendar_lembretes(
                    conn, usuario, compromisso_id, atual.quando, atual.antecedencia_min
                )
        conn.commit()
    return obter_compromisso(conn, usuario, compromisso_id)


def mudar_status(
    conn: sqlite3.Connection, usuario: Usuario, compromisso_id: int, status: str
) -> Compromisso | None:
    if status not in STATUS_VALIDOS:
        raise ValueError(f"status inválido: {status}")
    compromisso = obter_compromisso(conn, usuario, compromisso_id)
    if compromisso is None:
        return None
    conn.execute(
        "UPDATE compromissos SET status = ? WHERE id = ? AND chat_id = ?",
        (status, compromisso_id, usuario.chat_id),
    )
    if status != "ativo":
        _limpar_lembretes(conn, compromisso_id)
    conn.commit()
    return obter_compromisso(conn, usuario, compromisso_id)


def _para_compromisso(linha: sqlite3.Row, usuario: Usuario) -> Compromisso:
    return Compromisso(
        id=linha["id"],
        chat_id=linha["chat_id"],
        titulo=linha["titulo"],
        quando=db.de_texto(linha["quando_utc"], usuario.zona),
        duracao_min=linha["duracao_min"],
        local=linha["local"],
        observacao=linha["observacao"],
        recorrencia=linha["recorrencia"],
        antecedencia_min=linha["antecedencia_min"],
        status=linha["status"],
    )


# --------------------------------------------------------------------------- #
# Lembretes
# --------------------------------------------------------------------------- #

def _agendar_lembretes(
    conn: sqlite3.Connection,
    usuario: Usuario,
    compromisso_id: int,
    quando: datetime,
    antecedencia_min: int | None,
) -> None:
    antecedencia = usuario.antecedencia_min if antecedencia_min is None else antecedencia_min
    agora = db.agora_utc()
    criado = agora.strftime(db.FORMATO_UTC)

    disparos: list[tuple[str, datetime]] = []
    if antecedencia > 0:
        disparos.append(("antes", quando - timedelta(minutes=antecedencia)))
    disparos.append(("na_hora", quando))

    for tipo, momento in disparos:
        if momento.astimezone(agora.tzinfo) <= agora:
            continue  # já passou; não adianta agendar
        conn.execute(
            """INSERT INTO lembretes (compromisso_id, chat_id, disparo_utc, tipo, criado_em)
               VALUES (?, ?, ?, ?, ?)""",
            (compromisso_id, usuario.chat_id, db.para_texto(momento), tipo, criado),
        )


def _limpar_lembretes(conn: sqlite3.Connection, compromisso_id: int) -> None:
    conn.execute(
        "DELETE FROM lembretes WHERE compromisso_id = ? AND enviado = 0", (compromisso_id,)
    )


def criar_lembrete_avulso(
    conn: sqlite3.Connection, usuario: Usuario, texto: str, quando: datetime
) -> int:
    """Lembrete solto ("me lembra de tomar o remédio às 22h"), sem compromisso."""
    cur = conn.execute(
        """INSERT INTO lembretes (compromisso_id, chat_id, disparo_utc, tipo, texto, criado_em)
           VALUES (NULL, ?, ?, 'avulso', ?, ?)""",
        (
            usuario.chat_id, db.para_texto(quando), texto.strip(),
            db.agora_utc().strftime(db.FORMATO_UTC),
        ),
    )
    conn.commit()
    return int(cur.lastrowid)


def registrar_resumo_enviado(conn: sqlite3.Connection, chat_id: int, dia_local: str) -> None:
    conn.execute("UPDATE usuarios SET ultimo_resumo = ? WHERE chat_id = ?", (dia_local, chat_id))
    conn.commit()


# --------------------------------------------------------------------------- #
# Notas
# --------------------------------------------------------------------------- #

def salvar_nota(
    conn: sqlite3.Connection, usuario: Usuario, texto: str, etiquetas: str | None = None
) -> Nota:
    cur = conn.execute(
        "INSERT INTO notas (chat_id, texto, etiquetas, criado_em) VALUES (?, ?, ?, ?)",
        (
            usuario.chat_id, texto.strip(), etiquetas,
            db.agora_utc().strftime(db.FORMATO_UTC),
        ),
    )
    conn.commit()
    linha = conn.execute("SELECT * FROM notas WHERE id = ?", (cur.lastrowid,)).fetchone()
    return _para_nota(linha, usuario)


def listar_notas(conn: sqlite3.Connection, usuario: Usuario, limite: int = 20) -> list[Nota]:
    linhas = conn.execute(
        "SELECT * FROM notas WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
        (usuario.chat_id, int(limite)),
    )
    return [_para_nota(l, usuario) for l in linhas]


def buscar_notas(
    conn: sqlite3.Connection, usuario: Usuario, termo: str, limite: int = 20
) -> list[Nota]:
    padrao = f"%{termo.strip()}%"
    linhas = conn.execute(
        """SELECT * FROM notas
           WHERE chat_id = ? AND (texto LIKE ? OR IFNULL(etiquetas, '') LIKE ?)
           ORDER BY id DESC LIMIT ?""",
        (usuario.chat_id, padrao, padrao, int(limite)),
    )
    return [_para_nota(l, usuario) for l in linhas]


def apagar_nota(conn: sqlite3.Connection, usuario: Usuario, nota_id: int) -> bool:
    cur = conn.execute(
        "DELETE FROM notas WHERE id = ? AND chat_id = ?", (nota_id, usuario.chat_id)
    )
    conn.commit()
    return cur.rowcount > 0


def _para_nota(linha: sqlite3.Row, usuario: Usuario) -> Nota:
    return Nota(
        id=linha["id"],
        chat_id=linha["chat_id"],
        texto=linha["texto"],
        etiquetas=linha["etiquetas"],
        criado_em=db.de_texto(linha["criado_em"], usuario.zona),
    )


# --------------------------------------------------------------------------- #
# Histórico da conversa (memória curta usada pela IA)
# --------------------------------------------------------------------------- #

def salvar_mensagem(conn: sqlite3.Connection, chat_id: int, papel: str, conteudo: str) -> None:
    conn.execute(
        "INSERT INTO mensagens (chat_id, papel, conteudo, criado_em) VALUES (?, ?, ?, ?)",
        (chat_id, papel, conteudo, db.agora_utc().strftime(db.FORMATO_UTC)),
    )
    conn.commit()


def historico(conn: sqlite3.Connection, chat_id: int, limite: int = 20) -> list[dict]:
    """Histórico pronto para a API: começa em 'user' e sem papéis repetidos seguidos."""
    linhas = conn.execute(
        "SELECT papel, conteudo FROM mensagens WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
        (chat_id, int(limite)),
    ).fetchall()

    mensagens: list[dict] = []
    for linha in reversed(linhas):
        papel, conteudo = linha["papel"], linha["conteudo"]
        if not mensagens and papel != "user":
            continue  # a conversa precisa começar por uma mensagem da pessoa
        if mensagens and mensagens[-1]["role"] == papel:
            mensagens[-1]["content"] += f"\n{conteudo}"  # junta papéis repetidos
        else:
            mensagens.append({"role": papel, "content": conteudo})
    return mensagens


def limpar_historico(conn: sqlite3.Connection, chat_id: int) -> None:
    conn.execute("DELETE FROM mensagens WHERE chat_id = ?", (chat_id,))
    conn.commit()
