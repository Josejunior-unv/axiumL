// Versão dos vídeos para Reels do Instagram: 1080 × 1920, cada um com trilha sonora própria.
//
//   node projetos-ia/video/reels.js                 # os cinco reels
//   node projetos-ia/video/reels.js cofre           # só um (churn, demanda, fraude, recomendacao, cofre)
//   node projetos-ia/video/reels.js --previa cofre  # só alguns quadros em JPEG, para ajustar o enquadramento
//
// A página é aberta em 450 × 800 com escala 2,4, o tamanho de um celular, então o layout é o de celular.
// O topo e a base ficam lisos porque o Instagram desenha a interface por cima deles.
// Cada roteiro é medido em compassos da sua trilha: as trocas de cena caem na cabeça do compasso.
// A trilha é composta por trilhas/compor.py e misturada ao vídeo no fim.
// Saída: media/videos/projetos-ia/reels/ (pasta ignorada pelo git).

"use strict";
const path = require("path");
const fs = require("fs");
const { execFileSync } = require("child_process");
const { FPS, SAIDA, clicar, varrer, faixa, topoDe, gravar, duracao, abrirNavegador } = require("./gravar");

const RETRATO = { viewport: { width: 450, height: 800 }, escala: 2.4 }; // vídeo 1080 × 1920
const TOPO = 56;   // faixa de cima, coberta pelo título "Reels" e pela câmera
const BASE = 160;  // faixa de baixo, coberta por nome, legenda e áudio
const ROLAGEM = 1.4; // a mesma duração da rolagem em gravar.js
const PASTA = path.join(SAIDA, "reels");
const REPO = "github.com/Josejunior-unv/axiumL";

/* ---------------- moldura e cartelas ---------------- */

// faixas lisas em cima e embaixo, na cor de fundo da página; a de baixo esfuma o conteúdo
const moldura = fundo => `
  html { overflow-anchor: none; }
  body { padding-top: ${TOPO}px !important; }
  body::before, body::after { content: ""; position: fixed; left: 0; right: 0; z-index: 1000; pointer-events: none; background: ${fundo}; }
  body::before { top: 0; height: ${TOPO}px; }
  body::after { bottom: 0; height: ${BASE}px; box-shadow: 0 -22px 20px -6px ${fundo}; }
  .reel-cartela { position: fixed; inset: 0; z-index: 2000; display: grid; align-content: center; gap: 18px;
    padding: ${TOPO}px 34px ${BASE}px; background: ${fundo}; opacity: 0; visibility: hidden; }
  .reel-cartela .e { will-change: transform, opacity; }
  .reel-cartela .url { overflow-wrap: anywhere; }
`;

// cartela de abertura (já visível no primeiro quadro, que vira a capa) e de encerramento
const cartelas = ({ projeto, titulo, gancho, proximo, numeros }) => ({
  js: ([projeto, titulo, gancho, proximo, numeros, repo]) => {
    const div = (id, html) => { const d = document.createElement("div"); d.className = "reel-cartela"; d.id = id; d.innerHTML = html; document.body.append(d); return d; };
    const abre = div("reel-abre", `<div class="k e">${projeto}</div><h1 class="e">${titulo}</h1><p class="e">${gancho}</p>`);
    if (numeros) { const n = document.querySelector(numeros).cloneNode(true); n.classList.add("e", "reel-numeros"); n.removeAttribute("id"); abre.append(n); }
    div("reel-fecha", `<div class="k e">Código, testes e animação</div><h1 class="e url">${repo}</h1><p class="e">${proximo}</p>`);
    const estado = {};
    const lim = x => Math.max(0, Math.min(1, x));
    const saida = x => 1 - Math.pow(1 - lim(x), 3);
    function quadro() {
      const t = performance.now() / 1000;
      for (const [id, e] of Object.entries(estado)) {
        const el = document.getElementById(id);
        const entra = e.pronto ? 1 : saida((t - e.t0) / 0.4);
        const sai = e.t1 === undefined ? 0 : saida((t - e.t1) / 0.45);
        el.style.opacity = entra * (1 - sai);
        el.style.visibility = entra * (1 - sai) > 0 ? "visible" : "hidden";
        el.querySelectorAll(".e").forEach((x, i) => {
          const k = e.pronto ? 1 : saida((t - e.t0 - 0.12 - i * 0.2) / 0.6);
          const zoom = 1 + 0.025 * lim((t - e.t0) / 6);
          x.style.opacity = k;
          x.style.transform = `translateY(${(1 - k) * 16}px) scale(${zoom})`;
          x.style.transformOrigin = "left center";
        });
      }
      requestAnimationFrame(quadro);
    }
    requestAnimationFrame(quadro);
    window.__reel = {
      mostrar: (id, pronto = false) => { estado[id] = { t0: performance.now() / 1000, pronto }; },
      esconder: id => { estado[id].t1 = performance.now() / 1000; },
    };
    window.__reel.mostrar("reel-abre", true);
  },
  arg: [projeto, titulo, gancho, proximo, numeros, REPO],
});

