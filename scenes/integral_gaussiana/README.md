# A Integral Gaussiana — vídeo Manim

Vídeo vertical **1080x1920 (9:16)** com a demonstração clássica (nível superior):

$$I=\int_{-\infty}^{\infty}e^{-x^2}\,dx=\sqrt{\pi}$$

O truque de Poisson: elevar ao quadrado, virar integral dupla,
passar a coordenadas polares ($dx\,dy = r\,dr\,d\theta$), substituir $u=r^2$
e chegar em $I^2=\pi$.

Briefing correspondente: `prompts/PROMPT_INTEGRAL_GAUSSIANA_MANIM.md`.

## Como renderizar

Dentro desta pasta (`scenes/integral_gaussiana/`):

```powershell
python main.py --preview   # rápido, 540x960 @ 30 FPS
python main.py             # final, 1080x1920 @ 240 FPS
```

Saída: `media/videos/integral_gaussiana/<qualidade>/IntegralGaussiana.mp4`.

Mesmo modelo visual da série: título dourado, cartões azuis com rótulos
em português, resultado verde com glow, zooms suaves de câmera.
