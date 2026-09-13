"use strict";
/* ---- a cena de origem e o laço de animação ---- */
const LARG = 1120, ALT = 700;
const cfg = JSON.parse(JSON.stringify(PADRAO));
const saida = document.getElementById("tela");
saida.width = LARG; saida.height = ALT;
const aux = document.createElement("canvas");
const foto = document.createElement("canvas");
foto.width = LARG; foto.height = ALT;
desenharFloresta(foto.getContext("2d"), LARG, ALT);

let inicio = performance.now(), rodando = true;
function quadro(agora){
  const t = (agora - inicio) / 1000;
  renderizar(saida, foto, cfg, t, aux, null);
  if (rodando) requestAnimationFrame(quadro);
}
requestAnimationFrame(quadro);

/* ---- controles ---- */
const painel = document.getElementById("controles");
function campo(rotulo, elemento){
  const d = document.createElement("label");
  d.className = "ctl";
  const s = document.createElement("span"); s.textContent = rotulo;
  d.appendChild(s); d.appendChild(elemento);
  painel.appendChild(d);
  return elemento;
}
function seletor(rotulo, opcoes, valor, aoMudar){
  const s = document.createElement("select");
  opcoes.forEach(o => { const op = document.createElement("option"); op.value = o; op.textContent = o; s.appendChild(op); });
  s.value = valor;
  s.addEventListener("change", () => aoMudar(s.value));
  return campo(rotulo, s);
}
function faixa(rotulo, min, max, valor, aoMudar){
  const env = document.createElement("span"); env.className = "faixa-env";
  const r = document.createElement("input");
  r.type = "range"; r.min = min; r.max = max; r.value = valor;
  const n = document.createElement("b"); n.textContent = valor;
  r.addEventListener("input", () => { n.textContent = r.value; aoMudar(+r.value); });
  env.appendChild(r); env.appendChild(n);
  campo(rotulo, env);
}
function marca(rotulo, valor, aoMudar){
  const c = document.createElement("input");
  c.type = "checkbox"; c.checked = valor;
  c.addEventListener("change", () => aoMudar(c.checked));
  return campo(rotulo, c);
}

seletor("Modo", MODOS, cfg.renderMode, v => cfg.renderMode = v);
seletor("Conjunto", Object.keys(CONJUNTOS), cfg.charSet, v => cfg.charSet = v);
seletor("Animação", ["wave","pulse","shimmer","ripple","flicker"], cfg.animStyle, v => cfg.animStyle = v);
seletor("Fundo", ["blur","photo","solid","none"], cfg.bgMode, v => cfg.bgMode = v);
faixa("Célula", 4, 28, cfg.cellSize, v => cfg.cellSize = v);
faixa("Cobertura", 10, 100, cfg.coverage, v => cfg.coverage = v);
faixa("Fundo escuro", 0, 100, cfg.bgDim, v => cfg.bgDim = v);
faixa("Contraste", 40, 260, cfg.contrast, v => cfg.contrast = v);
faixa("Bordas", 0, 100, cfg.edgeEmphasis, v => cfg.edgeEmphasis = v);
faixa("Cinza", 0, 100, cfg.grayscale, v => cfg.grayscale = v);
faixa("Desfoque", 0, 100, cfg.blurAmount, v => cfg.blurAmount = v);
faixa("Velocidade", 0, 100, cfg.animSpeed.intensity, v => cfg.animSpeed.intensity = v);
faixa("Intensidade", 0, 100, cfg.animIntensity.intensity, v => cfg.animIntensity.intensity = v);
marca("Inverter", cfg.invert, v => cfg.invert = v);

const pos = document.getElementById("posefeitos");
Object.keys(cfg.pfx).forEach(k => {
  const l = document.createElement("label");
  l.className = "pastilha" + (cfg.pfx[k].enabled ? " on" : "");
  const c = document.createElement("input");
  c.type = "checkbox"; c.checked = cfg.pfx[k].enabled;
  c.addEventListener("change", () => {
    cfg.pfx[k].enabled = c.checked;
    l.classList.toggle("on", c.checked);
  });
  l.appendChild(c);
  l.appendChild(document.createTextNode(k));
  pos.appendChild(l);
});

/* ---- foto do usuário ---- */
const arquivo = document.getElementById("arquivo");
arquivo.addEventListener("change", e => {
  const f = e.target.files[0];
  if (!f) return;
  const img = new Image();
  img.onload = () => {
    const c = foto.getContext("2d");
    c.clearRect(0, 0, LARG, ALT);
    // cobre a tela mantendo a proporção
    const k = Math.max(LARG / img.width, ALT / img.height);
    const w = img.width * k, h = img.height * k;
    c.drawImage(img, (LARG - w) / 2, (ALT - h) / 2, w, h);
    URL.revokeObjectURL(img.src);
    document.getElementById("origem").textContent = f.name;
  };
  img.src = URL.createObjectURL(f);
});
document.getElementById("restaurar").addEventListener("click", () => {
  desenharFloresta(foto.getContext("2d"), LARG, ALT);
  document.getElementById("origem").textContent = "cena gerada";
  arquivo.value = "";
});
document.getElementById("baixar").addEventListener("click", () => {
  saida.toBlob(b => {
    const u = URL.createObjectURL(b);
    const a = document.createElement("a");
    a.href = u; a.download = "ascii-" + cfg.renderMode + ".png";
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(u), 2000);
  });
});
