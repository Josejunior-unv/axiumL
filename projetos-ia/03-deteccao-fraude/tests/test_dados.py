from fraude.dados import gerar_transacoes


def test_reprodutivel_e_ordenado():
    a = gerar_transacoes(clientes=200, dias=30, semente=1)
    b = gerar_transacoes(clientes=200, dias=30, semente=1)
    assert a.equals(b)
    assert a["data_hora"].is_monotonic_increasing
    assert a["transacao_id"].is_unique


def test_fraude_rara_mas_presente():
    df = gerar_transacoes(clientes=1500, dias=60, semente=2)
    assert 0.0005 < df["fraude"].mean() < 0.01
    assert (df["valor"] > 0).all()
