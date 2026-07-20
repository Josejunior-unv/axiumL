# A Fórmula de Euler — vídeo Manim

Vídeo vertical **1080x1920 (9:16)** com a demonstração via séries de Taylor
(nível superior), culminando na Identidade de Euler:

$$e^{i\pi}+1=0$$

Roteiro: série de $e^z$, substituição $z=ix$, separação em partes real e
imaginária, reconhecimento das séries de $\cos x$ e $\sin x$, fórmula
$e^{ix}=\cos x+i\sin x$, avaliação em $x=\pi$.

Briefing correspondente: `prompts/PROMPT_FORMULA_EULER_MANIM.md`.

## Como renderizar

Dentro desta pasta (`scenes/formula_euler/`):

```powershell
python main.py --preview   # rápido, 540x960 @ 30 FPS
python main.py             # final, 1080x1920 @ 240 FPS
```

Saída: `media/videos/formula_euler/<qualidade>/FormulaEuler.mp4`.

Mesmo modelo visual da série: título dourado, cartões azuis com rótulos
em português, resultado verde com glow, zooms suaves de câmera.
