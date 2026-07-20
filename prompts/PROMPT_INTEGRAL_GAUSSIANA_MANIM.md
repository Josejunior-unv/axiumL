# Prompt para Claude Code — Integral Gaussiana

> **Contexto**: Esta animação deve recriar a demonstração clássica da **Integral Gaussiana** (truque de Poisson com coordenadas polares), produzindo um vídeo vertical cinematográfico em **Manim Community Edition**.

## Objetivo

Crie um projeto completo em **Python + ManimCE** para um vídeo **1080x1920 (9:16)** a **240 FPS**.

### Questão

\[
I=\int_{-\infty}^{\infty}e^{-x^2}\,dx
\]

## Resolução (recriar exatamente)

1. Eleve ao quadrado, usando duas variáveis independentes:

\[
I^2=\left(\int_{-\infty}^{\infty}e^{-x^2}\,dx\right)\left(\int_{-\infty}^{\infty}e^{-y^2}\,dy\right)
=\iint_{\mathbb{R}^2}e^{-(x^2+y^2)}\,dx\,dy.
\]

2. Passe para **coordenadas polares**:

\[
x^2+y^2=r^2,\qquad dx\,dy=r\,dr\,d\theta.
\]

3. A integral dupla torna-se

\[
I^2=\int_0^{2\pi}\!\!\int_0^{\infty}e^{-r^2}\,r\,dr\,d\theta.
\]

4. Faça a substituição \(u=r^2,\ du=2r\,dr\):

\[
\int_0^{\infty}e^{-r^2}\,r\,dr=\frac12\int_0^{\infty}e^{-u}\,du=\frac12.
\]

5. Logo

\[
I^2=\int_0^{2\pi}\frac12\,d\theta=\pi.
\]

6. Como o integrando é positivo, \(I>0\):

\[
\boxed{I=\sqrt{\pi}.}
\]

# Storyboard

- Introdução com o texto **"A Integral Gaussiana"** e subtítulo **"O Truque de Poisson"**.
- Mostrar a integral sendo escrita.
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
