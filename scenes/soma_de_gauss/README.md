# A Soma de Gauss — vídeo Manim

Vídeo vertical **1080x1920 (9:16)** com a demonstração clássica:

$$S = 1+2+3+\cdots+n = \frac{n(n+1)}{2}$$

O truque lendário (Gauss aos 9 anos): escrever a soma de trás para frente,
somar as duas linhas — cada coluna dá $(n+1)$, e são $n$ colunas.
Fecha com o exemplo famoso $1+2+\cdots+100 = 5050$.

## Como renderizar

Dentro desta pasta (`scenes/soma_de_gauss/`):

```powershell
python main.py --preview   # rápido, 540x960 @ 30 FPS
python main.py             # final, 1080x1920 @ 240 FPS
```

Saída: `media/videos/soma_de_gauss/<qualidade>/SomaDeGauss.mp4`.

Mesmo modelo visual dos vídeos MIT Integration Bee: título dourado,
cartões azuis com rótulos em português, resultado verde com glow,
zooms suaves de câmera, e somente as animações do padrão
(`TransformMatchingTex`, `ReplacementTransform`, `Circumscribe`,
`LaggedStart`, `AnimationGroup`, `Write`, `FadeIn`, `FadeOut`).
