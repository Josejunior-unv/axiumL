"""Base sintética de clientes de uma operadora de telecom.

O churn é sorteado a partir de um modelo logístico com efeitos conhecidos
(contrato mensal, boleto, chamados no suporte, atrasos...). Assim dá para
conferir se o modelo aprende os padrões que de fato existem nos dados.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

CONTRATOS = ["mensal", "anual", "bianual"]
INTERNET = ["fibra", "dsl", "sem_internet"]
PAGAMENTOS = ["boleto", "cartao_credito", "pix", "debito_automatico"]
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]


def gerar_clientes(n: int = 7000, semente: int = 42) -> pd.DataFrame:
    """Gera `n` clientes com a coluna alvo `churn` (0/1)."""
    rng = np.random.default_rng(semente)

    contrato = rng.choice(CONTRATOS, size=n, p=[0.55, 0.25, 0.20])
    internet = rng.choice(INTERNET, size=n, p=[0.45, 0.35, 0.20])
    pagamento = rng.choice(PAGAMENTOS, size=n, p=[0.30, 0.25, 0.25, 0.20])
    regiao = rng.choice(REGIOES, size=n, p=[0.08, 0.27, 0.08, 0.42, 0.15])

    # Contratos longos costumam ter clientes mais antigos
    escala = np.select([contrato == "mensal", contrato == "anual"], [14.0, 30.0], 45.0)
    meses_cliente = np.clip(rng.exponential(escala), 1, 72).round().astype(int)

    idade = np.clip(rng.normal(41, 13, n), 18, 85).round().astype(int)
    dependentes = rng.poisson(0.8, n)
    streaming = rng.random(n) < np.where(internet == "sem_internet", 0.0, 0.5)

    preco_base = np.select([internet == "fibra", internet == "dsl"], [99.0, 69.0], 39.0)
    mensalidade = (preco_base + 25 * streaming + rng.normal(0, 8, n)).round(2)
    total_gasto = (mensalidade * meses_cliente * rng.uniform(0.95, 1.02, n)).round(2)

    chamados_suporte = rng.poisson(np.where(internet == "fibra", 1.6, 1.0))
    atrasos_pagamento = rng.poisson(np.where(pagamento == "boleto", 0.9, 0.35))

    logito = (
        -2.1
        + 1.3 * (contrato == "mensal")
        - 1.1 * (contrato == "bianual")
        - 1.4 * np.log1p(meses_cliente) / np.log(72)
        + 0.5 * (internet == "fibra")
        + 0.35 * chamados_suporte
        # fibra com suporte ruim é a combinação que mais derruba clientes
        + 0.6 * (internet == "fibra") * np.maximum(chamados_suporte - 2, 0)
        + 0.45 * atrasos_pagamento
        + 0.35 * (pagamento == "boleto")
        - 0.5 * (pagamento == "debito_automatico")
        + 0.015 * (mensalidade - 75)
        - 0.15 * dependentes
        - 0.01 * (idade - 41)
    )
    probabilidade = 1 / (1 + np.exp(-logito))
    churn = (rng.random(n) < probabilidade).astype(int)

    return pd.DataFrame(
        {
            "cliente_id": np.arange(1, n + 1),
            "contrato": contrato,
            "internet": internet,
            "pagamento": pagamento,
            "regiao": regiao,
            "meses_cliente": meses_cliente,
            "idade": idade,
            "dependentes": dependentes,
            "streaming": streaming,
            "mensalidade": mensalidade,
            "total_gasto": total_gasto,
            "chamados_suporte": chamados_suporte,
            "atrasos_pagamento": atrasos_pagamento,
            "churn": churn,
        }
    )
