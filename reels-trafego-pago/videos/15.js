// EP 15 — Quanto vale um cliente? LTV x CAC (narrado, trilha funk)
window.VIDEO = {
  ep: 15,
  slug: "quanto-vale-um-cliente",
  title: "Quanto vale um cliente?",
  music: "funk",
  theme: { a1: "#ff7eb6", a2: "#ffd23f", bg: "pink" },
  narr: [
    { id: "a", text: "Você pagaria cem reais pra conquistar um cliente que compra um produto de oitenta?",
      cap: "Você pagaria R$ 100 pra conquistar um cliente que compra um produto de R$ 80?", gap: 0.5 },
    { id: "b", text: "Parece prejuízo. Mas depende de quanto esse cliente vale com o tempo." },
    { id: "c", text: "Isso é o éle tê vê: quanto um cliente deixa de lucro durante toda a relação com você.",
      cap: "Isso é o LTV: quanto um cliente deixa de lucro durante toda a relação com você.", gap: 0.4 },
    { id: "d", text: "Exemplo: ele volta e compra dez vezes em dois anos, e cada compra deixa trinta reais de lucro.",
      cap: "Exemplo: ele volta e compra 10 vezes em 2 anos, e cada compra deixa R$ 30 de lucro." },
    { id: "e", text: "Dez vezes trinta: trezentos reais de lucro.", cap: "10 × R$ 30: R$ 300 de lucro." },
    { id: "f", text: "Já o cac é quanto você gastou pra conquistar esse cliente. Aqui, cem reais.",
      cap: "Já o CAC é quanto você gastou pra conquistar esse cliente. Aqui, R$ 100.", gap: 0.4 },
    { id: "g", text: "Trezentos contra cem: três vezes o que você investiu. Uma proporção que muita gente usa como referência de saúde.",
      cap: "R$ 300 contra R$ 100: 3× o que você investiu. Uma proporção que muita gente usa como referência de saúde." },
    { id: "h", text: "Então, antes de cortar um anúncio que parece caro, pergunta: esse cliente volta?", gap: 0.4 },
    { id: "i", text: "Salva e calcula o valor do seu cliente.", gap: 0.5, nocap: true },
  ],
  build(E) {
    const { tl, N } = E;
    const brl = (v) => "R$ " + Math.round(v).toLocaleString("pt-BR");

    // 1 — a pergunta (balança)
    const s1 = E.scene(0, N.c.t - 0.1, { exit: "whip", dolly: 0.05 });
    E.letterbox(0, true, 1, 0.01);
    E.letterbox(N.a.t + N.a.d * 0.4, false);
    E.cue("braam", 0.05, 0.7);
    const t1 = E.text(s1, "PAGARIA *R$ 100*\nPOR UM CLIENTE?", "t t-m", { position: "absolute", top: "330px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t1, N.a.t + 0.2, { stagger: 0.08 });
    const bal = E.el(s1, "abs", "", { left: "90px", width: "900px", top: "620px", height: "560px" });
    E.el(bal, "abs", "", { left: "440px", top: "120px", width: "20px", height: "400px", background: "#17171c", borderRadius: "10px" });
    E.el(bal, "abs", "", { left: "330px", top: "500px", width: "240px", height: "40px", background: "#17171c", borderRadius: "14px" });
    const beam = E.el(bal, "abs", "", { left: "50px", top: "110px", width: "800px", height: "24px", background: "#17171c", borderRadius: "12px", transformOrigin: "50% 50%" });
    const pan = (x, lbl, col) => {
      const p = E.el(beam, "abs", "", { left: x + "px", top: "12px", width: "260px", height: "230px", display: "flex", flexDirection: "column", alignItems: "center" });
      E.el(p, "", "", { width: "6px", height: "90px", background: "#17171c" });
      E.el(p, "badge", lbl, { width: "260px", height: "120px", borderRadius: "28px", background: col, font: "900 50px 'Inter Display'" });
      return p;
    };
    const pl = pan(-60, "R$ 100", "#ff5e5b");
    const pr = pan(600, "R$ 80", "#b8f35a");
    E.in(bal, N.a.t + 0.5, { from: "up", cue: "whoosh" });
    tl.to(beam, { rotate: -10, duration: 0.8, ease: "elastic.out(1, 0.5)" }, N.a.t + N.a.d * 0.55);
    tl.to([pl, pr], { rotate: 10, duration: 0.8, ease: "elastic.out(1, 0.5)" }, N.a.t + N.a.d * 0.55);
    const pz = E.el(s1, "abs", "", { left: 0, right: 0, top: "1220px", textAlign: "center" });
    const pzc = E.el(pz, "t", `<span class="g-red">PREJUÍZO?</span>`, { fontSize: "80px" });
    E.in(pzc, N.b.t + 0.1, { from: "pop", cue: "error" });
    // "mas depende..." a balança vira
    tl.to(beam, { rotate: 12, duration: 1.0, ease: "elastic.out(1, 0.45)" }, N.b.t + N.b.d * 0.5);
    tl.to([pl, pr], { rotate: -12, duration: 1.0, ease: "elastic.out(1, 0.45)" }, N.b.t + N.b.d * 0.5);
    tl.to(pzc, { opacity: 0, scale: 0.6, duration: 0.25 }, N.b.t + N.b.d * 0.5);
    E.cue("whoosh", N.b.t + N.b.d * 0.5, 0.7);

    // 2 — LTV
    const s2 = E.scene(N.c.t - 0.1, N.d.t - 0.1, { enter: "whip", exit: "whip", dolly: 0.06 });
    E.bgTo(N.c.t - 0.2, "yellow");
    const c2 = E.el(s2, "center", "", { bottom: "560px" });
    const ltv = E.el(c2, "t sticker", "LTV", { fontSize: "300px", lineHeight: 1, WebkitTextStroke: "14px #17171c", color: "#ff7eb6" });
    tl.fromTo(ltv, { scale: 2.6, opacity: 0, rotate: 12 }, { scale: 1, opacity: 1, rotate: -4, duration: 0.55, ease: "expo.out" }, N.c.t + 0.1);
    E.punch(N.c.t + 0.3, { amp: 18, flash: 0.3, cue: "boom" });
    const def = E.el(c2, "card", "", { marginTop: "50px", padding: "30px 40px", maxWidth: "880px" });
    def.innerHTML = `<div class="lbl">Lifetime value</div><div style="font:800 44px/1.2 Inter;margin-top:10px">Quanto de <span class="g-yellow" style="padding:0 .15em">lucro</span> um cliente deixa durante toda a relação com você</div>`;
    E.in(def, N.c.t + N.c.d * 0.35, { from: "up", cue: "swish" });

    // 3 — 10 compras x R$ 30
    const s3 = E.scene(N.d.t - 0.1, N.f.t - 0.1, { exit: "whip" });
    E.bgTo(N.d.t - 0.2, "teal");
    const k3 = E.el(s3, "abs", `<div class="kicker"><span class="dot"></span>2 anos de cliente</div>`, { left: 0, right: 0, top: "330px", textAlign: "center" });
    E.in(k3, N.d.t, { from: "pop" });
    const grid = E.el(s3, "abs", "", { left: "80px", right: "80px", top: "460px", display: "grid", gridTemplateColumns: "repeat(5,1fr)", gap: "22px" });
    const coins = Array.from({ length: 10 }, (_, i) => {
      const c = E.el(grid, "card", "", { padding: "18px 0", textAlign: "center", borderRadius: "26px", boxShadow: "7px 7px 0 #17171c" });
      const b = E.el(c, "badge", "", { width: "90px", height: "90px", borderRadius: "50%", background: "#ffd23f", boxShadow: "none", borderWidth: "4px" });
      b.appendChild(E.icon("coin", 54));
      E.el(c, "", "+R$ 30", { font: "900 30px 'Inter Display'", marginTop: "10px" });
      return c;
    });
    const sumBox = E.el(s3, "abs", "", { left: 0, right: 0, top: "960px", textAlign: "center" });
    E.el(sumBox, "lbl", "Lucro total do cliente", { color: "#17171c" });
    const sum = E.el(sumBox, "t", "", { fontSize: "170px", marginTop: "10px" });
    sum.innerHTML = `<span class="g-green">R$ 0</span>`;
    const sumIn = sum.firstChild;
    const ct0 = N.d.t + N.d.d * 0.35, cd = N.d.end - ct0 + N.e.d * 0.4;
    coins.forEach((c, i) => {
      const t = ct0 + (i / 10) * cd;
      tl.fromTo(c, { scale: 0, rotate: -20 }, { scale: 1, rotate: 0, duration: 0.35, ease: "back.out(2.4)" }, t);
      E.cue("pop", t, 0.45);
      tl.set(sumIn, { textContent: brl((i + 1) * 30) }, t + 0.1);
    });
    E.in(sumBox, ct0 - 0.2, { from: "fade" });
    E.punch(ct0 + cd + 0.15, { amp: 18, flash: 0.35, cue: "cash" });
    E.pulse(sum, ct0 + cd + 0.15, 1.15, 0.35);

    // 4 — CAC x LTV
    const s4 = E.scene(N.f.t - 0.1, N.h.t - 0.1, { exit: "whip", dolly: 0.04 });
    E.bgTo(N.f.t - 0.2, "cream");
    const t4 = E.text(s4, "*CAC* × LTV", "t t-l", { position: "absolute", top: "320px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t4, N.f.t + 0.1);
    const base = 1180;
    const barCol = (x, v, lbl, col, t, sub) => {
      const h = v * 1.9;
      const b = E.el(s4, "abs", "", { left: x + "px", top: base - h + "px", width: "300px", height: h + "px", background: col, border: "6px solid #17171c",
        borderBottom: "none", borderRadius: "30px 30px 0 0", transformOrigin: "bottom" });
      const l = E.el(s4, "abs", `<div style="font:900 64px 'Inter Display'">${brl(v)}</div><div style="font:800 30px Inter;opacity:.75">${sub}</div>`,
        { left: x + "px", width: "300px", top: base - h - 130 + "px", textAlign: "center" });
      const n = E.el(s4, "abs t", lbl, { left: x + "px", width: "300px", top: base + 20 + "px", textAlign: "center", fontSize: "60px" });
      tl.fromTo(b, { scaleY: 0 }, { scaleY: 1, duration: 0.7, ease: "back.out(1.4)" }, t);
      E.in([l, n], t + 0.3, { from: "pop", dur: 0.4, cue: "pop" });
    };
    barCol(160, 100, "CAC", "#ff5e5b", N.f.t + N.f.d * 0.75, "pra conquistar");
    barCol(620, 300, "LTV", "#b8f35a", N.g.t + 0.1, "de lucro");
    E.el(s4, "abs", "", { left: "80px", right: "80px", top: base + "px", height: "8px", background: "#17171c", borderRadius: "8px" });
    const ratio = E.el(s4, "abs t sticker", "3×", { left: "200px", top: "650px", fontSize: "200px", lineHeight: 1, WebkitTextStroke: "12px #17171c", color: "#ffd23f" });
    tl.fromTo(ratio, { scale: 0, rotate: -30 }, { scale: 1, rotate: -8, duration: 0.5, ease: "back.out(2.5)" }, N.g.t + N.g.d * 0.3);
    E.punch(N.g.t + N.g.d * 0.3, { amp: 20, flash: 0.35, cue: "boom" });
    E.cue("cash", N.g.t + N.g.d * 0.3 + 0.1, 0.7);

    // 5 — esse cliente volta?
    const s5 = E.scene(N.h.t - 0.1, N.i.t - 0.15, { exit: "whip", dolly: 0.08 });
    E.bgTo(N.h.t - 0.2, "orange");
    const c5 = E.el(s5, "center", "", { bottom: "560px" });
    const rp = E.el(c5, "badge", "", { width: "230px", height: "230px", borderRadius: "60px", background: "#fff", marginBottom: "60px" });
    rp.appendChild(E.icon("repeat", 140, "#17171c", 2.6));
    tl.fromTo(rp, { rotate: -180, scale: 0 }, { rotate: 0, scale: 1, duration: 0.7, ease: "back.out(1.6)" }, N.h.t + 0.1);
    tl.to(rp.firstChild, { rotate: 360, duration: 2.5, ease: "none" }, N.h.t + 0.8);
    const t5 = E.text(c5, "ESSE CLIENTE\n[g-white:VOLTA]?", "t t-xl");
    E.wordsIn(t5, N.h.t + N.h.d * 0.6, { stagger: 0.1 });
    E.punch(N.h.t + N.h.d * 0.75, { amp: 16, flash: 0.3 });

    E.bgTo(N.i.t - 0.3, "pink");
    E.cta(N.i.t - 0.15, N.i.end + 2.2, { text: "SALVA E\n*CALCULA O SEU*", next: "Segue pra mais episódios" });
  },
};
