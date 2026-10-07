# Reels — Tráfego Pago (série de 10 vídeos)

10 vídeos verticais (1080×1920, 30 fps, ~30 s, com trilha e efeitos sonoros) para Instagram/TikTok,
feitos com motion design em código: HTML + GSAP, renderizados quadro a quadro no Chromium e montados com ffmpeg.
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

Legendas prontas para postar: [`LEGENDAS.md`](LEGENDAS.md).

## Como renderizar

Precisa de Node 18+, Python 3 com `numpy` e `scipy`, ffmpeg e Playwright (Chromium).

```bash
cd reels-trafego-pago
npm install                      # instala o GSAP
pip install numpy scipy
node render.mjs                  # renderiza os 10 → saida/*.mp4
node render.mjs 03 07            # só alguns episódios
node render.mjs 05 --stills 2,9  # só prints desses segundos, para conferir o visual
node render.mjs --mute           # sem trilha
```

Para ver/ajustar uma animação no navegador, abra `engine/stage.html?v=03` e chame `__seek(4.5)` no console.

## Personalizar

- `config.js`: coloque seu `@` em `handle` (aparece na tela final) e mude o nome da série.
- Cores de cada episódio: campo `theme` no topo de cada `videos/NN.js`.
- Textos: marcação `*destaque*` (gradiente), `[g-green:texto]`, `[g-red:texto]`, `[b:negrito]` e `\n` para quebrar linha.

## Estrutura

```
engine/   stage.html, core.js (motor: fundo, texto cinético, cenas, câmera, HUD), core.css, icons.js
videos/   um roteiro por episódio
audio/    trilha.py (batida 120 BPM + whoosh, impacto, pop, caixa registradora...)
render.mjs
```
