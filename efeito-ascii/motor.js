/* ============================================================
   Motor do efeito ASCII — Canvas2D puro, sem bibliotecas.
   Recria o pipeline descrito na especificação "Forest":
   fundo -> amostragem em grade -> formas por célula -> ajustes
   de cor -> pós-efeitos -> luzes -> máscara.
   ============================================================ */
"use strict";

const PADRAO = {
  renderMode: "characters", bgMode: "blur", bgBlur: 2, bgOpacity: 90, bgDim: 88,
  cellSize: 10, coverage: 100, invert: false, styleBlend: "source-over",
  charSet: "standard", customChars: "",
  brightness: 0, contrast: 128, edgeEmphasis: 0, density: 0,
  toneCurve: [{x:0,y:0},{x:1,y:1}],
  tint: "#3ca6ff", tintOpacity: 0, overlayBlend: "multiply",
  saturation: 0, grayscale: 100,
  blurType: "tilt", blurAmount: 30, blurAngle: 0, directionalBothSides: false,
  tiltFocus: 35, tiltPosition: 50, tiltFeather: 15, lensFocus: 40,
  blurCenterX: 50, blurCenterY: 50, progressivePosition: 55, progressiveReverse: false,
  pfx: {
    vignette:{enabled:false,intensity:58}, scanLines:{enabled:false,intensity:40},
    chromatic:{enabled:true,intensity:20}, bloom:{enabled:false,intensity:25},
    filmGrain:{enabled:false,intensity:32}, glitch:{enabled:false,intensity:20},
    pixelate:{enabled:false,intensity:15}, halftone:{enabled:true,intensity:20},
    filmDust:{enabled:true,intensity:20}
  },
  animated: true, animStyle: "shimmer",
  animSpeed:{enabled:true,intensity:100}, animIntensity:{enabled:true,intensity:60},
  lights:{enabled:false,points:[]},
  mask:{enabled:false,tool:"freehand",brushSize:30,showOverlay:false,invert:false,dataUrl:null,shapes:[]}
};

const CONJUNTOS = {
  standard: " .:-=+*#%@",
  simple: " .:*#@",
  blocks: " ░▒▓█",
  binary: " 01",
  hex: " 0123456789ABCDEF",
  dots: " ·•●",
  arrows: " ←↑→↓↖↗↘↙",
  math: " +-×÷=≠≈∞",
  stars: " .·*✴✦✹",
  shades: " ▁▂▃▄▅▆▇█"
};

const rnd = (s) => { let x = Math.sin(s * 127.1) * 43758.5453; return x - Math.floor(x); };
const grampo = (v, a, b) => v < a ? a : v > b ? b : v;

/* ---------- 1. cena de origem, gerada quando não há foto ---------- */
function desenharFloresta(ctx, w, h){
  const g = ctx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0, "#cfd9e2"); g.addColorStop(.45, "#9fb1bf");
  g.addColorStop(.75, "#6b7f8c"); g.addColorStop(1, "#3d4a52");
  ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);

  // sol difuso
  const sol = ctx.createRadialGradient(w*.68, h*.22, 0, w*.68, h*.22, h*.5);
  sol.addColorStop(0, "rgba(255,250,235,.95)"); sol.addColorStop(1, "rgba(255,250,235,0)");
  ctx.fillStyle = sol; ctx.fillRect(0, 0, w, h);

  // camadas de árvores, das mais distantes às mais próximas
  const camadas = [
    { n: 34, alt: .42, base: .80, cor: "rgba(86,102,110,.55)", larg: .010 },
    { n: 24, alt: .56, base: .88, cor: "rgba(52,66,72,.72)",   larg: .015 },
    { n: 15, alt: .74, base: .98, cor: "rgba(22,31,35,.92)",   larg: .024 }
  ];
  camadas.forEach((c, ci) => {
    for (let i = 0; i < c.n; i++){
      const s = ci * 100 + i;
      const x = (i / c.n + rnd(s) * .05) * w * 1.05 - w * .02;
      const altura = h * c.alt * (.62 + rnd(s + 7) * .55);
      const baseY = h * c.base;
      const larg = w * c.larg * (.6 + rnd(s + 13) * .9);
      ctx.fillStyle = c.cor;
      ctx.beginPath();
      ctx.moveTo(x, baseY);
      ctx.lineTo(x - larg * .5, baseY);
      ctx.lineTo(x - larg * .22, baseY - altura * .55);
      ctx.lineTo(x - larg * .9, baseY - altura * .5);
      ctx.lineTo(x - larg * .16, baseY - altura);
      ctx.lineTo(x + larg * .16, baseY - altura);
      ctx.lineTo(x + larg * .9, baseY - altura * .5);
      ctx.lineTo(x + larg * .22, baseY - altura * .55);
      ctx.lineTo(x + larg * .5, baseY);
      ctx.closePath(); ctx.fill();
    }
    // névoa entre as camadas
    const n = ctx.createLinearGradient(0, h * (c.base - .3), 0, h * c.base);
    n.addColorStop(0, "rgba(207,217,226,0)");
    n.addColorStop(1, "rgba(207,217,226," + (.30 - ci * .08) + ")");
    ctx.fillStyle = n; ctx.fillRect(0, 0, w, h);
  });

  // chão
  const ch = ctx.createLinearGradient(0, h * .86, 0, h);
  ch.addColorStop(0, "#2b353a"); ch.addColorStop(1, "#171e21");
  ctx.fillStyle = ch; ctx.fillRect(0, h * .86, w, h * .14);
}

