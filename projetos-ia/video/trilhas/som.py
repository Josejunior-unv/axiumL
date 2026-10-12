"""Peças de áudio das trilhas: sintetizadores, bateria, instrumentos do FluidR3 e mixagem.

Tudo é gerado aqui: os timbres eletrônicos saem do NumPy e os acústicos (piano, contrabaixo,
vibrafone, marimba, flauta, cordas, guitarra, bateria de vassourinha) do banco de timbres
FluidR3_GM, de licença MIT, tocado pelo FluidSynth. Os efeitos e a masterização usam o pedalboard.
"""

import os
import subprocess
import tempfile

import mido
import numpy as np
import pyloudnorm
from pedalboard import (Chorus, Compressor, Delay, HighpassFilter, HighShelfFilter, LadderFilter, Limiter,
                        LowpassFilter, LowShelfFilter, Pedalboard, PeakFilter, Reverb)
from pedalboard.io import AudioFile
from scipy.ndimage import minimum_filter1d
from scipy.signal import butter, sosfilt

SR = 48000
BANCO = os.environ.get("SOUNDFONT", "/usr/share/sounds/sf2/FluidR3_GM.sf2")


def hz(nota):
    return 440.0 * 2 ** ((np.asarray(nota, dtype=float) - 69) / 12)


def amostras(seg):
    return max(1, int(round(seg * SR)))


def eixo(n):
    return np.arange(n) / SR


def ruido(n, semente=None):
    return np.random.default_rng(semente).uniform(-1, 1, n)


def _filtro(x, tipo, corte, ordem=2):
    nyq = SR / 2
    if tipo == "bandpass":
        lo, hi = max(20, corte[0]), min(nyq * 0.95, corte[1])
        sos = butter(ordem, [lo / nyq, hi / nyq], btype="bandpass", output="sos")
    else:
        sos = butter(ordem, min(corte, nyq * 0.95) / nyq, btype=tipo, output="sos")
    return sosfilt(sos, x)


def passa_baixa(x, corte, ordem=2):
    return _filtro(x, "lowpass", corte, ordem)


def passa_alta(x, corte, ordem=2):
    return _filtro(x, "highpass", corte, ordem)


def passa_banda(x, lo, hi, ordem=2):
    return _filtro(x, "bandpass", (lo, hi), ordem)


def envelope(n, ataque=0.005, soltura=0.05, dur=None):
    """Envelope trapezoidal: sobe em `ataque`, segura até `dur` e cai em `soltura`."""
    t = eixo(n)
    dur = n / SR - soltura if dur is None else dur
    sobe = np.clip(t / max(ataque, 1e-4), 0, 1)
    cai = np.clip(1 - (t - dur) / max(soltura, 1e-4), 0, 1)
    return np.minimum(sobe, cai) ** 1.5


def caida(n, tau):
    return np.exp(-eixo(n) / tau)


def _blep(p, dt):
    """Correção polyBLEP para a descontinuidade da onda dente de serra."""
    y = np.zeros_like(p)
    a = p < dt
    t = p[a] / dt[a]
    y[a] = t + t - t * t - 1
    b = p > 1 - dt
    t = (p[b] - 1) / dt[b]
    y[b] = t * t + t + t + 1
    return y


def serra(f, n, fase=0.0):
    f = np.broadcast_to(np.asarray(f, dtype=float), (n,))
    dt = f / SR
    p = (fase + np.cumsum(dt)) % 1.0
    return 2 * p - 1 - _blep(p, dt)


def quadrada(f, n, largura=0.5, fase=0.0):
    return 0.5 * (serra(f, n, fase) - serra(f, n, fase + largura))


def seno(f, n, fase=0.0):
    f = np.broadcast_to(np.asarray(f, dtype=float), (n,))
    return np.sin(2 * np.pi * (fase + np.cumsum(f) / SR))


def vibrato(f, n, taxa=5.5, cents=12, atraso=0.25):
    t = eixo(n)
    prof = np.clip((t - atraso) / 0.4, 0, 1) * cents
    return f * 2 ** (prof * np.sin(2 * np.pi * taxa * t) / 1200)


def saturar(x, drive=1.5):
    return np.tanh(drive * x) / np.tanh(drive)


