"""Gera a trilha (batida eletrônica) + efeitos sonoros sincronizados com o vídeo.

Uso: python3 trilha.py info.json saida.wav
O info.json vem do motor (duração, bpm e a lista de "cues" com tempo e nome do efeito).
Tudo é sintetizado aqui, então não há problema de direito autoral.
"""
import json
import sys
import wave

import numpy as np
import soundfile as sf
from scipy.signal import butter, resample_poly, sosfilt

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
    if name == "braam":  # o "BRAAAM" de trailer: metais graves desafinados + distorção
        t = t_axis(2.6)
        x = sum(saw(f, t, dt) for f in (note(38), note(45), note(50)) for dt in (-0.006, 0, 0.007))
        x = filt(x, "lp", 900) * env(len(t), 0.03, 0.9)
        sub = np.sin(2 * np.pi * note(26) * t) * env(len(t), 0.01, 0.8)
        return np.tanh(2.2 * (x * 0.18 + sub * 0.6)) * 0.55
    if name == "boom":
        t = t_axis(1.8)
        f = 30 + 70 * np.exp(-t / 0.12)
        return np.tanh(2 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.6)) * 0.75
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


# ---------------- estilos de trilha (um por episódio narrado) ----------------
def rhodes(freqs, d):
    t = t_axis(d)
    x = sum(np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.3) for f in freqs)
    trem = 1 + 0.18 * np.sin(2 * np.pi * 4.5 * t)
    return x / len(freqs) * env(len(t), 0.01, d * 0.7) * trem


def strings(freqs, d):
    t = t_axis(d)
    vib = 1 + 0.003 * np.sin(2 * np.pi * 5.2 * t)
    x = sum(saw(f * vib, t, dt) for f in freqs for dt in (-0.005, 0.0, 0.006)) / (3 * len(freqs))
    x = filt(x, "lp", 2200)
    a = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.3)
    return x * a


def tom(freq=70, d=0.6):
    t = t_axis(d)
    f = freq + freq * 1.4 * np.exp(-t / 0.04)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, d / 3)
    skin = filt(rng.standard_normal(len(t)), "bp", (150, 1200)) * env(len(t), 0.001, 0.05) * 0.5
    return np.tanh(1.5 * (body + skin))


def k808(freq, d, glide=None):
    t = t_axis(d)
    f = freq + 90 * np.exp(-t / 0.03)
    if glide:
        f = f + (glide - freq) * np.clip((t - d * 0.5) / (d * 0.3), 0, 1)
    return np.tanh(1.8 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, d * 0.45))


def bell(freq, d=0.6):
    t = t_axis(d)
    mod = np.sin(2 * np.pi * freq * 3.5 * t) * 2.5 * np.exp(-t / 0.15)
    return np.sin(2 * np.pi * freq * t + mod) * env(len(t), 0.001, d / 3)


def snare(soft=False):
    t = t_axis(0.25)
    n = filt(rng.standard_normal(len(t)), "bp", (1200, 7000)) * env(len(t), 0.001, 0.07 if soft else 0.1)
    b = np.sin(2 * np.pi * 190 * t) * env(len(t), 0.001, 0.04)
    return (n * 0.7 + b * 0.5) * (0.5 if soft else 0.8)


