// EP 02 — As 5 métricas que importam (CPM, CTR, CPC, CPA, ROAS), com um exemplo só do começo ao fim
window.VIDEO = {
  ep: 2,
  slug: "5-metricas-que-importam",
  title: "As 5 métricas que importam",
  theme: { a1: "#3da5ff", a2: "#ffd23f", bg: "sky" },
  build(E) {
    const { tl } = E;
    const brl = (v, d = 0) => "R$ " + v.toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });

    // 1 — gancho
    const h = E.hook(0, 3.3, { kicker: "Métricas de tráfego", text: "5 NÚMEROS\nQUE *SALVAM*\nSUA VERBA", cls: "t t-l" });
    E.punch(0.85, { amp: 14 });
    const ex = E.el(h.c, "chip", `${E.icon("wallet", 40).outerHTML}<span>Exemplo: <b>R$ 1.000</b> investidos</span>`, { marginTop: "60px", fontSize: "36px" });
    E.in(ex, 1.5, { from: "up", cue: "pop" });

    // 2 — cada métrica
    const M = [
      ["CPM", "Custo por mil impressões", "Investimento ÷ impressões × 1.000", "R$ 1.000 ÷ 50.000 × 1.000", 20, (v) => brl(v), "Quanto custa ser visto?", "eye"],
      ["CTR", "Taxa de cliques", "Cliques ÷ impressões × 100", "900 ÷ 50.000 × 100", 1.8, (v) => v.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + "%", "Seu anúncio prende atenção?", "cursor"],
      ["CPC", "Custo por clique", "Investimento ÷ cliques", "R$ 1.000 ÷ 900", 1.11, (v) => brl(v, 2), "Quanto custa cada visita?", "coin"],
      ["CPA", "Custo por aquisição", "Investimento ÷ vendas", "R$ 1.000 ÷ 40 vendas", 25, (v) => brl(v), "Quanto custa cada cliente?", "cart"],
      ["ROAS", "Retorno sobre o anúncio", "Receita ÷ investimento", "R$ 4.000 ÷ R$ 1.000", 4, (v) => v.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + "x", "Quanto volta pra cada R$ 1?", "trend"],
    ];
    // [fundo, cor de destaque]
    const cols = [["yellow", "#ff5e5b"], ["coral", "#ffd23f"], ["teal", "#ffd23f"], ["orange", "#3da5ff"], ["green", "#ffd23f"]];
    const D = 3.9;
    M.forEach(([ac, name, formula, calc, val, fmt, q, ic], i) => {
      const t0 = 3.3 + i * D;
      const s = E.scene(t0, t0 + D);
      E.bgTo(t0 - 0.2, cols[i][0]);
      const idx = E.el(s, "abs t", String(i + 1).padStart(2, "0"), { left: "80px", top: "300px", fontSize: "300px", color: "transparent",
        WebkitTextStroke: "5px #17171c", opacity: 0.9 });
      E.in(idx, t0 + 0.05, { from: "left", dur: 0.6 });
      const bd = E.el(s, "badge abs", "", { right: "80px", top: "340px", width: "150px", height: "150px", borderRadius: "44px",
        background: cols[i][1] });
      const icn = E.icon(ic, 80); bd.appendChild(icn);
      E.in(bd, t0 + 0.15, { from: "pop", cue: "pop" });
      E.draw(icn, t0 + 0.25, 0.7);
      const acr = E.el(s, "abs t sticker", ac, { left: "72px", top: "570px", fontSize: "250px", lineHeight: 1 });
      E.in(acr, t0 + 0.1, { from: "zoom", dur: 0.6, cue: "whoosh" });
      E.punch(t0 + 0.4, { amp: 12, flash: 0.2, vol: 0.7 });
      const nm = E.el(s, "abs p p-l", name, { left: "80px", top: "850px", color: "#17171c", fontWeight: 800 });
      E.in(nm, t0 + 0.45, { from: "up", dur: 0.5 });

      const card = E.el(s, "card abs", "", { left: "80px", right: "80px", top: "960px", padding: "36px 44px" });
      E.el(card, "lbl", "Fórmula");
      E.el(card, "", formula.replace(/([÷×])/g, `<span style="color:#ff5e5b">$1</span>`),
        { fontFamily: "Inter", fontWeight: 800, fontSize: "48px", marginTop: "10px", letterSpacing: "-.02em" });
      E.el(card, "", "", { height: "2px", background: "rgba(23,23,28,.12)", margin: "28px 0" });
      const row = E.el(card, "", "", { display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: "20px" });
      E.el(row, "p", calc, { fontSize: "36px" });
      const nv = E.el(row, "num g-green", "", { fontSize: "120px" });
      E.in(card, t0 + 0.6, { from: "up", dur: 0.6, cue: "swish" });
      E.counter(nv, t0 + 1.1, 1.0, 0, val, fmt);
      E.pulse(nv, t0 + 2.1, 1.15, 0.3);
      E.cue("ding", t0 + 2.1, 0.5);

      const qq = E.el(s, "abs", "", { left: "80px", right: "80px", top: "1420px", display: "flex", justifyContent: "center" });
      const ch = E.el(qq, "chip", `${E.icon("search", 36, "#17171c", 2.8).outerHTML}<span>${q}</span>`, { fontSize: "40px", padding: "18px 32px" });
      E.in(ch, t0 + 1.9, { from: "pop", dur: 0.5, cue: "pop" });
    });

    // 3 — resumo em painel
    const t3 = 3.3 + 5 * D;
    const s3 = E.scene(t3, t3 + 3.6);
    E.bgTo(t3 - 0.2, "sky");
    const tt = E.text(s3, "SEU *PAINEL*\nDE CONTROLE", "t t-m", { position: "absolute", top: "320px", left: "80px", right: "80px", textAlign: "center" });
    E.wordsIn(tt, t3 + 0.05);
    const grid = E.el(s3, "abs", "", { left: "80px", right: "80px", top: "620px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" });
    const cells = M.map(([ac, , , , val, fmt], i) => {
      const c = E.el(grid, "card", `<div class="lbl">${ac}</div><div class="num" style="font-size:96px;margin-top:8px">${fmt(val)}</div>`,
        { padding: "30px 36px", gridColumn: i === 4 ? "1 / span 2" : "auto" });
      return c;
    });
    E.in(cells, t3 + 0.35, { from: "flip", dur: 0.6, stagger: 0.12, cue: "whoosh" });
    for (let i = 0; i < 5; i++) E.cue("pop", t3 + 0.35 + i * 0.12, 0.5);
    tl.to(cells[4], { background: "#b8f35a", duration: 0.2 }, t3 + 1.5);
    E.pulse(cells[4], t3 + 1.5, 1.06, 0.3);
    E.cue("cash", t3 + 1.5, 0.8);
    const tip = E.el(s3, "abs p", "Começa pelo <b>CPA</b> e pelo <b>ROAS</b>: eles dizem se está dando lucro.", { left: "100px", right: "100px", top: "1440px", textAlign: "center", fontSize: "40px" });
    E.in(tip, t3 + 1.7, { from: "up" });

    E.cta(t3 + 3.6, t3 + 8.2, { next: "EP 03: ROAS 4 e mesmo assim prejuízo?" });
  },
};
