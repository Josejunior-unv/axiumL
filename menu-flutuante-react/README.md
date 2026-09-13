# Menu flutuante (versão React)

O componente `liquid-morph-floating-menu.tsx` é React + TypeScript + Tailwind e
precisa de um projeto com essa stack para funcionar. **Este repositório não tem
nenhuma delas** — o app da pesquisa (`../app-questionario/`) é HTML, CSS e
JavaScript puros, sem build.

Por isso o efeito foi **portado para o app**, em JS puro e na paleta do site.
Os arquivos aqui ficam guardados para o caso de você criar um projeto React
depois.

## Por que `components/ui`

O shadcn/ui não é uma biblioteca que você instala e importa: ele **copia o
código-fonte** dos componentes para dentro do seu projeto, para você poder
editá-los. O `components.json` guarda para onde copiar, e o padrão é
`components/ui`. O CLI (`npx shadcn@latest add ...`) e os imports gerados
(`@/components/ui/...`) assumem essa pasta. Fora dela, cada componente novo
precisaria de ajuste manual de caminho.

## Montar o projeto do zero

```bash
# 1. Next.js com TypeScript e Tailwind
npx create-next-app@latest meu-app --typescript --tailwind --eslint --app

cd meu-app

# 2. shadcn/ui — cria components.json e a pasta components/ui
npx shadcn@latest init

# 3. a dependência que este componente usa
npm install framer-motion
```

## Onde colocar os arquivos

```
meu-app/
├── components/
│   └── ui/
│       └── liquid-morph-floating-menu.tsx
└── app/
    └── page.tsx        <- conteúdo de demo.tsx
```

O `demo.tsx` importa `../components/ui/liquid-morph-floating-menu`. Se você
colocar a demo em `app/page.tsx`, troque o import por
`@/components/ui/liquid-morph-floating-menu`.

## Respostas às perguntas de integração

- **Props:** `items?: { label: string; onClick?: () => void }[]`. Sem `items`,
  usa Home / Works / Contact.
- **Estado:** todo interno (`isOpen`, `hovered` por item). Não precisa de
  Context, store nem provider.
- **Assets:** nenhum. O hambúrguer são duas `<span>` que giram; não usa ícone
  nem imagem, então não há necessidade de `lucide-react`.
- **Fontes:** o código pede `Trobika` e `Aeonik TRIAL`, que são comerciais e não
  vêm no projeto. Os fallbacks são `Bebas Neue` e `Inter` — inclua-os pelo
  Google Fonts ou troque pela fonte do seu projeto.
- **Responsivo:** é `fixed bottom-10 left-1/2`, centralizado embaixo em qualquer
  largura. Só o rótulo "Menu" muda de tamanho (14px, 20px a partir de `md`).
  O painel aberto tem 280x260 fixos — em telas bem estreitas convém reduzir.
- **Onde usar:** no layout raiz, para aparecer em todas as páginas. Cuidado com
  qualquer barra fixa no rodapé: as duas disputam o mesmo espaço.
