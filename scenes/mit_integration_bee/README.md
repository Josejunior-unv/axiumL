# MIT Integration Bee — vídeo Manim

Vídeo vertical **1080x1920 (9:16)** resolvendo a integral do MIT Integration Bee:

$$I_1=\int_0^{\pi/2}\sin(x)\sin(2x)\sin(3x)\,dx = \frac{1}{6}$$

> ⚠️ **Correção em relação ao briefing**: o prompt original pedia um boxed
> $-\tfrac16$, mas os próprios passos intermediários levam a $+\tfrac16$
> (verificado termo a termo). O vídeo usa o valor correto **+1/6**.

## Arquivos

| Arquivo | Papel |
|---|---|
| `main.py` | Ponto de entrada — escolhe preview ou render final |
| `scenes.py` | A cena `MITIntegrationBee` com todo o storyboard |
| `animations.py` | Efeitos reutilizáveis: glow, destaque, zoom suave |
| `config.py` | Resolução 9:16, FPS, fundo #0D1117, pastas de saída |
| `colors.py` | Paleta de cores centralizada |

## Como renderizar

Dentro desta pasta (`scenes/mit_integration_bee/`):

```powershell
# Pré-visualização rápida — 540x960 @ 30 FPS (recomendado para iterar)
python main.py --preview

# Render final — 1080x1920 @ 240 FPS (DEMORADO: são ~12.000 frames)
python main.py
```

A saída vai para `media/videos/mit_integration_bee/<qualidade>/MITIntegrationBee.mp4`
na raiz do repositório.

> 💡 240 FPS é um valor extremo (YouTube/Instagram exibem no máximo 60 FPS).
> Se o render final demorar demais, reduza `FPS_FINAL` em `config.py` para 60.

## Storyboard (≈ 50 s)

1. Título dourado "MIT Integration Bee" + subtítulo "Official Problem"
2. A integral é escrita; zoom suave de aproximação
3. Identidade $\sin A\sin B$ destacada (Circumscribe) e aplicada
4. Distribuição de $\sin(3x)$
5. Identidades produto→soma em cartão (LaggedStart) e aplicação
6. Integração termo a termo
7. Avaliação nos limites e simplificação
8. Resultado **+1/6** em verde com glow; zoom de encerramento

Somente as animações permitidas pelo briefing são usadas
(`TransformMatchingTex`, `ReplacementTransform`, `Circumscribe`,
`LaggedStart`, `AnimationGroup`, `Write`, `FadeIn`, `FadeOut`),
além do movimento de câmera exigido para os zooms.
