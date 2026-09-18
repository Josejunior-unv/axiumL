# Pesquisa — Uso da Tecnologia no Ensino Superior

App de coleta do questionário de 10 perguntas, feito para rodar no tablet:
você marca as respostas de cada estudante na tela e, no fim, baixa tudo em uma
planilha do Excel (`.xlsx`).

- **Funciona sem internet** depois da primeira abertura.
- **Instala como aplicativo** no tablet (ícone na tela inicial, tela cheia).
- **Não depende de servidor nem de conta**: as respostas ficam no próprio aparelho.
- **Sem bibliotecas externas**: a planilha é gerada pelo próprio app.
- **Tipografia do sistema**: no iPhone e no iPad usa a SF Pro da Apple; nos
  outros aparelhos, a Inter, que é o equivalente mais próximo.

| Arquivo | O que é |
| --- | --- |
| `index.html` | O app inteiro — telas, perguntas e gerador da planilha |
| `manifest.webmanifest` | Faz o tablet reconhecer como aplicativo instalável |
| `sw.js` | Guarda o app no aparelho para funcionar offline |
| `vercel.json` | Cabeçalhos de cache, se publicar na Vercel |
| `icones/` | Ícone do app na tela inicial |
| `QUESTIONARIO.md` | O questionário em texto, para conferir ou imprimir |
| `config.json` | Onde as respostas vão parar (veja abaixo) |
| `apps-script.gs` | O script que grava as respostas na sua planilha do Google |

---

## 1. Receber as respostas

Sem isto, cada resposta fica no aparelho de quem respondeu. Configurando, **você
manda um link, a pessoa responde e a resposta cai num lugar seu**. Há dois
caminhos; escolha um.

### Opção A — banco da própria Vercel (menos passos)

Tudo dentro do painel onde o site já está. Você não copia endereço nenhum.

1. No projeto da Vercel: **Storage → Create Database → Upstash for Redis**,
   e conecte ao projeto. A Vercel injeta as chaves sozinha.
2. **Settings → Environment Variables →** `CHAVE_LEITURA` = uma senha sua.
3. **Redeploy.**

Pronto. O app pergunta sozinho a `/api/respostas` se o banco está de pé e,
estando, passa a enviar para lá. O arquivo `api/respostas.js` é a função que
grava; ela precisa ficar na **raiz do repositório**, que é a pasta padrão da
importação.

### Opção B — planilha do Google

Quando você prefere ver as respostas caindo numa planilha, ao vivo.

1. Crie uma planilha em **sheets.new**
2. **Extensões → Apps Script**, apague tudo e cole o `apps-script.gs`
3. Troque `CHAVE_LEITURA` por uma senha sua
4. **Implantar → Nova implantação → App da Web**
   · *Executar como:* Eu · *Quem pode acessar:* **Qualquer pessoa**
5. Copie o endereço que termina em `/exec` e ponha no `config.json`:

```json
{ "endpoint": "https://script.google.com/.../exec" }
```

### Como o app fica depois

| Endereço | Quem usa | O que vê |
| --- | --- | --- |
| `.../app-questionario/` | quem você convidar | só o questionário; responde, envia e agradece |
| `.../app-questionario/#painel` | você | o painel, o resumo e os botões de baixar |

O botão de compartilhar entrega sempre o endereço de responder, nunca o
`#painel`.

**A chave de leitura não fica em arquivo nenhum do repositório.** O
`config.json` é servido para todo mundo que abre o link; se a senha estivesse
ali, qualquer pessoa baixaria todas as respostas. Você digita a chave uma vez,
ao tocar em **Buscar respostas enviadas**, e ela fica guardada só no seu
aparelho.

**Sem internet na hora de responder?** A resposta fica guardada no aparelho da
pessoa e sobe sozinha quando a conexão voltar.

**Reenvio não duplica:** cada resposta tem um código próprio, e o servidor
recusa a segunda gravação do mesmo código.

**Apagar apaga de verdade.** A lixeira de cada resposta e o *Apagar tudo*
alcançam o banco, não só o aparelho — apagar só aqui faria a resposta voltar na
busca seguinte. Apagar exige a mesma chave da leitura, e o servidor tenta lá
primeiro: se não conseguir, nada some da tela, para o que você vê continuar
sendo verdade. Cuidado com o *Apagar tudo* quando o banco está ligado: ele leva
junto o que as outras pessoas enviaram.

