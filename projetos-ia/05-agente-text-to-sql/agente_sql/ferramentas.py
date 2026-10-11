"""Acesso somente leitura ao SQLite: é tudo o que o agente consegue fazer no banco.

A proteção tem três camadas independentes:
1. a conexão abre o arquivo em `mode=ro`, então o SQLite recusa qualquer escrita;
2. um autorizador só libera leitura (SELECT, leitura de colunas, funções e CTEs)
   e duas pragmas de consulta de esquema; ATTACH, PRAGMA de escrita etc. são negados;
3. um tempo limite interrompe consultas que demoram demais.
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

_LIBERADAS = {
    sqlite3.SQLITE_SELECT,
    sqlite3.SQLITE_READ,
    sqlite3.SQLITE_FUNCTION,
    sqlite3.SQLITE_RECURSIVE,
}
_PRAGMAS_LEITURA = {"table_info", "foreign_key_list"}


class ErroConsulta(Exception):
    """Erro que volta para o modelo como resultado da ferramenta, para ele corrigir."""


def _autorizador(acao, arg1, arg2, banco, origem):
    if acao in _LIBERADAS:
        return sqlite3.SQLITE_OK
    if acao == sqlite3.SQLITE_PRAGMA and arg1 in _PRAGMAS_LEITURA:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


class BancoSomenteLeitura:
    def __init__(self, caminho: str | Path, limite_linhas: int = 200, tempo_limite: float = 5.0):
        caminho = Path(caminho).resolve()
        if not caminho.exists():
            raise FileNotFoundError(caminho)
        self.limite_linhas = limite_linhas
        self.tempo_limite = tempo_limite
        self._prazo = float("inf")
        self.conexao = sqlite3.connect(f"{caminho.as_uri()}?mode=ro", uri=True)
        self.conexao.set_authorizer(_autorizador)
        self.conexao.set_progress_handler(self._estourou_o_prazo, 10_000)

    def _estourou_o_prazo(self) -> int:
        return int(time.monotonic() > self._prazo)

    def _traduzir(self, erro: sqlite3.Error) -> ErroConsulta:
        mensagem = str(erro)
        if mensagem == "interrupted":
            mensagem = f"consulta interrompida: passou de {self.tempo_limite:g} s"
        elif mensagem == "not authorized":
            mensagem = "operação não permitida: o banco é somente leitura (use apenas SELECT/WITH)"
        return ErroConsulta(mensagem)

    def _executar(self, consulta: str) -> sqlite3.Cursor:
        self._prazo = time.monotonic() + self.tempo_limite
        try:
            return self.conexao.execute(consulta)
        except sqlite3.Error as erro:
            raise self._traduzir(erro) from erro

    def _tabelas(self) -> list[str]:
        cursor = self._executar(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        return [linha[0] for linha in cursor.fetchall()]

    def listar_tabelas(self) -> str:
        tabelas = {
            nome: self._executar(f'SELECT COUNT(*) FROM "{nome}"').fetchone()[0] for nome in self._tabelas()
        }
        return json.dumps({"tabelas": tabelas}, ensure_ascii=False)

    def descrever_tabela(self, tabela: str) -> str:
        if tabela not in self._tabelas():
            raise ErroConsulta(f"tabela '{tabela}' não existe. Tabelas: {', '.join(self._tabelas())}")
        colunas = [
            {"nome": nome, "tipo": tipo, "chave_primaria": bool(pk)}
            for _, nome, tipo, _, _, pk in self._executar(f'PRAGMA table_info("{tabela}")').fetchall()
        ]
        chaves = [
            {"coluna": origem, "referencia": f"{destino}.{coluna_destino}"}
            for _, _, destino, origem, coluna_destino, *_ in
            self._executar(f'PRAGMA foreign_key_list("{tabela}")').fetchall()
        ]
        cursor = self._executar(f'SELECT * FROM "{tabela}" LIMIT 3')
        exemplos = [dict(zip([c[0] for c in cursor.description], linha)) for linha in cursor.fetchall()]
        return json.dumps(
            {"tabela": tabela, "colunas": colunas, "chaves_estrangeiras": chaves, "exemplos": exemplos},
            ensure_ascii=False,
        )

    def executar_sql(self, consulta: str) -> dict:
        """Roda uma consulta e devolve no máximo `limite_linhas` linhas."""
        cursor = self._executar(consulta)
        if cursor.description is None:
            raise ErroConsulta("a instrução não devolveu linhas; use SELECT")
        try:
            linhas = cursor.fetchmany(self.limite_linhas + 1)
        except sqlite3.Error as erro:
            raise self._traduzir(erro) from erro
        return {
            "colunas": [c[0] for c in cursor.description],
            "linhas": [list(linha) for linha in linhas[: self.limite_linhas]],
            "truncado": len(linhas) > self.limite_linhas,
        }

    def fechar(self) -> None:
        self.conexao.close()
