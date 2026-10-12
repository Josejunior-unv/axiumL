"""Exporta os números reais do projeto para dentro da animação (index.html).

    python animacao/exportar_dados.py

Treina o pipeline como `churn.treinar` (mesma semente e mesma divisão) e grava
no bloco <script id="dados"> da página: coeficientes do modelo para o simulador,
superfície de probabilidade, curva de lucro, validação cruzada e amostra de clientes.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from churn.dados import gerar_clientes  # noqa: E402
from churn.modelo import (  # noqa: E402
    CATEGORICAS,
    ENTRADAS,
    NUMERICAS,
    candidatos,
    importancia_variaveis,
    limiar_otimo,
    lucro_campanha,
    validar_candidatos,
)

SEMENTE = 42
GRUPOS = {
    "meses_cliente": "tempo", "log_meses_cliente": "tempo", "cliente_novo": "tempo",
    "mensalidade": "gasto", "total_gasto": "gasto", "gasto_medio_mensal": "gasto",
    "chamados_suporte": "chamados", "atrasos_pagamento": "atrasos", "idade": "idade",
    "dependentes": "dependentes", "streaming": "streaming", "contrato": "contrato",
    "internet": "internet", "pagamento": "pagamento", "regiao": "regiao",
}


def gravar_no_html(dados: dict) -> None:
    pagina = Path(__file__).with_name("index.html")
    bloco = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = pagina.read_text()
    novo, n = re.subn(r'(<script id="dados" type="application/json">).*?(</script>)',
                      lambda m: m.group(1) + bloco + m.group(2), html, flags=re.S)
    assert n == 1, "bloco de dados não encontrado"
    pagina.write_text(novo)
    print(f"{len(bloco) / 1024:.0f} KB de dados gravados em {pagina}")


def r(x, casas=4):
    return float(round(float(x), casas))


def main() -> None:
    df = gerar_clientes(7000, SEMENTE)
    X, y = df[ENTRADAS], df["churn"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEMENTE)

    validacao = validar_candidatos(X_tr, y_tr, SEMENTE)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMENTE)
    folds = list(cv.split(X_tr, y_tr))
    validacao_json = []
    for res in validacao:
        por_fold = [r(roc_auc_score(y_tr.iloc[te], res.probabilidades[te]), 3) for _, te in folds]
        validacao_json.append({"nome": res.nome, "roc_auc": r(res.roc_auc, 3),
                               "pr_auc": r(res.pr_auc, 3), "folds": por_fold})
    vencedor = validacao[0]
    valor_tr = (X_tr["mensalidade"] * 12).to_numpy()
    limiar, _ = limiar_otimo(y_tr.to_numpy(), vencedor.probabilidades, valor_tr)

    pipeline = candidatos(SEMENTE)[vencedor.nome].fit(X_tr, y_tr)
    prob_te = pipeline.predict_proba(X_te)[:, 1]
    y_np, valor_te = y_te.to_numpy(), (X_te["mensalidade"] * 12).to_numpy()

    limiares = np.round(np.arange(0.02, 0.981, 0.01), 2)
    curva = [
        {"t": float(t),
         "lucro": r(lucro_campanha(y_np, prob_te, valor_te, t), 2),
         "lucro_oof": r(lucro_campanha(y_tr.to_numpy(), vencedor.probabilidades, valor_tr, t), 2),
         "acionados": int((prob_te >= t).sum()),
         "churn_acionados": int(y_np[prob_te >= t].sum())}
        for t in limiares
    ]

    # Parâmetros exatos do pipeline, para o simulador recalcular a probabilidade no navegador
    prep, modelo = pipeline.named_steps["prep"], pipeline.named_steps["modelo"]
    escala = prep.named_transformers_["num"]
    onehot = prep.named_transformers_["cat"]
    coef = modelo.coef_[0]
    # Média de cada coluna transformada no treino: a referência das contribuições (SHAP linear)
    transformado_tr = prep.transform(pipeline.named_steps["features"].transform(X_tr))
    media_tr = np.asarray(transformado_tr.mean(axis=0)).ravel()
    parametros = {
        "intercepto": r(modelo.intercept_[0], 6),
        "numericas": [{"nome": n, "media": r(m, 6), "escala": r(s, 6), "coef": r(c, 6)}
                      for n, m, s, c in zip(NUMERICAS, escala.mean_, escala.scale_, coef[:len(NUMERICAS)])],
        "categoricas": [],
    }
    pos = len(NUMERICAS)
    for nome, categorias in zip(CATEGORICAS, onehot.categories_):
        parametros["categoricas"].append({
            "nome": nome, "categorias": list(categorias),
            "coef": [r(c, 6) for c in coef[pos:pos + len(categorias)]],
            # frequência de cada categoria no treino: é o "cliente médio" das contribuições
            "freq": [r(f, 6) for f in media_tr[pos:pos + len(categorias)]]})
        pos += len(categorias)

    nomes_saida = list(NUMERICAS) + [f"{c}" for c, cats in zip(CATEGORICAS, onehot.categories_) for _ in cats]
    base_logito = float(modelo.intercept_[0] + coef @ media_tr)

    def fatura(linha):
        x = np.asarray(prep.transform(pipeline.named_steps["features"].transform(linha))[0]).ravel()
        itens = {}
        for nome, c, xi, mi in zip(nomes_saida, coef, x, media_tr):
            grupo = GRUPOS[nome]
            itens[grupo] = itens.get(grupo, 0.0) + c * (xi - mi)
        return {k: r(v) for k, v in itens.items()}

    amostra_idx = np.random.default_rng(7).choice(len(X_te), 420, replace=False)
    amostra = X_te.iloc[amostra_idx]
    clientes = [
        {"meses": int(c.meses_cliente), "chamados": int(c.chamados_suporte), "contrato": c.contrato,
         "internet": c.internet, "pagamento": c.pagamento, "mensalidade": r(c.mensalidade, 2),
         "atrasos": int(c.atrasos_pagamento), "idade": int(c.idade),
         "p": r(p, 4), "churn": int(t)}
        for c, p, t in zip(amostra.itertuples(), prob_te[amostra_idx], y_np[amostra_idx])
    ]

    # Três clientes reais do teste para a "fatura de risco": alto, médio e baixo risco
    ordem = np.argsort(prob_te)
    exemplos = []
    for quantil in (0.97, 0.6, 0.08):
        i = ordem[int(quantil * (len(ordem) - 1))]
        linha = X_te.iloc[[i]]
        exemplos.append({"cliente": {k: (v.item() if hasattr(v, "item") else v)
                                     for k, v in linha.iloc[0].to_dict().items()},
                         "p": r(prob_te[i]), "churn": int(y_np[i]), "itens": fatura(linha)})

    # Superfície: probabilidade por tempo de casa x chamados, para cada tipo de contrato
    meses_grade = list(range(1, 73, 3))
    chamados_grade = list(range(0, 9))
    superficies = {}
    for contrato in ("mensal", "anual", "bianual"):
        linhas = []
        for ch in chamados_grade:
            grade = X_te.iloc[[0] * len(meses_grade)].copy()
            grade["contrato"], grade["internet"], grade["pagamento"] = contrato, "fibra", "cartao_credito"
            grade["regiao"], grade["idade"], grade["dependentes"] = "Sudeste", 41, 0
            grade["streaming"], grade["mensalidade"], grade["atrasos_pagamento"] = False, 99.0, 0
            grade["meses_cliente"] = meses_grade
            grade["total_gasto"] = 99.0 * np.array(meses_grade)
            grade["chamados_suporte"] = ch
            linhas.append([r(p, 4) for p in pipeline.predict_proba(grade)[:, 1]])
        superficies[contrato] = linhas

    importancias = importancia_variaveis(pipeline, X_te, y_te, SEMENTE)

    dados = {
        "n_clientes": len(df), "taxa_churn": r(y.mean()), "n_treino": len(X_tr), "n_teste": len(X_te),
        "validacao": validacao_json, "vencedor": vencedor.nome, "limiar": limiar,
        "teste": {"roc_auc": r(roc_auc_score(y_np, prob_te), 3)},
        "custos": {"oferta": 120.0, "sucesso": 0.30, "meses_valor": 12},
        "curva": curva, "lucro_todos": r(lucro_campanha(y_np, prob_te, valor_te, 0.0), 2),
        "parametros": parametros, "base_logito": r(base_logito),
        "exemplos": exemplos, "clientes": clientes,
        "superficie": {"meses": meses_grade, "chamados": chamados_grade, "p": superficies},
        "importancia": {k: r(v) for k, v in importancias.items()},
    }
    gravar_no_html(dados)


if __name__ == "__main__":
    main()