> Sem nenhuma das duas opções, o app volta a funcionar como antes: tudo no
> aparelho e a junção feita pelos arquivos de cópia.

## 2. Colocar o app no ar

O tablet precisa baixar o app de um endereço `https://` para poder instalá-lo.
Duas opções, as duas gratuitas.

### Vercel — endereço em uso

**https://analisededados.vercel.app/**

Foi assim que ele subiu:

1. Entre em [vercel.com](https://vercel.com) com a sua conta do GitHub.
2. **Add New → Project** e importe o repositório `axiumL`.
3. Clique em **Deploy**. Não precisa mudar mais nada — o `vercel.json` da raiz
   já redireciona o endereço principal para o app e cuida do cache.

Se quiser o endereço mais curto possível (o app na raiz, sem `/app-questionario`
no fim), antes de dar Deploy clique em *Edit* em **Root Directory** e escolha a
pasta `app-questionario`. Funciona das duas formas.

Cada push na branch publica sozinho. O `vercel.json` já vai junto e diz para o navegador nunca guardar o
`index.html` e o `sw.js` em cache — assim uma versão nova chega na hora.

### GitHub Pages

Já está configurado neste repositório: em **Settings → Pages**, com *Deploy from
a branch* apontando para a branch do app. O endereço é
`https://josejunior-unv.github.io/axiumL/`.

**Atualizações.** Quando você publica uma versão nova, ela chega ao tablet na
próxima vez que o app for aberto com internet — o service worker busca primeiro
no servidor e só usa a cópia guardada quando está offline. O rodapé do painel
mostra qual versão está rodando.

> Sem internet na hora de instalar? Dá para copiar a pasta `app-questionario`
> para o tablet e abrir o `index.html` direto. Nesse modo o app funciona e
> exporta a planilha normalmente, só não instala como ícone na tela inicial.

## 3. Instalar no tablet

**Android / Chrome** — abra o endereço, toque no menu **⋮** e escolha
**Instalar aplicativo** (ou *Adicionar à tela inicial*).

**iPad / Safari** — abra o endereço, toque em **Compartilhar** (o quadrado com
a seta) e escolha **Adicionar à Tela de Início**.

Pronto: o ícone verde de check aparece junto dos outros apps e abre em tela cheia.
A partir daí ele funciona mesmo sem sinal — útil para aplicar a pesquisa no pátio
ou na sala.

## 4. Menu flutuante

No painel, embaixo e no centro, há uma pílula azul escrita **Menu**. Tocando
nela, um círculo escuro sobe e a transforma num painel com três atalhos: *Nova
resposta*, *Baixar Excel* e *Compartilhar*. Fecha tocando fora, no X ou com Esc.

Ele some durante a coleta, para não disputar espaço com o botão **Salvar
resposta**, que fica fixo no rodapé.

## 5. A gatinha

Toda vez que um botão é apertado, uma gatinha chega e **aperta junto**: a
patinha dela encosta exatamente no ponto em que o dedo tocou, afunda no mesmo
instante e levanta quando o dedo levanta. Ela vem pela esquerda e se espelha
sozinha quando não cabe.

O desenho é original, em SVG, na paleta do app. O botão **trocar figura**, no
rodapé, troca a gatinha por uma imagem sua — ela é reduzida para 160px e fica
guardada só neste aparelho.

O desenho tem `pointer-events: none`, então nunca rouba o toque: o botão recebe
o clique normalmente mesmo com ela por cima. Também não aparece nas alternativas
do questionário, que são tocadas o tempo todo e ficariam poluídas.

No rodapé do painel há um interruptor para desligá-la. A escolha fica salva no
aparelho — útil na hora de aplicar a pesquisa a sério.

## 6. Aplicar a pesquisa

1. Toque em **Nova resposta**.
2. Preencha a identificação e o curso se quiser (os dois são opcionais — a pesquisa pode
   ser anônima).
3. Marque as alternativas de cada estudante. A barra no topo mostra quantas das 10
   já foram respondidas, e a faixa verde na lateral marca as concluídas.
   - **P3** aceita quantas marcações quiser.
   - **P5** e **P6** travam em três marcações, como pede o questionário.
   - **P4** tem um campo livre para anotar o "por quê" dito pelo estudante.
4. Toque em **Salvar resposta**. Se faltar alguma pergunta, o app avisa antes —
   e deixa salvar mesmo assim, se for o caso.
5. Repita para o próximo estudante. O painel mostra o total coletado e um resumo com
   as porcentagens de cada alternativa, que já atualiza a cada resposta.

## 7. Levar os dados para o Excel

No painel, toque em **Baixar Excel (.xlsx)**. O arquivo sai com duas abas e os
gráficos já montados:

- **Respostas** — uma linha por estudante, uma coluna por pergunta. Cabeçalho
  congelado e filtro ligado. Data e hora são valores de data de verdade (dá para
  ordenar e filtrar por período), e a coluna *Respondidas* traz quantas das 10
  perguntas aquele estudante respondeu. Nas perguntas de múltipla escolha as
  alternativas vêm separadas por `|` na mesma célula.
- **Resumo** — uma tabela por pergunta com a contagem, a porcentagem (formatada
  como percentual de verdade, não texto) e a base, e **ao lado de cada tabela um
  gráfico de barras pronto**, já em porcentagem, com o número de respondentes no
  título (*n = 9*).

Os números do Resumo são **fórmulas ligadas à aba Respostas**, não valores
colados: `CONT.SE` para contar cada alternativa, `CONT.VALORES` para a base e uma
divisão para a porcentagem. Corrija uma resposta na aba Respostas e a tabela e o
gráfico se atualizam sozinhos. As faixas vão até a linha 1000, então dá para
acrescentar respostas à mão que elas entram na conta. Nas perguntas de múltipla
escolha a contagem procura o texto dentro da célula, porque as alternativas
ficam juntas separadas por `|`.

Os gráficos são gráficos nativos do Excel, não imagens: clique com o botão
direito para mudar cor, tipo ou título, e é só copiar e colar no Word do
trabalho. Como estão ligados às células, se você corrigir um número na tabela o
gráfico se atualiza sozinho.

Também existe **Baixar CSV**, com separador `;` e acentuação preservada, caso
você prefira abrir no Google Planilhas ou em outro programa.

> As respostas ficam guardadas no navegador do tablet. Elas somem se você limpar
> os dados de navegação ou desinstalar o app — então **baixe a planilha antes de
> usar "Apagar tudo"**.

## 8. Dividir a coleta com o grupo

Dá para várias pessoas aplicarem a pesquisa ao mesmo tempo, cada uma no próprio
celular ou tablet, e no fim juntar tudo numa planilha só.

No painel, a seção **Coleta em grupo** mostra os três passos na ordem, cada um
com o próprio botão ao lado.

**Passo 1 — passar o app adiante.** Toque em **Compartilhar o app**.
Aparece o link, um botão de copiar e o **QR code** para os colegas apontarem a
câmera. Em celular e tablet aparece também **Compartilhar…**, que abre o
WhatsApp, e-mail e o resto do sistema. Ninguém precisa criar conta nem instalar
nada além do próprio app.

O QR é gerado pelo app a partir do endereço em que ele está sendo aberto, então
continua certo se você mudar de hospedagem — não há endereço fixo no código para
lembrar de trocar. O botão **Baixar QR** salva a imagem em SVG, para projetar no
telão ou imprimir sem perder qualidade.

**Passo 2 e 3 — juntar as respostas no fim.** Cada colega toca em **Exportar cópia** e manda o
arquivo `.json` para quem vai montar o trabalho (WhatsApp, e-mail, o que for
mais fácil). Quem recebe toca em **Juntar respostas**, seleciona todos os
arquivos de uma vez e pronto: o app soma tudo, ignora as respostas repetidas
(se o mesmo arquivo entrar duas vezes) e avisa quantas entraram. Depois é só
**Baixar Excel** para sair a planilha do grupo inteiro, com o resumo já
recalculado em cima do total.

> Cada resposta tem um código próprio, então nada é contado duas vezes, mesmo
> que os arquivos se cruzem entre os colegas.

## 9. Mudar as perguntas

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
