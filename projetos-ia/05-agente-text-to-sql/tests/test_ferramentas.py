import hashlib
import json

import pytest

from agente_sql.ferramentas import BancoSomenteLeitura, ErroConsulta

ESCRITAS = [
    "INSERT INTO produtos (nome, categoria, preco) VALUES ('x', 'y', 1)",
    "UPDATE produtos SET preco = 0",
    "DELETE FROM pedidos",
    "DROP TABLE clientes",
    "CREATE TABLE t (x)",
    "ATTACH DATABASE 'outro.db' AS outro",
    "PRAGMA journal_mode = WAL",
    "PRAGMA writable_schema = 1",
]


def test_leitura(banco):
    resultado = banco.executar_sql("SELECT COUNT(*) AS n FROM pedidos")
    assert resultado == {"colunas": ["n"], "linhas": [[400]], "truncado": False}


@pytest.mark.parametrize("consulta", ESCRITAS)
def test_bloqueia_escrita(banco, caminho_banco, consulta):
    antes = hashlib.sha256(caminho_banco.read_bytes()).hexdigest()
    with pytest.raises(ErroConsulta):
        banco.executar_sql(consulta)
    assert hashlib.sha256(caminho_banco.read_bytes()).hexdigest() == antes


def test_uma_instrucao_por_vez(banco):
    with pytest.raises(ErroConsulta):
        banco.executar_sql("SELECT 1; DROP TABLE clientes")


def test_interrompe_consulta_lenta(banco):
    infinita = "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r) SELECT COUNT(*) FROM r"
    with pytest.raises(ErroConsulta, match="interrompida"):
        banco.executar_sql(infinita)
    # a conexão continua utilizável depois da interrupção
    assert banco.executar_sql("SELECT 1")["linhas"] == [[1]]


def test_trunca_resultados_grandes(caminho_banco):
    banco = BancoSomenteLeitura(caminho_banco, limite_linhas=10)
    resultado = banco.executar_sql("SELECT * FROM itens_pedido")
    assert len(resultado["linhas"]) == 10
    assert resultado["truncado"] is True


def test_esquema(banco):
    tabelas = json.loads(banco.listar_tabelas())["tabelas"]
    assert set(tabelas) == {"clientes", "produtos", "pedidos", "itens_pedido"}

    pedidos = json.loads(banco.descrever_tabela("pedidos"))
    assert [c["nome"] for c in pedidos["colunas"]] == ["id", "cliente_id", "data_pedido", "status", "canal"]
    assert pedidos["chaves_estrangeiras"] == [{"coluna": "cliente_id", "referencia": "clientes.id"}]
    assert len(pedidos["exemplos"]) == 3


def test_tabela_inexistente(banco):
    with pytest.raises(ErroConsulta, match="não existe"):
        banco.descrever_tabela('pedidos"; DROP TABLE clientes; --')
