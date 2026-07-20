# Prompt para Claude Code — Problema da Basileia

> **Contexto**: Esta animação deve recriar a solução de **Euler (1735)** para o **Problema da Basileia**, produzindo um vídeo vertical cinematográfico em **Manim Community Edition**.

## Objetivo

Crie um projeto completo em **Python + ManimCE** para um vídeo **1080x1920 (9:16)** a **240 FPS**.

### Questão

\[
\sum_{n=1}^{\infty}\frac{1}{n^2}=1+\frac14+\frac19+\frac1{16}+\cdots=\ ?
\]

## Resolução (recriar exatamente — o argumento original de Euler)

1. Comece pela **série de Taylor** do seno:

\[
\frac{\sin x}{x}=1-\frac{x^2}{3!}+\frac{x^4}{5!}-\cdots
\]

2. Euler enxergou \(\frac{\sin x}{x}\) como um "polinômio infinito" cujas raízes são \(\pm\pi,\pm2\pi,\pm3\pi,\ldots\), e o fatorou como **produto infinito**:

\[
\frac{\sin x}{x}=\prod_{n=1}^{\infty}\left(1-\frac{x^2}{n^2\pi^2}\right).
\]

3. Expanda o produto e recolha o coeficiente de \(x^2\):

\[
\prod_{n=1}^{\infty}\left(1-\frac{x^2}{n^2\pi^2}\right)
=1-\left(\sum_{n=1}^{\infty}\frac{1}{n^2\pi^2}\right)x^2+\cdots
\]

4. **Iguale os coeficientes de \(x^2\)** das duas expressões:

\[
-\frac{1}{3!}=-\sum_{n=1}^{\infty}\frac{1}{n^2\pi^2}.
\]

5. Multiplique por \(-\pi^2\):

\[
\boxed{\sum_{n=1}^{\infty}\frac{1}{n^2}=\frac{\pi^2}{6}.}
\]

# Storyboard

- Introdução com o texto **"O Problema da Basileia"** e subtítulo **"A Solução de Euler (1735)"**.
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
