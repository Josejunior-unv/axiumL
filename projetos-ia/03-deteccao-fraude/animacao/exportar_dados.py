"""Exporta os números reais do projeto para dentro da animação (index.html).

    python animacao/exportar_dados.py

Gera as transações, calcula as features, treina os detectores como em
`fraude.avaliar` e grava no bloco <script id="dados"> da página: um cartão
comprometido real, a nuvem de pontos do teste, a posição de cada fraude no
ranking de cada detector e as métricas.
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

from fraude.dados import gerar_transacoes  # noqa: E402
from fraude.features import adicionar_features  # noqa: E402
from fraude.modelo import (  # noqa: E402
    DetectorAnomalia,
    DetectorSupervisionado,
    avaliar,
    pontuacao_regras,
    separar_por_tempo,
)

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


def r(v, c=3):
    v = float(v)
    return None if np.isnan(v) else round(v, c)


def main() -> None:
    df = adicionar_features(gerar_transacoes(semente=SEMENTE))
    treino, teste = separar_por_tempo(df)
    inicio = df["data_hora"].min().normalize()
    gb = DetectorSupervisionado().fit(treino)
    iso = DetectorAnomalia().fit(treino)
    gba = DetectorSupervisionado(usar_anomalia=True).fit(treino)
    notas = {
        "regras_de_negocio": pontuacao_regras(teste),
        "isolation_forest": iso.pontuar(teste),
        "gradient_boosting": gb.pontuar(teste),
        "gb_mais_anomalia": gba.pontuar(teste),
    }
    teste = teste.assign(nota_gb=notas["gradient_boosting"], nota_if=notas["isolation_forest"])
    y = teste["fraude"].to_numpy()

    metricas = {orc: {nome: {k: round(v, 3) for k, v in avaliar(y, p, teste["valor"], orc).items()}
                      for nome, p in notas.items()} for orc in (0.005, 0.01)}

    # posição (0 = mais suspeita) de cada fraude no ranking de cada detector
    posicoes = {}
    for nome, p in notas.items():
        ordem = np.argsort(-p, kind="stable")
        rank = np.empty(len(p), dtype=int); rank[ordem] = np.arange(len(p))
        posicoes[nome] = sorted(int(v) for v in rank[y == 1])

    # o caso: cartão comprometido com a rajada no teste e várias transações
    rajadas = teste[teste.fraude == 1].groupby("cliente_id").size()
    candidatos = rajadas[rajadas.between(5, 7)].index
    def pontos_do_caso(c):
        f = teste[(teste.cliente_id == c) & (teste.fraude == 1)]
        return f["dispositivo_novo"].sum() + (f["hora"] < 6).sum() + f["internacional"].sum()
    caso_id = max(candidatos, key=pontos_do_caso)
    caso = df[df.cliente_id == caso_id].sort_values("data_hora")
    caso_notas = gb.pontuar(caso)
    colunas = ["valor", "categoria", "distancia_casa_km", "dispositivo_novo", "internacional", "online", "fraude",
               "n_transacoes_1h", "n_transacoes_24h", "n_transacoes_7d", "valor_24h", "razao_valor_media",
               "minutos_desde_anterior", "categoria_nova", "n_historico"]
    caso_json = []
    for (_, t), nota in zip(caso.iterrows(), caso_notas):
        item = {"h": round((t["data_hora"] - inicio).total_seconds() / 3600, 3), "nota": r(nota, 4)}
        for c in colunas:
            v = t[c]
            item[c] = v if isinstance(v, str) else r(v, 2)
        caso_json.append(item)

    # nuvem 3D: amostra de legítimas do teste + todas as fraudes do teste
    rng = np.random.default_rng(3)
    legit = teste[teste.fraude == 0]
    amostra = pd.concat([legit.iloc[rng.choice(len(legit), 1400, replace=False)], teste[teste.fraude == 1]])
    nuvem = [[r(np.log10(max(a.razao_valor_media, 0.01)) if not np.isnan(a.razao_valor_media) else 0.0, 3),
              r(np.log10(1 + (a.minutos_desde_anterior if not np.isnan(a.minutos_desde_anterior) else 1e4)), 3),
              r(np.log10(1 + a.distancia_casa_km), 3), r(a.nota_gb, 4), int(a.fraude),
              r(a.log_valor, 3), r(a.nota_if, 4), int(a.internacional)] for a in amostra.itertuples()]

    # fila do analista: as transações mais suspeitas do teste pelo gradient boosting
    fila = teste.sort_values("nota_gb", ascending=False).head(14)
    fila_json = [{"h": round((t.data_hora - inicio).total_seconds() / 3600, 2), "valor": r(t.valor, 2),
                  "categoria": t.categoria, "nota": r(t.nota_gb, 4), "fraude": int(t.fraude),
                  "novo": int(t.dispositivo_novo), "intl": int(t.internacional)} for t in fila.itertuples()]

    # linha do tempo: transações e fraudes por dia, e o corte treino/teste
    dia = ((df["data_hora"] - inicio).dt.total_seconds() // 86400).astype(int)
    por_dia = df.groupby(dia).agg(n=("fraude", "size"), f=("fraude", "sum"))
    corte = (treino["data_hora"].max() - inicio).total_seconds() / 86400

    # quantas rajadas ficariam dos dois lados num corte aleatório 75/25 das transações
    fraudes = df[df.fraude == 1]
    divididas = []
    for s in range(50):
        sorteio = np.random.default_rng(s).random(len(fraudes)) < 0.75
        lados = pd.Series(sorteio, index=fraudes.index).groupby(fraudes["cliente_id"]).agg(["min", "max"])
        divididas.append(float((lados["min"] != lados["max"]).mean()))

    # nota mínima para entrar na fila, para cada orçamento de alertas
    ordenadas = np.sort(notas["gradient_boosting"])[::-1]
    orcamentos = [round(v, 4) for v in np.geomspace(0.001, 0.05, 40)]
    cortes_gb = [[o, r(ordenadas[max(1, int(round(len(ordenadas) * o))) - 1], 5)] for o in orcamentos]

    # cada rajada: dia em que começou e quantas transações teve; quantas cruzam o corte no tempo
    por_cliente = fraudes.groupby("cliente_id")["data_hora"].agg(["min", "max", "size"]).sort_values("min")
    rajadas = [[round((m - inicio).total_seconds() / 86400, 2), int(n)] for m, n in zip(por_cliente["min"], por_cliente["size"])]
    limite = treino["data_hora"].max()
    cruzam = int(((por_cliente["min"] <= limite) & (por_cliente["max"] > limite)).sum())

    dados = {
        "cortes_gb": cortes_gb, "rajadas": rajadas, "rajadas_divididas_tempo": cruzam,
        "n_transacoes": len(df), "n_fraudes": int(df.fraude.sum()), "n_clientes": int(df.cliente_id.nunique()),
        "n_treino": len(treino), "n_teste": len(teste), "fraudes_teste": int(y.sum()),
        "valor_fraude_teste": round(float(teste.loc[teste.fraude == 1, "valor"].sum()), 2),
        "metricas": metricas, "posicoes": posicoes,
        "caso": {"cliente": int(caso_id), "transacoes": caso_json},
        "nuvem": nuvem, "fila": fila_json,
        "por_dia": {"n": [int(v) for v in por_dia["n"]], "f": [int(v) for v in por_dia["f"]]},
        "corte_dia": round(corte, 2),
        "rajadas_divididas": round(float(np.mean(divididas)), 3),
        "n_rajadas": int(fraudes["cliente_id"].nunique()),
    }
    gravar_no_html(dados)


if __name__ == "__main__":
    main()