/* ---------- 2. amostragem da grade ---------- */
function amostrar(origem, cols, linhas, aux){
  aux.width = cols; aux.height = linhas;
  const a = aux.getContext("2d", { willReadFrequently: true });
  a.clearRect(0, 0, cols, linhas);
  a.drawImage(origem, 0, 0, cols, linhas);
  return a.getImageData(0, 0, cols, linhas).data;
}

function sobel(lumi, cols, linhas){
  const saida = new Float32Array(cols * linhas);
  for (let y = 1; y < linhas - 1; y++)
    for (let x = 1; x < cols - 1; x++){
      const i = y * cols + x;
      const gx = -lumi[i-cols-1] - 2*lumi[i-1] - lumi[i+cols-1] + lumi[i-cols+1] + 2*lumi[i+1] + lumi[i+cols+1];
      const gy = -lumi[i-cols-1] - 2*lumi[i-cols] - lumi[i-cols+1] + lumi[i+cols-1] + 2*lumi[i+cols] + lumi[i+cols+1];
      saida[i] = Math.min(1, Math.hypot(gx, gy));
    }
  return saida;
}

function aplicarCurva(v, pontos){
  if (!pontos || pontos.length < 2) return v;
  for (let i = 0; i < pontos.length - 1; i++){
    const a = pontos[i], b = pontos[i+1];
    if (v >= a.x && v <= b.x){
      const k = (v - a.x) / Math.max(1e-6, b.x - a.x);
      return a.y + (b.y - a.y) * k;
    }
  }
  return v;
}