def crackle(n):
    x = np.zeros(n)
    idx = rng.integers(0, n, n // 900)
    x[idx] = rng.standard_normal(len(idx)) * 0.5
    return filt(x, "bp", (800, 6000)) + filt(rng.standard_normal(n), "lp", 900) * 0.01


def arrange(dur, style):
    """Devolve (mix, bpm). Cada estilo tem seu tempo, tom, timbres e levada."""
    st = STYLES[style]
    bpm = st["bpm"]
    beat = 60 / bpm
    bar = beat * 4
    n = int((dur + 3) * SR)
    dr, ba, hm = np.zeros(n), np.zeros(n), np.zeros(n)
    nb = int(np.ceil(dur / bar)) + 1
    for b in range(nb):
        t0 = b * bar
        ch = st["prog"][b % len(st["prog"])]
        intro = b == 0
        st["bar"](dr, ba, hm, t0, beat, ch, b, intro, dur)
    t = np.arange(n) / SR
    duck = 1 - st.get("duck", 0.5) * np.exp(-((t % beat)) / 0.1)
    return (dr * st.get("dr", 0.9) + (ba + hm) * duck)[: int(dur * SR)], bpm


def bar_epic(dr, ba, hm, t0, beat, ch, b, intro, dur):
    add(hm, strings([note(x) for x in ch], beat * 4 + 0.2), t0, 0.5)
    add(ba, strings([note(ch[0] - 24)], beat * 4 + 0.2), t0, 0.5)
    # ostinato de cordas em colcheias
    for i in range(8):
        add(hm, pluck(note(ch[0] - 12 + (12 if i % 4 == 3 else 0)), 0.16, 1600), t0 + i * beat / 2, 0.22)
    if intro:
        return
    for k, v in ((0, 1.0), (1.5, 0.6), (2, 0.8), (3, 0.6), (3.5, 0.7)):
        add(dr, tom(62 if k in (0, 2) else 95), t0 + k * beat, v)
    if b % 2 == 0:
        add(dr, sfx("boom"), t0, 0.5)
    add(dr, snare(), t0 + 2 * beat, 0.35)


def bar_lofi(dr, ba, hm, t0, beat, ch, b, intro, dur):
    sw = beat * 0.08  # swing
    add(hm, rhodes([note(x) for x in ch], beat * 4), t0, 0.55)
    add(ba, bass(note(ch[0] - 24), beat * 1.6), t0, 0.5)
    add(ba, bass(note(ch[0] - 24), beat * 1.2), t0 + 2.5 * beat, 0.45)
    if intro:
        return
    K = kick()
    for k in (0, 2.5):
        add(dr, K, t0 + k * beat, 0.6)
    for k in (1, 3):
        add(dr, snare(True), t0 + k * beat, 0.6)
    for i in range(8):
        add(dr, hat(), t0 + i * beat / 2 + (sw if i % 2 else 0), 0.25 if i % 2 else 0.35)
    if b % 2 == 1:
        add(hm, bell(note(ch[2] + 12), 0.8), t0 + 3.5 * beat, 0.08)


def bar_trap(dr, ba, hm, t0, beat, ch, b, intro, dur):
    add(hm, pad([note(x) for x in ch], beat * 4 + 0.1), t0, 0.28)
    mel = [ch[0] + 12, ch[2] + 12, ch[1] + 12, ch[2] + 12, ch[0] + 24, ch[2] + 12, ch[1] + 12, ch[0] + 12]
    for i, m in enumerate(mel):
        add(hm, bell(note(m), 0.5), t0 + i * beat / 2, 0.11)
    if intro:
        return
    # 808 com deslize no fim do compasso
    add(dr, k808(note(ch[0] - 24), beat * 1.5), t0, 0.9)
    add(dr, k808(note(ch[0] - 24), beat * 1.0), t0 + 1.75 * beat, 0.75)
    add(dr, k808(note(ch[0] - 24), beat * 1.2, glide=note(ch[0] - 19)), t0 + 3 * beat, 0.7)
    add(dr, clap(), t0 + 2 * beat, 0.8)
    roll = b % 2 == 1
    for i in range(16):
        add(dr, hat(), t0 + i * beat / 4, 0.3 if i % 2 == 0 else 0.18)
        if roll and i >= 12:
            add(dr, hat(), t0 + i * beat / 4 + beat / 8, 0.2)


def bar_house(dr, ba, hm, t0, beat, ch, b, intro, dur):
    for k in range(4):
        add(dr, kick(), t0 + k * beat, 0.95)
        add(ba, bass(note(ch[0] - 24), beat / 2), t0 + k * beat + beat / 2, 0.55)
        if not intro:
            add(dr, hat(True), t0 + k * beat + beat / 2, 0.35)
            if k in (1, 3):
                add(dr, clap(), t0 + k * beat, 0.55)
    # acordes de piano no contratempo
    for k in (0.5, 1.5, 2.75, 3.5):
        add(hm, pluck(note(ch[0]), 0.25, 3200) + pluck(note(ch[1]), 0.25, 3200) + pluck(note(ch[2]), 0.25, 3200), t0 + k * beat, 0.13)
    add(hm, pad([note(x) for x in ch], beat * 4), t0, 0.18)


def bar_funk(dr, ba, hm, t0, beat, ch, b, intro, dur):
    patt = [0, 0.75, 1.5, 2.25, 2.5, 3.25]
    for i, k in enumerate(patt):
        nn = ch[0] - 24 + (12 if i in (2, 5) else 0)
        add(ba, pluck(note(nn), 0.18, 1400) * 1.4, t0 + k * beat, 0.45)
    for k in (0.5, 1.5, 2.5, 3.5):  # guitarrinha/clav curtinha
        add(hm, pluck(note(ch[1] + 12), 0.09, 4500) + pluck(note(ch[2] + 12), 0.09, 4500), t0 + k * beat, 0.12)
    add(hm, pad([note(x) for x in ch], beat * 4), t0, 0.14)
    if intro:
        return
    for k in (0, 1.75, 2.5):
        add(dr, kick(), t0 + k * beat, 0.85)
    for k in (1, 3):
        add(dr, clap(), t0 + k * beat, 0.6)
    for i in range(16):  # pandeirola
        add(dr, hat(), t0 + i * beat / 4, 0.22 if i % 4 == 2 else 0.12)


STYLES = {
    "epico": {"bpm": 96, "prog": [[50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55]], "bar": bar_epic, "duck": 0.25},
    "lofi": {"bpm": 84, "prog": [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]], "bar": bar_lofi, "duck": 0.35},
    "trap": {"bpm": 140, "prog": [[54, 57, 61], [50, 54, 57], [52, 56, 59], [49, 52, 56]], "bar": bar_trap, "duck": 0.3},
    "house": {"bpm": 124, "prog": [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]], "bar": bar_house, "duck": 0.6},
    "funk": {"bpm": 108, "prog": [[52, 56, 59], [49, 52, 56], [57, 61, 64], [59, 63, 66]], "bar": bar_funk, "duck": 0.4},
}


