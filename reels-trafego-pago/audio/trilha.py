"""Gera a trilha (batida eletrônica) + efeitos sonoros sincronizados com o vídeo.

Uso: python3 trilha.py info.json saida.wav
O info.json vem do motor (duração, bpm e a lista de "cues" com tempo e nome do efeito).
Tudo é sintetizado aqui, então não há problema de direito autoral.
"""
import json
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
rng = np.random.default_rng(7)


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def filt(x, kind, f, order=2):
    if kind == "bp":
        sos = butter(order, [f[0] / (SR / 2), f[1] / (SR / 2)], btype="band", output="sos")
    else:
        sos = butter(order, f / (SR / 2), btype=kind, output="sos")
    return sosfilt(sos, x)


def env(n, a, d):
    """ataque linear (a s) e queda exponencial (d s)"""
    t = np.arange(n) / SR
    e = np.exp(-np.maximum(t - a, 0) / d)
    if a > 0:
        e = np.where(t < a, t / a, e)
    return e


def saw(freq, t, detune=0.0):
    ph = (freq * (1 + detune) * t) % 1.0
    return 2 * ph - 1


def note(n):  # número MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


# ---------------- instrumentos ----------------
def kick():
    t = t_axis(0.45)
    f = 48 + 120 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * env(len(t), 0.001, 0.16)
    click = filt(rng.standard_normal(len(t)), "hp", 3000) * env(len(t), 0, 0.004) * 0.4
    return np.tanh(1.6 * (body + click))


def clap():
    t = t_axis(0.35)
    n = filt(rng.standard_normal(len(t)), "bp", (900, 3200))
    e = np.zeros(len(t))
    for k, off in enumerate([0, 0.011, 0.022]):
        i = int(off * SR)
        e[i:] += env(len(t) - i, 0.0005, 0.012 if k < 2 else 0.09)
    return n * e * 0.6


def hat(open_=False):
    t = t_axis(0.25 if open_ else 0.08)
    n = filt(rng.standard_normal(len(t)), "hp", 7500)
    return n * env(len(t), 0.0005, 0.08 if open_ else 0.018) * 0.35


def pluck(freq, d=0.22, bright=2400):
    t = t_axis(d)
    x = saw(freq, t) + 0.6 * saw(freq, t, 0.006)
    x = filt(x, "lp", bright)
    return x * env(len(t), 0.002, d / 3.2)


def bass(freq, d):
    t = t_axis(d)
    x = 0.8 * np.sin(2 * np.pi * freq * t) + 0.35 * filt(saw(freq, t), "lp", 500)
    return np.tanh(1.4 * x) * env(len(t), 0.004, d * 0.6)


def pad(freqs, d):
    t = t_axis(d)
    x = np.zeros(len(t))
    for f in freqs:
        for dt in (-0.004, 0, 0.005):
            x += saw(f, t, dt) / 3
    x = filt(x, "lp", 1400) / len(freqs)
    a = np.minimum(1, t / 0.25) * np.minimum(1, (d - t) / 0.15)
    return x * a


def add(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf) or i + len(sig) <= 0:
        return
    j = min(len(buf), i + len(sig))
    if i < 0:
        sig = sig[-i:]
        i = 0
    buf[i:j] += sig[: j - i] * gain


