"""Treina o modelo de churn de ponta a ponta.

    python -m churn.treinar
    python -m churn.treinar --clientes 20000 --saida artefatos
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
from sklearn.model_selection import train_test_split

from churn.dados import gerar_clientes
from churn.modelo import (
    ENTRADAS,
    avaliar,
    candidatos,
    importancia_variaveis,
    limiar_otimo,
    lucro_campanha,
    validar_candidatos,
)


def treinar(n_clientes: int = 7000, semente: int = 42, saida: Path = Path("artefatos")) -> dict:
    df = gerar_clientes(n_clientes, semente)
    X, y = df[ENTRADAS], df["churn"]
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=semente
    )
    print(f"Clientes: {len(df):,} | taxa de churn: {y.mean():.1%}")

    print("\nValidação cruzada (5 folds) no treino:")
    validacao = validar_candidatos(X_treino, y_treino, semente)
    for r in validacao:
        print(f"  {r.nome:<22} ROC-AUC {r.roc_auc:.3f} | PR-AUC {r.pr_auc:.3f}")
    vencedor = validacao[0]

    # O limiar sai das previsões fora da amostra do treino: o teste fica intocado
    valor_treino = (X_treino["mensalidade"] * 12).to_numpy()
    limiar, _ = limiar_otimo(y_treino.to_numpy(), vencedor.probabilidades, valor_treino)

    pipeline = candidatos(semente)[vencedor.nome].fit(X_treino, y_treino)
    prob_teste = pipeline.predict_proba(X_teste)[:, 1]
    metricas = avaliar(y_teste.to_numpy(), prob_teste)

    valor_teste = (X_teste["mensalidade"] * 12).to_numpy()
    y_np = y_teste.to_numpy()
    lucro = {
        "modelo": lucro_campanha(y_np, prob_teste, valor_teste, limiar),
        "ninguem": 0.0,
        "todos": lucro_campanha(y_np, prob_teste, valor_teste, 0.0),
    }
    acionados = float((prob_teste >= limiar).mean())

    print(f"\nModelo escolhido: {vencedor.nome}")
    print(f"Teste: ROC-AUC {metricas['roc_auc']:.3f} | PR-AUC {metricas['pr_auc']:.3f} "
          f"| Brier {metricas['brier']:.3f}")
    print(f"Limiar de negócio: {limiar:.2f} (aciona {acionados:.1%} da base)")
    print("Lucro da campanha de retenção no teste:")
    print(f"  usando o modelo:        R$ {lucro['modelo']:>12,.2f}")
    print(f"  oferecendo para todos:  R$ {lucro['todos']:>12,.2f}")
    print(f"  sem campanha:           R$ {lucro['ninguem']:>12,.2f}")

    importancias = importancia_variaveis(pipeline, X_teste, y_teste, semente)
    print("\nVariáveis mais importantes (queda de ROC-AUC ao embaralhar):")
    for nome, valor in importancias.head(6).items():
        print(f"  {nome:<20} {valor:.3f}")

    saida.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "limiar": limiar, "modelo": vencedor.nome},
                saida / "modelo.joblib")
    relatorio = {
        "modelo": vencedor.nome,
        "validacao": {r.nome: {"roc_auc": r.roc_auc, "pr_auc": r.pr_auc} for r in validacao},
        "teste": metricas,
        "limiar": limiar,
        "fracao_acionada": acionados,
        "lucro_teste": lucro,
        "importancia": importancias.round(4).to_dict(),
    }
    (saida / "metricas.json").write_text(json.dumps(relatorio, indent=2, ensure_ascii=False))
    print(f"\nModelo salvo em {saida / 'modelo.joblib'}")
    return relatorio


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clientes", type=int, default=7000)
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--saida", type=Path, default=Path("artefatos"))
    args = parser.parse_args()
    treinar(args.clientes, args.semente, args.saida)


if __name__ == "__main__":
    main()
