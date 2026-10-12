// Grava as animações dos projetos como vídeo MP4, quadro a quadro.
//
//   node projetos-ia/video/gravar.js            # todos os vídeos + o completo
//   node projetos-ia/video/gravar.js churn      # só um (churn, demanda, fraude, recomendacao, cofre)
//
// Precisa de Node com o pacote playwright (e o Chromium dele) e de ffmpeg com libx264.
// Em vez de gravar a tela, o script troca o relógio da página por um relógio
// controlado: a cada quadro ele avança 1/30 s, a página desenha e o quadro é
// capturado. Assim o vídeo sai liso mesmo que a captura seja lenta.
// Saída: media/videos/projetos-ia/ (pasta ignorada pelo git).

"use strict";
const path = require("path");
const fs = require("fs");
const { spawn, execFileSync } = require("child_process");
const { chromium } = require("playwright");

const RAIZ = path.resolve(__dirname, "..");
const SAIDA = path.resolve(RAIZ, "..", "media", "videos", "projetos-ia");
const FPS = 30;
// 1280 × 720 com escala 1,5 = vídeo 1920 × 1080, com texto grande o bastante para ler
const PAISAGEM = { viewport: { width: 1280, height: 720 }, escala: 1.5 };
const EXECUTAVEL = process.env.CHROMIUM || undefined;

// relógio controlado: performance.now e requestAnimationFrame passam a obedecer ao script
const RELOGIO = `(() => {
  let agora = 0; const fila = [];
  performance.now = () => agora;
  window.requestAnimationFrame = cb => { fila.push(cb); return fila.length; };
  window.cancelAnimationFrame = () => {};
  window.__avancar = ms => { agora += ms; const lista = fila.splice(0); for (const cb of lista) { try { cb(agora); } catch (e) { console.error(e); } } };
})();`;

const suave = t => (t = Math.max(0, Math.min(1, t)), t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const arquivo = rel => "file://" + path.join(RAIZ, rel);

// ações que rodam dentro da página
const clicar = id => ({ js: id => document.getElementById(id).click(), arg: id });
const faixa = (id, valor) => ({ js: ([id, v]) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event("input", { bubbles: true })); }, arg: [id, valor] });
// varre um controle deslizante de `de` até `ate` entre os instantes t0 e t1 do segmento
const varrer = (id, de, ate, t0, t1, passo = 1) => ({ t0, t1, quadro: t => { const k = suave((t - t0) / (t1 - t0)); const v = de + (ate - de) * k; return faixa(id, Math.round(v / passo) * passo); } });

/* ---------------- roteiros ---------------- */

const CSS_BASE = `html { scrollbar-width: none; } ::-webkit-scrollbar { display: none; } * { caret-color: transparent; }`;

// posição de rolagem que deixa um elemento a `margem` px do topo da tela
const topoDe = (seletor, margem) => ({ js: ([s, m]) => document.querySelector(s).getBoundingClientRect().top + scrollY - m, arg: [seletor, margem] });

// posição de rolagem que centraliza um passo da história do churn
const centroDoPasso = i => ({ js: i => { const el = document.querySelector(`.passo[data-passo='${i}']`); const r = el.getBoundingClientRect(); return Math.max(0, r.top + scrollY - (innerHeight - r.height) / 2); }, arg: i });