def load_voice(info, n):
    """Coloca cada fala no seu tempo e devolve (voz, envelope de presença da voz)."""
    v = np.zeros(n)
    pres = np.zeros(n)
    for f in info.get("voice") or []:
        a, sr = sf.read(f"{info['voiceDir']}/{f['id']}.wav")
        if a.ndim > 1:
            a = a.mean(axis=1)
        a = resample_poly(a, SR, sr)
        a = filt(a, "hp", 90)
        add(v, a, f["t"])
        i0, i1 = int(f["t"] * SR), int((f["t"] + f["d"]) * SR)
        pres[max(0, i0):min(n, i1)] = 1
    # suaviza a entrada/saída do "abaixa a música"
    k = int(0.25 * SR)
    pres = np.convolve(pres, np.ones(k) / k, mode="same")
    pk = np.abs(v).max()
    if pk > 0:
        v = np.tanh(v / pk * 1.6) * 0.62  # compressão leve e nível fixo
    return v, np.clip(pres * 1.4, 0, 1)


def main():
    info = json.load(open(sys.argv[1]))
    dur = info["duration"]
    bpm = info.get("bpm", 120)
    style = info.get("music", "pop")
    if style in STYLES:
        m, _ = arrange(dur, style)
        m = m / max(1e-9, np.abs(m).max()) * 0.55
    else:
        m = music(dur, bpm) * 0.42
    voz, pres = load_voice(info, len(m))
    if info.get("voice"):
        m = m * (1 - 0.68 * pres)  # música desce quando tem fala
    fx = np.zeros(len(m))
    last = {}
    for c in info["cues"]:
        name = c["name"]
        # evita empilhar o mesmo efeito várias vezes no mesmo instante
        if name in last and c["t"] - last[name] < (0.04 if name == "tick" else 0.08):
            continue
        last[name] = c["t"]
        add(fx, sfx(name), c["t"], c.get("vol", 1))
    mix = m + fx * (0.6 if info.get("voice") else 0.85) * (1 - 0.35 * pres) + voz
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
