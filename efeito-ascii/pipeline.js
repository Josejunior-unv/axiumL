/* ============================================================
   Pipeline de renderização, na ordem da especificação.
   ============================================================ */
"use strict";

function novaTela(w, h){
  const c = document.createElement("canvas");
  c.width = w; c.height = h;
  return c;
}

/* ---- fundo (passo 1) ---- */
function desenharFundo(ctx, foto, cfg, w, h){
  ctx.clearRect(0, 0, w, h);
  const a = cfg.bgOpacity / 100;
  if (cfg.bgMode === "none" || a <= 0) return;
  ctx.save();
  ctx.globalAlpha = a;
  if (cfg.bgMode === "solid"){
    ctx.fillStyle = cfg.bgColor || "#0b0f13";
    ctx.fillRect(0, 0, w, h);
  } else {
    if (cfg.bgMode === "blur") ctx.filter = "blur(" + cfg.bgBlur + "px)";
    ctx.drawImage(foto, 0, 0, w, h);
  }
  ctx.restore();
  // escurece o fundo para a arte ler na frente dele: sem isto, os glifos
  // saem na mesma cor do que está atrás e o desenho desaparece
  const dim = (cfg.bgDim == null ? 0 : cfg.bgDim) / 100;
  if (dim > 0){
    ctx.save();
    ctx.fillStyle = "rgba(6,10,14," + dim + ")";
    ctx.fillRect(0, 0, w, h);
    ctx.restore();
  }
}

/* ---- animação (passo 8), modula a luminância de cada célula ---- */
function modular(l, coluna, linha, cfg, tempo){
  if (!cfg.animated) return l;
  const amp = (cfg.animIntensity.enabled ? cfg.animIntensity.intensity : 0) / 100 * .55;
  if (amp <= 0) return l;
  const vel = (cfg.animSpeed.enabled ? cfg.animSpeed.intensity : 0) / 100 * 2.2;
  const t = tempo * vel;
  let d = 0;
  switch (cfg.animStyle){
    case "wave":    d = Math.sin(coluna * .28 + linha * .12 + t * 2) * amp; break;
    case "pulse":   d = Math.sin(t * 2.4) * amp; break;
    case "shimmer": d = Math.sin(t * 3 + rnd(coluna * 37 + linha * 71) * 6.2832) * amp; break;
    case "ripple": {
      const dx = coluna - cfg._cols / 2, dy = linha - cfg._linhas / 2;
      d = Math.sin(Math.hypot(dx, dy) * .45 - t * 3) * amp; break;
    }
    case "flicker": d = (rnd(coluna * 13 + linha * 29 + Math.floor(t * 9) * 101) - .5) * amp * 2; break;
  }
  return grampo(l + d, 0, 1);
}

