# 0,999… = 1 — vídeo Manim

Vídeo vertical **1080x1920 (9:16)** com a demonstração do truque do 10x:

$$x = 0{,}999\ldots \;\Rightarrow\; 10x = 9{,}999\ldots \;\Rightarrow\; 9x = 9 \;\Rightarrow\; x = 1$$

A igualdade é exata — as infinitas casas 9 se cancelam na subtração.
Fecha com a frase: "Não é aproximação. É igualdade."

## Como renderizar

Dentro desta pasta (`scenes/dizima_0999/`):

```powershell
python main.py --preview   # rápido, 540x960 @ 30 FPS
python main.py             # final, 1080x1920 @ 240 FPS
```

Saída: `media/videos/dizima_0999/<qualidade>/Dizima0999.mp4`.

Mesmo modelo visual dos vídeos MIT Integration Bee: título dourado,
cartões azuis com rótulos em português, resultado verde com glow e
zooms suaves de câmera.
