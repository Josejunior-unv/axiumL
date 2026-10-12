"""Exporta os números reais do projeto para dentro da animação (index.html).

    python animacao/exportar_dados.py

Refaz o treino do ALS guardando os fatores a cada meia-iteração (e confere que
o resultado final é idêntico a `ALSImplicito().fit`), projeta os fatores em 3D
com PCA e grava no bloco <script id="dados"> da página: um recorte da matriz,
usuários de exemplo com histórico, itens escondidos e recomendações reais.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from recomendacao.avaliacao import cobertura, recall_ndcg, separar_ultimos  # noqa: E402
from recomendacao.dados import GENEROS, gerar_interacoes  # noqa: E402
from recomendacao.modelos import ALSImplicito, ItemKNN, Popularidade, matriz_interacoes, recomendar  # noqa: E402

K = 10


def gravar_no_html(dados: dict) -> None:
    pagina = Path(__file__).with_name("index.html")
    bloco = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = pagina.read_text()
    novo, n = re.subn(r'(<script id="dados" type="application/json">).*?(</script>)',
                      lambda m: m.group(1) + bloco + m.group(2), html, flags=re.S)
    assert n == 1, "bloco de dados não encontrado"
    pagina.write_text(novo)
    print(f"{len(bloco) / 1024:.0f} KB de dados gravados em {pagina}")


def lista(a, c=3):
    return [round(float(v), c) for v in np.ravel(a)]


def main() -> None:
    interacoes, catalogo = gerar_interacoes()
    n_u, n_i = interacoes["usuario_id"].max() + 1, len(catalogo)
    treino, teste = separar_ultimos(interacoes)
    R = matriz_interacoes(treino, n_u, n_i)
    usuarios = np.arange(n_u)
    relevantes = teste.groupby("usuario_id")["item_id"].apply(set).reindex(usuarios).tolist()

    # ALS passo a passo, mesmo código de ALSImplicito.fit
    als = ALSImplicito()
    rng = np.random.default_rng(als.semente)
    conf = (R * als.alpha).tocsr(); conf_t = conf.T.tocsr()
    U = rng.normal(0, 0.01, (n_u, als.fatores)); V = rng.normal(0, 0.01, (n_i, als.fatores))
    fotos = [(U.copy(), V.copy())]
    for _ in range(als.iteracoes):
        U = als._resolver(conf, V); fotos.append((U.copy(), V.copy()))
        V = als._resolver(conf_t, U); fotos.append((U.copy(), V.copy()))
    referencia = ALSImplicito().fit(R)
    assert np.allclose(U, referencia.U) and np.allclose(V, referencia.V), "o ALS refeito não bate com o do projeto"
    als = referencia

    # PCA dos fatores dos filmes; usuários vão para o mesmo espaço
    media = V.mean(axis=0)
    _, s, Vt = np.linalg.svd(V - media, full_matrices=False)
    comp = Vt[:3]
    escala = np.abs((V - media) @ comp.T).max(axis=0)
    proj = lambda X: (X - media) @ comp.T / escala  # noqa: E731
    variancia = float((s[:3] ** 2).sum() / (s ** 2).sum())

    genero_principal = [GENEROS.index(g.split(" / ")[0]) if g != "Variados" else -1 for g in catalogo["generos"]]
    popularidade = np.asarray(R.sum(axis=0)).ravel()
    filmes = {"titulo": catalogo["titulo"].tolist(), "generos": catalogo["generos"].tolist(),
              "genero": genero_principal, "vistos": [int(v) for v in popularidade],
              "xyz": [lista(p, 3) for p in proj(V)]}

    # recorte da matriz: 10 gêneros x 12 filmes populares; 60 usuários ordenados pelo gênero preferido
    generos_recorte = list(range(10))
    itens_rec = []
    for g in generos_recorte:
        doG = [i for i in np.argsort(-popularidade) if genero_principal[i] == g][:12]
        itens_rec += doG
    gosto_usuario = np.zeros((n_u, len(GENEROS)))
    for u, i in zip(treino["usuario_id"], treino["item_id"]):
        if genero_principal[i] >= 0:
            gosto_usuario[u, genero_principal[i]] += 1
    preferido = gosto_usuario.argmax(axis=1)
    usuarios_rec = []
    for g in generos_recorte:
        doG = [u for u in np.argsort(-gosto_usuario[:, g]) if preferido[u] == g][:6]
        usuarios_rec += doG
    Rrec = R[usuarios_rec][:, itens_rec].toarray()
    notas_rec = U[usuarios_rec] @ V[itens_rec].T
    lo, hi = np.percentile(notas_rec, [5, 99])
    recorte = {"usuarios": [int(u) for u in usuarios_rec], "itens": [int(i) for i in itens_rec],
               "generos": [GENEROS[g] for g in generos_recorte],
               "vistos": [[int(v) for v in linha] for linha in Rrec],
               "notas": [lista(np.clip((linha - lo) / (hi - lo), 0, 1), 2) for linha in notas_rec],
               "U": [lista(x / np.abs(U[usuarios_rec]).max(), 2) for x in U[usuarios_rec]],
               "V": [lista(x / np.abs(V[itens_rec]).max(), 2) for x in V[itens_rec]]}

    # fotos do treino em 2D (duas primeiras componentes) para uma amostra de usuários e filmes
    am_u = np.random.default_rng(1).choice(n_u, 90, replace=False)
    am_i = np.random.default_rng(2).choice(n_i, 180, replace=False)
    passos = [{"u": [lista(p[:2], 3) for p in proj(Uf[am_u])], "i": [lista(p[:2], 3) for p in proj(Vf[am_i])]}
              for Uf, Vf in fotos]

    # modelos e recomendações
    knn = ItemKNN().fit(R); pop = Popularidade().fit(R)
    recs = {"als": recomendar(als, R, usuarios, K), "knn": recomendar(knn, R, usuarios, K), "pop": recomendar(pop, R, usuarios, K)}
    metricas = {}
    for nome, rr in recs.items():
        rc, nd = recall_ndcg(rr, relevantes, K)
        metricas[nome] = {"recall": round(rc, 3), "ndcg": round(nd, 3), "cobertura": round(cobertura(rr, n_i), 3),
                          "itens_cobertos": sorted(int(i) for i in np.unique(rr))}

    # usuários de exemplo com gostos diferentes: um que acerta muito, dois típicos e um em que o modelo erra tudo
    acertos = np.array([len(set(recs["als"][u]) & relevantes[u]) for u in usuarios])
    n_hist = np.bincount(treino["usuario_id"], minlength=n_u)
    escolhidos, vistos_g = [], set()
    for alvo in (3, 1, 2, 0):
        for u in usuarios:
            if (acertos[u] >= alvo if alvo == 3 else acertos[u] == alvo) and preferido[u] not in vistos_g and 12 <= n_hist[u] <= 40:
                escolhidos.append(u); vistos_g.add(preferido[u]); break
    exemplos = []
    for u in escolhidos:
        g = preferido[u]
        hist = treino[treino.usuario_id == u].sort_values("data_hora")["item_id"].tolist()
        notas_u = als.pontuar(np.array([u]))[0]
        rc, nd = recall_ndcg(recs["als"][[u]], [relevantes[u]], K)
        knn_contrib = []
        for c in recs["knn"][u][:5]:
            contrib = sorted(((int(h), round(float(knn.similaridade[h, c]), 3)) for h in hist if knn.similaridade[h, c] > 0),
                             key=lambda x: -x[1])
            knn_contrib.append({"item": int(c), "total": round(sum(v for _, v in contrib), 3), "de": contrib[:6]})
        exemplos.append({
            "usuario": int(u), "genero": GENEROS[g], "historico": [int(i) for i in hist],
            "escondidos": sorted(int(i) for i in relevantes[u]),
            "als": [int(i) for i in recs["als"][u]], "als_notas": lista(notas_u[recs["als"][u]], 3),
            "knn": [int(i) for i in recs["knn"][u]], "pop": [int(i) for i in recs["pop"][u]],
            "recall": round(rc, 3), "ndcg": round(nd, 3), "xyz": lista(proj(U[[u]])[0], 3),
            "notas_todos": lista(notas_u, 3), "knn_contrib": knn_contrib, "acertos": int(acertos[u]),
        })

    # vizinhos de um filme do primeiro exemplo
    co = (R.T @ R).toarray()
    filme = max(exemplos[0]["historico"], key=lambda i: popularidade[i])
    viz = np.argsort(-knn.similaridade[:, filme])[:8]
    vizinhos = {"filme": int(filme), "vistos": int(co[filme, filme]),
                "lista": [{"item": int(j), "sim": round(float(knn.similaridade[j, filme]), 3), "juntos": int(co[filme, j]),
                           "vistos": int(co[j, j])} for j in viz]}

    dados = {
        "n_usuarios": int(n_u), "n_filmes": int(n_i), "n_interacoes": len(interacoes),
        "densidade": round(R.nnz / (n_u * n_i), 4), "generos": GENEROS, "fatores": als.fatores,
        "variancia_3d": round(variancia, 3), "filmes": filmes, "recorte": recorte, "passos": passos,
        "perda": [round(v) for v in als.historico_perda], "metricas": metricas,
        "exemplos": exemplos, "vizinhos": vizinhos,
        "distribuicao_acertos": [int(v) for v in np.bincount(acertos, minlength=6)[:6]],
    }
    gravar_no_html(dados)


if __name__ == "__main__":
    main()