/* ---- grade e formas (passos 2 e 3) ---- */
function desenharArte(ctx, foto, cfg, w, h, tempo, aux){
  const s = Math.max(2, cfg.cellSize);
  const cols = Math.ceil(w / s), linhas = Math.ceil(h / s);
  cfg._cols = cols; cfg._linhas = linhas;
  const px = amostrar(foto, cols, linhas, aux);

  const lumi = new Float32Array(cols * linhas);
  for (let i = 0, j = 0; i < lumi.length; i++, j += 4)
    lumi[i] = (0.2126 * px[j] + 0.7152 * px[j+1] + 0.0722 * px[j+2]) / 255;

  const bordas = cfg.edgeEmphasis > 0 ? sobel(lumi, cols, linhas) : null;
  const cobertura = cfg.coverage / 100;
  const densidade = cfg.density / 100;
  const fonteMono = 'ui-monospace, "SF Mono", SFMono-Regular, Menlo, monospace';
  const conjunto = cfg.charSet === "custom" && cfg.customChars
    ? cfg.customChars : (CONJUNTOS[cfg.charSet] || CONJUNTOS.standard);

  const forma = FORMAS[cfg.renderMode] || FORMAS.characters;
  const ctx2 = { conjunto, fonteMono, densidade, tempo, coluna:0, linha:0, lumCima:null, lumBaixo:null };

  ctx.save();
  ctx.globalCompositeOperation = cfg.styleBlend || "source-over";
  for (let ly = 0; ly < linhas; ly++){
    for (let lx = 0; lx < cols; lx++){
      const i = ly * cols + lx;
      if (cobertura < 1 && rnd(lx * 91.7 + ly * 53.3) > cobertura) continue;

      let l = aplicarCurva(lumi[i], cfg.toneCurve);
      if (bordas) l = grampo(l + bordas[i] * (cfg.edgeEmphasis / 100), 0, 1);
      l = modular(l, lx, ly, cfg, tempo);
      if (cfg.invert) l = 1 - l;
      if (l <= 0.012) continue;

      const j = i * 4;
      const cor = "rgb(" + px[j] + "," + px[j+1] + "," + px[j+2] + ")";
      ctx2.coluna = lx; ctx2.linha = ly;
      if (cfg.renderMode === "halfblocks"){
        ctx2.lumCima  = lumi[Math.max(0, i - cols)];
        ctx2.lumBaixo = lumi[Math.min(lumi.length - 1, i + cols)];
      }
      forma(ctx, lx * s, ly * s, s, l, cor, ctx2);
    }
  }
  ctx.restore();
}

/* ---- ajustes de cor (passo 4) ---- */
function filtroDeCor(cfg){
  const f = [];
  if (cfg.brightness) f.push("brightness(" + (100 + cfg.brightness) + "%)");
  if (cfg.contrast !== 100) f.push("contrast(" + cfg.contrast + "%)");
  if (cfg.saturation) f.push("saturate(" + (100 + cfg.saturation) + "%)");
  if (cfg.grayscale) f.push("grayscale(" + cfg.grayscale + "%)");
  return f.join(" ") || "none";
}

function aplicarDesfoque(destino, origem, cfg, w, h){
  const d = destino.getContext("2d");
  const q = cfg.blurAmount;
  if (!q || cfg.blurType === "none"){ d.drawImage(origem, 0, 0); return; }

  const borrado = novaTela(w, h);
  const b = borrado.getContext("2d");
  // escala suave: o desfoque precisa amaciar sem apagar os glifos da grade
  b.filter = "blur(" + (q / 10) + "px)";
  b.drawImage(origem, 0, 0);
  b.filter = "none";

  if (cfg.blurType === "full"){ d.drawImage(borrado, 0, 0); return; }

  // máscara: branco onde fica borrado
  const m = novaTela(w, h), mc = m.getContext("2d");
  const pena = Math.max(1, cfg.tiltFeather) / 100;
  if (cfg.blurType === "tilt" || cfg.blurType === "progressive"){
    const pos = (cfg.blurType === "tilt" ? cfg.tiltPosition : cfg.progressivePosition) / 100;
    const foco = (cfg.blurType === "tilt" ? cfg.tiltFocus : 0) / 100;
    const g = mc.createLinearGradient(0, 0, 0, h);
    const a1 = Math.max(0, pos - foco/2 - pena), a2 = Math.max(0, pos - foco/2);
    const b1 = Math.min(1, pos + foco/2), b2 = Math.min(1, pos + foco/2 + pena);
    const inv = cfg.blurType === "progressive" && cfg.progressiveReverse;
    g.addColorStop(0, inv ? "black" : "white");
    g.addColorStop(a1, inv ? "black" : "white");
    g.addColorStop(a2, inv ? "white" : "black");
    g.addColorStop(b1, inv ? "white" : "black");
    g.addColorStop(b2, inv ? "black" : "white");
    g.addColorStop(1, inv ? "black" : "white");
    mc.fillStyle = g; mc.fillRect(0, 0, w, h);
  } else { // lens / radial
    const g = mc.createRadialGradient(
      w * cfg.blurCenterX/100, h * cfg.blurCenterY/100, 0,
      w * cfg.blurCenterX/100, h * cfg.blurCenterY/100, Math.max(w, h) * .75);
    const f = cfg.lensFocus / 100;
    g.addColorStop(0, "black"); g.addColorStop(Math.min(.99, f), "black");
    g.addColorStop(1, "white");
    mc.fillStyle = g; mc.fillRect(0, 0, w, h);
  }
  // recorta o borrado pela máscara e assenta sobre o nítido
  const rec = novaTela(w, h), rc = rec.getContext("2d");
  rc.drawImage(borrado, 0, 0);
  rc.globalCompositeOperation = "destination-in";
  rc.drawImage(m, 0, 0);
  d.drawImage(origem, 0, 0);
  d.drawImage(rec, 0, 0);
}

