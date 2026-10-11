import pandas as pd

from demanda.dados import black_friday, eventos_calendario, gerar_vendas


def test_black_friday():
    assert black_friday(2023) == pd.Timestamp("2023-11-24")
    assert black_friday(2024) == pd.Timestamp("2024-11-29")
    assert black_friday(2025) == pd.Timestamp("2025-11-28")


def test_eventos_calendario():
    datas = pd.DatetimeIndex(["2025-12-25", "2025-12-20", "2025-11-28", "2025-03-03"])
    eventos = eventos_calendario(datas)
    assert eventos["feriado"].tolist() == [1, 0, 0, 0]
    assert eventos["vespera_natal"].tolist() == [0, 1, 0, 0]
    assert eventos["black_friday"].tolist() == [0, 0, 1, 0]


def test_series_completas_e_reprodutiveis():
    a = gerar_vendas(lojas=2, produtos=3, inicio="2024-01-01", fim="2024-06-30", semente=1)
    b = gerar_vendas(lojas=2, produtos=3, inicio="2024-01-01", fim="2024-06-30", semente=1)
    assert a.equals(b)
    dias = pd.date_range("2024-01-01", "2024-06-30").size
    assert (a.groupby(["loja", "produto"]).size() == dias).all()
    assert (a["vendas"] >= 0).all()
