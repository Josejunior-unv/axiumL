import pytest

from agente_sql.banco import criar_banco
from agente_sql.ferramentas import BancoSomenteLeitura


@pytest.fixture(scope="session")
def caminho_banco(tmp_path_factory):
    return criar_banco(tmp_path_factory.mktemp("dados") / "loja.db", clientes=80, pedidos=400, semente=1)


@pytest.fixture
def banco(caminho_banco):
    conexao = BancoSomenteLeitura(caminho_banco, tempo_limite=0.5)
    yield conexao
    conexao.fechar()
