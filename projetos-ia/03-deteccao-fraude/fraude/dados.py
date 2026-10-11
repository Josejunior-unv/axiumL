"""Transações de cartão sintéticas com fraudes raras e realistas.

Cada cliente tem hábitos próprios (valor típico, horário, categorias, celular).
Alguns cartões são comprometidos: o fraudador faz um teste com valor baixo e
depois uma rajada de compras altas, de madrugada, em aparelho novo, longe de
casa. Também há "ruído legítimo" (viagens, compras grandes, troca de celular)
para o problema não ficar fácil demais.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

CATEGORIAS = [
    "supermercado", "restaurante", "combustivel", "farmacia", "vestuario",
    "eletronicos", "viagem", "joias", "gift_card", "streaming",
]
PESOS_LEGITIMOS = np.array([0.24, 0.20, 0.13, 0.10, 0.10, 0.05, 0.04, 0.02, 0.02, 0.10])
PESOS_FRAUDE = np.array([0.10, 0.06, 0.05, 0.03, 0.12, 0.25, 0.07, 0.10, 0.17, 0.05])


def gerar_transacoes(
    clientes: int = 3000,
    dias: int = 120,
    taxa_comprometidos: float = 0.04,
    semente: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(semente)
    inicio = pd.Timestamp("2025-06-01")

    valor_tipico = rng.lognormal(4.0, 0.6, clientes)
    frequencia = rng.lognormal(-1.0, 0.5, clientes)  # transações por dia
    hora_preferida = rng.normal(14, 4, clientes)
    tem_vida_noturna = rng.random(clientes) < 0.08

    linhas = []
    for c in range(clientes):
        visitas = rng.poisson(frequencia[c] * dias * 0.75)
        if visitas == 0:
            continue
        dia = np.floor(rng.uniform(0, dias, visitas))
        hora = rng.normal(hora_preferida[c], 3.5, visitas)
        # Sessões de compra: parte das visitas tem outras compras minutos depois
        extras = rng.geometric(0.6, visitas) - 1
        dia, hora = np.repeat(dia, extras + 1), np.repeat(hora, extras + 1)
        hora = hora + np.concatenate([np.r_[0, rng.exponential(0.7, k)].cumsum() for k in extras])
        n = len(dia)
        if tem_vida_noturna[c]:
            hora = np.where(rng.random(n) < 0.4, rng.uniform(0, 5, n), hora)
        hora = np.clip(hora, 0, 23.99)
        viajando = rng.random(n) < 0.05
        linhas.append(
            pd.DataFrame(
                {
                    "cliente_id": c + 1,
                    "data_hora": inicio + pd.to_timedelta(dia + hora / 24, unit="D"),
                    "valor": valor_tipico[c] * rng.lognormal(0, 0.7, n)
                    * np.where(rng.random(n) < 0.03, rng.uniform(3, 10, n), 1.0),
                    "categoria": rng.choice(CATEGORIAS, n, p=PESOS_LEGITIMOS),
                    "distancia_casa_km": np.where(
                        viajando, rng.uniform(300, 3000, n), rng.exponential(8, n)
                    ),
                    "internacional": viajando & (rng.random(n) < 0.3),
                    "dispositivo_novo": rng.random(n) < 0.03,
                    "online": rng.random(n) < 0.35,
                    "fraude": 0,
                }
            )
        )

    comprometidos = rng.choice(clientes, int(clientes * taxa_comprometidos), replace=False)
    for c in comprometidos:
        n = rng.integers(2, 8)
        comeco = rng.uniform(10, dias - 1)
        # rajada de horas ou dias, começando de madrugada em quase metade dos casos
        duracao = rng.choice([4, 12, 48])
        horas = np.sort(rng.uniform(0, duracao, n)) + np.where(rng.random() < 0.45, 0, rng.uniform(6, 15))
        momentos = np.floor(comeco) + horas / 24
        valores = valor_tipico[c] * rng.uniform(1.5, 8, n)
        valores[0] = rng.uniform(1, 5)  # transação de teste
        estrangeiro = rng.random() < 0.25
        linhas.append(
            pd.DataFrame(
                {
                    "cliente_id": c + 1,
                    "data_hora": inicio + pd.to_timedelta(momentos, unit="D"),
                    "valor": valores,
                    "categoria": rng.choice(CATEGORIAS, n, p=PESOS_FRAUDE),
                    "distancia_casa_km": np.where(
                        rng.random(n) < 0.5, rng.exponential(25, n), rng.uniform(100, 8000, n)
                    ),
                    "internacional": np.full(n, estrangeiro),
                    "dispositivo_novo": rng.random(n) < 0.45,
                    "online": rng.random(n) < 0.7,
                    "fraude": 1,
                }
            )
        )

    df = pd.concat(linhas, ignore_index=True)
    df["valor"] = df["valor"].round(2)
    df["distancia_casa_km"] = df["distancia_casa_km"].round(1)
    df = df.sort_values("data_hora", kind="stable").reset_index(drop=True)
    df.insert(0, "transacao_id", np.arange(1, len(df) + 1))
    return df
