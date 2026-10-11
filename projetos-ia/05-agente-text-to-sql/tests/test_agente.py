"""Testa o laço do agente com um cliente falso que devolve respostas roteirizadas,
sem chamar a API."""

from types import SimpleNamespace as NS

import pytest

from agente_sql.agente import MODELO, AgenteSQL, ErroAgente


def texto(t):
    return NS(type="text", text=t)


def ferramenta(id_, nome, **entrada):
    return NS(type="tool_use", id=id_, name=nome, input=entrada)


def resposta(stop_reason, *blocos):
    return NS(stop_reason=stop_reason, content=list(blocos))


class ClienteFalso:
    def __init__(self, *respostas):
        self.respostas = list(respostas)
        self.chamadas = []
        self.beta = NS(messages=NS(create=self._create))

    def _create(self, **kwargs):
        self.chamadas.append({**kwargs, "messages": list(kwargs["messages"])})
        return self.respostas.pop(0)


def test_fluxo_completo(banco):
    cliente = ClienteFalso(
        resposta("tool_use", ferramenta("t1", "listar_tabelas")),
        resposta("tool_use", texto("Vou contar."), ferramenta("t2", "executar_sql",
                                                              consulta="SELECT COUNT(*) FROM clientes")),
        resposta("end_turn", texto("Temos 80 clientes.")),
    )
    r = AgenteSQL(banco, cliente=cliente).perguntar("Quantos clientes temos?")

    assert r.texto == "Temos 80 clientes."
    assert r.ultima_consulta == "SELECT COUNT(*) FROM clientes"
    primeira = cliente.chamadas[0]
    assert primeira["model"] == MODELO
    assert primeira["fallbacks"] == "default"
    assert [f["name"] for f in primeira["tools"]] == ["listar_tabelas", "descrever_tabela", "executar_sql"]

    resultado_sql = cliente.chamadas[2]["messages"][-1]["content"][0]
    assert resultado_sql["tool_use_id"] == "t2"
    assert "[[80]]" in resultado_sql["content"]


def test_erro_de_sql_volta_para_o_modelo(banco):
    cliente = ClienteFalso(
        resposta("tool_use", ferramenta("t1", "executar_sql", consulta="DROP TABLE clientes")),
        resposta("end_turn", texto("Não posso apagar tabelas.")),
    )
    r = AgenteSQL(banco, cliente=cliente).perguntar("Apague a tabela de clientes")

    erro = cliente.chamadas[1]["messages"][-1]["content"][0]
    assert erro["is_error"] is True
    assert "somente leitura" in erro["content"]
    assert r.consultas == []


def test_chamadas_paralelas_voltam_juntas(banco):
    cliente = ClienteFalso(
        resposta("tool_use", ferramenta("a", "descrever_tabela", tabela="pedidos"),
                 ferramenta("b", "descrever_tabela", tabela="itens_pedido")),
        resposta("end_turn", texto("ok")),
    )
    AgenteSQL(banco, cliente=cliente).perguntar("Como os pedidos se ligam aos itens?")
    resultados = cliente.chamadas[1]["messages"][-1]["content"]
    assert [r["tool_use_id"] for r in resultados] == ["a", "b"]


def test_conversa_guarda_historico(banco):
    cliente = ClienteFalso(
        resposta("end_turn", texto("Primeira.")),
        resposta("end_turn", texto("Segunda.")),
    )
    agente = AgenteSQL(banco, cliente=cliente)
    agente.perguntar("Pergunta 1")
    agente.perguntar("E agora?")
    historico = cliente.chamadas[1]["messages"]
    assert [m["role"] for m in historico] == ["user", "assistant", "user"]
    agente.reiniciar()
    assert agente.mensagens == []


def test_recusa_nao_suja_o_historico(banco):
    cliente = ClienteFalso(
        resposta("end_turn", texto("Oi.")),
        resposta("tool_use", ferramenta("t1", "listar_tabelas")),
        resposta("refusal"),
    )
    agente = AgenteSQL(banco, cliente=cliente)
    agente.perguntar("Olá")
    with pytest.raises(ErroAgente, match="recusou"):
        agente.perguntar("Outra coisa")
    assert len(agente.mensagens) == 2


def test_limite_de_passos(banco):
    cliente = ClienteFalso(*[resposta("tool_use", ferramenta(f"t{i}", "listar_tabelas")) for i in range(3)])
    with pytest.raises(ErroAgente, match="3 passos"):
        AgenteSQL(banco, cliente=cliente, max_passos=3).perguntar("?")