const alturaDaTela = px => ({ js: px => { document.getElementById("tela").style.setProperty("height", px + "px", "important"); }, arg: px });
const esconderAbertura = { js: () => window.__reel.esconder("reel-abre") };
const mostrarFecho = { js: () => window.__reel.mostrar("reel-fecha") };

/* ---------------- roteiros (em compassos) ---------------- */

// churn: a figura fica presa no topo e o texto rola embaixo dela
const FIGURA_CHURN = 330;
const abaixoDaFigura = (seletor, folga = 12) => ({
  js: ([s, folga, topo]) => document.querySelector(s).getBoundingClientRect().top + scrollY - (topo + document.querySelector(".figura").offsetHeight) - folga,
  arg: [seletor, folga, TOPO],
});
const passoChurn = i => abaixoDaFigura(`.passo[data-passo='${i}'] .rotulo`);
const controlesChurn = i => abaixoDaFigura(`.passo[data-passo='${i}'] .controles`);

// fraude: a faixa de abas rola de lado para a aba escolhida ficar à vista
const aba = n => ({ js: n => {
  const b = document.getElementById(`aba-${n}`), faixa = document.getElementById("abas");
  b.click(); faixa.scrollLeft = b.offsetLeft - faixa.offsetLeft - (faixa.clientWidth - b.offsetWidth) / 2;
}, arg: n });

