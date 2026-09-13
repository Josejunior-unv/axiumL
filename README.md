# axiumL — Projeto de vídeos com Manim

Este repositório guarda dois projetos:

- **`scenes/`** — os vídeos de matemática feitos com Manim (descrito abaixo).
- **`app-questionario/`** — app de tablet para aplicar a pesquisa *Uso da
  Tecnologia no Ensino Superior* e exportar as respostas para o Excel.
  No ar em **https://analisededados.vercel.app/**.
  Veja [`app-questionario/README.md`](app-questionario/README.md).

---

## Vídeos com Manim

### Estrutura das pastas

```
axiumL/
├── app-questionario/  # App da pesquisa (ver README próprio)
├── manim.cfg          # Configuração do Manim (saída, qualidade, etc.)
├── scenes/            # Código das cenas (.py) — um arquivo por vídeo/tema
│   └── exemplo.py
├── assets/            # Recursos usados nas cenas
│   ├── images/        # Imagens (logos, figuras)
│   ├── audio/         # Trilhas e narração
│   └── fonts/         # Fontes customizadas
├── scripts/           # Scripts auxiliares (roteiros, automações)
└── media/             # SAÍDA — vídeos renderizados (gerado pelo Manim)
    └── videos/<arquivo>/<qualidade>/NomeDaCena.mp4
```

### Como renderizar

Rode sempre a partir da raiz do projeto (onde está o `manim.cfg`):

```powershell
# Qualidade média (padrão, 720p) — bom para testar
manim scenes/exemplo.py Exemplo

# Alta qualidade (1080p 60fps) — versão final
manim -qh scenes/exemplo.py Exemplo

# Rascunho rápido (480p) — iteração rápida
manim -ql scenes/exemplo.py Exemplo
```

Os vídeos ficam em `media/videos/<nome_do_arquivo>/<qualidade>/`.

### Convenções

- Um arquivo `.py` por vídeo dentro de `scenes/`, com nome descritivo em minúsculas (ex.: `intro_derivadas.py`).
- Cada cena é uma classe com nome em PascalCase (ex.: `IntroDerivadas`).
- Assets sempre referenciados a partir de `assets/`.
