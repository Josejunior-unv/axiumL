import numpy as np
import pandas as pd
import pytest

from fraude.features import adicionar_features

T0 = pd.Timestamp("2025-06-01 10:00")


def transacoes(linhas):
    df = pd.DataFrame(linhas, columns=["cliente_id", "data_hora", "valor", "categoria"])
    df.insert(0, "transacao_id", range(1, len(df) + 1))
    df["distancia_casa_km"] = 1.0
    df["internacional"] = False
    df["dispositivo_novo"] = False
    df["online"] = False
    df["fraude"] = 0
    return df


@pytest.fixture
def exemplo():
    return transacoes(
        [
            (1, T0, 100.0, "supermercado"),
            (2, T0 + pd.Timedelta(minutes=10), 999.0, "joias"),
            (1, T0 + pd.Timedelta(minutes=30), 50.0, "supermercado"),
            (1, T0 + pd.Timedelta(hours=2), 30.0, "farmacia"),
            (1, T0 + pd.Timedelta(hours=25), 400.0, "eletronicos"),
        ]
    )


def test_janelas_contam_so_o_passado_do_mesmo_cliente(exemplo):
    f = adicionar_features(exemplo)
    assert f["n_transacoes_1h"].tolist() == [0, 0, 1, 0, 0]
    assert f["n_transacoes_24h"].tolist() == [0, 0, 1, 2, 1]
    assert f["valor_24h"].tolist() == [0, 0, 100, 150, 30]
    assert f["n_historico"].tolist() == [0, 0, 1, 2, 3]


def test_razao_e_categoria_nova(exemplo):
    f = adicionar_features(exemplo)
    assert np.isnan(f["razao_valor_media"].iloc[0])
    assert f["razao_valor_media"].iloc[4] == pytest.approx(400 / 60)
    assert f["categoria_nova"].tolist() == [1, 1, 0, 1, 1]
    assert f["minutos_desde_anterior"].iloc[2] == pytest.approx(30)


def test_transacao_futura_nao_altera_o_passado(exemplo):
    antes = adicionar_features(exemplo)
    futura = transacoes([(1, T0 + pd.Timedelta(minutes=40), 5000.0, "joias")])
    futura["transacao_id"] = 99
    depois = adicionar_features(pd.concat([exemplo, futura], ignore_index=True))
    passado = exemplo["data_hora"] < futura["data_hora"].iloc[0]
    pd.testing.assert_frame_equal(antes[passado], depois.iloc[: len(exemplo)][passado])
