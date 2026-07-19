# MIT Integration Bee I2 — vídeo Manim

Vídeo vertical **1080x1920 (9:16)** resolvendo a segunda integral do MIT Integration Bee:

$$I_2=\int_0^{\pi/2}\sin^3(2x)\cos x\,dx = \frac{16}{35}$$

Gabarito do briefing conferido termo a termo — está correto (**16/35**).

## Arquivos

| Arquivo | Papel |
|---|---|
| `main.py` | Ponto de entrada — escolhe preview ou render final |
| `scenes.py` | A cena `MITIntegrationBeeI2` com todo o storyboard |
| `animations.py` | Efeitos reutilizáveis: glow, destaque, zoom suave |
| `config.py` | Resolução 9:16, FPS, fundo #0D1117, pastas de saída |
| `colors.py` | Paleta de cores centralizada |

## Como renderizar

Dentro desta pasta (`scenes/mit_integration_bee_i2/`):

```powershell
# Pré-visualização rápida — 540x960 @ 30 FPS (recomendado para iterar)
python main.py --preview

# Render final — 1080x1920 @ 240 FPS (demorado)
python main.py
```

A saída vai para `media/videos/mit_integration_bee_i2/<qualidade>/MITIntegrationBeeI2.mp4`
na raiz do repositório.

## Storyboard (≈ 47 s)

1. Título dourado "MIT Integration Bee" + subtítulo "Official Problem"
2. A integral $I_2$ é escrita; zoom suave de aproximação
3. Cartão "Arco duplo": $\sin(2x)=2\sin x\cos x$, elevado ao cubo → $8\sin^3x\cos^4x$
4. Cartão "Pitágoras": $\sin^2x=1-\cos^2x$
5. Cartão "Substituição": $t=\cos x$, com a troca dos limites ($1\to0$)
6. Sinal invertido: $-8\int_1^0 \to 8\int_0^1(t^4-t^6)\,dt$
7. Primitiva e avaliação: $8\left(\frac15-\frac17\right)$
8. Resultado **16/35** em verde com glow; zoom de encerramento

Mesmo padrão do vídeo I1: somente `TransformMatchingTex`,
`ReplacementTransform`, `Circumscribe`, `LaggedStart`, `AnimationGroup`,
`Write`, `FadeIn`, `FadeOut`, além do movimento de câmera para os zooms.