# ---------------- efeitos ----------------
def sfx(name):
    if name == "whoosh":
        t = t_axis(0.55)
        n = rng.standard_normal(len(t))
        lo = filt(n, "bp", (300, 1200)) * np.exp(-((t - 0.16) / 0.1) ** 2)
        hi = filt(n, "bp", (1800, 6000)) * np.exp(-((t - 0.26) / 0.09) ** 2)
        return (lo * 0.9 + hi * 0.7) * 0.55
    if name == "swish":
        t = t_axis(0.35)
        n = rng.standard_normal(len(t))
        hi = filt(n, "bp", (2500, 9000)) * np.exp(-((t - 0.2) / 0.07) ** 2)
        lo = filt(n, "bp", (600, 2000)) * np.exp(-((t - 0.28) / 0.06) ** 2)
        return (hi * 0.6 + lo * 0.5) * 0.45
    if name == "hit":
        t = t_axis(1.1)
        f = 42 + 90 * np.exp(-t / 0.05)
        boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, 0.35)
        crack = filt(rng.standard_normal(len(t)), "lp", 5000) * env(len(t), 0.0005, 0.06)
        tail = filt(rng.standard_normal(len(t)), "bp", (200, 900)) * env(len(t), 0.01, 0.4) * 0.25
        return np.tanh(1.8 * (boom + 0.5 * crack + tail)) * 0.8
    if name == "pop":
        t = t_axis(0.12)
        f = 520 + 900 * (1 - np.exp(-t / 0.02))
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, 0.03) * 0.5
    if name == "tick":
        t = t_axis(0.03)
        return np.sin(2 * np.pi * 2600 * t) * env(len(t), 0.0005, 0.005) * 0.35
    if name == "click":
        t = t_axis(0.05)
        return filt(rng.standard_normal(len(t)), "bp", (1500, 6000)) * env(len(t), 0.0003, 0.006) * 0.8
    if name in ("ding", "cash"):
        t = t_axis(1.2)
        def bell(f0, d):
            parts = [(1, 1), (2.76, 0.5), (5.4, 0.25), (8.93, 0.12)]
            return sum(a * np.sin(2 * np.pi * f0 * r * t) * env(len(t), 0.001, d / r ** 0.5) for r, a in parts)
        if name == "ding":
            return bell(1318.5, 0.5) * 0.22
        x = bell(2093, 0.25) * 0.16
        y = np.zeros(len(t))
        y[int(0.09 * SR):] = bell(2637, 0.35)[: len(t) - int(0.09 * SR)] * 0.18
        sh = filt(rng.standard_normal(len(t)), "hp", 6000) * env(len(t), 0.002, 0.08) * 0.25
        return x + y + sh
    if name == "glitch":
        t = t_axis(0.35)
        x = np.sign(np.sin(2 * np.pi * 180 * t)) * 0.3
        chop = (np.floor(t * 40) % 2 == 0).astype(float)
        n = np.round(rng.standard_normal(len(t)) * 3) / 3 * 0.3
        return (x + n) * chop * env(len(t), 0.001, 0.12) * 0.55
    if name == "error":
        t = t_axis(0.5)
        f = np.where(t < 0.18, 330, 247)
        x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR))
        return filt(x, "lp", 2200) * env(len(t), 0.002, 0.2) * 0.3
    if name == "riser":
        t = t_axis(1.5)
        n = filt(rng.standard_normal(len(t)), "hp", 2500)
        f = 200 * 2 ** (t / 1.5 * 3)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
        return (n * 0.4 + s) * (t / 1.5) ** 2 * 0.5
    if name == "type":
        t = t_axis(0.03)
        return filt(rng.standard_normal(len(t)), "bp", (2000, 7000)) * env(len(t), 0.0002, 0.004) * 0.4
    raise ValueError(name)


# ---------------- arranjo ----------------
def music(dur, bpm):
    n = int((dur + 2) * SR)
    drums = np.zeros(n)
    bas = np.zeros(n)
    syn = np.zeros(n)
    beat = 60 / bpm
    bar = beat * 4
    prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
    K, C, Hh, Ho = kick(), clap(), hat(), hat(True)
    nbars = int(np.ceil(dur / bar)) + 1
    for b in range(nbars):
        t0 = b * bar
        ch = prog[b % 4]
        last = t0 + bar > dur - 0.5
        add(syn, pad([note(x) for x in ch], bar + 0.1), t0, 0.32)
        for k in range(4):
            tb = t0 + k * beat
            add(drums, K, tb, 0.95)
            if k in (1, 3):
                add(drums, C, tb, 0.55)
            add(drums, Ho if k == 3 else Hh, tb + beat / 2, 0.5)
            for s in (0.25, 0.75):
                add(drums, Hh, tb + beat * s, 0.22)
            for e in (0, 0.5):
                add(bas, bass(note(ch[0] - 24), beat / 2), tb + beat * e, 0.5)
        if b >= 1 and not last:  # arpejo entra depois do gancho
            seq = [ch[0], ch[1], ch[2], ch[1] + 12, ch[2], ch[1], ch[0] + 12, ch[2]]
            for i in range(16):
                add(syn, pluck(note(seq[i % 8] + 12), 0.2), t0 + i * beat / 4, 0.12)
    t = np.arange(n) / SR
    duck = 1 - 0.65 * np.exp(-((t % beat)) / 0.09)
    mix = drums * 0.9 + (bas + syn) * duck
    return mix[: int(dur * SR)]


def main():
    info = json.load(open(sys.argv[1]))
    dur = info["duration"]
    bpm = info.get("bpm", 120)
    m = music(dur, bpm) * 0.42
    fx = np.zeros(len(m))
    last = {}
    for c in info["cues"]:
        name = c["name"]
        # evita empilhar o mesmo efeito várias vezes no mesmo instante
        if name in last and c["t"] - last[name] < (0.04 if name == "tick" else 0.08):
            continue
        last[name] = c["t"]
        add(fx, sfx(name), c["t"], c.get("vol", 1))
    mix = m + fx * 0.85
    t = np.arange(len(mix)) / SR
    fade = np.clip((dur - t) / 1.2, 0, 1) * np.clip(t / 0.03, 0, 1)
    mix = np.tanh(mix * 1.15 * fade)
    mix = mix / max(1e-9, np.abs(mix).max()) * 0.93
    st = np.stack([mix, mix], axis=1)
    # leve abertura estéreo nos agudos
    side = filt(mix, "hp", 3000) * 0.18
    st[:, 0] += np.roll(side, 240)
    st[:, 1] -= np.roll(side, 240)
    st = np.clip(st, -1, 1)
    with wave.open(sys.argv[2], "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main()
