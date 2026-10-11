from churn.dados import gerar_clientes


def test_gera_base_reprodutivel():
    a = gerar_clientes(500, semente=1)
    b = gerar_clientes(500, semente=1)
    assert a.equals(b)
    assert len(a) == 500
    assert a["cliente_id"].is_unique


def test_valores_plausiveis():
    df = gerar_clientes(3000, semente=7)
    assert df["meses_cliente"].between(1, 72).all()
    assert (df["mensalidade"] > 0).all()
    assert 0.15 < df["churn"].mean() < 0.40


def test_contrato_mensal_cancela_mais():
    df = gerar_clientes(5000, semente=3)
    taxa = df.groupby("contrato")["churn"].mean()
    assert taxa["mensal"] > taxa["anual"] > taxa["bianual"]
