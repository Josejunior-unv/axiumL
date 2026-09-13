# Pesquisa — Uso da Tecnologia no Ensino Médio

App de coleta do questionário de 10 perguntas, feito para rodar no tablet:
você marca as respostas de cada aluno na tela e, no fim, baixa tudo em uma
planilha do Excel (`.xlsx`).

- **Funciona sem internet** depois da primeira abertura.
- **Instala como aplicativo** no tablet (ícone na tela inicial, tela cheia).
- **Não depende de servidor nem de conta**: as respostas ficam no próprio aparelho.
- **Sem bibliotecas externas**: a planilha é gerada pelo próprio app.

| Arquivo | O que é |
| --- | --- |
| `index.html` | O app inteiro — telas, perguntas e gerador da planilha |
| `manifest.webmanifest` | Faz o tablet reconhecer como aplicativo instalável |
| `sw.js` | Guarda o app no aparelho para funcionar offline |
| `icones/` | Ícone do app na tela inicial |
| `QUESTIONARIO.md` | O questionário em texto, para conferir ou imprimir |

---

## 1. Colocar o app no ar

O tablet precisa baixar o app de um endereço `https://` para poder instalá-lo.
O jeito mais simples é o GitHub Pages, que já está configurado neste repositório:

1. No GitHub, abra **Settings → Pages**.
2. Em **Source**, escolha **GitHub Actions**.
3. Vá em **Actions → Publicar app no GitHub Pages → Run workflow**
   (ou faça um push na branch `master` — a publicação roda sozinha).
4. O endereço aparece no fim da execução, algo como:
   `https://josejunior-unv.github.io/axiumL/`

> Sem internet na hora de instalar? Dá para copiar a pasta `app-questionario`
> para o tablet e abrir o `index.html` direto. Nesse modo o app funciona e
> exporta a planilha normalmente, só não instala como ícone na tela inicial.

## 2. Instalar no tablet

**Android / Chrome** — abra o endereço, toque no menu **⋮** e escolha
**Instalar aplicativo** (ou *Adicionar à tela inicial*).

**iPad / Safari** — abra o endereço, toque em **Compartilhar** (o quadrado com
a seta) e escolha **Adicionar à Tela de Início**.

Pronto: o ícone verde de check aparece junto dos outros apps e abre em tela cheia.
A partir daí ele funciona mesmo sem sinal — útil para aplicar a pesquisa no pátio
ou na sala.

## 3. Aplicar a pesquisa

1. Toque em **Nova resposta**.
2. Preencha o nome e a turma se quiser (os dois são opcionais — a pesquisa pode
   ser anônima).
3. Marque as alternativas de cada aluno. A barra no topo mostra quantas das 10
   já foram respondidas, e a faixa verde na lateral marca as concluídas.
   - **P3** aceita quantas marcações quiser.
   - **P5** e **P6** travam em três marcações, como pede o questionário.
   - **P4** tem um campo livre para anotar o "por quê" dito pelo aluno.
4. Toque em **Salvar resposta**. Se faltar alguma pergunta, o app avisa antes —
   e deixa salvar mesmo assim, se for o caso.
5. Repita para o próximo aluno. O painel mostra o total coletado e um resumo com
   as porcentagens de cada alternativa, que já atualiza a cada resposta.

## 4. Levar os dados para o Excel

No painel, toque em **Baixar Excel (.xlsx)**. O arquivo sai com duas abas:

- **Respostas** — uma linha por aluno, uma coluna por pergunta. Cabeçalho
  congelado e filtro já ligado. Nas perguntas de múltipla escolha as alternativas
  vêm separadas por `|` na mesma célula.
- **Resumo** — a contagem e a porcentagem de cada alternativa, pergunta por
  pergunta, pronta para virar gráfico no Excel (selecione as colunas
  *Alternativa* e *Respostas* → **Inserir → Gráfico**).

Também existe **Baixar CSV**, com separador `;` e acentuação preservada, caso
você prefira abrir no Google Planilhas ou em outro programa.

> As respostas ficam guardadas no navegador do tablet. Elas somem se você limpar
> os dados de navegação ou desinstalar o app — então **baixe a planilha antes de
> usar "Apagar tudo"**.

## 5. Mudar as perguntas

Todo o questionário está em uma única lista no começo do `<script>` do
`index.html`, na constante `PERGUNTAS`:

```js
{ id:"p5", curto:"Principais benefícios", tipo:"multipla", max:3,
  texto:"Quais são, na sua opinião, os principais benefícios ...?",
  ajuda:"Marque até três opções.",
  opcoes:["Acesso a uma variedade de recursos de aprendizado", "..."] },
```

- `id` — identificador interno; não repita entre perguntas.
- `curto` — o nome que vira cabeçalho da coluna na planilha.
- `tipo` — `"unica"` (uma alternativa) ou `"multipla"` (várias).
- `max` — limite de marcações numa pergunta múltipla (`0` = sem limite).
- `aberta` — se presente, cria um campo de texto livre embaixo das alternativas.

Acrescente ou remova perguntas nessa lista e o app, o resumo e a planilha se
ajustam sozinhos. Se mudar as perguntas depois de já ter coletado respostas,
baixe a planilha antiga primeiro: as colunas mudam de nome junto.
