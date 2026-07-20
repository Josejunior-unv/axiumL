# Prompt para Claude Code — Fórmula de Euler

> **Contexto**: Esta animação deve recriar a demonstração da **Fórmula de Euler** via séries de Taylor, culminando na identidade \(e^{i\pi}+1=0\), produzindo um vídeo vertical cinematográfico em **Manim Community Edition**.

## Objetivo

Crie um projeto completo em **Python + ManimCE** para um vídeo **1080x1920 (9:16)** a **240 FPS**.

### Questão

\[
e^{i\pi}+1=\ ?
\]

## Resolução (recriar exatamente)

1. Comece pela **série de Taylor** da exponencial:

\[
e^z=\sum_{n=0}^{\infty}\frac{z^n}{n!}=1+z+\frac{z^2}{2!}+\frac{z^3}{3!}+\cdots
\]

2. Substitua \(z=ix\) e use \(i^2=-1\):

\[
e^{ix}=1+ix-\frac{x^2}{2!}-i\frac{x^3}{3!}+\frac{x^4}{4!}+i\frac{x^5}{5!}-\cdots
\]

3. **Separe** as parcelas reais e imaginárias:

\[
e^{ix}=\left(1-\frac{x^2}{2!}+\frac{x^4}{4!}-\cdots\right)
+i\left(x-\frac{x^3}{3!}+\frac{x^5}{5!}-\cdots\right).
\]

4. Reconheça as duas séries de Taylor:

\[
\cos x=1-\frac{x^2}{2!}+\frac{x^4}{4!}-\cdots,
\qquad
\sin x=x-\frac{x^3}{3!}+\frac{x^5}{5!}-\cdots
\]

Obtendo a **Fórmula de Euler**:

\[
e^{ix}=\cos x+i\,\sin x.
\]

5. Avalie em \(x=\pi\):

\[
e^{i\pi}=\cos\pi+i\,\sin\pi=-1+0i=-1.
\]

6. Conclua com a **Identidade de Euler**:

\[
\boxed{e^{i\pi}+1=0.}
\]

# Storyboard

- Introdução com o texto **"A Fórmula de Euler"** e subtítulo **"A Equação Mais Bela da Matemática"**.
- Mostrar a série sendo escrita.
- Destacar cada passagem antes de aplicá-la (cartões com rótulos em português).
- Utilizar exclusivamente `TransformMatchingTex`, `ReplacementTransform`, `Circumscribe`, `LaggedStart`, `AnimationGroup`, `Write`, `FadeIn`, `FadeOut`.
- Nunca usar screenshots.
- Toda a matemática em MathTex.
- Câmera com zooms suaves.
- Fundo #0D1117.
- Resultado final em verde com glow.
- Duração entre 40 e 55 segundos.
- Comentários explicando cada trecho do código.
- Projeto modular (main.py, scenes.py, animations.py, config.py, colors.py, README.md).