/* ---- pós-efeitos (passo 5) ---- */
function posEfeitos(ctx, cfg, w, h, tempo){
  const p = cfg.pfx, on = (k) => p[k] && p[k].enabled && p[k].intensity > 0;
  const forca = (k) => p[k].intensity / 100;

  if (on("pixelate")){
    const f = Math.max(2, Math.round(forca("pixelate") * 20));
    const t = novaTela(Math.ceil(w/f), Math.ceil(h/f)), tc = t.getContext("2d");
    tc.imageSmoothingEnabled = false; tc.drawImage(ctx.canvas, 0, 0, t.width, t.height);
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(t, 0, 0, w, h); ctx.imageSmoothingEnabled = true;
  }
  if (on("bloom")){
    const g = forca("bloom");
    ctx.save(); ctx.globalCompositeOperation = "lighter"; ctx.globalAlpha = g * .55;
    ctx.filter = "blur(" + (6 + g * 14) + "px) brightness(135%)";
    ctx.drawImage(ctx.canvas, 0, 0); ctx.restore();
  }
  if (on("chromatic")){
    const d = forca("chromatic") * 6;
    const copia = novaTela(w, h); copia.getContext("2d").drawImage(ctx.canvas, 0, 0);
    ctx.save(); ctx.globalCompositeOperation = "screen"; ctx.globalAlpha = .5;
    ctx.filter = "url(#nada)";
    ctx.filter = "none";
    ctx.drawImage(copia, -d, 0);
    ctx.drawImage(copia,  d, 0);
    ctx.restore();
  }
  if (on("halftone")){
    const a = forca("halftone"), passo = 4;
    ctx.save(); ctx.globalCompositeOperation = "multiply"; ctx.globalAlpha = a * .5;
    ctx.fillStyle = "#000";
    for (let y = 0; y < h; y += passo)
      for (let x = 0; x < w; x += passo){
        ctx.beginPath(); ctx.arc(x, y, passo * .22, 0, 6.2832); ctx.fill();
      }
    ctx.restore();
  }
  if (on("scanLines")){
    const a = forca("scanLines");
    ctx.save(); ctx.fillStyle = "rgba(0,0,0," + (a * .45) + ")";
    for (let y = 0; y < h; y += 3) ctx.fillRect(0, y, w, 1);
    ctx.restore();
  }
  if (on("glitch")){
    const a = forca("glitch");
    const n = Math.round(a * 8);
    for (let i = 0; i < n; i++){
      const y = rnd(i * 31 + Math.floor(tempo * 6) * 17) * h;
      const alt = 4 + rnd(i * 7 + Math.floor(tempo * 6)) * 22;
      const dx = (rnd(i * 53 + Math.floor(tempo * 6)) - .5) * a * 60;
      const faixa = ctx.getImageData(0, y, w, Math.min(alt, h - y));
      ctx.putImageData(faixa, dx, y);
    }
  }
  if (on("filmGrain")){
    const a = forca("filmGrain");
    const g = ctx.getImageData(0, 0, w, h), d = g.data;
    for (let i = 0; i < d.length; i += 4){
      const r = (Math.random() - .5) * a * 70;
      d[i] += r; d[i+1] += r; d[i+2] += r;
    }
    ctx.putImageData(g, 0, 0);
  }
  if (on("filmDust")){
    const a = forca("filmDust");
    const n = Math.round(a * 90);
    const q = Math.floor(tempo * 8);
    ctx.save();
    for (let i = 0; i < n; i++){
      const sx = rnd(i * 11 + q * 3), sy = rnd(i * 29 + q * 7), st = rnd(i * 43 + q * 5);
      ctx.fillStyle = st > .5 ? "rgba(255,255,255,.5)" : "rgba(0,0,0,.45)";
      if (st > .82){
        ctx.fillRect(sx * w, sy * h, 1, 3 + rnd(i + q) * 14);   // risco
      } else {
        ctx.beginPath(); ctx.arc(sx * w, sy * h, .4 + rnd(i*3+q) * 1.3, 0, 6.2832); ctx.fill();
      }
    }
    ctx.restore();
  }
  if (on("vignette")){
    const a = forca("vignette");
    const g = ctx.createRadialGradient(w/2, h/2, Math.min(w,h) * .28, w/2, h/2, Math.max(w,h) * .72);
    g.addColorStop(0, "rgba(0,0,0,0)");
    g.addColorStop(1, "rgba(0,0,0," + (a * .9) + ")");
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  }
}

