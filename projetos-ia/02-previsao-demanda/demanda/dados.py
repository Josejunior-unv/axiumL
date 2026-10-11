"""Vendas diárias sintéticas de uma rede de varejo (lojas x produtos).

Cada série combina nível, tendência, sazonalidade semanal e anual, feriados
nacionais, Black Friday, véspera de Natal, promoções e ruído de contagem.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

FERIADOS_FIXOS = ["01-01", "04-21", "05-01", "09-07", "10-12", "11-02", "11-15", "11-20", "12-25"]

# Peso de cada dia da semana (segunda = 0) por perfil de produto
PERFIS_SEMANAIS = {
    "dia_a_dia": [1.00, 0.95, 0.95, 1.00, 1.10, 1.25, 0.75],
    "fim_de_semana": [0.80, 0.80, 0.85, 0.95, 1.20, 1.55, 0.85],
}


def black_friday(ano: int) -> pd.Timestamp:
    """Sexta-feira seguinte à quarta quinta-feira de novembro (Ação de Graças nos EUA)."""
    primeiro = pd.Timestamp(year=ano, month=11, day=1)
    primeira_quinta = primeiro + pd.Timedelta(days=(3 - primeiro.dayofweek) % 7)
    return primeira_quinta + pd.Timedelta(weeks=3, days=1)


def eventos_calendario(datas: pd.DatetimeIndex) -> pd.DataFrame:
    """Flags de calendário conhecidas com antecedência (usadas também como features)."""
    mes_dia = datas.strftime("%m-%d")
    bf = {black_friday(a) for a in datas.year.unique()}
    natal = pd.to_datetime([f"{a}-12-25" for a in datas.year])
    dias_ate_natal = (natal - datas).days
    return pd.DataFrame(
        {
            "feriado": np.isin(mes_dia, FERIADOS_FIXOS).astype(int),
            "black_friday": datas.isin(bf).astype(int),
            "vespera_natal": ((dias_ate_natal >= 1) & (dias_ate_natal <= 10)).astype(int),
        },
        index=datas,
    )


def gerar_vendas(
    lojas: int = 5,
    produtos: int = 10,
    inicio: str = "2023-01-01",
    fim: str = "2025-12-31",
    semente: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(semente)
    datas = pd.date_range(inicio, fim, freq="D")
    t = np.arange(len(datas)) / 365.25
    eventos = eventos_calendario(datas)

    efeito_eventos = (
        np.where(eventos["feriado"] == 1, 0.6, 1.0)
        * np.where(eventos["black_friday"] == 1, 2.2, 1.0)
        * np.where(eventos["vespera_natal"] == 1, 1.35, 1.0)
    )

    tamanho_loja = rng.lognormal(0, 0.3, lojas)
    nivel_produto = rng.lognormal(2.6, 0.6, produtos)
    perfil_produto = rng.choice(list(PERFIS_SEMANAIS), produtos)
    amplitude_anual = rng.uniform(0.05, 0.35, produtos)
    fase_anual = rng.uniform(0, 2 * np.pi, produtos)
    crescimento = rng.normal(0.06, 0.08, (lojas, produtos))

    blocos = []
    for loja in range(lojas):
        for produto in range(produtos):
            semanal = np.array(PERFIS_SEMANAIS[perfil_produto[produto]])[datas.dayofweek]
            anual = 1 + amplitude_anual[produto] * np.sin(2 * np.pi * t + fase_anual[produto])
            tendencia = np.exp(crescimento[loja, produto] * t)
            promocao = (rng.random(len(datas)) < 0.07).astype(int)
            media = (
                tamanho_loja[loja]
                * nivel_produto[produto]
                * semanal
                * anual
                * tendencia
                * efeito_eventos
                * np.where(promocao == 1, 1.45, 1.0)
            )
            # Poisson com média gama: ruído de contagem com sobredispersão
            vendas = rng.poisson(media * rng.gamma(20, 1 / 20, len(datas)))
            blocos.append(
                pd.DataFrame(
                    {
                        "data": datas,
                        "loja": loja + 1,
                        "produto": produto + 1,
                        "promocao": promocao,
                        "vendas": vendas,
                    }
                )
            )
    return pd.concat(blocos, ignore_index=True)