def normalizar(x, pico=0.9):
    m = np.abs(x).max()
    return x * (pico / m) if m > 0 else x


# ---------------------------------------------------------------- bateria sintetizada

FREQS_808 = (205.3, 304.4, 369.6, 522.7, 540.0, 800.0)


def metal(n, escala=1.0):
    t = eixo(n)
    return sum(np.sign(np.sin(2 * np.pi * f * escala * t + i)) for i, f in enumerate(FREQS_808)) / 6


def bumbo(tom=50, queda=0.3, soco=3.0, clique=0.25, dur=0.6):
    n = amostras(dur)
    t = eixo(n)
    corpo = seno(tom * (1 + soco * np.exp(-t / 0.032)), n) * np.exp(-t / queda)
    ataque = passa_alta(ruido(n, 1), 1800) * np.exp(-t / 0.004) * clique
    return saturar(corpo + ataque, 1.8) * envelope(n, 0.0005, 0.03)


def caixa(tom=185, queda=0.16, corpo=0.55, brilho=7500, dur=0.45, semente=2):
    n = amostras(dur)
    t = eixo(n)
    tonal = seno(tom * (1 + 0.5 * np.exp(-t / 0.015)), n) * np.exp(-t / 0.06) * corpo
    chiado = passa_banda(ruido(n, semente), 1400, brilho) * np.exp(-t / queda)
    return normalizar(tonal + chiado) * envelope(n, 0.0008, 0.03)


def caixa_portao(dur=0.28, semente=3):
    """Caixa com reverb cortado: cauda densa que para de repente, típica dos anos 80."""
    n = amostras(dur + 0.03)
    t = eixo(n)
    golpe = caixa(dur=0.2, queda=0.12, semente=semente)
    cauda = passa_banda(ruido(n, semente + 1), 500, 7000) * (0.55 + 0.45 * np.exp(-t / 0.05))
    cauda *= np.clip(1 - (t - dur) / 0.025, 0, 1)
    x = cauda * 0.6
    x[:len(golpe)] += golpe
    return normalizar(x)


def palmas(semente=4, dur=0.4):
    n = amostras(dur)
    t = eixo(n)
    x = np.zeros(n)
    base = passa_banda(ruido(n, semente), 900, 2600)
    for atraso in (0.0, 0.009, 0.018, 0.029):
        tt = np.clip(t - atraso, 0, None)
        x += base * np.where(t >= atraso, np.exp(-tt / 0.007), 0)
    x += base * np.exp(-t / 0.13) * 0.55 * (t > 0.029)
    return normalizar(x)


def chimbal(aberto=False, semente=5):
    dur = 0.45 if aberto else 0.12
    n = amostras(dur)
    x = passa_banda(metal(n), 6500, 15000) * 0.7 + passa_alta(ruido(n, semente), 8500) * 0.45
    x *= np.exp(-eixo(n) / (0.16 if aberto else 0.032))
    return normalizar(x) * envelope(n, 0.0008, 0.02)


def chocalho(semente=6):
    n = amostras(0.12)
    t = eixo(n)
    x = passa_banda(ruido(n, semente), 5200, 11000)
    return normalizar(x * np.clip(t / 0.012, 0, 1) * np.exp(-t / 0.045))


def prato(dur=2.6, semente=7, tom=1.0):
    n = amostras(dur)
    t = eixo(n)
    x = passa_alta(ruido(n, semente), 3500 * tom) * 0.8 + passa_banda(metal(n, 1.7 * tom), 3000, 12000) * 0.5
    return normalizar(x * np.exp(-t / (dur / 3.2)) * envelope(n, 0.002, 0.2))


def tambor(tom=110, queda=0.32):
    n = amostras(0.7)
    t = eixo(n)
    x = seno(tom * (1 + 0.6 * np.exp(-t / 0.05)), n) * np.exp(-t / queda)
    x += passa_banda(ruido(n, 8), 200, 3000) * np.exp(-t / 0.03) * 0.3
    return normalizar(saturar(x, 1.3))