const ROTEIROS = {
  churn: {
    titulo: "01-fatura-de-risco", pagina: "01-previsao-churn/animacao/index.html",
    css: `.pagina { max-width: none; } .passo { transition: none !important; } .historia { grid-template-columns: minmax(0, 22rem) minmax(0, 1fr) !important; }`,
    segmentos: [
      { dur: 5 },
      { rolarPara: centroDoPasso(1), dur: 6.5 },
      { rolarPara: centroDoPasso(2), dur: 10.5, acoes: [{ t: 6, ...clicar("ex-2") }] },
      { rolarPara: centroDoPasso(3), dur: 12, acoes: [{ t: 1.6, ...clicar("s-contrato-anual") }, { t: 3, ...clicar("s-pag-debito") }, { t: 8.8, ...clicar("s-contrato-mensal") }, { t: 9.6, ...clicar("s-pag-boleto") }],
        varreduras: [varrer("s-meses", 4, 48, 4.2, 7.6), varrer("s-chamados", 3, 7, 10, 11)] },
      { rolarPara: centroDoPasso(4), dur: 12, varreduras: [varrer("corte", 0, 8, 1.2, 6)], acoes: [{ t: 6.8, ...clicar("c3-bianual") }, { t: 9.5, ...faixa("corte", 3) }] },
      { rolarPara: centroDoPasso(5), dur: 10 },
      { rolarPara: centroDoPasso(6), dur: 11, varreduras: [varrer("limiar", 0.36, 0.9, 1.5, 4, 0.01), varrer("limiar", 0.9, 0.08, 4.6, 7.6, 0.01), varrer("limiar", 0.08, 0.36, 8.2, 9.8, 0.01)] },
      { rolarPara: centroDoPasso(7), dur: 8.5 },
      { rolarPara: centroDoPasso(8), dur: 8 },
    ],
  },
  demanda: {
    titulo: "02-quadro-de-demanda", pagina: "02-previsao-demanda/animacao/index.html",
    // o player troca de capítulo sozinho; no vídeo, só os títulos dos outros capítulos aparecem
    css: `.barra, .notas { display: none !important; } #tela { height: 676px !important; } body { padding-bottom: 400px; }
          .capitulos li button:not([aria-current]) .d { display: none; } .capitulos li button { padding-block: 9px 10px; }`,
    // a página toca sozinha desde o carregamento: os instantes abaixo contam a partir do fim da rolagem (4,4 s)
    segmentos: [{ dur: 3 }, { rolarPara: topoDe(".player", 12), dur: 96.5, acoes: [{ t: 63.6, ...clicar("op-4-1") }] }],
  },
  fraude: {
    titulo: "03-mesa-antifraude", pagina: "03-deteccao-fraude/animacao/index.html",
    css: `.indice, .rodape { display: none !important; } .acoes button { display: none !important; } #tela { height: 470px !important; }`,
    segmentos: [
      { dur: 3.5 },
      { rolarPara: { js: () => document.getElementById("abas").getBoundingClientRect().top + scrollY - 8 }, dur: 8 },
      { dur: 13, acoes: [{ t: 0, ...clicar("aba-2") }] },
      { dur: 10, acoes: [{ t: 0, ...clicar("acao-1-1") }] },
      { dur: 19, acoes: [{ t: 0, ...clicar("aba-3") }] },
      { dur: 10.5, acoes: [{ t: 0, ...clicar("aba-4") }], varreduras: [varrer("orc4", 16, 36, 3.5, 6.5), varrer("orc4", 36, 16, 7.5, 9.5)] },
      { dur: 10.5, acoes: [{ t: 0, ...clicar("aba-5") }], varreduras: [varrer("orc5", 16, 30, 4.5, 7), varrer("orc5", 30, 16, 8, 9.8)] },
      { dur: 16.5, acoes: [{ t: 0, ...clicar("aba-6") }] },
    ],
  },
  recomendacao: {
    titulo: "04-gosto-em-duas-tintas", pagina: "04-sistema-recomendacao/animacao/index.html",
    css: `.navega, .pontos, .notas, .rodape { display: none !important; } #tela { height: 690px !important; } body { padding-bottom: 400px; }`,
    segmentos: [
      { dur: 3 },
      { rolarPara: topoDe(".lamina", 14), dur: 4.5 },
      { dur: 9.5, acoes: [{ t: 0, ...clicar("lamina-2") }] },
      { dur: 18.5, acoes: [{ t: 0, ...clicar("lamina-3") }] },
      { dur: 13, acoes: [{ t: 0, ...clicar("lamina-4") }, { t: 6.5, ...clicar("op-3-1") }] },
      { dur: 9.5, acoes: [{ t: 0, ...clicar("lamina-5") }] },
      { dur: 9.5, acoes: [{ t: 0, ...clicar("lamina-6") }] },
    ],
  },
  cofre: {
    titulo: "05-cofre-de-consultas", pagina: "05-agente-text-to-sql/animacao/index.html",
    css: `#anterior, #proximo, #repetir, .resumo, .rodape { display: none !important; } #tela { height: 600px !important; }
          .roteiro { max-height: 690px !important; } .controles { min-height: 0; padding-block: 8px; } .controles:has(.lab[hidden]) { display: none; }
          body { padding-bottom: 400px; }`,
    segmentos: [
      { dur: 3 },
      { rolarPara: topoDe(".palco", 10), dur: 3 },
      { dur: 7, acoes: [{ t: 0, ...clicar("passo-2") }] },
      { dur: 7.5, acoes: [{ t: 0, ...clicar("passo-3") }] },
      { dur: 12, acoes: [{ t: 0, ...clicar("passo-4") }] },
      { dur: 5.5, acoes: [{ t: 0, ...clicar("passo-5") }] },
      { dur: 15, acoes: [{ t: 0, ...clicar("passo-6") }, { t: 4.6, ...clicar("tentativa-1") }, { t: 8.6, ...clicar("tentativa-6") }] },
      { dur: 9.5, acoes: [{ t: 0, ...clicar("passo-7") }] },
    ],
  },
  abertura: { titulo: "00-abertura", pagina: "video/abertura.html#inicio", segmentos: [{ dur: 6 }] },
  encerramento: { titulo: "99-encerramento", pagina: "video/abertura.html#fim", segmentos: [{ dur: 5.5 }] },
};

