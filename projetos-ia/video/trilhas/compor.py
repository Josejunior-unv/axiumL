"""Compõe a trilha de um reel, no tamanho exato do vídeo.

    python compor.py <estilo> <bpm> <compassos por cena> <saida.wav>
    python compor.py cofre 110 2,2,3,4,6,3,7,4,3 cofre.wav

Cada cena do vídeo começa na cabeça de um compasso. A primeira cena (a cartela de abertura)
é a introdução, a última (a cartela de encerramento) é o acorde final, e a cena mais próxima
do meio do vídeo vira um respiro, sem bateria. As outras tocam com tudo. A harmonia recomeça
do primeiro acorde em cada cena, e a última batida de cada cena ganha uma virada.

Estilos, um por projeto:
    churn         96 bpm   ré menor, pulso eletrônico limpo, arpejo com eco
    demanda      120 bpm   nu-disco, baixo em oitavas, guitarra funk e cordas
    fraude        84 bpm   jazz noir com swing, vassourinha, contrabaixo andando e vibrafone
    recomendacao  90 bpm   lo-fi com chiado de disco, marimba e flauta conversando
    cofre        110 bpm   synthwave, arpejo que abre o filtro e cliques de fechadura
"""

import sys
from dataclasses import dataclass

import numpy as np
from scipy.ndimage import uniform_filter1d

import som
from som import (Chorus, Delay, HighpassFilter, HighShelfFilter, LadderFilter, LowpassFilter, LowShelfFilter,
                 PeakFilter, Reverb)


@dataclass
class Compasso:
    i: int        # índice no reel
    cena: int
    k: int        # posição dentro da cena
    ultimo: bool  # último compasso da cena
    nivel: str    # intro, entrada, cheio, respiro, fim
    proximo: str  # nível da cena seguinte
    b: float      # batida em que começa


def estrutura(compassos):
    total = sum(compassos)
    inicios = np.cumsum([0] + list(compassos[:-1]))
    meio = [c for c in range(2, len(compassos) - 2)]
    respiro = min(meio, key=lambda c: abs(inicios[c] / total - 0.55)) if meio else None

    def nivel(c):
        if c == 0:
            return "intro"
        if c == len(compassos) - 1:
            return "fim"
        if c == 1:
            return "entrada"
        return "respiro" if c == respiro else "cheio"

    barras = []
    for c, n in enumerate(compassos):
        prox = nivel(c + 1) if c + 1 < len(compassos) else "fim"
        for k in range(n):
            barras.append(Compasso(len(barras), c, k, k == n - 1, nivel(c), prox, 4.0 * len(barras)))
    return barras


def acorde_de(prog, x):
    return prog[x.k % len(prog)]


def transicoes(tr, barras, prato_fn, subir=True, bater=True, nome="fx"):
    """Prato na entrada das cenas com bateria; subida de ruído e impacto nas entradas grandes."""
    for x in barras:
        if x.k == 0 and x.cena > 0 and x.nivel in ("cheio", "entrada", "fim"):
            tr.por(nome, prato_fn(), x.b, ganho=0.8)
        if subir and x.ultimo and x.nivel in ("intro", "respiro") and x.proximo in ("cheio", "entrada"):
            tr.por(nome, som.subida(4 * tr.batida), x.b, ganho=0.9)
        if bater and x.k == 0 and x.cena > 0 and barras[x.i - 1].nivel in ("intro", "respiro"):
            tr.por(nome, som.impacto(), x.b, ganho=0.7)


GANHO_DO_NIVEL = {"intro": -3.5, "entrada": -2.0, "cheio": 0.0, "respiro": -4.0, "fim": 0.0}


