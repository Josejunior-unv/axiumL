# Reels — Tráfego Pago (série de 10 vídeos)

10 vídeos verticais (1080×1920, 30 fps, ~30 s, com trilha e efeitos sonoros) para Instagram/TikTok,
feitos com motion design em código (visual colorido e alegre: fundos chapados, texto escuro, cartões tipo adesivo): HTML + GSAP, renderizados quadro a quadro no Chromium e montados com ffmpeg.
A trilha e os efeitos são sintetizados em Python (sem problema de direito autoral).

| EP | Tema | Arquivo de roteiro |
|----|------|--------------------|
| 01 | O que é tráfego pago (orgânico × pago, do anúncio à venda) | `videos/01.js` |
| 02 | As 5 métricas: CPM, CTR, CPC, CPA, ROAS | `videos/02.js` |
| 03 | ROAS 4 e mesmo assim prejuízo? (ROAS de equilíbrio) | `videos/03.js` |
| 04 | Funil topo/meio/fundo + remarketing | `videos/04.js` |
| 05 | Leilão da Meta: quem paga mais não ganha | `videos/05.js` |
| 06 | Criativo é a nova segmentação (Andromeda, ângulos) | `videos/06.js` |
| 07 | Anatomia de um anúncio que vende | `videos/07.js` |
| 08 | Pixel + API de Conversões | `videos/08.js` |
| 09 | Google Ads × Meta Ads | `videos/09.js` |
| 10 | 5 erros que queimam sua verba | `videos/10.js` |
| 11 | Quanto investir por dia? — narrado, trilha épica | `videos/11.js` |
| 12 | Teste A/B do jeito certo — narrado, trilha lo-fi | `videos/12.js` |
| 13 | Escalar sem quebrar a campanha — narrado, trilha trap | `videos/13.js` |
| 14 | Dobre as vendas sem gastar mais (landing page) — narrado, trilha house | `videos/14.js` |
| 15 | Quanto vale um cliente? (LTV × CAC) — narrado, trilha funk | `videos/15.js` |

Legendas prontas para postar: [`LEGENDAS.md`](LEGENDAS.md).

Os EP 11–15 são **narrados** (voz neural Kokoro em português, gerada offline), com legenda
palavra a palavra na tela, abertura com barras de cinema, transições em chicote e uma trilha
diferente em cada um (`music` no roteiro: `epico`, `lofi`, `trap`, `house`, `funk`).

## Como renderizar

Precisa de Node 18+, Python 3 com `numpy` e `scipy`, ffmpeg e Playwright (Chromium).

```bash
cd reels-trafego-pago
npm install                      # instala o GSAP
pip install numpy scipy soundfile kokoro-onnx
# modelo de voz (só para os episódios narrados), ~350 MB:
mkdir -p .tmp/voz && cd .tmp/voz
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd ../..
node render.mjs                  # renderiza os 10 → saida/*.mp4
node render.mjs 03 07            # só alguns episódios
node render.mjs 05 --stills 2,9  # só prints desses segundos, para conferir o visual
node render.mjs --mute           # sem trilha
```

Para ver/ajustar uma animação no navegador, abra `engine/stage.html?v=03` e chame `__seek(4.5)` no console.

## Personalizar

- `config.js`: coloque seu `@` em `handle` (aparece na tela final), mude o nome da série e a voz
  da narração (`voz`: `pm_alex`, `pm_santa` ou `pf_dora`).
- Narração: lista `narr` no roteiro. `text` é o que a voz fala, `cap` o que aparece na legenda
  (útil para números: fala "trinta reais", mostra "R$ 30"). A timeline se ajusta à duração real de cada fala.
- Cores de cada episódio: campo `theme` no topo de cada `videos/NN.js`.
- Textos: marcação `*destaque*` (gradiente), `[g-green:texto]`, `[g-red:texto]`, `[b:negrito]` e `\n` para quebrar linha.

## Estrutura

```
engine/   stage.html, core.js (motor: fundo, texto cinético, cenas, câmera, HUD), core.css, icons.js
videos/   um roteiro por episódio
audio/    trilha.py (5 estilos de trilha + efeitos + mixagem com a voz), narrar.py (TTS Kokoro)
render.mjs
```