/* ---------------- gravação ---------------- */

// grava o roteiro `r` em `destino`; com `previa` (uma pasta), só salva um JPEG a cada `cada` quadros, sem gerar vídeo
async function gravar(navegador, r, destino, formato = PAISAGEM, { previa = null, cada = 15 } = {}) {
  const pagina = await navegador.newPage({ viewport: formato.viewport, deviceScaleFactor: formato.escala, colorScheme: "light", reducedMotion: "no-preference" });
  const erros = [];
  pagina.on("pageerror", e => erros.push(e.message));
  pagina.on("console", m => { if (m.type() === "error") erros.push(m.text()); });
  await pagina.addInitScript(RELOGIO);
  await pagina.goto(arquivo(r.pagina));
  await pagina.evaluate(() => document.fonts.ready);
  await pagina.waitForTimeout(400);
  await pagina.addStyleTag({ content: CSS_BASE + (r.css || "") });
  if (r.preparar) await pagina.evaluate(r.preparar.js, r.preparar.arg);
  await pagina.evaluate(() => window.__avancar(0));

  let ffmpeg = null, fimDoFfmpeg = Promise.resolve();
  if (previa) fs.mkdirSync(previa, { recursive: true });
  else {
    ffmpeg = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(FPS), "-i", "-",
      "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", destino]);
    fimDoFfmpeg = new Promise((ok, falha) => ffmpeg.on("close", c => c === 0 ? ok() : falha(new Error(`ffmpeg saiu com ${c}`))));
  }
  const escrever = buf => new Promise(ok => { if (ffmpeg.stdin.write(buf)) ok(); else ffmpeg.stdin.once("drain", ok); });

  let quadros = 0;
  const ROLAGEM = 1.4;
  for (const seg of r.segmentos) {
    let rolarDe = null, rolarAte = null;
    if (seg.rolarPara) { rolarDe = await pagina.evaluate(() => scrollY); rolarAte = await pagina.evaluate(seg.rolarPara.js, seg.rolarPara.arg); }
    const extra = seg.rolarPara ? ROLAGEM : 0;
    const n = Math.round((seg.dur + extra) * FPS);
    const feitas = new Set();
    for (let i = 0; i < n; i++) {
      const t = i / FPS;
      if (rolarAte !== null && t <= ROLAGEM + 1 / FPS) await pagina.evaluate(y => window.scrollTo(0, y), rolarDe + (rolarAte - rolarDe) * suave(t / ROLAGEM));
      const ts = t - extra; // tempo dentro do segmento, depois da rolagem
      for (const [k, a] of (seg.acoes || []).entries()) if (!feitas.has(k) && ts >= a.t) { feitas.add(k); await pagina.evaluate(a.js, a.arg); }
      for (const v of seg.varreduras || []) if (ts >= v.t0 && ts <= v.t1 + 1 / FPS) { const a = v.quadro(ts); await pagina.evaluate(a.js, a.arg); }
      await pagina.evaluate(ms => window.__avancar(ms), 1000 / FPS);
      if (!previa) await escrever(await pagina.screenshot({ type: "jpeg", quality: 95 }));
      else if (quadros % cada === 0) await pagina.screenshot({ type: "jpeg", quality: 80, path: path.join(previa, `${String(quadros).padStart(5, "0")}.jpg`) });
      quadros++;
    }
  }
  if (ffmpeg) ffmpeg.stdin.end();
  await fimDoFfmpeg;
  await pagina.close();
  console.log(`${path.basename(destino)}: ${quadros} quadros (${(quadros / FPS).toFixed(1)} s)${erros.length ? " · erros: " + erros.join(" | ") : ""}`);
  return destino;
}