/* ---- luzes (passo 6) ---- */
function desenharLuzes(ctx, cfg, w, h){
  if (!cfg.lights.enabled) return;
  ctx.save(); ctx.globalCompositeOperation = "lighter";
  cfg.lights.points.forEach(pt => {
    const g = ctx.createRadialGradient(pt.x * w, pt.y * h, 0, pt.x * w, pt.y * h, pt.radius * Math.max(w, h));
    g.addColorStop(0, "rgba(255,244,214," + (pt.intensity / 100) + ")");
    g.addColorStop(1, "rgba(255,244,214,0)");
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  });
  ctx.restore();
}

/* ---- máscara de revelação (passo 7) ---- */
function aplicarMascara(ctx, foto, cfg, w, h, mascaraImg){
  if (!cfg.mask.enabled || !mascaraImg) return;
  const rev = novaTela(w, h), r = rev.getContext("2d");
  r.drawImage(foto, 0, 0, w, h);
  r.globalCompositeOperation = "destination-in";
  if (cfg.mask.invert){
    const inv = novaTela(w, h), ic = inv.getContext("2d");
    ic.fillStyle = "#fff"; ic.fillRect(0, 0, w, h);
    ic.globalCompositeOperation = "destination-out";
    ic.drawImage(mascaraImg, 0, 0, w, h);
    r.drawImage(inv, 0, 0);
  } else {
    r.drawImage(mascaraImg, 0, 0, w, h);
  }
  ctx.drawImage(rev, 0, 0);
}

/* ---- orquestra tudo ---- */
function renderizar(saida, foto, cfg, tempo, aux, mascaraImg){
  const w = saida.width, h = saida.height;
  const arte = novaTela(w, h), ac = arte.getContext("2d");

  desenharFundo(ac, foto, cfg, w, h);          // 1
  desenharArte(ac, foto, cfg, w, h, tempo, aux); // 2 e 3

  const corrigida = novaTela(w, h), cc = corrigida.getContext("2d");
  cc.filter = filtroDeCor(cfg);                 // 4
  cc.drawImage(arte, 0, 0);
  cc.filter = "none";
  if (cfg.tintOpacity > 0){
    cc.save(); cc.globalCompositeOperation = cfg.overlayBlend;
    cc.globalAlpha = cfg.tintOpacity / 100;
    cc.fillStyle = cfg.tint; cc.fillRect(0, 0, w, h); cc.restore();
  }

  const ctx = saida.getContext("2d");
  ctx.clearRect(0, 0, w, h);
  aplicarDesfoque(saida, corrigida, cfg, w, h); // 4, desfoque
  posEfeitos(ctx, cfg, w, h, tempo);            // 5
  desenharLuzes(ctx, cfg, w, h);                // 6
  aplicarMascara(ctx, foto, cfg, w, h, mascaraImg); // 7
}
