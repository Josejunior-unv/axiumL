# O Problema da Basileia — vídeo Manim

Vídeo vertical **1080x1920 (9:16)** com a solução de Euler (1735), nível superior:

$$\sum_{n=1}^{\infty}\frac{1}{n^2}=1+\frac14+\frac19+\cdots=\frac{\pi^2}{6}$$

O argumento original de Euler: a série de Taylor de $\frac{\sin x}{x}$,
o produto infinito pelas raízes $\pm n\pi$, e a comparação dos
coeficientes de $x^2$.

Briefing correspondente: `prompts/PROMPT_PROBLEMA_BASILEIA_MANIM.md`.

## Como renderizar

Dentro desta pasta (`scenes/problema_basileia/`):

```powershell
python main.py --preview   # rápido, 540x960 @ 30 FPS
python main.py             # final, 1080x1920 @ 240 FPS
```

Saída: `media/videos/problema_basileia/<qualidade>/ProblemaBasileia.mp4`.

Mesmo modelo visual da série: título dourado, cartões azuis com rótulos
em português, resultado verde com glow, zooms suaves de câmera.
