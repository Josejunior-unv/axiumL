"""Exporta os números reais do projeto para dentro da animação (index.html).

    python animacao/exportar_dados.py

Refaz o gerador para guardar cada componente do sinal de uma série (e confere
que as vendas batem com `gerar_vendas`), roda o backtest de 3 janelas e a
previsão das próximas 4 semanas, e grava tudo no bloco <script id="dados">.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from demanda.dados import PERFIS_SEMANAIS, black_friday, eventos_calendario, gerar_vendas  # noqa: E402
from demanda.modelo import backtest, cobertura, prever_futuro, resumir, wape  # noqa: E402

SEMENTE = 42


def gravar_no_html(dados: dict) -> None:
    pagina = Path(__file__).with_name("index.html")
    bloco = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = pagina.read_text()
    novo, n = re.subn(r'(<script id="dados" type="application/json">).*?(</script>)',
                      lambda m: m.group(1) + bloco + m.group(2), html, flags=re.S)
    assert n == 1, "bloco de dados não encontrado"
    pagina.write_text(novo)
    print(f"{len(bloco) / 1024:.0f} KB de dados gravados em {pagina}")


def componentes(lojas=5, produtos=10, inicio="2023-01-01", fim="2025-12-31", semente=SEMENTE):
    """Mesmo código de `gerar_vendas`, guardando cada fator multiplicativo."""
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
    saida = {}
    for loja in range(lojas):
        for produto in range(produtos):
            semanal = np.array(PERFIS_SEMANAIS[perfil_produto[produto]])[datas.dayofweek]
            anual = 1 + amplitude_anual[produto] * np.sin(2 * np.pi * t + fase_anual[produto])
            tendencia = np.exp(crescimento[loja, produto] * t)
            promocao = (rng.random(len(datas)) < 0.07).astype(int)
            fator_promo = np.where(promocao == 1, 1.45, 1.0)
            nivel = tamanho_loja[loja] * nivel_produto[produto]
            media = nivel * semanal * anual * tendencia * efeito_eventos * fator_promo
            ruido = rng.gamma(20, 1 / 20, len(datas))
            vendas = rng.poisson(media * ruido)
            saida[(loja + 1, produto + 1)] = {
                "nivel": nivel, "tendencia": tendencia, "semanal": semanal, "anual": anual,
                "eventos": efeito_eventos, "promocao": fator_promo, "ruido": ruido,
                "media": media, "vendas": vendas, "perfil": perfil_produto[produto],
                "amplitude": amplitude_anual[produto],
            }
    return datas, saida


def r(x, casas=2):
    return [float(round(float(v), casas)) for v in x]


def main() -> None:
    vendas = gerar_vendas(semente=SEMENTE)
    datas, comps = componentes()
    for (loja, produto), c in comps.items():
        real = vendas[(vendas.loja == loja) & (vendas.produto == produto)]["vendas"].to_numpy()
        assert np.array_equal(real, c["vendas"]), "o gerador refeito não bate com gerar_vendas"

    # série de exemplo: perfil de fim de semana, sazonalidade anual forte e volume médio
    candidatas = [(k, c) for k, c in comps.items() if c["perfil"] == "fim_de_semana" and 12 < c["nivel"] < 45]
    (loja, produto), c = max(candidatas, key=lambda kc: kc[1]["amplitude"])
    print("série de exemplo:", loja, produto, round(c["nivel"], 1), round(c["amplitude"], 2))

    ano = datas.year == 2025
    serie = {
        "loja": loja, "produto": produto, "perfil": c["perfil"],
        "inicio": "2025-01-01",
        "nivel": round(float(c["nivel"]), 2),
        "tendencia": r(c["tendencia"][ano], 3), "semanal": r(c["semanal"][ano], 3),
        "anual": r(c["anual"][ano], 3), "eventos": r(c["eventos"][ano], 3),
        "promocao": r(c["promocao"][ano], 3), "ruido": r(c["ruido"][ano], 3),
        "media": r(c["media"][ano], 2), "vendas": [int(v) for v in c["vendas"][ano]],
    }

    total_dia = vendas.groupby("data")["vendas"].sum()
    eventos = eventos_calendario(pd.DatetimeIndex(total_dia.index))
    calendario = {
        "inicio": str(total_dia.index[0].date()),
        "vendas": [int(v) for v in total_dia.to_numpy()],
        "feriado": [int(v) for v in eventos["feriado"]],
        "black_friday": [int(v) for v in eventos["black_friday"]],
        "vespera_natal": [int(v) for v in eventos["vespera_natal"]],
    }

    resultado = backtest(vendas, janelas=3)
    tabela = resumir(resultado)
    janelas = []
    for origem, jan in resultado.groupby("origem"):
        janelas.append({
            "origem": str(origem.date()),
            **{m: round(wape(jan["vendas"], jan[m]), 3) for m in ("sazonal_ingenuo", "media_4_semanas", "gradient_boosting")},
        })
    exemplo = resultado[(resultado.loja == loja) & (resultado.produto == produto)].sort_values("data")
    primeira_origem = pd.Timestamp(resultado["origem"].min())
    hist = vendas[(vendas.loja == loja) & (vendas.produto == produto)
                  & (vendas.data >= primeira_origem - pd.Timedelta(days=84)) & (vendas.data < primeira_origem)]
    bf = resultado[resultado["data"] == black_friday(2025)]

    # resíduos da série de exemplo: realizado ÷ previsão, para a explicação da perda quantílica
    razao = (exemplo["vendas"] / exemplo["gradient_boosting"]).to_numpy()

    futuro = prever_futuro(vendas)
    total_futuro = futuro.groupby("data")["previsao"].sum()
    ex_futuro = futuro[(futuro.loja == loja) & (futuro.produto == produto)].sort_values("data")
    ev_futuro = eventos_calendario(pd.DatetimeIndex(total_futuro.index))

    # vendas semanais de cada série em 2025, para desenhar os 50 fios que entram no modelo global
    v25 = vendas[vendas.data.dt.year == 2025].copy()
    v25["semana"] = (v25["data"] - pd.Timestamp("2025-01-01")).dt.days // 7
    fios = [[int(x) for x in g.groupby("semana")["vendas"].sum().to_numpy()[:52]]
            for _, g in v25.groupby(["loja", "produto"])]

    dados = {
        "n_series": int(vendas.groupby(["loja", "produto"]).ngroups), "n_linhas": len(vendas),
        "fios": fios,
        "serie": serie, "calendario": calendario,
        "metricas": {m: {k: round(float(v), 3) for k, v in tabela.loc[m].items()} for m in tabela.index},
        "cobertura": round(cobertura(resultado["vendas"], resultado["p10"], resultado["p90"]), 3),
        "janelas": janelas,
        "black_friday": {"data": str(black_friday(2025).date()), "vendas": int(bf["vendas"].sum()),
                         "modelo": int(round(bf["gradient_boosting"].sum())), "media_4_semanas": int(round(bf["media_4_semanas"].sum())),
                         "sazonal_ingenuo": int(round(bf["sazonal_ingenuo"].sum()))},
        "backtest": {
            "historico_inicio": str(hist["data"].min().date()), "historico": [int(v) for v in hist["vendas"]],
            "inicio": str(exemplo["data"].min().date()),
            "origens": sorted({str(pd.Timestamp(o).date()) for o in resultado["origem"]}),
            "vendas": [int(v) for v in exemplo["vendas"]],
            "modelo": r(exemplo["gradient_boosting"], 1), "p10": r(exemplo["p10"], 1), "p90": r(exemplo["p90"], 1),
            "sazonal_ingenuo": r(exemplo["sazonal_ingenuo"], 1), "media_4_semanas": r(exemplo["media_4_semanas"], 1),
            "promocao": [int(v) for v in vendas.set_index(["loja", "produto", "data"]).loc[(loja, produto)].loc[exemplo["data"], "promocao"]],
        },
        "razao_residuos": r(razao, 3),
        "futuro": {
            "inicio": str(total_futuro.index[0].date()),
            "total": [int(round(v)) for v in total_futuro.to_numpy()],
            "feriado": [int(v) for v in ev_futuro["feriado"]],
            "serie": {"previsao": r(ex_futuro["previsao"], 1), "p10": r(ex_futuro["p10"], 1), "p90": r(ex_futuro["p90"], 1)},
        },
    }
    gravar_no_html(dados)


if __name__ == "__main__":
    main()