def estalo(f=3200, semente=9):
    """Clique metálico curto, como o dente de uma fechadura."""
    n = amostras(0.09)
    t = eixo(n)
    x = seno(f, n) * np.exp(-t / 0.009) + seno(f * 1.507, n) * np.exp(-t / 0.005) * 0.6
    x += passa_alta(ruido(n, semente), 4500) * np.exp(-t / 0.0018) * 0.8
    return normalizar(x)


def chiado_vinil(n, semente=10):
    """Chiado de disco: estalos esparsos sobre um ruído baixo e abafado."""
    rng = np.random.default_rng(semente)
    x = passa_banda(rng.normal(0, 1, n), 300, 4000) * 0.03
    estalos = rng.random(n) < 7 / SR
    pulso = np.zeros(n)
    pulso[estalos] = rng.uniform(0.3, 1.0, estalos.sum()) * rng.choice([-1, 1], estalos.sum())
    x += passa_alta(np.convolve(pulso, np.exp(-np.arange(40) / 6), "same"), 1500)
    return x


# ---------------------------------------------------------------- efeitos de transição

def subida(dur, semente=11):
    """Ruído que sobe de tom até a cabeça do compasso seguinte."""
    n = amostras(dur)
    t = eixo(n) / dur
    x = ruido(n, semente)
    filtro = LadderFilter(mode=LadderFilter.Mode.BPF12, cutoff_hz=300, resonance=0.55)
    saida = np.zeros(n)
    bloco = 512
    for i in range(0, n, bloco):
        filtro.cutoff_hz = float(300 * (9000 / 300) ** t[i])
        saida[i:i + bloco] = filtro.process(x[i:i + bloco].astype(np.float32)[None, :], SR, reset=False)[0]
    return normalizar(saida * t ** 2.2) * envelope(n, 0.05, 0.01)


def prato_reverso(dur, semente=12):
    x = prato(dur + 0.3, semente)[::-1]
    return x[-amostras(dur):] * np.linspace(0.2, 1, amostras(dur)) ** 2


def impacto(semente=13):
    n = amostras(2.2)
    t = eixo(n)
    x = seno(42 * (1 + 1.5 * np.exp(-t / 0.08)), n) * np.exp(-t / 0.7)
    x += passa_baixa(ruido(n, semente), 1200) * np.exp(-t / 0.15) * 0.35
    return normalizar(saturar(x, 1.4))


# ---------------------------------------------------------------- sintetizadores

def supersaw(f, n, vozes=5, cents=11, semente=14):
    rng = np.random.default_rng(semente)
    desvios = np.linspace(-cents, cents, vozes)
    return sum(serra(f * 2 ** (d / 1200), n, rng.random()) for d in desvios) / vozes


def pad(notas, dur, corte=2500, ataque=0.5, soltura=0.9, semente=15):
    n = amostras(dur + soltura)
    x = sum(supersaw(hz(m), n, semente=semente + i) for i, m in enumerate(notas)) / max(1, len(notas)) ** 0.7
    return passa_baixa(x, corte, 2) * envelope(n, ataque, soltura, dur)


def pluck(nota, dur, brilho=4000, queda=0.18, semente=16):
    n = amostras(dur + 0.25)
    t = eixo(n)
    f = hz(nota)
    bruto = 0.7 * serra(f, n, 0.1) + 0.3 * quadrada(f * 1.003, n, 0.35, 0.4)
    claro, escuro = passa_baixa(bruto, brilho, 2), passa_baixa(bruto, 700, 2)
    k = np.exp(-t / 0.045)
    return (claro * k + escuro * (1 - k)) * np.exp(-t / queda) * envelope(n, 0.002, 0.2, dur)


def baixo_seno(nota, dur, ataque=0.006, soltura=0.05):
    n = amostras(dur + soltura)
    f = hz(nota)
    x = seno(f, n) + 0.22 * seno(2 * f, n) + 0.06 * seno(3 * f, n)
    return saturar(x * envelope(n, ataque, soltura, dur), 1.4)


def baixo_serra(nota, dur, brilho=1400, queda=0.25):
    n = amostras(dur + 0.04)
    t = eixo(n)
    f = hz(nota)
    bruto = 0.6 * serra(f, n) + 0.5 * seno(f, n)
    claro, escuro = passa_baixa(bruto, brilho, 2), passa_baixa(bruto, 260, 2)
    k = np.exp(-t / queda)
    return saturar((claro * k + escuro * (1 - k)) * envelope(n, 0.003, 0.04, dur), 1.6)