/* ---------- 3. as formas, uma por modo ---------- */
function formas(){
  const F = {};
  const quad = (c, x, y, s, t) => c.fillRect(x + (1-t)*s/2, y + (1-t)*s/2, s*t, s*t);

  F.characters = (c, x, y, s, l, cor, ctx2) => {
    const set = ctx2.conjunto;
    const i = grampo(Math.floor(l * (set.length - 1) + .5), 0, set.length - 1);
    c.fillStyle = cor;
    c.font = (s * (0.95 + ctx2.densidade * .4)) + "px " + ctx2.fonteMono;
    c.textAlign = "center"; c.textBaseline = "middle";
    c.fillText(set[i], x + s/2, y + s/2 + s*.05);
  };
  F.dither = (c, x, y, s, l, cor) => {
    const M = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]];
    const p = s / 4;
    c.fillStyle = cor;
    for (let j = 0; j < 4; j++) for (let i = 0; i < 4; i++)
      if (l * 16 > M[j][i]) c.fillRect(x + i*p, y + j*p, p, p);
  };
  F.mosaic = (c, x, y, s, l, cor) => { c.fillStyle = cor; c.fillRect(x, y, s-1, s-1); };
  F.pixel  = (c, x, y, s, l, cor) => { c.fillStyle = cor; c.fillRect(x, y, s, s); };
  F.dots = (c, x, y, s, l, cor) => {
    c.fillStyle = cor; c.beginPath();
    c.arc(x + s/2, y + s/2, s*.48*l, 0, 6.2832); c.fill();
  };
  F.cross = (c, x, y, s, l, cor) => {
    const e = Math.max(1, s*.18*l), m = s*.5*l;
    c.fillStyle = cor;
    c.fillRect(x + s/2 - m, y + s/2 - e/2, m*2, e);
    c.fillRect(x + s/2 - e/2, y + s/2 - m, e, m*2);
  };
  F.diamond = (c, x, y, s, l, cor) => {
    const m = s*.5*l; c.fillStyle = cor; c.beginPath();
    c.moveTo(x+s/2, y+s/2-m); c.lineTo(x+s/2+m, y+s/2);
    c.lineTo(x+s/2, y+s/2+m); c.lineTo(x+s/2-m, y+s/2);
    c.closePath(); c.fill();
  };
  F.voxel = (c, x, y, s, l, cor) => {
    const h = s * l; c.fillStyle = cor;
    c.fillRect(x, y + s - h, s*.8, h);
    c.fillStyle = "rgba(255,255,255,.22)";
    c.beginPath(); c.moveTo(x, y+s-h); c.lineTo(x+s*.2, y+s-h-s*.2);
    c.lineTo(x+s, y+s-h-s*.2); c.lineTo(x+s*.8, y+s-h); c.closePath(); c.fill();
  };
  F.lego = (c, x, y, s, l, cor) => {
    c.fillStyle = cor; c.fillRect(x, y, s-1, s-1);
    c.fillStyle = "rgba(255,255,255,.28)"; c.beginPath();
    c.arc(x+s/2, y+s/2, s*.22, 0, 6.2832); c.fill();
    c.fillStyle = "rgba(0,0,0,.18)"; c.beginPath();
    c.arc(x+s/2, y+s/2+s*.04, s*.22, .3, 2.9); c.fill();
  };
  F.mixed = (c, x, y, s, l, cor, ctx2) => {
    const ordem = ["dots","cross","diamond","mosaic"];
    F[ordem[Math.floor(rnd(x*3+y*7) * ordem.length)]](c, x, y, s, l, cor, ctx2);
  };
  F.lines = (c, x, y, s, l, cor) => {
    c.strokeStyle = cor; c.lineWidth = Math.max(.6, s*.16*l); c.lineCap = "round";
    c.beginPath(); c.moveTo(x+s*.1, y+s/2); c.lineTo(x+s*.9, y+s/2); c.stroke();
  };
  F.diagonal = (c, x, y, s, l, cor) => {
    c.strokeStyle = cor; c.lineWidth = Math.max(.6, s*.16*l); c.lineCap = "round";
    c.beginPath(); c.moveTo(x+s*.15, y+s*.85); c.lineTo(x+s*.85, y+s*.15); c.stroke();
  };
  F.braille = (c, x, y, s, l, cor) => {
    const p = [[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[0,3],[1,3]];
    const n = Math.round(l * 8); c.fillStyle = cor;
    for (let i = 0; i < n; i++){
      const [cx, cy] = p[i];
      c.beginPath();
      c.arc(x + s*(.3 + cx*.4), y + s*(.16 + cy*.23), s*.09, 0, 6.2832); c.fill();
    }
  };
  F.disco = (c, x, y, s, l, cor, ctx2) => {
    c.fillStyle = "hsl(" + ((x*2 + y*3 + ctx2.tempo*60) % 360) + ",85%," + (28 + l*46) + "%)";
    c.beginPath(); c.arc(x+s/2, y+s/2, s*.46*Math.max(.25,l), 0, 6.2832); c.fill();
  };
  F.hexdump = (c, x, y, s, l, cor, ctx2) => {
    const d = "0123456789ABCDEF";
    c.fillStyle = cor; c.font = (s*.9) + "px " + ctx2.fonteMono;
    c.textAlign = "center"; c.textBaseline = "middle";
    c.fillText(d[grampo(Math.floor(l*15.99),0,15)], x+s/2, y+s/2);
  };
  F.matrix = (c, x, y, s, l, cor, ctx2) => {
    const glifos = "アカサタナハマヤラワ0123456789";
    const queda = (ctx2.tempo * 6 + rnd(x) * 40) % 40;
    const dist = Math.abs((y / s) - queda);
    const brilho = Math.max(0, 1 - dist / 12) * (0.35 + l);
    if (brilho < .04) return;
    c.fillStyle = dist < 1 ? "rgba(200,255,210," + Math.min(1,brilho) + ")"
                           : "rgba(46,220,110," + Math.min(1,brilho*.85) + ")";
    c.font = (s*.95) + "px " + ctx2.fonteMono;
    c.textAlign = "center"; c.textBaseline = "middle";
    c.fillText(glifos[Math.floor(rnd(x*5+y*11+Math.floor(ctx2.tempo*4)) * glifos.length)], x+s/2, y+s/2);
  };
  F.rings = (c, x, y, s, l, cor) => {
    c.strokeStyle = cor; c.lineWidth = Math.max(.5, s*.09);
    const n = 1 + Math.round(l*2);
    for (let i = 1; i <= n; i++){
      c.beginPath(); c.arc(x+s/2, y+s/2, s*.46*(i/n), 0, 6.2832); c.stroke();
    }
  };
  F.hearts = (c, x, y, s, l, cor) => {
    const r = s*.42*Math.max(.3,l); c.fillStyle = cor;
    c.beginPath();
    c.moveTo(x+s/2, y+s/2+r*.9);
    c.bezierCurveTo(x+s/2-r*1.4, y+s/2-r*.2, x+s/2-r*.4, y+s/2-r*1.2, x+s/2, y+s/2-r*.35);
    c.bezierCurveTo(x+s/2+r*.4, y+s/2-r*1.2, x+s/2+r*1.4, y+s/2-r*.2, x+s/2, y+s/2+r*.9);
    c.fill();
  };
  F.stars = (c, x, y, s, l, cor) => {
    const R = s*.48*Math.max(.25,l); c.fillStyle = cor; c.beginPath();
    for (let i = 0; i < 10; i++){
      const ang = -Math.PI/2 + i*Math.PI/5, r = i%2 ? R*.42 : R;
      c[i?"lineTo":"moveTo"](x+s/2 + Math.cos(ang)*r, y+s/2 + Math.sin(ang)*r);
    }
    c.closePath(); c.fill();
  };
  F.hexagons = (c, x, y, s, l, cor, ctx2) => {
    const R = s*.55*Math.max(.25,l);
    const dx = (ctx2.linha % 2) ? s*.5 : 0;
    c.fillStyle = cor; c.beginPath();
    for (let i = 0; i < 6; i++){
      const a = Math.PI/6 + i*Math.PI/3;
      c[i?"lineTo":"moveTo"](x+s/2+dx + Math.cos(a)*R, y+s/2 + Math.sin(a)*R);
    }
    c.closePath(); c.fill();
  };
  F.triangles = (c, x, y, s, l, cor, ctx2) => {
    c.fillStyle = cor; c.beginPath();
    if ((ctx2.coluna + ctx2.linha) % 2){ c.moveTo(x, y); c.lineTo(x+s, y); c.lineTo(x, y+s); }
    else { c.moveTo(x+s, y); c.lineTo(x+s, y+s); c.lineTo(x, y+s); }
    c.closePath(); c.fill();
  };
  F.bubbles = (c, x, y, s, l, cor) => {
    const r = s*.46*Math.max(.2,l);
    c.strokeStyle = cor; c.lineWidth = Math.max(.6, s*.08);
    c.beginPath(); c.arc(x+s/2, y+s/2, r, 0, 6.2832); c.stroke();
    c.fillStyle = "rgba(255,255,255,.35)";
    c.beginPath(); c.arc(x+s/2-r*.3, y+s/2-r*.3, r*.22, 0, 6.2832); c.fill();
  };
  F.hatch = (c, x, y, s, l, cor) => {
    const n = Math.round(l*4); c.strokeStyle = cor; c.lineWidth = Math.max(.4, s*.07);
    c.beginPath();
    for (let i = 0; i < n; i++){
      const o = (i+1) * s/(n+1);
      c.moveTo(x, y+o); c.lineTo(x+o, y);
      if (i % 2){ c.moveTo(x+s-o, y); c.lineTo(x+s, y+s-o); }
    }
    c.stroke();
  };
  F.contour = (c, x, y, s, l, cor) => {
    const faixa = Math.round(l * 7) / 7;
    if (Math.abs(l - faixa) > .055) return;
    c.strokeStyle = cor; c.lineWidth = Math.max(.6, s*.1);
    c.beginPath(); c.moveTo(x, y+s/2); c.lineTo(x+s, y+s/2); c.stroke();
  };
  F.halfblocks = (c, x, y, s, l, cor, ctx2) => {
    c.fillStyle = cor;
    const cima = ctx2.lumCima != null ? ctx2.lumCima : l;
    const baixo = ctx2.lumBaixo != null ? ctx2.lumBaixo : l;
    if (cima  > .5) c.fillRect(x, y, s, s/2);
    if (baixo > .5) c.fillRect(x, y+s/2, s, s/2);
    if (cima <= .5 && baixo <= .5 && l > .25){
      c.globalAlpha = l; c.fillRect(x, y+s*.35, s, s*.3); c.globalAlpha = 1;
    }
  };
  return F;
}
const FORMAS = formas();
const MODOS = Object.keys(FORMAS);
