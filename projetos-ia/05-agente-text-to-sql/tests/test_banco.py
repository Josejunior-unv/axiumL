import sqlite3

from agente_sql.banco import criar_banco


def _resumo(caminho):
    with sqlite3.connect(caminho) as c:
        return c.execute(
            "SELECT (SELECT COUNT(*) FROM itens_pedido), (SELECT SUM(preco_unitario) FROM itens_pedido),"
            " (SELECT GROUP_CONCAT(nome) FROM clientes)"
        ).fetchone()


def test_banco_reprodutivel(tmp_path):
    a = criar_banco(tmp_path / "a.db", clientes=40, pedidos=150, semente=9)
    b = criar_banco(tmp_path / "b.db", clientes=40, pedidos=150, semente=9)
    assert _resumo(a) == _resumo(b)


def test_integridade(caminho_banco):
    with sqlite3.connect(caminho_banco) as c:
        assert c.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0] == 400
        orfaos = c.execute(
            "SELECT COUNT(*) FROM itens_pedido i LEFT JOIN pedidos p ON p.id = i.pedido_id WHERE p.id IS NULL"
        ).fetchone()[0]
        assert orfaos == 0
        # nenhum pedido antes do cadastro do cliente
        antes = c.execute(
            "SELECT COUNT(*) FROM pedidos p JOIN clientes c ON c.id = p.cliente_id"
            " WHERE p.data_pedido < c.data_cadastro"
        ).fetchone()[0]
        assert antes == 0
