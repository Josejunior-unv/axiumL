/* Motor de motion para Reels (1080x1920).
 * Tudo é função do tempo: a timeline do GSAP fica pausada e o renderizador
 * chama window.__seek(t) quadro a quadro, então o vídeo sai idêntico sempre. */
(() => {
  const W = 1080, H = 1920;
  gsap.registerPlugin(DrawSVGPlugin, MotionPathPlugin, CustomEase);
  CustomEase.create("snap", "M0,0 C0.12,0.9 0.2,1 1,1");
  CustomEase.create("whip", "M0,0 C0.7,0 0.2,1 1,1");

  const $ = (s, r = document) => r.querySelector(s);
  const layer = $("#layer"), cam = $("#cam"), hud = $("#hud");
  const bgc = $("#bg").getContext("2d"), fxc = $("#fx").getContext("2d");

  const tl = gsap.timeline({ paused: true, defaults: { ease: "power3.out" } });
  const cues = [];
  const chapters = [];

  // aleatório com semente: o mesmo vídeo sempre sai igual
  function rng(seed) {
    return () => {
      seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const rand = rng(1337);

  // ---------- fundo ----------
  const BG = {
    base: "#05050b", c1: "#7c3aed", c2: "#ff2e88", c3: "#22d3ee",
    blob: 0.55, grid: 0.55, speed: 0.12, part: 1, horizon: 1420, flash: 0, vig: 0.85, zoom: 1,
  };
  function rgb(c) {
    if (c[0] === "#") {
      const n = parseInt(c.slice(1), 16);
      return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
    }
    const m = c.match(/[\d.]+/g).map(Number);
    return [m[0], m[1], m[2]];
  }
  const rgba = (c, a) => { const [r, g, b] = rgb(c); return `rgba(${r},${g},${b},${a})`; };

  const pr = rng(42);
  const parts = Array.from({ length: 70 }, () => ({
    x: pr() * W, y: pr() * H, v: 25 + pr() * 90, s: 1.5 + pr() * 4.5, k: Math.floor(pr() * 3),
    ph: pr() * 6.28, dx: (pr() - 0.5) * 30,
  }));

  function drawBG(t) {
    const c = bgc;
    c.globalCompositeOperation = "source-over";
    c.fillStyle = BG.base; c.fillRect(0, 0, W, H);
    const cols = [BG.c1, BG.c2, BG.c3];

    // manchas de cor
    c.globalCompositeOperation = "lighter";
    const blobs = [
      [0.22, 0.28, 0.33, 0.21, 0.0, 820], [0.8, 0.55, 0.27, 0.17, 2.1, 760], [0.45, 0.85, 0.21, 0.29, 4.2, 900],
    ];
    blobs.forEach(([bx, by, fx, fy, ph, r], i) => {
      const x = W * (bx + 0.16 * Math.sin(t * fx + ph));
      const y = H * (by + 0.1 * Math.cos(t * fy + ph));
      const rr = r * BG.zoom * (1 + 0.08 * Math.sin(t * 0.7 + i));
      const g = c.createRadialGradient(x, y, 0, x, y, rr);
      g.addColorStop(0, rgba(cols[i], 0.42 * BG.blob));
      g.addColorStop(0.45, rgba(cols[i], 0.16 * BG.blob));
      g.addColorStop(1, rgba(cols[i], 0));
      c.fillStyle = g; c.fillRect(0, 0, W, H);
    });

    // piso em perspectiva (estilo synthwave)
    c.globalCompositeOperation = "source-over";
    if (BG.grid > 0.01) {
      const hz = BG.horizon, vx = W / 2;
      c.lineWidth = 2;
      for (let k = -14; k <= 14; k++) {
        const g = c.createLinearGradient(0, hz, 0, H);
        g.addColorStop(0, rgba(BG.c1, 0)); g.addColorStop(1, rgba(BG.c1, 0.5 * BG.grid));
        c.strokeStyle = g;
        c.beginPath(); c.moveTo(vx + k * 26, hz); c.lineTo(vx + k * 230, H + 40); c.stroke();
      }
      const N = 14, off = (t * BG.speed) % 1;
      for (let i = 0; i < N; i++) {
        const p = ((i + off) / N);
        const y = hz + (H - hz) * Math.pow(p, 2.3);
        c.strokeStyle = rgba(BG.c1, Math.min(1, p * 1.2) * 0.5 * BG.grid);
        c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke();
      }
      const hg = c.createLinearGradient(0, hz - 140, 0, hz + 60);
      hg.addColorStop(0, rgba(BG.c2, 0)); hg.addColorStop(0.7, rgba(BG.c2, 0.22 * BG.grid)); hg.addColorStop(1, rgba(BG.c2, 0));
      c.fillStyle = hg; c.fillRect(0, hz - 140, W, 200);
    }

    // partículas subindo
    c.globalCompositeOperation = "lighter";
    for (const p of parts) {
      const y = ((p.y - t * p.v) % (H + 80) + H + 80) % (H + 80) - 40;
      const x = p.x + Math.sin(t * 0.8 + p.ph) * p.dx;
      const a = (0.35 + 0.35 * Math.sin(t * 2.2 + p.ph)) * BG.part;
      c.fillStyle = rgba(cols[p.k], a * 0.25);
      c.beginPath(); c.arc(x, y, p.s * 3.2, 0, 6.283); c.fill();
      c.fillStyle = rgba("#ffffff", a * 0.8);
      c.beginPath(); c.arc(x, y, p.s * 0.6, 0, 6.283); c.fill();
    }
    c.globalCompositeOperation = "source-over";
  }

  // granulação pré-gerada (4 variações) + vinheta + flash
  const grains = Array.from({ length: 4 }, (_, k) => {
    const cv = document.createElement("canvas"); cv.width = cv.height = 256;
    const x = cv.getContext("2d"), id = x.createImageData(256, 256), r = rng(900 + k);
    for (let i = 0; i < id.data.length; i += 4) {
      const v = r() > 0.5 ? 255 : 0;
      id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = r() * 10;
    }
    x.putImageData(id, 0, 0);
    return fxc.createPattern(cv, "repeat");
  });
  function drawFX(t, frame) {
    const c = fxc;
    c.clearRect(0, 0, W, H);
    const v = c.createRadialGradient(W / 2, H / 2, H * 0.28, W / 2, H / 2, H * 0.75);
    v.addColorStop(0, "rgba(0,0,0,0)"); v.addColorStop(1, `rgba(0,0,0,${BG.vig})`);
    c.fillStyle = v; c.fillRect(0, 0, W, H);
    c.save();
    const g = Math.floor(frame / 3);
    c.scale(2, 2);
    c.translate((g * 73) % 256, (g * 151) % 256);
    c.fillStyle = grains[g % 4]; c.fillRect(-256, -256, W / 2 + 512, H / 2 + 512);
    c.restore();
    if (BG.flash > 0.001) { c.fillStyle = `rgba(255,255,255,${BG.flash})`; c.fillRect(0, 0, W, H); }
  }

  // ---------- utilidades de DOM ----------
  function el(parent, cls = "", html = "", css) {
    const d = document.createElement("div");
    if (cls) d.className = cls;
    if (html) d.innerHTML = html;
    if (css) Object.assign(d.style, css);
    (parent || layer).appendChild(d);
    return d;
  }
  function icon(name, size = 80, color = "#fff", sw = 2.2, fill = "none") {
    const d = document.createElement("span");
    d.className = "ico";
    d.style.width = d.style.height = size + "px";
    d.innerHTML = `<svg viewBox="0 0 24 24" fill="${fill}" stroke="${color}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round">${ICONS[name]}</svg>`;
    return d;
  }

  // texto com marcação:  *destaque*  e  [classe:texto]  — \n quebra linha
  function text(parent, spec, cls = "t t-xl", css) {
    const box = el(parent, cls, "", css);
    const words = [];
    spec.split("\n").forEach((line) => {
      const ln = document.createElement("span");
      ln.className = "ln";
      const re = /\*([^*]+)\*(\S*)|\[([\w\- ]+):([^\]]+)\](\S*)|(\S+)/g;
      let m, first = true;
      while ((m = re.exec(line))) {
        let k = "", body, tail = "";
        if (m[1]) { k = "hl"; body = m[1]; tail = m[2]; }
        else if (m[4]) { k = m[3]; body = m[4]; tail = m[5]; }
        else body = m[6];
        const ws = body.split(" ");
        ws.forEach((w, wi) => {
          if (!first) ln.appendChild(document.createTextNode(" "));
          first = false;
          const o = document.createElement("span"); o.className = "w";
          const i = document.createElement("span"); i.className = "wi " + k; i.textContent = w;
          o.appendChild(i);
          // pontuação colada ao destaque fica junto, sem herdar a cor
          if (tail && wi === ws.length - 1) { const tt = document.createElement("span"); tt.className = "tail"; tt.textContent = tail; i.appendChild(tt); }
          ln.appendChild(o); words.push(i);
        });
      }
      box.appendChild(ln);
    });
    box.words = words;
    return box;
  }

  // ---------- animações ----------
  const at = (x) => x;
  function cue(name, t, vol = 1) { cues.push({ name, t: +t.toFixed(3), vol }); }

  function wordsIn(box, t, o = {}) {
    const words = box.words || box;
    const st = o.stagger ?? 0.07, d = o.dur ?? 0.6, mode = o.from || "up";
    const from = {
      up: { yPercent: 135, rotate: 6, opacity: 0 },
      down: { yPercent: -135, rotate: -6, opacity: 0 },
      pop: { scale: 0, rotate: -12, opacity: 0 },
      blur: { opacity: 0, filter: "blur(24px)", scale: 1.3 },
      left: { xPercent: -120, opacity: 0 },
    }[mode];
    const to = { yPercent: 0, xPercent: 0, rotate: 0, scale: 1, opacity: 1, filter: "blur(0px)", duration: d, stagger: st,
      ease: mode === "pop" ? "back.out(2.2)" : "expo.out" };
    tl.fromTo(words, from, to, t);
    if (o.cue !== false) cue(o.cue || (mode === "pop" ? "pop" : "whoosh"), t, o.vol ?? 0.8);
    // depois de entrar, solta a máscara para o brilho não ser cortado
    tl.set(words.map((w) => w.parentNode), { overflow: "visible" }, t + d + st * words.length);
    return t + d + st * (words.length - 1);
  }

  function inn(node, t, o = {}) {
    const d = o.dur ?? 0.7;
    const from = {
      up: { y: 140, opacity: 0 }, down: { y: -140, opacity: 0 },
      left: { x: -260, opacity: 0 }, right: { x: 260, opacity: 0 },
      pop: { scale: 0, opacity: 0, rotate: o.rot ?? -8 },
      zoom: { scale: 2.4, opacity: 0, filter: "blur(30px)" },
      blur: { opacity: 0, filter: "blur(30px)", scale: 0.9 },
      fade: { opacity: 0 },
      flip: { rotateX: -90, opacity: 0, transformPerspective: 1400, y: 60 },
    }[o.from || "up"];
    const to = { x: 0, y: 0, scale: 1, opacity: 1, rotate: 0, rotateX: 0, filter: "blur(0px)", duration: d,
      ease: o.ease || (o.from === "pop" ? "back.out(1.9)" : "expo.out"), stagger: o.stagger ?? 0 };
    tl.fromTo(node, from, to, t);
    if (o.cue) cue(o.cue, t, o.vol ?? 0.8);
    return t + d;
  }
  function out(node, t, o = {}) {
    const d = o.dur ?? 0.4;
    const to = {
      up: { y: -160, opacity: 0 }, down: { y: 160, opacity: 0 },
      left: { x: -300, opacity: 0 }, right: { x: 300, opacity: 0 },
      shrink: { scale: 0, opacity: 0 }, blur: { opacity: 0, filter: "blur(30px)", scale: 1.15 },
      fade: { opacity: 0 },
    }[o.to || "blur"];
    tl.to(node, { ...to, duration: d, ease: "power3.in", stagger: o.stagger ?? 0 }, t);
    if (o.cue) cue(o.cue, t, o.vol ?? 0.6);
    return t + d;
  }

  function scene(start, end, o = {}) {
    const s = el(layer, "scene");
    tl.set(s, { visibility: "visible" }, start);
    if (o.chapter !== false) chapters.push(start);
    if (end != null) {
      const d = o.exitDur ?? 0.35;
      if (o.exit !== "none") {
        tl.to(s, { opacity: 0, scale: o.exit === "in" ? 0.85 : 1.12, filter: "blur(22px)", duration: d, ease: "power2.in" }, end - d);
        if (o.exitCue !== false) cue("swish", end - d, 0.55);
      }
      tl.set(s, { visibility: "hidden" }, end);
    }
    return s;
  }

  function shake(t, amp = 22, d = 0.45) {
    const n = 8;
    for (let i = 0; i < n; i++) {
      const k = 1 - i / n;
      tl.to(cam, { x: (rand() - 0.5) * 2 * amp * k, y: (rand() - 0.5) * 2 * amp * k, rotate: (rand() - 0.5) * 1.2 * k,
        duration: d / n, ease: "none" }, t + (i * d) / n);
    }
    tl.to(cam, { x: 0, y: 0, rotate: 0, duration: 0.08, ease: "none" }, t + d);
  }
  function flash(t, k = 0.55, d = 0.35) {
    tl.fromTo(BG, { flash: k }, { flash: 0, duration: d, ease: "power2.out", immediateRender: false }, t);
  }
  function punch(t, o = {}) {
    if (o.flash !== false) flash(t, o.flash ?? 0.45);
    shake(t, o.amp ?? 22, o.dur ?? 0.45);
    cue(o.cue || "hit", t, o.vol ?? 1);
  }
  function glitch(node, t, d = 0.4) {
    tl.fromTo(node, { textShadow: "14px 0 0 rgba(255,46,136,.9), -14px 0 0 rgba(34,211,238,.9)", x: -10 },
      { textShadow: "0px 0 0 rgba(255,46,136,0), 0px 0 0 rgba(34,211,238,0)", x: 0, duration: d, ease: "steps(6)", immediateRender: false }, t);
    cue("glitch", t, 0.7);
  }
  function mark(node, t, d = 0.5) {
    tl.fromTo(node, { "--k": 0 }, { "--k": 1, duration: d, ease: "expo.inOut" }, t);
  }
  function counter(node, t, d, from, to, fmt = (v) => Math.round(v).toLocaleString("pt-BR"), o = {}) {
    const obj = { v: from };
    node.textContent = fmt(from);
    tl.to(obj, { v: to, duration: d, ease: o.ease || "power2.out", onUpdate: () => (node.textContent = fmt(obj.v)) }, t);
    if (o.cue !== false) {
      const n = Math.max(3, Math.round(d * 12));
      for (let i = 0; i < n; i++) cue("tick", t + (d * 0.85 * i) / n, 0.35);
    }
    return t + d;
  }
  function draw(node, t, d = 0.8, o = {}) {
    const shapes = "path,circle,rect,line,polyline,polygon";
    const p = node.matches && node.matches(shapes) ? node : node.querySelectorAll ? node.querySelectorAll(shapes) : node;
    tl.fromTo(p, { drawSVG: o.from ?? "0%" }, { drawSVG: "100%", duration: d, ease: o.ease || "power2.inOut", stagger: o.stagger ?? 0.08 }, t);
    return t + d;
  }
  function bgTo(t, props, d = 1) { tl.to(BG, { ...props, duration: d, ease: "power2.inOut" }, t); }
  function float(node, t0, t1, amp = 14, period = 2.4) {
    const n = Math.max(1, Math.floor((t1 - t0) / period));
    for (let i = 0; i < n; i++) {
      tl.to(node, { y: `+=${amp}`, duration: period / 2, ease: "sine.inOut" }, t0 + i * period);
      tl.to(node, { y: `-=${amp}`, duration: period / 2, ease: "sine.inOut" }, t0 + i * period + period / 2);
    }
  }
  function pulse(node, t, s = 1.12, d = 0.3) {
    tl.to(node, { scale: s, duration: d / 2, ease: "power2.out", yoyo: true, repeat: 1 }, t);
  }

  // ---------- telas prontas ----------
  // gancho de abertura: kicker + frase gigante com impacto
  function hook(start, end, o) {
    const s = scene(start, end);
    const c = el(s, "center");
    let k;
    if (o.kicker) {
      k = el(c, "kicker", `<span class="dot"></span>${o.kicker}`, { marginBottom: "56px" });
      inn(k, start + 0.05, { from: "pop", dur: 0.55 });
    }
    const tx = text(c, o.text, o.cls || "t t-xl");
    const done = wordsIn(tx, start + 0.12, { stagger: o.stagger ?? 0.08, from: o.from || "up", cue: "whoosh" });
    if (o.sub) {
      const sb = text(c, o.sub, "p p-l", { marginTop: "56px" });
      wordsIn(sb, done + 0.15, { stagger: 0.04, from: "up", dur: 0.5, cue: false });
    }
    if (o.punchAt != null) punch(start + o.punchAt);
    return { s, c, tx, k };
  }

  // tela final: salvar, compartilhar, seguir
  function cta(start, end, o = {}) {
    const s = scene(start, end, { exit: "none" });
    const c = el(s, "center");
    const row = el(c, "", "", { display: "flex", gap: "44px", marginBottom: "80px" });
    const names = ["heart", "send", "bookmark"];
    const badges = names.map((n) => {
      const b = el(row, "badge", "", { width: "150px", height: "150px", borderRadius: "44px" });
      const ic = icon(n, 78, "#fff", 2.4);
      b.appendChild(ic);
      return b;
    });
    inn(badges, start + 0.05, { from: "pop", dur: 0.6, stagger: 0.12, cue: "pop" });
    cue("pop", start + 0.17, 0.7); cue("pop", start + 0.29, 0.7);
    badges.forEach((b, i) => draw(b, start + 0.15 + i * 0.12, 0.6));
    // o salvar "pisca" no final
    tl.to(badges[2].querySelector("svg"), { attr: { fill: "#fff" }, duration: 0.25 }, start + 1.3);
    pulse(badges[2], start + 1.3, 1.22, 0.35);
    cue("ding", start + 1.3, 0.8);

    const tx = text(c, o.text || "SALVA ESSE\n*VÍDEO*", "t t-l");
    const d1 = wordsIn(tx, start + 0.35, { stagger: 0.07, cue: "whoosh" });
    const sb = text(c, o.sub || "e manda pra quem [b:investe em anúncio]", "p p-l", { marginTop: "48px", maxWidth: "860px" });
    wordsIn(sb, d1 + 0.05, { stagger: 0.04, dur: 0.5, cue: false });
    const nx = el(c, "chip", `${icon("play", 34, "#fff", 2.6).outerHTML}<span>${o.next || "Segue pra ver o próximo"}</span>`,
      { marginTop: "70px", fontSize: "38px", padding: "20px 34px", borderColor: "color-mix(in srgb, var(--a2) 70%, transparent)",
        background: "color-mix(in srgb, var(--a2) 18%, transparent)" });
    inn(nx, d1 + 0.6, { from: "up", dur: 0.6, cue: "pop" });
    if (CONFIG.handle) {
      const hd = el(c, "", CONFIG.handle, { marginTop: "34px", fontFamily: "Inter", fontWeight: 800, fontSize: "44px", color: "rgba(255,255,255,.8)" });
      inn(hd, d1 + 0.8, { from: "fade", dur: 0.6 });
    }
    float(row, start + 1.2, end, 10, 2);
    return s;
  }

  // ---------- HUD ----------
  let progBars = [];
  function buildHUD(V, dur) {
    const top = el(hud, "hud-top");
    el(top, "hud-pill", `<span class="dot"></span>${CONFIG.serie}`);
    el(top, "hud-ep", `EP ${String(V.ep).padStart(2, "0")}/${String(CONFIG.total).padStart(2, "0")}`);
    const pg = el(hud, "hud-prog");
    const ch = [...new Set(chapters)].sort((a, b) => a - b);
    progBars = ch.map((c0, i) => {
      const seg = el(pg, ""); const bar = document.createElement("i"); seg.appendChild(bar);
      return { bar, a: c0, b: i + 1 < ch.length ? ch[i + 1] : dur };
    });
    tl.fromTo(top, { y: -60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6 }, 0.1);
    tl.fromTo(pg, { opacity: 0 }, { opacity: 1, duration: 0.6 }, 0.2);
  }
  function drawHUD(t) {
    for (const p of progBars) {
      const k = Math.max(0, Math.min(1, (t - p.a) / (p.b - p.a)));
      p.bar.style.transform = `scaleX(${k})`;
    }
  }

  // ---------- ciclo ----------
  let fps = 30;
  window.__seek = (t) => {
    tl.seek(t, false);
    const f = Math.round(t * fps);
    drawBG(t); drawFX(t, f); drawHUD(t);
  };

  window.Engine = {
    async boot() {
      const V = window.VIDEO;
      fps = CONFIG.fps;
      await Promise.all([
        document.fonts.load('900 100px "Inter Display"'), document.fonts.load('800 50px "Inter"'), document.fonts.load('600 50px "Inter"'),
      ]).catch(() => {});
      const th = V.theme || {};
      if (th.a1) document.documentElement.style.setProperty("--a1", th.a1);
      if (th.a2) document.documentElement.style.setProperty("--a2", th.a2);
      Object.assign(BG, th.bg || {});
      V.build(E);
      const dur = V.duration || tl.duration();
      tl.set({}, {}, dur);
      buildHUD(V, dur);
      window.__info = () => ({ duration: dur, fps, cues: cues.sort((a, b) => a.t - b.t), ep: V.ep, slug: V.slug, title: V.title, bpm: V.bpm || 120 });
      window.__seek(0);
      window.__ready = true;
    },
  };

  const E = (window.E = {
    W, H, tl, BG, layer, el, icon, text, scene, wordsIn, in: inn, out, shake, flash, punch, glitch, mark, counter, draw,
    bgTo, float, pulse, hook, cta, cue, rand, rng, at,
  });
})();
