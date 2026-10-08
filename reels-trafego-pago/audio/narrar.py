"""Gera a narração de cada fala com o Kokoro (voz neural em português, roda offline).

Uso: python3 narrar.py falas.json saida_dir [voz] [pasta_do_modelo]
falas.json = [{"id": "a", "text": "...", "say": "texto falado (opcional)"}, ...]
Escreve saida_dir/<id>.wav (24 kHz) e saida_dir/duracoes.json ({id: segundos}).
Áudios iguais (mesmo texto, voz e velocidade) são reaproveitados do cache.
"""
import hashlib
import json
import os
import sys

import numpy as np
import soundfile as sf

falas = json.load(open(sys.argv[1]))
out = sys.argv[2]
voz = sys.argv[3] if len(sys.argv) > 3 else "pm_alex"
modelos = sys.argv[4] if len(sys.argv) > 4 else os.path.join(os.path.dirname(__file__), "..", ".tmp", "voz")
VEL = float(os.environ.get("NARR_SPEED", "1.12"))
os.makedirs(out, exist_ok=True)
cache = os.path.join(modelos, "cache")
os.makedirs(cache, exist_ok=True)

kokoro = None
dur = {}
for f in falas:
    txt = f.get("say") or f["text"]
    h = hashlib.sha1(f"{voz}|{VEL}|{txt}".encode()).hexdigest()[:16]
    cpath = os.path.join(cache, h + ".wav")
    if not os.path.exists(cpath):
        if kokoro is None:
            from kokoro_onnx import Kokoro
            kokoro = Kokoro(os.path.join(modelos, "kokoro-v1.0.onnx"), os.path.join(modelos, "voices-v1.0.bin"))
        a, sr = kokoro.create(txt, voice=voz, speed=VEL, lang="pt-br")
        # corta o silêncio das pontas (fica só um respiro curto)
        idx = np.where(np.abs(a) > 0.012)[0]
        if len(idx):
            a = a[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.06 * sr)]
        sf.write(cpath, a, sr)
    a, sr = sf.read(cpath)
    sf.write(os.path.join(out, f["id"] + ".wav"), a, sr)
    dur[f["id"]] = round(len(a) / sr, 3)
    print(f"  fala {f['id']}: {dur[f['id']]:.2f}s")

json.dump(dur, open(os.path.join(out, "duracoes.json"), "w"))