def rhodes(nota, dur, vel=0.8):
    """Piano elétrico por FM: o índice de modulação cai logo depois do ataque, como no Rhodes."""
    n = amostras(dur + 0.6)
    t = eixo(n)
    f = hz(nota)
    indice = (1.4 * vel) * np.exp(-t / 0.5) + 0.25
    x = np.sin(2 * np.pi * f * t + indice * np.sin(2 * np.pi * f * t))
    x += 0.05 * vel * np.sin(2 * np.pi * f * 14 * t) * np.exp(-t / 0.025)
    x *= 1 + 0.12 * np.sin(2 * np.pi * 4.8 * t)
    return x * np.exp(-t / 2.2) * envelope(n, 0.002, 0.45, dur)


def sino(nota, dur, vel=0.8):
    n = amostras(dur + 1.2)
    t = eixo(n)
    f = hz(nota)
    x = np.sin(2 * np.pi * f * t + 2.2 * vel * np.exp(-t / 0.8) * np.sin(2 * np.pi * f * 3.5 * t))
    return x * np.exp(-t / 1.1) * envelope(n, 0.002, 0.8, dur)


def lead(nota, dur, brilho=3200, largura=0.38):
    n = amostras(dur + 0.15)
    f = vibrato(hz(nota), n)
    x = 0.65 * quadrada(f, n, largura) + 0.35 * serra(f * 1.004, n, 0.3)
    return passa_baixa(x, brilho, 2) * envelope(n, 0.012, 0.12, dur)


# ---------------------------------------------------------------- linha do tempo e mixagem

class Trilha:
    """Acumula notas e sons numa linha do tempo medida em batidas."""

    def __init__(self, bpm, batidas, swing=0.5, grade=0.5, semente=42):
        self.bpm = bpm
        self.batida = 60.0 / bpm
        self.swing, self.grade = swing, grade
        self.dur = batidas * self.batida
        self.n = amostras(self.dur)
        self.stems = {}
        self.envios = {}
        self.gm = {}
        self.bumbos = []
        self.rng = np.random.default_rng(semente)

    def t(self, b, humano=0.0):
        """Batida → segundos, com swing na grade escolhida e um pouco de imprecisão humana."""
        g = self.grade
        pos = b % (2 * g)
        if abs(pos - g) < 1e-6:
            b = b + (self.swing - 0.5) * 2 * g
        return b * self.batida + (self.rng.normal(0, humano) if humano else 0.0)

    def stem(self, nome):
        if nome not in self.stems:
            self.stems[nome] = np.zeros((2, self.n + amostras(6)))
        return self.stems[nome]

    def por(self, nome, som, b, ganho=1.0, pan=0.0, humano=0.0, segundos=None):
        s = self.stem(nome)
        i = max(0, amostras(segundos if segundos is not None else self.t(b, humano)))
        som = np.asarray(som, dtype=float)
        if som.ndim == 1:
            som = np.vstack([som * np.cos((pan + 1) * np.pi / 4), som * np.sin((pan + 1) * np.pi / 4)]) * np.sqrt(2)
        m = min(som.shape[1], s.shape[1] - i)
        if m > 0:
            s[:, i:i + m] += som[:, :m] * ganho

    def nota(self, instrumento, b, nota, dur_b, vel=90, humano=0.0):
        """Nota de um instrumento do FluidR3: (banco, programa) ou "bateria:<kit>"."""
        self.gm.setdefault(instrumento, []).append((self.t(b, humano), dur_b * self.batida, int(nota), int(np.clip(vel, 1, 127))))

    def bumbo_em(self, b):
        self.bumbos.append(self.t(b))

    # -- instrumentos do FluidR3

    def renderizar_gm(self):
        for nome, notas in self.gm.items():
            self.stems[nome] = renderizar_fluid(nome, notas, self.stems.get(nome, np.zeros((2, self.n + amostras(6)))).shape[1])

    # -- mixagem

    def mixar(self, ajustes, reverb=None, alvo_lufs=-14.0, curva=None, dinamica=None):
        """ajustes: nome → dict(nivel=dB RMS, efeitos=[...], envio=0..1, abafar=profundidade do sidechain)."""
        tam = self.n + amostras(6)
        soma = np.zeros((2, tam))
        envio = np.zeros((2, tam))
        for nome, x in self.stems.items():
            a = ajustes.get(nome, {})
            x = x[:, :tam]
            if a.get("efeitos"):
                x = Pedalboard(a["efeitos"])(x.astype(np.float32), SR).astype(float)
            x = nivelar(x, a.get("nivel", -20))
            if a.get("abafar"):
                x = x * abafamento(tam, self.bumbos, a["abafar"], self.batida * 0.45)
            soma += x
            envio += x * a.get("envio", 0.0)
        if reverb is not None:
            soma += Pedalboard(reverb)(envio.astype(np.float32), SR).astype(float)
        soma = soma[:, :self.n]
        if dinamica is not None:
            soma = soma * dinamica[:self.n]
        return masterizar(soma, alvo_lufs, curva)


