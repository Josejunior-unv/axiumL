// EP 03 — ROAS 4 e mesmo assim prejuízo? (margem e ROAS de equilíbrio)
window.VIDEO = {
  ep: 3,
  slug: "roas-de-equilibrio",
  title: "ROAS 4 e mesmo assim prejuízo?",
  theme: { a1: "#22f28a", a2: "#22d3ee", bg: { c1: "#059669", c2: "#22d3ee", c3: "#8b5cf6" } },
  build(E) {
    const { tl } = E;
    const brl = (v) => (v < 0 ? "−R$ " : "R$ ") + Math.abs(Math.round(v)).toLocaleString("pt-BR");

    // 1 — gancho
    const h = E.hook(0, 3.4, { kicker: "Cuidado com o ROAS", text: "ROAS 4\nE MESMO ASSIM\n[g-red:PREJUÍZO]?", cls: "t t-l" });
    E.punch(1.0, { amp: 20, cue: "hit" });
    E.glitch(h.tx.words[4], 1.05, 0.5);
    E.bgTo(0.9, { c1: "#dc2626", c2: "#ff7a1a" }, 0.4);
    E.bgTo(2.6, { c1: "#059669", c2: "#22d3ee" }, 0.8);

    // 2 — a conta que todo mundo faz
    const s2 = E.scene(3.4, 9.0);
    const t2 = E.text(s2, "A CONTA QUE\nTODO MUNDO FAZ", "t t-m", { position: "absolute", top: "320px", left: "80px", right: "80px", textAlign: "center" });
    E.wordsIn(t2, 3.5);
    const card = E.el(s2, "card abs", "", { left: "80px", right: "80px", top: "620px", padding: "40px 48px" });
    const rows = [["Investiu em anúncio", 1000, "#fff"], ["Vendeu 50 × R$ 80", 4000, "#22f28a"]];
    const vals = rows.map(([l, v, c], i) => {
      const r = E.el(card, "", "", { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "26px 0",
        borderBottom: i === 0 ? "2px solid rgba(255,255,255,.1)" : "none" });
      E.el(r, "p", l, { fontSize: "42px", color: "rgba(255,255,255,.8)" });
      const n = E.el(r, "num", "", { fontSize: "76px", color: c });
      return { r, n, v };
    });
    E.in(card, 4.0, { from: "up", cue: "swish" });
    E.in(vals[0].r, 4.2, { from: "left" });
    E.counter(vals[0].n, 4.3, 0.8, 0, 1000, brl);
    E.in(vals[1].r, 5.0, { from: "left" });
    E.counter(vals[1].n, 5.1, 0.9, 0, 4000, brl);
    E.cue("cash", 6.0, 0.7);
    const res = E.el(s2, "abs center", "", { top: "1080px", bottom: "auto", height: "380px" });
    const roas = E.text(res, "ROAS [g-green:4X]", "t t-xxl");
    E.wordsIn(roas, 6.3, { from: "pop", stagger: 0.12 });
    E.punch(6.45, { amp: 14, flash: 0.25 });
    const ok = E.el(res, "chip", "Parece ótimo, né?", { marginTop: "30px" });
    E.in(ok, 7.0, { from: "up", cue: "pop" });

    // 3 — a margem muda tudo
    const s3 = E.scene(9.0, 15.4);
    const t3 = E.text(s3, "MAS SUA MARGEM\nÉ DE [g-yellow:20%]", "t t-m", { position: "absolute", top: "320px", left: "80px", right: "80px", textAlign: "center" });
    E.wordsIn(t3, 9.1);
    E.punch(9.75, { amp: 10, flash: 0.15 });
    const lbl = E.el(s3, "abs p", "Dos <b>R$ 4.000</b> que entraram:", { left: "80px", top: "620px", fontSize: "42px" });
    E.in(lbl, 9.8, { from: "fade" });
    const bar = E.el(s3, "abs", "", { left: "80px", right: "80px", top: "710px", height: "150px", borderRadius: "30px", overflow: "hidden",
      display: "flex", background: "rgba(255,255,255,.06)", border: "2px solid rgba(255,255,255,.12)" });
    const seg1 = E.el(bar, "", `<span>Custo do produto</span>`, { width: "80%", background: "linear-gradient(90deg,#334155,#475569)", display: "flex",
      alignItems: "center", paddingLeft: "34px", fontFamily: "Inter", fontWeight: 800, fontSize: "36px", transformOrigin: "left" });
    const seg2 = E.el(bar, "", `<span>20%</span>`, { width: "20%", background: "linear-gradient(90deg,#ffd400,#ff7a1a)", display: "flex",
      alignItems: "center", justifyContent: "center", fontFamily: "Inter", fontWeight: 900, fontSize: "40px", color: "#111", transformOrigin: "left" });
    tl.fromTo(seg1, { scaleX: 0 }, { scaleX: 1, duration: 0.8, ease: "expo.out" }, 10.0);
    tl.fromTo(seg2, { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "expo.out" }, 10.6);
    E.cue("whoosh", 10.0, 0.6); E.cue("pop", 10.6, 0.7);
    const lines = [["Sobra de margem", 800, "#ffd400", 11.2], ["Gasto com anúncio", -1000, "#fff", 12.0]];
    const card3 = E.el(s3, "card abs", "", { left: "80px", right: "80px", top: "920px", padding: "26px 48px" });
    lines.forEach(([l, v, c, t], i) => {
      const r = E.el(card3, "", "", { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "22px 0",
        borderBottom: "2px solid rgba(255,255,255,.1)" });
      E.el(r, "p", l, { fontSize: "40px", color: "rgba(255,255,255,.8)" });
      const n = E.el(r, "num", "", { fontSize: "70px", color: c });
      E.in(r, t, { from: "left", cue: "swish" });
      E.counter(n, t + 0.1, 0.6, 0, v, brl);
    });
    const fr = E.el(card3, "", "", { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "26px 0 10px" });
    E.el(fr, "t", "Resultado", { fontSize: "56px" });
    const fn = E.el(fr, "num g-red", "", { fontSize: "110px" });
    E.in(card3, 11.0, { from: "up", dur: 0.5 });
    E.in(fr, 12.9, { from: "zoom", dur: 0.5 });
    E.counter(fn, 12.95, 0.5, 0, -200, brl, { cue: false });
    E.punch(13.2, { amp: 26, flash: 0.35, cue: "error" });
    E.cue("hit", 13.2, 0.8);
    E.bgTo(13.0, { c1: "#dc2626", c2: "#ff7a1a" }, 0.4);
    const st = E.el(s3, "abs t g-red", "PREJUÍZO", { left: 0, right: 0, top: "1420px", textAlign: "center", fontSize: "120px" });
    E.in(st, 13.3, { from: "pop", dur: 0.5 });

    // 4 — ROAS de equilíbrio
    const s4 = E.scene(15.4, 22.4);
    E.bgTo(15.2, { c1: "#059669", c2: "#22d3ee" }, 0.8);
    const k4 = E.el(s4, "abs", `<div class="kicker"><span class="dot"></span>A conta certa</div>`, { left: 0, right: 0, top: "320px", textAlign: "center" });
    E.in(k4, 15.5, { from: "pop" });
    const f = E.text(s4, "ROAS MÍNIMO\n= *1 ÷ MARGEM*", "t t-l", { position: "absolute", top: "450px", left: "60px", right: "60px", textAlign: "center" });
    E.wordsIn(f, 15.6, { stagger: 0.09 });
    E.punch(16.2, { amp: 14, flash: 0.25 });
    const tab = E.el(s4, "abs", "", { left: "80px", right: "80px", top: "820px", display: "flex", flexDirection: "column", gap: "22px" });
    const ex = [["Margem 50%", 2, "2x"], ["Margem 30%", 3.33, "3,3x"], ["Margem 20%", 5, "5x"]];
    ex.forEach(([m, v, txt], i) => {
      const t = 16.9 + i * 0.9;
      const r = E.el(tab, "card", "", { padding: "28px 40px", display: "grid", gridTemplateColumns: "290px 1fr 150px", alignItems: "center", gap: "26px" });
      E.el(r, "p", m, { color: "#fff", fontWeight: 800, fontSize: "40px" });
      const b = E.el(r, "bar", "<i></i>", { height: "30px" });
      E.el(r, "num", txt, { fontSize: "70px", textAlign: "right", color: i === 2 ? "#ffd400" : "#22f28a" });
      E.in(r, t, { from: "right", dur: 0.55, cue: "swish" });
      tl.fromTo(b.firstChild, { scaleX: 0 }, { scaleX: v / 5, duration: 0.7, ease: "expo.out" }, t + 0.2);
      E.cue("pop", t + 0.25, 0.5);
    });
    const nt = E.el(s4, "abs p", "Abaixo disso, <b>cada venda dá prejuízo</b>. Acima, é lucro.", { left: "90px", right: "90px", top: "1400px", textAlign: "center", fontSize: "42px" });
    E.in(nt, 19.8, { from: "up" });

    // 5 — fechamento
    const s5 = E.scene(22.4, 26.0);
    const c5 = E.el(s5, "center");
    const a5 = E.text(c5, "ROAS BOM NÃO\nÉ O [mute:MAIOR].", "t t-l");
    E.wordsIn(a5, 22.5, { stagger: 0.07 });
    const b5 = E.text(c5, "É O QUE\n[g-green:DÁ LUCRO].", "t t-xl", { marginTop: "60px" });
    E.wordsIn(b5, 23.6, { stagger: 0.09 });
    E.punch(24.0, { amp: 18, flash: 0.35, cue: "cash" });

    E.cta(26.0, 30.6, { text: "SALVA E\n*CALCULA O SEU*", next: "EP 04: o funil que vende todo dia" });
  },
};