const REELS = {
  churn: {
    titulo: "reel-01-fatura-de-risco", pagina: "01-previsao-churn/animacao/index.html", trilha: "churn", bpm: 96,
    cartelas: { projeto: "Projeto 01 de 05 · previsão de churn", titulo: "Fatura de Risco",
      gancho: "Quem vai cancelar o plano, e para quem vale a pena oferecer um desconto?", numeros: "header .resumo",
      proximo: "Próximo: Quadro de Demanda, a previsão de vendas do varejo." },
    fundo: "var(--papel)",
    css: `
      .figura { top: ${TOPO}px !important; }
      .figura-fixa { height: ${FIGURA_CHURN}px !important; min-height: 0 !important; }
      .passo { min-height: 760px !important; transition: none !important; }
      .texto { padding-bottom: 700px !important; }
      .reel-cartela { color: var(--tinta); font-family: var(--f-texto); }
      .reel-cartela .k { font: 500 13px/1.3 var(--f-mono); letter-spacing: .12em; text-transform: uppercase; color: var(--tinta-2); }
      .reel-cartela h1 { font: 700 76px/.92 var(--f-display); margin: 0; color: var(--faixa); }
      .reel-cartela h1.url { font: 600 25px/1.2 var(--f-mono); color: var(--risco); }
      .reel-cartela p { font-size: 23px; line-height: 1.35; margin: 0; color: var(--tinta); }
      .reel-cartela .resumo { font-size: 14px; gap: 6px 22px; border-top: 2px solid var(--tinta); padding-top: 14px; }`,
    segmentos: [
      { c: 2, rolarPara: passoChurn(0) },
      { c: 2, acoes: [{ t: 0, ...esconderAbertura }] },
      { c: 3, rolarPara: passoChurn(1) },
      { c: 4, rolarPara: passoChurn(2), acoes: [{ t: 4.2, ...clicar("ex-2") }] },
      { c: 2, rolarPara: passoChurn(3) },
      { c: 4, rolarPara: controlesChurn(3),
        acoes: [{ t: 0.6, ...clicar("s-contrato-anual") }, { t: 1.6, ...clicar("s-pag-debito") }, { t: 6.0, ...clicar("s-contrato-mensal") }, { t: 6.6, ...clicar("s-pag-boleto") }],
        varreduras: [varrer("s-meses", 4, 48, 2.6, 5.2), varrer("s-chamados", 3, 7, 7.0, 8.0)] },
      { c: 2, rolarPara: passoChurn(4) },
      { c: 3, rolarPara: controlesChurn(4), varreduras: [varrer("corte", 3, 8, 0.4, 2.0), varrer("corte", 8, 0, 2.2, 3.6)],
        acoes: [{ t: 4.2, ...clicar("c3-bianual") }, { t: 5.4, ...faixa("corte", 3) }] },
      { c: 4, rolarPara: passoChurn(5) },
      { c: 2, rolarPara: passoChurn(6) },
      { c: 4, rolarPara: controlesChurn(6),
        varreduras: [varrer("limiar", 0.36, 0.9, 0.6, 2.4, 0.01), varrer("limiar", 0.9, 0.08, 3.0, 5.4, 0.01), varrer("limiar", 0.08, 0.36, 6.0, 7.6, 0.01)] },
      { c: 3, rolarPara: passoChurn(7) },
      { c: 3, rolarPara: passoChurn(8) },
      { c: 2, acoes: [{ t: 0, ...mostrarFecho }] },
    ],
  },
  demanda: {
    titulo: "reel-02-quadro-de-demanda", pagina: "02-previsao-demanda/animacao/index.html", trilha: "demanda", bpm: 120,
    cartelas: { projeto: "Projeto 02 de 05 · previsão de demanda", titulo: "Quadro de Demanda",
      gancho: "Quanto cada loja vai vender nas próximas 4 semanas, e com que margem de erro?", numeros: ".placas",
      proximo: "Próximo: Mesa Antifraude, a detecção de fraude em cartão." },
    fundo: "var(--fundo)",
    // cada capítulo é aberto por um clique na cabeça do compasso, antes que o player troque sozinho
    css: `
      .barra, .notas { display: none !important; }
      body { padding-bottom: 700px; }
      #tela { height: 410px !important; }
      .capitulos li:not(:has(button[aria-current])) { display: none; }
      .reel-cartela { color: var(--tinta); font-family: var(--f-display); }
      .reel-cartela .k { justify-self: start; font: 500 13px/1 var(--f-mono); letter-spacing: .08em; text-transform: uppercase; background: var(--etiqueta); padding: 6px 8px; }
      .reel-cartela h1 { font-size: 58px; line-height: .9; font-weight: 900; font-stretch: 125%; letter-spacing: -.02em; margin: 0; }
      .reel-cartela h1.url { font: 500 25px/1.2 var(--f-mono); color: var(--modelo); }
      .reel-cartela p { font-size: 22px; line-height: 1.35; margin: 0; color: var(--tinta-2); font-stretch: 95%; }
      .reel-cartela .placas { justify-content: flex-start; border-top: 6px solid var(--tinta); padding-top: 16px; }`,
    segmentos: [
      { c: 2, rolarPara: topoDe(".player", TOPO + 8) },
      { c: 7, acoes: [{ t: 0, ...esconderAbertura }, { t: 0, ...clicar("cap-1") }] },
      { c: 7, acoes: [{ t: 0, ...clicar("cap-2") }] },
      { c: 8, acoes: [{ t: 0, ...clicar("cap-3") }] },
      { c: 7, acoes: [{ t: 0, ...clicar("cap-4") }] },
      { c: 7, acoes: [{ t: 0, ...clicar("cap-5") }, { t: 2.6, ...clicar("op-4-1") }] },
      { c: 5, acoes: [{ t: 0, ...clicar("cap-6") }] },
      { c: 6, acoes: [{ t: 0, ...clicar("cap-7") }] },
      { c: 2, acoes: [{ t: 0, ...mostrarFecho }] },
    ],
  },
  fraude: {
    titulo: "reel-03-mesa-antifraude", pagina: "03-deteccao-fraude/animacao/index.html", trilha: "fraude", bpm: 84,
    cartelas: { projeto: "Projeto 03 de 05 · detecção de fraude", titulo: "Mesa Antifraude",
      gancho: "Como pegar 85% das fraudes revisando só 0,5% das compras de cartão?", numeros: ".valores",
      proximo: "Próximo: Gosto em Duas Tintas, um sistema de recomendação." },
    fundo: "var(--papel)",
    css: `
      .indice, .rodape, .extrato { display: none !important; }
      .acoes button { display: none !important; }
      .abas { scrollbar-width: none; }
      body { padding-bottom: 700px; }
      #tela { height: 350px !important; }
      .reel-cartela { color: var(--tinta); font-family: var(--f-texto); }
      .reel-cartela .k { font: 500 12px/1.4 var(--f-mono); letter-spacing: .1em; text-transform: uppercase; color: var(--tinta-2); }
      .reel-cartela h1 { font: 700 72px/.9 var(--f-display); margin: 0; }
      .reel-cartela h1.url { font: 500 21px/1.3 var(--f-mono); color: var(--ouro); }
      .reel-cartela p { font: 600 italic 29px/1.15 var(--f-display); margin: 0; color: var(--tinta-2); }
      .reel-cartela .valores { text-align: left; grid-template-columns: repeat(3, minmax(0, 1fr)); border-top: 1px solid var(--tinta); padding-top: 14px; }
      .reel-cartela .valores span { justify-self: start; }`,
    segmentos: [
      { c: 2, rolarPara: topoDe("#abas", TOPO + 6) },
      { c: 3, acoes: [{ t: 0, ...esconderAbertura }, { t: 0, ...aba(1) }] },
      { c: 4, acoes: [{ t: 0, ...aba(2) }] },
      { c: 3, acoes: [{ t: 0, ...clicar("acao-1-1") }] },
      { c: 6, acoes: [{ t: 0, ...aba(3) }] },
      { c: 4, acoes: [{ t: 0, ...aba(4) }], varreduras: [varrer("orc4", 16, 36, 3.0, 5.6), varrer("orc4", 36, 16, 6.6, 8.6)] },
      { c: 4, acoes: [{ t: 0, ...aba(5) }], varreduras: [varrer("orc5", 16, 30, 3.6, 6.0), varrer("orc5", 30, 16, 7.0, 8.8)] },
      { c: 6, acoes: [{ t: 0, ...aba(6) }] },
      { c: 2, acoes: [{ t: 0, ...mostrarFecho }] },
    ],
  },
  recomendacao: {
    titulo: "reel-04-gosto-em-duas-tintas", pagina: "04-sistema-recomendacao/animacao/index.html", trilha: "recomendacao", bpm: 90,
    cartelas: { projeto: "Projeto 04 de 05 · sistema de recomendação", titulo: `<span class="r">Gosto em</span> <span class="a">Duas Tintas</span>`,
      gancho: "Como adivinhar o próximo filme de 2.000 pessoas a partir do que elas já viram?", numeros: ".fichas",
      proximo: "Próximo: Cofre de Consultas, um agente de IA que consulta o banco de dados." },
    fundo: "var(--papel)",
    css: `
      .navega, .pontos, .notas, .rodape { display: none !important; }
      body { padding-bottom: 700px; }
      #tela { height: 380px !important; }
      .lamina { gap: 10px !important; }
      .contador { font-size: 40px !important; } .contador small { font-size: 18px !important; }
      .texto { gap: 8px !important; } .texto h2 { font-size: 26px !important; }
      .reel-cartela { color: var(--preto); font-family: var(--f-display); }
      .reel-cartela .k { justify-self: start; font: 500 12.5px/1 var(--f-mono); letter-spacing: .06em; text-transform: uppercase; background: var(--amarelo); padding: 6px 8px; }
      .reel-cartela h1 { font-size: 66px; line-height: .9; font-weight: 800; letter-spacing: -.04em; margin: 0; }
      .reel-cartela h1 .r { color: var(--rosa); mix-blend-mode: multiply; } .reel-cartela h1 .a { color: var(--azul); mix-blend-mode: multiply; }
      .reel-cartela h1.url { font: 500 23px/1.25 var(--f-mono); letter-spacing: 0; color: var(--azul); }
      .reel-cartela p { font-size: 23px; line-height: 1.3; margin: 0; }
      .reel-cartela .fichas { display: flex; gap: 26px; }`,
    segmentos: [
      { c: 2, rolarPara: topoDe(".lamina", TOPO + 8) },
      { c: 2, acoes: [{ t: 0, ...esconderAbertura }, { t: 0, ...clicar("lamina-1") }] },
      { c: 4, acoes: [{ t: 0, ...clicar("lamina-2") }] },
      { c: 7, acoes: [{ t: 0, ...clicar("lamina-3") }] },
      { c: 5, acoes: [{ t: 0, ...clicar("lamina-4") }, { t: 6.5, ...clicar("op-3-1") }] },
      { c: 4, acoes: [{ t: 0, ...clicar("lamina-5") }] },
      { c: 4, acoes: [{ t: 0, ...clicar("lamina-6") }] },
      { c: 2, acoes: [{ t: 0, ...mostrarFecho }] },
    ],
  },
  cofre: {
    titulo: "reel-05-cofre-de-consultas", pagina: "05-agente-text-to-sql/animacao/index.html", trilha: "cofre", bpm: 110,
    cartelas: { projeto: "Projeto 05 de 05 · agente text-to-SQL", titulo: "Cofre de Consultas",
      gancho: "Uma IA que responde perguntas consultando o banco de dados, sem conseguir apagar nada.", numeros: ".camadas",
      proximo: "Os outros quatro projetos estão no perfil." },
    fundo: "var(--cimento)",
    css: `
      #anterior, #proximo, #repetir, .rodape, .topo { display: none !important; }
      body { padding-bottom: 700px; }
      .palco { margin-top: 8px; }
      #tela { height: 300px !important; }
      .controles { min-height: 0; padding-block: 8px; } .controles:has(.lab[hidden]) { display: none; }
      .roteiro { max-height: 320px !important; }
      .roteiro header { padding: 10px 14px 6px; } .roteiro header h2 { font-size: 21px; } .roteiro header p { font-size: 14.5px; }
      .passos { padding: 6px 14px 0; } .passos button { width: 26px; height: 26px; font-size: 12px; }
      .reel-cartela { font-family: var(--f); color: var(--tinta); }
      .reel-cartela .k { font-size: 13px; font-variation-settings: "MONO" 1; letter-spacing: .06em; text-transform: uppercase; color: var(--tinta-2); }
      .reel-cartela h1 { font-size: 64px; line-height: .95; font-weight: 900; font-variation-settings: "CASL" 1; margin: 0; }
      .reel-cartela h1.url { font-size: 26px; font-weight: 700; font-variation-settings: "MONO" 1; color: var(--lilas); }
      .reel-cartela p { font-size: 22px; line-height: 1.35; margin: 0; color: var(--tinta-2); }
      .reel-cartela .camadas { justify-content: flex-start; }`,
    segmentos: [
      { c: 2, rolarPara: topoDe(".palco", TOPO + 8) },
      { c: 2, acoes: [{ t: 0, ...esconderAbertura }, { t: 0, ...clicar("passo-1") }] },
      { c: 3, acoes: [{ t: 0, ...clicar("passo-2") }] },
      { c: 4, acoes: [{ t: 0, ...clicar("passo-3") }] },
      { c: 6, acoes: [{ t: 0, ...clicar("passo-4") }] },
      { c: 3, acoes: [{ t: 0, ...clicar("passo-5") }] },
      { c: 7, acoes: [{ t: 0, ...clicar("passo-6") }, { t: 4.6, ...clicar("tentativa-1") }, { t: 8.6, ...clicar("tentativa-6") }] },
      { c: 4, acoes: [{ t: 0, ...alturaDaTela(440) }, { t: 0, ...clicar("passo-7") }] },
      { c: 3, acoes: [{ t: 0, ...mostrarFecho }] },
    ],
  },
};