def renderizar_fluid(instrumento, notas, n):
    """Toca as notas no FluidSynth, sem o reverb e o chorus dele: os efeitos vêm depois."""
    mid = mido.MidiFile(ticks_per_beat=1000)
    trilha = mido.MidiTrack()
    mid.tracks.append(trilha)
    trilha.append(mido.MetaMessage("set_tempo", tempo=1_000_000))  # 1 batida = 1 s = 1000 ticks
    if isinstance(instrumento, str) and instrumento.startswith("bateria:"):
        canal, banco, programa = 9, 128, int(instrumento.split(":")[1])
    else:
        canal, (banco, programa) = 0, instrumento
    if canal != 9:
        trilha.append(mido.Message("control_change", channel=canal, control=0, value=banco, time=0))
    trilha.append(mido.Message("program_change", channel=canal, program=programa, time=0))
    eventos = []
    for t, d, nota, vel in notas:
        eventos.append((max(0, int(t * 1000)), 1, nota, vel))
        eventos.append((max(1, int((t + max(d, 0.03)) * 1000)), 0, nota, 0))
    eventos.sort(key=lambda e: (e[0], e[1]))
    agora = 0
    for tick, liga, nota, vel in eventos:
        tipo = "note_on" if liga else "note_off"
        trilha.append(mido.Message(tipo, channel=canal, note=nota, velocity=vel, time=tick - agora))
        agora = tick
    with tempfile.TemporaryDirectory() as tmp:
        arq_mid, arq_wav = os.path.join(tmp, "t.mid"), os.path.join(tmp, "t.wav")
        mid.save(arq_mid)
        subprocess.run(["fluidsynth", "-ni", "-q", "-R", "0", "-C", "0", "-g", "0.5", "-r", str(SR), "-F", arq_wav, BANCO, arq_mid],
                       check=True, capture_output=True)
        with AudioFile(arq_wav) as f:
            x = f.read(f.frames).astype(float)
    if x.shape[0] == 1:
        x = np.vstack([x, x])
    saida = np.zeros((2, n))
    m = min(n, x.shape[1])
    saida[:, :m] = x[:, :m]
    return saida


def rms_ativo(x):
    """RMS só dos trechos com som, para o nível não depender de quanto tempo o instrumento toca."""
    mono = np.abs(x).mean(0)
    bloco = SR // 20
    k = len(mono) // bloco
    if k == 0:
        return 0.0
    blocos = np.sqrt((mono[:k * bloco].reshape(k, bloco) ** 2).mean(1))
    ativos = blocos[blocos > blocos.max() * 0.1] if blocos.max() > 0 else blocos
    return float(np.sqrt((ativos ** 2).mean())) if len(ativos) else 0.0


def nivelar(x, db):
    r = rms_ativo(x)
    return x * (10 ** (db / 20) / r) if r > 0 else x


