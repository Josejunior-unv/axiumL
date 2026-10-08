// EP 14 — Dobre as vendas sem gastar mais: a página de destino (narrado, trilha house)
window.VIDEO = {
  ep: 14,
  slug: "landing-page-que-converte",
  title: "Dobre as vendas sem gastar mais",
  music: "house",
  theme: { a1: "#00c2a8", a2: "#ffd23f", bg: "green" },
  narr: [
    { id: "a", text: "E se desse pra dobrar as vendas sem gastar um real a mais em anúncio?", gap: 0.5 },
    { id: "b", text: "Olha a conta. Mil cliques na sua página. Um por cento compra. Dez vendas.",
      cap: "Olha a conta. 1.000 cliques na sua página. 1% compra. 10 vendas.", gap: 0.4 },
    { id: "c", text: "Agora melhora a página, e a conversão vai pra dois por cento. Os mesmos mil cliques viram vinte vendas.",
      cap: "Agora melhora a página, e a conversão vai pra 2%. Os mesmos 1.000 cliques viram 20 vendas." },
    { id: "d", text: "Mesmo investimento, o dobro de vendas. O custo por venda cai pela metade." },
    { id: "e", text: "O que mais pesa numa página que converte?", gap: 0.5 },
    { id: "f", text: "Uma promessa clara, logo no topo." },
    { id: "g", text: "Prova: depoimentos, números, fotos reais." },
    { id: "h", text: "Um botão só, sem distração." },
    { id: "i", text: "Carregar rápido no celular." },
    { id: "j", text: "E a mesma promessa do anúncio. Quem clicou numa coisa tem que encontrar ela na página." },
    { id: "k", text: "Salva e revisa a sua página hoje.", gap: 0.5, nocap: true },
  ],
  build(E) {
    const { tl, N } = E;

    // 1 — abertura
    const s1 = E.scene(0, N.b.t - 0.1, { exit: "whip", dolly: 0.08 });
    E.letterbox(0, true, 1, 0.01);
    E.letterbox(N.a.t + N.a.d * 0.5, false);
    E.cue("braam", 0.05, 0.7);
    const c1 = E.el(s1, "center", "", { bottom: "560px" });
    const two = E.el(c1, "t sticker", "2×", { fontSize: "380px", lineHeight: 1, WebkitTextStroke: "14px #17171c", color: "#b8f35a" });
    tl.fromTo(two, { scale: 3, opacity: 0, rotate: -20 }, { scale: 1, opacity: 1, rotate: -6, duration: 0.6, ease: "expo.out" }, N.a.t + 0.2);
    E.punch(N.a.t + 0.45, { amp: 22, flash: 0.35, cue: "boom" });
    const t1 = E.text(c1, "VENDAS", "t t-xl");
    E.wordsIn(t1, N.a.t + 0.5);
    const z = E.el(c1, "chip", `${E.icon("wallet", 40).outerHTML}<span><b>R$ 0</b> a mais em anúncio</span>`, { marginTop: "40px", fontSize: "40px" });
    E.in(z, N.a.t + N.a.d * 0.6, { from: "up", cue: "pop" });

    // 2 — a conta: 1% x 2%
    const s2 = E.scene(N.b.t - 0.1, N.e.t - 0.1, { enter: "whip", exit: "whip" });
    E.bgTo(N.b.t - 0.2, "cream");
    const mk = (y, lbl, pct, sales, col, t0, d) => {
      const c = E.el(s2, "card abs", "", { left: "80px", right: "80px", top: y + "px", padding: "30px 40px" });
      const hd = E.el(c, "", "", { display: "flex", justifyContent: "space-between", alignItems: "center" });
      E.el(hd, "t", `<span class="g-white" style="background:${col}">${lbl}</span>`, { fontSize: "54px" });
      E.el(hd, "chip", `conversão <b>${pct}</b>`, { fontSize: "32px", padding: "8px 18px" });
      const rows = E.el(c, "", "", { display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: "26px" });
      const clk = E.el(rows, "", "", { textAlign: "left" });
      E.el(clk, "lbl", "Cliques");
      const cn = E.el(clk, "num", "0", { fontSize: "80px" });
      E.el(rows, "", E.icon("play", 60, "#17171c", 2.4, "#17171c").outerHTML);
      const sv = E.el(rows, "", "", { textAlign: "right" });
      E.el(sv, "lbl", "Vendas");
      const vn = E.el(sv, "num", "0", { fontSize: "110px", color: col === "#ff5e5b" ? "#17171c" : "#1a9e55" });
      E.in(c, t0, { from: "left", cue: "whoosh" });
      E.counter(cn, t0 + d * 0.2, 0.7, 0, 1000, (v) => Math.round(v).toLocaleString("pt-BR"));
      E.counter(vn, t0 + d * 0.75, 0.5, 0, sales, (v) => Math.round(v), { cue: false });
      E.cue(sales > 10 ? "cash" : "ding", t0 + d * 0.75 + 0.5, 0.8);
      return c;
    };
    const k2 = E.el(s2, "abs", `<div class="kicker"><span class="dot"></span>Mesmo investimento</div>`, { left: 0, right: 0, top: "320px", textAlign: "center" });
    E.in(k2, N.b.t, { from: "pop" });
    const ca = mk(440, "ANTES", "1%", 10, "#ff5e5b", N.b.t + 0.2, N.b.d);
    const cb = mk(840, "DEPOIS", "2%", 20, "#b8f35a", N.c.t + 0.1, N.c.d);
    tl.to(ca, { opacity: 0.5, scale: 0.96, duration: 0.3 }, N.c.t + 0.2);
    // custo por venda pela metade
    const half = E.el(s2, "abs", "", { left: 0, right: 0, top: "1225px", textAlign: "center" });
    const hc = E.el(half, "t", `<span class="g-green">CUSTO POR VENDA ÷ 2</span>`, { fontSize: "64px" });
    E.in(hc, N.d.t + N.d.d * 0.45, { from: "pop" });
    E.punch(N.d.t + N.d.d * 0.45, { amp: 18, flash: 0.3, cue: "boom" });
    E.bgTo(N.d.t, "green");

    // 3 — anatomia da página (celular + checklist)
    const s3 = E.scene(N.e.t - 0.1, N.k.t - 0.15, { exit: "whip" });
    E.bgTo(N.e.t - 0.2, "sky");
    const t3 = E.text(s3, "PÁGINA QUE *CONVERTE*", "t t-m", { position: "absolute", top: "320px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t3, N.e.t + 0.1);
    const ph = E.el(s3, "abs", "", { left: "70px", top: "470px", width: "430px", height: "840px", borderRadius: "60px", padding: "14px", background: "#17171c" });
    const scr = E.el(ph, "", "", { position: "relative", width: "100%", height: "100%", borderRadius: "48px", background: "#fff", overflow: "hidden" });
    E.in(ph, N.e.t + 0.3, { from: "left", cue: "whoosh" });
    // seções da página
    const speed = E.el(scr, "abs", "", { left: 0, right: 0, top: 0, height: "56px", background: "#f1f1f3", borderBottom: "3px solid #17171c" });
    const spBar = E.el(speed, "abs", "", { left: 0, top: 0, bottom: 0, width: "100%", background: "#b8f35a", transformOrigin: "left", transform: "scaleX(0)" });
    const head = E.el(scr, "abs", `<div style="font:900 40px/1.05 'Inter Display';text-transform:uppercase">Clareie os dentes em 1 sessão</div><div style="font:600 22px Inter;margin-top:8px;opacity:.7">Resultado no mesmo dia</div>`,
      { left: "26px", right: "26px", top: "84px", padding: "18px", borderRadius: "18px", border: "4px dashed transparent" });
    const proof = E.el(scr, "abs", "", { left: "26px", right: "26px", top: "300px", height: "200px", borderRadius: "18px", border: "4px dashed transparent", padding: "14px" });
    proof.innerHTML = `<div style="display:flex;gap:4px">${Array(5).fill(E.icon("star", 36, "#17171c", 2.2, "#ffd23f").outerHTML).join("")}</div>
      <div style="display:flex;gap:10px;margin-top:14px">${[0, 1, 2].map(() => `<div style="flex:1;height:96px;border-radius:12px;background:#e4e4e7;border:3px solid #17171c"></div>`).join("")}</div>`;
    const btn = E.el(scr, "abs", "QUERO AGENDAR", { left: "26px", right: "26px", top: "560px", height: "100px", borderRadius: "22px", background: "#ff5e5b", color: "#fff",
      border: "5px solid #17171c", boxShadow: "6px 6px 0 #17171c", font: "900 34px/90px 'Inter Display'", textAlign: "center" });
    const items = [
      ["f", "Promessa clara no topo", head, "target"],
      ["g", "Prova social", proof, "star"],
      ["h", "Um botão só", btn, "cursor"],
      ["i", "Rápida no celular", speed, "bolt"],
      ["j", "Mesma promessa do anúncio", head, "repeat"],
    ];
    const list = E.el(s3, "abs", "", { left: "540px", right: "60px", top: "480px", display: "flex", flexDirection: "column", gap: "18px" });
    items.forEach(([id, lb, node, ic], i) => {
      const it = E.el(list, "card", "", { padding: "18px 20px", display: "flex", alignItems: "center", gap: "16px", borderRadius: "24px", boxShadow: "8px 8px 0 #17171c" });
      const b = E.el(it, "badge", "", { flex: "none", width: "70px", height: "70px", borderRadius: "20px", background: "#ffd23f", boxShadow: "4px 4px 0 #17171c", borderWidth: "4px" });
      b.appendChild(E.icon(ic, 40));
      E.el(it, "", lb, { font: "800 30px/1.15 Inter" });
      const t = N[id].t + 0.05;
      E.in(it, t, { from: "right", dur: 0.5, cue: "whoosh", vol: 0.5 });
      tl.to(b, { background: "#b8f35a", duration: 0.2 }, t + 0.4);
      E.cue("ding", t + 0.4, 0.4);
      if (node !== speed) {
        tl.to(node, { borderColor: "#ff5e5b", duration: 0.15 }, t);
        tl.to(node, { borderColor: "transparent", duration: 0.2 }, N[id].end + 0.1);
      }
      E.pulse(node, t + 0.1, 1.05, 0.3);
    });
    tl.to(spBar, { scaleX: 1, duration: 0.6, ease: "power2.out" }, N.i.t + 0.2);
    E.cue("riser", N.i.t, 0.3);
    // anúncio voando para dentro do topo da página
    const ad = E.el(s3, "abs card", `<div style="font:800 20px Inter;opacity:.6">Patrocinado</div><div style="font:900 30px/1.05 'Inter Display';text-transform:uppercase;margin-top:6px">Clareie os dentes em 1 sessão</div>`,
      { left: "560px", top: "1135px", width: "420px", padding: "18px 22px", borderRadius: "24px", background: "#ffd23f" });
    tl.set(ad, { opacity: 0 }, 0);
    E.in(ad, N.j.t + 0.1, { from: "up", cue: "pop" });
    tl.to(ad, { left: 110, top: 560, scale: 0.85, opacity: 0, duration: 0.7, ease: "power2.in" }, N.j.t + N.j.d * 0.45);
    E.cue("whoosh", N.j.t + N.j.d * 0.45, 0.7);
    E.punch(N.j.t + N.j.d * 0.45 + 0.7, { amp: 10, flash: 0.2, cue: "ding" });

    E.bgTo(N.k.t - 0.3, "green");
    E.cta(N.k.t - 0.15, N.k.end + 2.2, { text: "SALVA E\n*REVISA HOJE*", next: "EP 15: quanto vale um cliente?" });
  },
};
