// EP 04 — Funil de tráfego (topo, meio, fundo) + remarketing
window.VIDEO = {
  ep: 4,
  slug: "funil-de-trafego",
  title: "O funil que vende todo dia",
  theme: { a1: "#ff5e5b", a2: "#ffd23f", bg: "orange" },
  build(E) {
    const { tl } = E;

    // 1 — gancho
    const h = E.hook(0, 4.0, { kicker: "Funil de vendas", text: "VOCÊ PEDE EM\nCASAMENTO NO\n[g-yellow:1º ENCONTRO]?", cls: "t t-l",
      sub: "É isso que faz quem mostra [b:só oferta] pra quem nunca te viu." });
    E.punch(1.15, { amp: 18 });
    E.glitch(h.tx.words[5], 1.2);

    // 2 — o funil
    const s2 = E.scene(4.0, 17.4);
    E.bgTo(3.9, "cream");
    const ttl = E.text(s2, "O FUNIL EM *3 ETAPAS*", "t t-s", { position: "absolute", top: "320px", left: "60px", right: "60px", textAlign: "center" });
    E.wordsIn(ttl, 4.1);
    const L = [
      { y: 450, w: 920, n: "TOPO", tag: "Público frio", c: ["#3da5ff", "#3da5ff"], ic: "eye",
        a: "Nunca ouviu falar de você", b: "Vídeo curto, dica, entretenimento" },
      { y: 690, w: 700, n: "MEIO", tag: "Público morno", c: ["#ffd23f", "#ffd23f"], ic: "heart",
        a: "Engajou ou visitou o site", b: "Prova social, depoimento, comparação" },
      { y: 930, w: 480, n: "FUNDO", tag: "Público quente", c: ["#ff5e5b", "#ff5e5b"], ic: "cart",
        a: "Quase comprou (carrinho, checkout)", b: "Oferta, bônus, urgência" },
    ];
    const layers = L.map((l, i) => {
      // a sombra deslocada fica no invólucro, porque o clip-path cortaria a do próprio trapézio
      const wrap = E.el(s2, "abs", "", { left: (1080 - l.w) / 2 + "px", width: l.w + "px", top: l.y + "px", height: "210px",
        filter: "drop-shadow(0 0 0 #17171c) drop-shadow(10px 10px 0 #17171c)", opacity: 0.4 });
      const d = E.el(wrap, "abs", "", { inset: 0,
        clipPath: i < 2 ? "polygon(0 0,100% 0,88% 100%,12% 100%)" : "polygon(0 0,100% 0,72% 100%,28% 100%)",
        background: l.c[0], display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column" });
      E.el(d, "t", l.n, { fontSize: i === 2 ? "62px" : "78px", marginTop: "-14px" });
      E.el(d, "", l.tag, { fontFamily: "Inter", fontWeight: 800, fontSize: i === 2 ? "26px" : "32px", letterSpacing: ".08em", textTransform: "uppercase", opacity: 0.9 });
      E.in(wrap, 4.4 + i * 0.15, { from: "down", dur: 0.6, cue: i === 0 ? "whoosh" : false });
      return wrap;
    });
    // pessoas (pontos) caindo pelo funil: muitas entram, poucas saem
    const dots = E.el(s2, "abs", "", { left: 0, top: 0, width: "1080px", height: "1920px" });
    const r = E.rng(11);
    for (let i = 0; i < 46; i++) {
      const pass = i % 8 === 0;
      const x0 = 120 + r() * 840;
      const dd = E.el(dots, "abs", "", { left: x0 + "px", top: "400px", width: "22px", height: "22px", borderRadius: "50%",
        background: pass ? "#b8f35a" : "#fff", border: "4px solid #17171c", opacity: 0 });
      const t = 5.0 + r() * 2.2;
      const endY = pass ? 1150 : 500 + r() * 560;
      const endX = pass ? 540 - 11 : x0 + (x0 < 540 ? -60 : 60);
      tl.to(dd, { opacity: 1, duration: 0.1 }, t);
      tl.to(dd, { top: endY, left: endX, duration: pass ? 1.4 : 0.9, ease: "power1.in" }, t);
      if (!pass) tl.to(dd, { opacity: 0, scale: 0.3, duration: 0.3 }, t + 0.7);
      else { tl.to(dd, { top: 1210, scale: 1.4, duration: 0.4, ease: "back.out(3)" }, t + 1.4); E.cue("pop", t + 1.4, 0.35); }
    }
    tl.to(dots, { opacity: 0, duration: 0.4 }, 8.6);

    // detalhe de cada etapa
    const info = E.el(s2, "card abs", "", { left: "80px", right: "80px", top: "1200px", padding: "36px 44px", minHeight: "300px" });
    const blocks = L.map((l, i) => {
      const b = E.el(info, "abs", "", { left: "44px", right: "44px", top: "36px" });
      const hd = E.el(b, "", "", { display: "flex", alignItems: "center", gap: "22px" });
      const bd = E.el(hd, "badge", "", { width: "84px", height: "84px", borderRadius: "24px", background: l.c[0] });
      bd.appendChild(E.icon(l.ic, 46));
      E.el(hd, "t", l.n, { fontSize: "64px" });
      E.el(b, "p", `<b>Quem é:</b> ${l.a}`, { fontSize: "38px", marginTop: "22px" });
      E.el(b, "p", `<b>O que mostrar:</b> ${l.b}`, { fontSize: "38px", marginTop: "10px" });
      return b;
    });
    E.in(info, 8.8, { from: "up", cue: "swish" });
    blocks.forEach((b, i) => {
      const t = 9.0 + i * 2.8;
      tl.set(b, { opacity: 0 }, 0);
      E.in(b, t, { from: "right", dur: 0.5, cue: "whoosh" });
      if (i < 2) E.out(b, t + 2.6, { to: "left", dur: 0.25 });
      tl.to(layers[i], { opacity: 1, scale: 1.04, duration: 0.3 }, t);
      E.pulse(layers[i], t, 1.08, 0.3);
      if (i > 0) tl.to(layers[i - 1], { opacity: 0.4, scale: 1, duration: 0.3 }, t);
    });

    // 3 — remarketing
    const s3 = E.scene(17.4, 25.0);
    E.bgTo(17.2, "sky");
    const t3 = E.text(s3, "A MAIORIA *NÃO*\n*COMPRA* NA 1ª\nVISITA", "t t-m", { position: "absolute", top: "320px", left: "60px", right: "60px", textAlign: "center" });
    E.wordsIn(t3, 17.5);
    E.punch(18.0, { amp: 12, flash: 0.2 });
    // ciclo do remarketing
    const cx = 540, cy = 1020, R = 230;
    const ring = E.el(s3, "abs", `<svg width="760" height="760" viewBox="0 0 760 760">
      <circle cx="380" cy="380" r="${R}" fill="none" stroke="rgba(23,23,28,.15)" stroke-width="14"/>
      <circle class="arc" cx="380" cy="380" r="${R}" fill="none" stroke="#17171c" stroke-width="14" stroke-linecap="round" transform="rotate(-90 380 380)"/></svg>`,
      { left: cx - 380 + "px", top: cy - 380 + "px" });
    E.draw(ring.querySelector(".arc"), 18.6, 4.2, { ease: "none" });
    const steps = [["globe", "Visitou"], ["x", "Saiu"], ["repeat", "Viu o anúncio\nde novo"], ["coin", "Voltou e\ncomprou"]];
    steps.forEach(([ic, lb], i) => {
      const a = -Math.PI / 2 + (i * Math.PI) / 2;
      const x = cx + R * Math.cos(a), y = cy + R * Math.sin(a);
      const n = E.el(s3, "abs", "", { left: x - 75 + "px", top: y - 75 + "px", width: "150px", height: "150px", display: "flex", flexDirection: "column", alignItems: "center" });
      const last = i === 3;
      const bd = E.el(n, "badge", "", { width: "130px", height: "130px", borderRadius: "40px",
        background: ["#ffd23f", "#e4e4e7", "#ff8a3d", "#b8f35a"][i] });
      bd.appendChild(E.icon(ic, 68));
      const side = { left: "-120px", right: "-120px", top: i === 0 ? "-60px" : "146px", textAlign: "center" };
      E.el(n, "abs", lb.replace("\n", "<br>"), { ...side, fontFamily: "Inter", fontWeight: 800, fontSize: "36px", lineHeight: 1.1, whiteSpace: "nowrap" });
      const t = 18.6 + i * 1.4;
      E.in(n, t, { from: "pop", cue: last ? "cash" : "pop" });
      if (last) E.punch(t + 0.1, { amp: 12, flash: 0.25, cue: "ding" });
    });
    const tag = E.el(s3, "abs", "", { left: 0, right: 0, top: "1470px", textAlign: "center" });
    const ch = E.el(tag, "kicker", `<span class="dot"></span>Isso é remarketing`);
    E.in(ch, 23.0, { from: "up", cue: "whoosh" });

    E.cta(25.0, 29.6, { next: "EP 05: por que quem paga mais não ganha" });
  },
};