def dinamica(tr, barras, rampa=0.25):
    """Envelope de volume por cena: introdução e respiro mais baixos, para a música crescer junto com o vídeo."""
    por_barra = np.array([10 ** (GANHO_DO_NIVEL[x.nivel] / 20) for x in barras])
    barra = np.minimum((np.arange(tr.n) / som.SR / tr.batida // 4).astype(int), len(barras) - 1)
    return uniform_filter1d(por_barra[barra], som.amostras(rampa), mode="nearest")


def fim_suave(x, seg=1.4):
    n = som.amostras(seg)
    x[:, -n:] *= np.linspace(1, 0, n) ** 2
    return x


# ---------------------------------------------------------------- 01 · churn

def churn(tr, barras):
    prog = [  # (baixo, acorde) — Dm9, B♭maj9, Fmaj9, Cadd9
        (38, [57, 60, 64, 65]), (34, [57, 60, 62, 65]), (41, [57, 60, 64, 67]), (36, [55, 60, 62, 64])]
    onda = [0, 2, 4, 6, 7, 5, 3, 1, 2, 4, 6, 7, 6, 4, 2, 1]
    bumbo, caixa, palmas = som.bumbo(48, 0.32), som.caixa(200, 0.15), som.palmas()
    fechado, aberto, aro = som.chimbal(), som.chimbal(True), som.estalo(2100)
    for x in barras:
        baixo, acorde = acorde_de(prog, x)
        tons = sorted(acorde + [a + 12 for a in acorde])
        nv = x.nivel
        if nv == "fim":
            if x.k == 0:
                tr.por("pad", som.pad(acorde + [baixo + 24], 4 * len([y for y in barras if y.cena == x.cena]) * tr.batida, 2400, 0.05, 3.0), x.b)
                tr.nota((0, 0), x.b, baixo + 12, 6, 80)
                for a in acorde:
                    tr.nota((0, 0), x.b, a + 12, 6, 70)
                tr.por("sub", som.baixo_seno(baixo - 12, 3.5, soltura=1.5), x.b)
                tr.por("bumbo", bumbo, x.b); tr.bumbo_em(x.b)
            continue
        corte = {"intro": 900, "entrada": 1600, "cheio": 2600, "respiro": 1100}[nv]
        tr.por("pad", som.pad(acorde + [baixo + 24], 4 * tr.batida, corte, 0.35, 0.8), x.b)
        if nv in ("entrada", "cheio"):
            brilho = 2000 if nv == "entrada" else 3600
            for s in range(16):
                tr.por("arpejo", som.pluck(tons[onda[s]], 0.22 * tr.batida, brilho, 0.16), x.b + s / 4, ganho=0.75 + 0.25 * (s % 4 == 0), pan=0.25 * np.sin(s))
        if nv == "intro":
            for b, j in ((0, 3), (0.75, 5), (1.5, 6), (2.5, 4), (3.0, 7)):
                tr.por("arpejo", som.pluck(tons[j], 0.4 * tr.batida, 1300, 0.3), x.b + b, ganho=0.8)
        if nv in ("intro", "respiro") or (nv == "cheio" and x.k % 4 == 0):
            for b, d, j in ((0, 1.5, -1), (1.5, 1, -2), (2.5, 1.5, -3)):
                tr.nota((0, 0), x.b + b, acorde[j] + 12, d, 62 if nv == "cheio" else 72, humano=0.006)
        if nv == "entrada":
            for b in (0, 2.5):
                tr.por("bumbo", bumbo, x.b + b); tr.bumbo_em(x.b + b)
            for b in (1, 3):
                tr.por("aro", aro, x.b + b, ganho=0.8)
            for s in range(8):
                tr.por("chimbal", fechado, x.b + s / 2, ganho=0.55 + 0.3 * (s % 2), pan=0.3)
            tr.por("sub", som.baixo_seno(baixo, 2.2 * tr.batida), x.b)
            tr.por("sub", som.baixo_seno(baixo, 1.3 * tr.batida), x.b + 2.5)
        if nv == "cheio":
            for b in (0, 1.75, 2.5):
                tr.por("bumbo", bumbo, x.b + b); tr.bumbo_em(x.b + b)
            for b in (1, 3):
                tr.por("caixa", caixa, x.b + b)
                tr.por("palmas", palmas, x.b + b, pan=-0.1)
            for s in range(16):
                if s != 14:
                    tr.por("chimbal", fechado, x.b + s / 4, ganho=(1.0, 0.45, 0.7, 0.45)[s % 4], pan=0.3)
            tr.por("aberto", aberto, x.b + 3.5, pan=-0.3)
            for b, d in ((0, 0.6), (0.75, 0.5), (1.5, 0.6), (2.5, 0.6), (3.25, 0.5)):
                tr.por("sub", som.baixo_seno(baixo + (12 if b == 3.25 else 0), d * tr.batida), x.b + b)
            if x.ultimo:
                for j, b in enumerate((3.0, 3.25, 3.5, 3.75)):
                    tr.por("caixa", caixa, x.b + b, ganho=0.4 + 0.18 * j)
        if nv == "respiro":
            for s in range(8):
                tr.por("aro", aro, x.b + s / 2, ganho=0.25 + 0.2 * (s % 2 == 0), pan=0.4 * (-1) ** s)
    transicoes(tr, barras, lambda: som.prato(2.4))
    ajustes = {
        "bumbo": dict(nivel=-13), "caixa": dict(nivel=-21, envio=0.18), "palmas": dict(nivel=-23, envio=0.3),
        "chimbal": dict(nivel=-29, efeitos=[HighpassFilter(5000)]), "aberto": dict(nivel=-31, envio=0.1),
        "aro": dict(nivel=-29, envio=0.25), "sub": dict(nivel=-16, abafar=0.55),
        "pad": dict(nivel=-23, efeitos=[HighpassFilter(160), Chorus(rate_hz=0.4, depth=0.3, mix=0.4)], envio=0.35, abafar=0.35),
        "arpejo": dict(nivel=-22, efeitos=[HighpassFilter(250), Delay(delay_seconds=0.75 * tr.batida, feedback=0.35, mix=0.28)], envio=0.25, abafar=0.25),
        (0, 0): dict(nivel=-21, efeitos=[HighpassFilter(120), HighShelfFilter(6000, -3)], envio=0.35),
        "fx": dict(nivel=-25, envio=0.3),
    }
    return ajustes, [HighpassFilter(250), Reverb(room_size=0.78, damping=0.55, wet_level=1, dry_level=0, width=1), LowpassFilter(8000)]


# ---------------------------------------------------------------- 02 · demanda

def demanda(tr, barras):
    prog = [  # Fmaj7, G6, Em7, Am7
        (41, [53, 57, 60, 64]), (43, [55, 59, 62, 64]), (40, [52, 55, 59, 62]), (45, [57, 60, 64, 67])]
    gancho = [[(0, 76, 0.5), (0.75, 79, 0.5), (1.5, 81, 0.75), (2.5, 79, 0.5), (3, 76, 0.75)],
              [(0, 74, 0.5), (0.75, 76, 0.5), (1.5, 72, 0.75), (2.5, 69, 1.25)]]
    bumbo, palmas, caixa = som.bumbo(52, 0.26, 3.5, 0.35), som.palmas(), som.caixa(210, 0.13)
    aberto, fechado, chocalho = som.chimbal(True), som.chimbal(), som.chocalho()
    for x in barras:
        baixo, acorde = acorde_de(prog, x)
        nv = x.nivel
        if nv == "fim":
            if x.k == 0:
                for a in acorde + [acorde[0] + 12]:
                    tr.por("teclas", som.rhodes(a, 3.0, 0.9), x.b)
                    tr.nota((0, 48), x.b, a + 12, 7, 80)
                tr.por("baixo", som.baixo_serra(baixo - 12, 3.0 * tr.batida, 900, 0.6), x.b)
                tr.por("bumbo", bumbo, x.b); tr.bumbo_em(x.b)
                tr.por("palmas", palmas, x.b)
            continue
        if nv == "intro":
            # bumbo abafado, como se a festa estivesse na sala ao lado, e o gancho já tocando
            for b in range(4):
                tr.por("abafado", bumbo, x.b + b)
            for b in (0.5, 1.5, 2.5, 3.5):
                for a in acorde:
                    tr.por("teclas", som.rhodes(a + 12, 0.35 * tr.batida, 0.6), x.b + b)
            for b, n, d in gancho[x.k % 2]:
                tr.por("gancho", som.pluck(n, d * tr.batida, 1800, 0.35), x.b + b, ganho=0.7, pan=0.1)
            continue
        if nv == "respiro":
            for a in acorde:
                tr.nota((0, 48), x.b, a + 12, 4, 70)
                tr.por("teclas", som.rhodes(a, 3.5 * tr.batida, 0.55), x.b)
            for s in range(8):
                tr.por("chocalho", chocalho, x.b + s / 2, ganho=0.5 + 0.3 * (s % 2))
            continue
        cheio = nv == "cheio"
        for b in range(4):
            tr.por("bumbo", bumbo, x.b + b); tr.bumbo_em(x.b + b)
            if cheio:
                tr.por("aberto", aberto, x.b + b + 0.5, ganho=0.8, pan=0.2)
            else:
                tr.por("chimbal", fechado, x.b + b + 0.5, pan=0.2)
        if cheio:
            for b in (1, 3):
                tr.por("palmas", palmas, x.b + b)
            for s in range(16):
                tr.por("chocalho", chocalho, x.b + s / 4, ganho=(0.5, 0.3, 0.8, 0.3)[s % 4], pan=-0.35)
        for s in range(8):
            nota = baixo + (12 if s % 2 else 0) if cheio else baixo
            if cheio or s % 2:
                tr.por("baixo", som.baixo_serra(nota, 0.42 * tr.batida, 1700 if cheio else 1100, 0.12), x.b + s / 2, ganho=1.0 if s % 2 == 0 else 0.8)
        for b in (0.5, 1.75, 2.5, 3.5) if cheio else (0.5, 2.5):
            for a in acorde:
                tr.por("teclas", som.rhodes(a + 12, 0.3 * tr.batida, 0.7), x.b + b, humano=0.004)
        if cheio:
            for s in (1, 3, 6, 7, 9, 11, 14, 15):
                tr.nota((8, 28), x.b + s / 4, acorde[-1 - (s % 2)] + 12, 0.12, 70 + 25 * (s % 4 == 3), humano=0.004)
            for a in acorde:
                tr.nota((0, 48), x.b, a + 12, 4, 58)
            for b, n, d in gancho[x.k % 2]:
                tr.por("gancho", som.pluck(n, d * tr.batida, 5200, 0.35), x.b + b, pan=0.1)
            if x.ultimo:
                for j in range(8):
                    tr.por("caixa", caixa, x.b + 2 + j / 4, ganho=0.3 + 0.1 * j)
    transicoes(tr, barras, lambda: som.prato(2.2, tom=1.1))
    ajustes = {
        "bumbo": dict(nivel=-12), "abafado": dict(nivel=-17, efeitos=[LowpassFilter(320)]),
        "palmas": dict(nivel=-20, envio=0.25), "caixa": dict(nivel=-23, envio=0.2),
        "aberto": dict(nivel=-27, efeitos=[HighpassFilter(6000)]), "chimbal": dict(nivel=-28, efeitos=[HighpassFilter(6000)]),
        "chocalho": dict(nivel=-31), "baixo": dict(nivel=-16, abafar=0.6, efeitos=[LowpassFilter(3500)]),
        "teclas": dict(nivel=-22, efeitos=[HighpassFilter(200), Chorus(rate_hz=0.8, depth=0.25, mix=0.35)], envio=0.25, abafar=0.3),
        (8, 28): dict(nivel=-25, efeitos=[HighpassFilter(400)], envio=0.15),
        (0, 48): dict(nivel=-26, efeitos=[HighpassFilter(250)], envio=0.45, abafar=0.25),
        "gancho": dict(nivel=-22, efeitos=[HighpassFilter(300), Delay(delay_seconds=0.75 * tr.batida, feedback=0.3, mix=0.22)], envio=0.25),
        "fx": dict(nivel=-24, envio=0.3),
    }
    return ajustes, [HighpassFilter(300), Reverb(room_size=0.6, damping=0.5, wet_level=1, dry_level=0, width=1), LowpassFilter(9000)]


# ---------------------------------------------------------------- 03 · fraude

def fraude(tr, barras):
    prog = [  # (raiz, terça, quinta, acorde sem a raiz) — Cm9, Fm9, Dm7(♭5), G7(♭9)
        (36, 3, 7, [58, 62, 63, 67]), (41, 3, 7, [56, 60, 63, 67]), (38, 3, 6, [53, 56, 60, 62]), (43, 4, 7, [53, 56, 59, 63])]
    kit, piano, vibra, baixo_ac, cordas = "bateria:40", (0, 0), (0, 11), (0, 32), (0, 49)
    rng = np.random.default_rng(7)
    frases = [[(0, 1.5), (1.5, 0.5), (2, 2)], [(0.5, 1), (1.5, 0.5), (2, 1), (3, 1)], [(0, 3), (3, 1)], [(1, 0.5), (1.5, 1.5), (3, 1)]]
    for x in barras:
        raiz, terca, quinta, acorde = acorde_de(prog, x)
        prox_raiz = prog[(x.k + 1) % len(prog)][0] if not x.ultimo else prog[0][0]
        nv = x.nivel
        if nv == "fim":
            if x.k == 0:
                for a in acorde:
                    tr.nota(piano, x.b, a, 8, 70)
                tr.nota(piano, x.b, raiz, 8, 78)
                tr.nota(vibra, x.b, acorde[-1] + 12, 8, 80)
                tr.nota(baixo_ac, x.b, raiz, 6, 90)
                tr.nota(kit, x.b, 57, 2, 70)
                tr.nota(kit, x.b, 40, 2, 70)
                tr.nota(cordas, x.b, raiz + 24, 8, 60)
            continue
        if nv in ("intro", "respiro"):
            for a in acorde[1:]:
                tr.nota(cordas, x.b, a + 12, 4, 52)
            for b in (0, 2):
                tr.nota(kit, x.b + b, 40, 1.8, 58 + rng.integers(0, 12))
            tr.nota(baixo_ac, x.b, raiz, 3.5, 80)
        else:
            # contrabaixo andando: raiz, terça, quinta e aproximação cromática da próxima raiz
            caminho = [raiz, raiz + terca, raiz + quinta, prox_raiz + (1 if rng.random() < 0.5 else -1)]
            if rng.random() < 0.3:
                caminho[1] = raiz + 12 - 2
            for b, n in enumerate(caminho):
                tr.nota(baixo_ac, x.b + b, n, 0.9, 92 + (8 if b == 0 else 0) + rng.integers(-6, 6), humano=0.008)
            # prato de condução: "ding, ding-da ding"
            for b in (0, 1, 1.5, 2, 3, 3.5):
                tr.nota(kit, x.b + b, 51, 0.5, (82 if b in (1, 3) else 64) + rng.integers(-6, 6), humano=0.006)
            for b in (1, 3):
                tr.nota(kit, x.b + b, 44, 0.2, 70)
                tr.nota(kit, x.b + b, 38, 0.2, 50 + rng.integers(0, 14), humano=0.01)
            tr.nota(kit, x.b, 40, 1.8, 48 + rng.integers(0, 10))
            tr.nota(kit, x.b + 2, 40, 1.8, 44 + rng.integers(0, 10))
            # piano no ritmo do charleston
            for b, d, v in ((0, 0.7, 62), (1.5, 0.45, 58)) if nv == "cheio" else ((0, 1.6, 56),):
                for a in acorde:
                    tr.nota(piano, x.b + b, a, d, v + rng.integers(-5, 5), humano=0.007)
            if x.ultimo and nv == "cheio":
                for j, b in enumerate((3, 3.333, 3.667)):
                    tr.nota(kit, x.b + b, 38, 0.2, 60 + 12 * j)
        if nv in ("intro", "cheio", "respiro") and (nv != "cheio" or x.cena % 2 == 0 or x.k % 2 == 1):
            frase = frases[(x.i + x.cena) % len(frases)]
            alvos = acorde[1:] + [acorde[0] + 12]
            for b, d in frase:
                nota = int(rng.choice(alvos)) + 12
                tr.nota(vibra, x.b + b, nota, d, 74 + rng.integers(-8, 8), humano=0.008)
    transicoes(tr, barras, lambda: np.zeros(1), subir=False, bater=False)
    for x in barras:
        if x.k == 0 and x.cena > 0 and x.nivel == "cheio":
            tr.nota(kit, x.b, 49, 2, 64)
    ajustes = {
        kit: dict(nivel=-21, efeitos=[HighpassFilter(80)], envio=0.18),
        baixo_ac: dict(nivel=-17, efeitos=[LowShelfFilter(90, 2), LowpassFilter(4000)], envio=0.06),
        piano: dict(nivel=-21, efeitos=[HighpassFilter(150)], envio=0.28),
        vibra: dict(nivel=-21, efeitos=[HighpassFilter(250), Chorus(rate_hz=5.5, depth=0.12, mix=0.3)], envio=0.42),
        cordas: dict(nivel=-27, efeitos=[HighpassFilter(250), LowpassFilter(5000)], envio=0.5),
        "fx": dict(nivel=-26, envio=0.3),
    }
    return ajustes, [HighpassFilter(220), Reverb(room_size=0.55, damping=0.6, wet_level=1, dry_level=0, width=0.9), LowpassFilter(7000)]


# ---------------------------------------------------------------- 04 · recomendacao

def recomendacao(tr, barras):
    prog = [  # Fmaj9, Am7, Dm9, B♭maj9
        (41, [57, 60, 64, 67]), (45, [55, 60, 64, 69]), (38, [57, 60, 64, 65]), (34, [57, 60, 62, 65])]
    penta = [65, 67, 69, 72, 74, 77, 79, 81]  # fá maior pentatônica
    marimba, flauta = (0, 12), (0, 73)
    rng = np.random.default_rng(4)
    bumbo, caixa, fechado = som.bumbo(55, 0.34, 2.2, 0.15), som.caixa(205, 0.2, 0.7, 5000), som.chimbal()
    tr.por("vinil", som.chiado_vinil(tr.n), 0)
    ritmos = [[(0, 0.5), (0.75, 0.5), (1.5, 1)], [(0.5, 0.5), (1, 0.5), (2, 1.5)], [(0, 0.75), (1, 0.5), (1.75, 0.75), (2.75, 1)]]
    for x in barras:
        baixo, acorde = acorde_de(prog, x)
        nv = x.nivel
        if nv == "fim":
            if x.k == 0:
                for j, a in enumerate(acorde):
                    tr.por("teclas", som.rhodes(a, 6, 0.7), x.b, segundos=tr.t(x.b) + 0.03 * j)
                for j, n in enumerate([65, 69, 72, 76, 79]):
                    tr.nota(marimba, x.b + j * 0.25, n, 1, 70)
                tr.por("baixo", som.baixo_seno(baixo - 12, 4, soltura=1.2), x.b)
            continue
        # piano elétrico com as notas dedilhadas
        for b, d in ((0, 1.75), (2.5, 1.25)):
            for j, a in enumerate(acorde):
                tr.por("teclas", som.rhodes(a, d * tr.batida, 0.55 + 0.15 * rng.random()), x.b + b, segundos=tr.t(x.b + b) + 0.014 * j)
        if nv in ("entrada", "cheio"):
            for b in (0, 1.75, 2.5) if nv == "cheio" else (0, 2.5):
                tr.por("bumbo", bumbo, x.b + b, humano=0.006); tr.bumbo_em(x.b + b)
            for b in (1, 3):
                tr.por("caixa", caixa, x.b + b, humano=0.008)
            for s in range(8 if nv == "cheio" else 4):
                passo = 0.5 if nv == "cheio" else 1
                tr.por("chimbal", fechado, x.b + s * passo, ganho=0.5 + 0.35 * (s % 2 == 0), pan=0.25, humano=0.006)
            for b, d, n in ((0, 1.5, baixo), (2.5, 1, baixo), (3.5, 0.5, baixo + 7)):
                tr.por("baixo", som.baixo_seno(n, d * tr.batida, 0.02, 0.08), x.b + b)
        # duas vozes: a marimba pergunta, a flauta responde
        ritmo = ritmos[(x.i // 2) % len(ritmos)]
        if nv in ("intro", "entrada", "cheio") and x.k % 4 in (0, 1):
            for b, d in ritmo:
                tr.nota(marimba, x.b + b, int(rng.choice(penta[2:])), d, 78 + rng.integers(-8, 8), humano=0.006)
        if (nv == "cheio" and x.k % 4 in (2, 3)) or nv == "respiro":
            for b, d in ritmo:
                tr.nota(flauta, x.b + b, int(rng.choice(penta[:6])), d + 0.25, 70 + rng.integers(-6, 6), humano=0.01)
        if nv == "respiro":
            tr.por("baixo", som.baixo_seno(baixo, 3.5 * tr.batida, 0.05, 0.3), x.b)
    transicoes(tr, barras, lambda: np.zeros(1), subir=False, bater=False)
    ajustes = {
        "bumbo": dict(nivel=-15, efeitos=[LowpassFilter(3500)]),
        "caixa": dict(nivel=-21, efeitos=[LowpassFilter(4500), HighpassFilter(150)], envio=0.15),
        "chimbal": dict(nivel=-30, efeitos=[LowpassFilter(7500), HighpassFilter(3000)]),
        "baixo": dict(nivel=-17, abafar=0.35),
        "teclas": dict(nivel=-20, efeitos=[HighpassFilter(150), LowpassFilter(6000), Chorus(rate_hz=0.35, depth=0.35, mix=0.45)], envio=0.3, abafar=0.2),
        marimba: dict(nivel=-22, efeitos=[HighpassFilter(300)], envio=0.3),
        flauta: dict(nivel=-23, efeitos=[HighpassFilter(300), LowpassFilter(7000)], envio=0.4),
        "vinil": dict(nivel=-38, efeitos=[LowpassFilter(5000)]),
        "fx": dict(nivel=-27, efeitos=[LowpassFilter(6000)], envio=0.3),
    }
    return ajustes, [HighpassFilter(250), Reverb(room_size=0.65, damping=0.65, wet_level=1, dry_level=0, width=1), LowpassFilter(6500)]


# ---------------------------------------------------------------- 05 · cofre

def cofre(tr, barras):
    prog = [  # Em9, Cmaj7, Am9, B7
        (40, [55, 59, 62, 66]), (36, [55, 59, 60, 64]), (33, [57, 60, 64, 67]), (35, [57, 59, 63, 66])]
    bumbo, caixa = som.bumbo(46, 0.36, 3.2, 0.3), som.caixa_portao()
    fechado = som.chimbal()
    cliques = [som.estalo(3300), som.estalo(2500, 21), som.estalo(4100, 22)]
    for x in barras:
        baixo, acorde = acorde_de(prog, x)
        tons = sorted(acorde + [a + 12 for a in acorde])
        nv = x.nivel
        if nv == "fim":
            if x.k == 0:
                tr.por("pad", som.pad(acorde + [baixo + 24, acorde[-1] + 12], 5.5, 2600, 0.05, 2.5), x.b)
                tr.por("lead", som.lead(acorde[-1] + 12, 2.5, 2800), x.b)
                tr.por("baixo", som.baixo_serra(baixo, 3.0, 700, 1.0), x.b)
                tr.por("bumbo", bumbo, x.b); tr.bumbo_em(x.b)
                for j, b in enumerate((1.5, 1.75, 2.0)):
                    tr.por("cliques", cliques[j], x.b + b, ganho=0.7, pan=0.3 * (j - 1))
            continue
        corte = {"intro": 1100, "entrada": 1800, "cheio": 2600, "respiro": 1300}[nv]
        tr.por("pad", som.pad(acorde + [baixo + 24], 4 * tr.batida, corte, 0.3, 0.6), x.b)
        if nv != "intro" or x.k > 0:
            for s in range(16):
                tr.por("arpejo", som.pluck(tons[s % len(tons)] + (12 if (s // 8) % 2 and nv == "cheio" else 0), 0.2 * tr.batida, 5200, 0.12), x.b + s / 4, ganho=(1, 0.6, 0.8, 0.6)[s % 4], pan=0.35 * np.sin(s * 0.9))
        # cliques de fechadura nas semicolcheias fora do tempo
        for j, b in enumerate((0.75, 1.25, 2.75, 3.5)):
            if nv in ("intro", "respiro", "cheio", "entrada"):
                tr.por("cliques", cliques[(x.i + j) % 3], x.b + b, ganho=0.75 if nv != "respiro" else 0.5, pan=(-0.5, 0.5, -0.3, 0.3)[j])
        if nv in ("entrada", "cheio"):
            for b in (0, 2) if nv == "entrada" else (0, 1, 2, 3):
                tr.por("bumbo", bumbo, x.b + b); tr.bumbo_em(x.b + b)
            for b in (1, 3):
                tr.por("caixa", caixa, x.b + b)
            for s in range(16 if nv == "cheio" else 8):
                passo = 0.25 if nv == "cheio" else 0.5
                tr.por("chimbal", fechado, x.b + s * passo, ganho=(1, 0.5, 0.75, 0.5)[s % 4] if nv == "cheio" else 0.8, pan=0.25)
            for s in range(16 if nv == "cheio" else 8):
                passo = 0.25 if nv == "cheio" else 0.5
                nota = baixo + (12 if s % 4 == 3 else 0)
                tr.por("baixo", som.baixo_serra(nota, 0.8 * passo * tr.batida, 1300 if nv == "cheio" else 900, 0.08), x.b + s * passo, ganho=1 if s % 4 == 0 else 0.8)
            if nv == "cheio" and x.cena % 2 == 0:
                tr.por("lead", som.lead(acorde[-1] + 12 if x.k % 2 == 0 else acorde[-2] + 12, 2.6 * tr.batida), x.b)
                tr.por("lead", som.lead(acorde[1] + 12, 1.2 * tr.batida), x.b + 3)
            if x.ultimo and nv == "cheio":
                for j, (b, f) in enumerate(((3, 150), (3.25, 125), (3.5, 100), (3.75, 82))):
                    tr.por("tambores", som.tambor(f), x.b + b, pan=0.4 - 0.25 * j)
        if nv in ("intro", "respiro"):
            tr.por("baixo", som.baixo_serra(baixo, 3.8 * tr.batida, 500, 1.5), x.b)
    transicoes(tr, barras, lambda: som.prato(2.6, tom=0.9))
    ajustes = {
        "bumbo": dict(nivel=-13), "caixa": dict(nivel=-20, envio=0.15), "chimbal": dict(nivel=-29, efeitos=[HighpassFilter(6000)]),
        "cliques": dict(nivel=-27, efeitos=[HighpassFilter(1500)], envio=0.25), "tambores": dict(nivel=-21, envio=0.3),
        "baixo": dict(nivel=-16, abafar=0.55),
        "pad": dict(nivel=-23, efeitos=[HighpassFilter(180), Chorus(rate_hz=0.3, depth=0.4, mix=0.5)], envio=0.4, abafar=0.35),
        "arpejo": dict(nivel=-23, efeitos=[HighpassFilter(300), Delay(delay_seconds=0.75 * tr.batida, feedback=0.3, mix=0.25)], envio=0.2, abafar=0.3),
        "lead": dict(nivel=-22, efeitos=[HighpassFilter(300), Delay(delay_seconds=0.5 * tr.batida, feedback=0.35, mix=0.3)], envio=0.4),
        "fx": dict(nivel=-24, envio=0.3),
    }
    return ajustes, [HighpassFilter(250), Reverb(room_size=0.82, damping=0.45, wet_level=1, dry_level=0, width=1), LowpassFilter(8500)]


ESTILOS = {
    "churn": dict(fn=churn),
    "demanda": dict(fn=demanda),
    "fraude": dict(fn=fraude, swing=0.64, grade=0.5, curva={31.5: -14, 63: -3, 8000: -22, 16000: -30}),
    "recomendacao": dict(fn=recomendacao, swing=0.57, grade=0.25, curva={8000: -24, 16000: -34}),
    "cofre": dict(fn=cofre),
}


def abrir_filtro(tr, barras, nome, de=500, ate=6000):
    """Abre o filtro de um instrumento ao longo de cada cena (o arpejo do cofre 'destrava')."""
    x = tr.stems.get(nome)
    if x is None:
        return
    filtro = LadderFilter(mode=LadderFilter.Mode.LPF24, cutoff_hz=de, resonance=0.35)
    cenas = {}
    for c in barras:
        cenas.setdefault(c.cena, []).append(c)
    bloco = 256
    saida = np.zeros_like(x)
    for i in range(0, x.shape[1], bloco):
        b = i / som.SR / tr.batida
        c = barras[min(int(b // 4), len(barras) - 1)]
        cena = cenas[c.cena]
        frac = (b - cena[0].b) / (4 * len(cena))
        filtro.cutoff_hz = float(de * (ate / de) ** np.clip(frac, 0, 1))
        saida[:, i:i + bloco] = filtro.process(x[:, i:i + bloco].astype(np.float32), som.SR, reset=False)
    tr.stems[nome] = saida


def compor(estilo, bpm, compassos):
    e = ESTILOS[estilo]
    barras = estrutura(compassos)
    tr = som.Trilha(bpm, 4 * sum(compassos), e.get("swing", 0.5), e.get("grade", 0.5))
    ajustes, reverb = e["fn"](tr, barras)
    tr.renderizar_gm()
    if estilo == "cofre":
        abrir_filtro(tr, barras, "arpejo", 600, 7000)
    curva = {**som.CURVA_REFERENCIA, **e.get("curva", {})}
    return fim_suave(tr.mixar(ajustes, reverb, curva=curva, dinamica=dinamica(tr, barras)))


if __name__ == "__main__":
    estilo, bpm, compassos, saida = sys.argv[1], float(sys.argv[2]), [int(c) for c in sys.argv[3].split(",")], sys.argv[4]
    x = compor(estilo, bpm, compassos)
    som.salvar(saida, x)
    print(f"{saida}: {x.shape[1] / som.SR:.1f} s")