/* ---------------- montagem ---------------- */

// converte compassos em segundos: a rolagem conta dentro do compasso. As fronteiras são
// arredondadas para quadros a partir do início, para o erro não se acumular cena a cena.
function emSegundos(reel) {
  const barra = 240 / reel.bpm;
  let compassos = 0;
  return reel.segmentos.map(s => {
    const de = Math.round(compassos * barra * FPS), ate = Math.round((compassos + s.c) * barra * FPS);
    compassos += s.c;
    return { ...s, dur: (ate - de) / FPS - (s.rolarPara ? ROLAGEM : 0) };
  });
}

function roteiroDe(reel) {
  return {
    pagina: reel.pagina,
    css: moldura(reel.fundo) + reel.css,
    preparar: cartelas(reel.cartelas),
    segmentos: emSegundos(reel),
  };
}

async function main() {
  const args = process.argv.slice(2);
  const previa = args.includes("--previa");
  const pedidos = args.filter(a => !a.startsWith("--"));
  const nomes = pedidos.length ? pedidos.filter(n => REELS[n]) : Object.keys(REELS);
  fs.mkdirSync(PASTA, { recursive: true });
  const navegador = await abrirNavegador();
  for (const nome of nomes) {
    const reel = REELS[nome];
    const mudo = path.join(PASTA, `${reel.titulo}-mudo.mp4`);
    if (previa) { await gravar(navegador, roteiroDe(reel), mudo, RETRATO, { previa: path.join(PASTA, "previa", nome), cada: 15 }); continue; }
    await gravar(navegador, roteiroDe(reel), mudo, RETRATO);
    const compassos = reel.segmentos.map(s => s.c);
    const audio = path.join(PASTA, `${reel.titulo}.wav`);
    execFileSync(process.env.PYTHON || "python3", [path.join(__dirname, "trilhas", "compor.py"), reel.trilha, String(reel.bpm), compassos.join(","), audio], { stdio: "inherit" });
    const final = path.join(PASTA, `${reel.titulo}.mp4`);
    execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-i", mudo, "-i", audio, "-map", "0:v", "-map", "1:a",
      "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", final]);
    // a trilha também fica sozinha, em AAC, para quem quiser reaproveitar
    execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-i", audio, "-c:a", "aac", "-b:a", "256k", path.join(PASTA, `${reel.titulo.replace("reel-", "trilha-")}.m4a`)]);
    fs.unlinkSync(mudo);
    fs.unlinkSync(audio);
    console.log(`${path.basename(final)}: ${duracao(final).toFixed(1)} s`);
  }
  await navegador.close();
}

module.exports = { REELS, RETRATO, roteiroDe };

if (require.main === module) main();