const abrirNavegador = () => chromium.launch({ executablePath: EXECUTAVEL, proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined, args: ["--ignore-certificate-errors"] });

function duracao(arq) {
  return parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq]).toString());
}

// junta abertura, projetos e encerramento com fusões curtas entre eles
function juntar(arquivos, destino, fusao = 0.6) {
  const entradas = arquivos.flatMap(a => ["-i", a]);
  let filtro = "", ultimo = "[0:v]", acumulado = duracao(arquivos[0]);
  for (let i = 1; i < arquivos.length; i++) {
    const saida = i === arquivos.length - 1 ? "[v]" : `[x${i}]`;
    filtro += `${ultimo}[${i}:v]xfade=transition=fade:duration=${fusao}:offset=${(acumulado - fusao).toFixed(3)}${saida};`;
    acumulado += duracao(arquivos[i]) - fusao;
    ultimo = saida;
  }
  execFileSync("ffmpeg", ["-y", "-loglevel", "error", ...entradas, "-filter_complex", filtro.replace(/;$/, ""), "-map", "[v]",
    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", destino]);
  console.log(`${path.basename(destino)}: ${duracao(destino).toFixed(1)} s`);
}

module.exports = { FPS, SAIDA, CSS_BASE, suave, clicar, faixa, varrer, topoDe, gravar, duracao, abrirNavegador };

if (require.main === module) (async () => {
  fs.mkdirSync(SAIDA, { recursive: true });
  const pedidos = process.argv.slice(2);
  const nomes = pedidos.length ? pedidos.filter(n => ROTEIROS[n]) : Object.keys(ROTEIROS);
  const navegador = await abrirNavegador();
  for (const nome of nomes) await gravar(navegador, ROTEIROS[nome], path.join(SAIDA, `${ROTEIROS[nome].titulo}.mp4`));
  await navegador.close();
  if (!pedidos.length || pedidos.includes("completo")) {
    const ordem = ["abertura", "churn", "demanda", "fraude", "recomendacao", "cofre", "encerramento"].map(n => path.join(SAIDA, `${ROTEIROS[n].titulo}.mp4`));
    juntar(ordem, path.join(SAIDA, "projetos-ia-completo.mp4"));
  }
})();