def abafamento(n, bumbos, profundidade, soltura):
    """Ganho que abaixa um instrumento a cada bumbo (sidechain), para o grave não embolar."""
    g = np.ones(n)
    curva = 1 - profundidade * np.exp(-np.arange(amostras(soltura * 4)) / (soltura * SR))
    ataque = amostras(0.004)
    curva[:ataque] = np.minimum(curva[:ataque], np.linspace(1, curva[ataque], ataque))
    for t in bumbos:
        i = amostras(t)
        m = min(len(curva), n - i)
        if m > 0:
            g[i:i + m] = np.minimum(g[i:i + m], curva[:m])
    return g


def limitar(x, teto_db=-1.5, antecipacao=0.005, soltura=0.12, bloco=32):
    """Limitador com antecipação: o ganho desce antes do pico e volta devagar, sem passar do teto."""
    teto = 10 ** (teto_db / 20)
    k = x.shape[1] // bloco + 1
    pad = np.zeros((x.shape[0], k * bloco))
    pad[:, :x.shape[1]] = x
    pico = np.abs(pad).max(0).reshape(k, bloco).max(1)
    preciso = np.minimum(1.0, teto / np.maximum(pico, 1e-9))
    passos = max(1, int(antecipacao * SR / bloco))
    adiante = minimum_filter1d(preciso, size=2 * passos + 1, origin=-passos, mode="nearest")
    volta = 1 - np.exp(-bloco / (soltura * SR))
    g = np.empty(k)
    atual = 1.0
    for i in range(k):
        atual = min(adiante[i], atual + (1 - atual) * volta)
        g[i] = atual
    ganho = np.interp(np.arange(k * bloco), np.arange(k) * bloco, g)[:x.shape[1]]
    return np.clip(x * ganho, -teto, teto)


# espectro médio de mixagens comerciais, em dB por oitava, relativo à oitava mais forte
CURVA_REFERENCIA = {31.5: -7, 63: 0, 125: -1, 250: -4, 500: -7, 1000: -10, 2000: -13, 4000: -16, 8000: -20, 16000: -27}


def oitavas(x):
    from scipy.signal import welch
    f, p = welch(x.mean(0), SR, nperseg=16384)
    niveis = {c: 10 * np.log10(p[(f >= c / 2 ** 0.5) & (f < c * 2 ** 0.5)].sum() + 1e-20) for c in CURVA_REFERENCIA}
    topo = max(niveis[c] for c in (63, 125, 250))
    return {c: v - topo for c, v in niveis.items()}


def equilibrar(x, curva, forca=0.7, limite=6.0):
    """Puxa o espectro médio na direção da curva de referência, oitava por oitava, sem passar de ±6 dB."""
    for _ in range(2):
        medido = oitavas(x)
        filtros = []
        for c, alvo in curva.items():
            if c < 60:
                continue
            g = float(np.clip((alvo - medido[c]) * forca, -limite, limite))
            if abs(g) < 0.5:
                continue
            filtros.append(HighShelfFilter(11000, g) if c == 16000 else PeakFilter(c, g, 1.1))
        if not filtros:
            break
        x = Pedalboard(filtros)(x.astype(np.float32), SR).astype(float)
    return x


def masterizar(x, alvo_lufs=-14.0, curva=None):
    """Equilibra o timbre, cola a mixagem e leva a loudness ao alvo do Instagram (cerca de −14 LUFS), com pico abaixo de −1,5 dB."""
    x = equilibrar(x, curva or CURVA_REFERENCIA)
    cadeia = Pedalboard([HighpassFilter(28), Compressor(threshold_db=-18, ratio=2.0, attack_ms=15, release_ms=150)])
    y = cadeia(x.astype(np.float32), SR).astype(float)
    medidor = pyloudnorm.Meter(SR)
    for _ in range(4):
        y = y * 10 ** ((alvo_lufs - medidor.integrated_loudness(y.T)) / 20)
        y = limitar(y)
    return y


def salvar(caminho, x):
    with AudioFile(caminho, "w", SR, num_channels=2, bit_depth=24) as f:
        f.write(x.astype(np.float32))


__all__ = [n for n in dir() if not n.startswith("_")] + [
    "Chorus", "Compressor", "Delay", "HighpassFilter", "HighShelfFilter", "LadderFilter", "Limiter",
    "LowpassFilter", "LowShelfFilter", "PeakFilter", "Reverb"]
