// EP 11 — Quanto investir por dia? (narrado, trilha épica)
window.VIDEO = {
  ep: 11,
  slug: "quanto-investir-por-dia",
  title: "Quanto investir por dia?",
  music: "epico",
  theme: { a1: "#ff5e5b", a2: "#ffd23f", bg: "yellow" },
  narr: [
    { id: "a", text: "Quanto você precisa investir por dia em anúncio?", gap: 0.5 },
    { id: "b", text: "A resposta não é um número mágico. É uma conta." },
    { id: "c", text: "O algoritmo da Meta precisa de umas cinquenta conversões por semana pra sair da fase de aprendizado.",
      cap: "O algoritmo da Meta precisa de umas 50 conversões por semana pra sair da fase de aprendizado." },
    { id: "d", text: "Então pega o seu custo por venda. Vamos supor: trinta reais.", cap: "Então pega o seu custo por venda. Vamos supor: R$ 30." },
    { id: "e", text: "Trinta reais vezes cinquenta vendas: mil e quinhentos reais por semana.", cap: "R$ 30 × 50 vendas: R$ 1.500 por semana." },
    { id: "f", text: "Dividido por sete dias, dá uns duzentos e quinze reais por dia.", cap: "Dividido por 7 dias, dá uns R$ 215 por dia." },
    { id: "g", text: "Não tem esse orçamento? Otimiza pra um evento mais barato, como adicionar ao carrinho, até ganhar volume.", gap: 0.5 },
    { id: "h", text: "Orçamento pequeno demais deixa o algoritmo sem dados. E sem dados, ele chuta." },
    { id: "i", text: "Salva esse vídeo e faz a sua conta.", gap: 0.5, nocap: true },
  ],
  build(E) {
    const { tl, N } = E;
    const brl = (v) => "R$ " + Math.round(v).toLocaleString("pt-BR");

    // 1 — abertura de cinema
    const s1 = E.scene(0, N.b.t - 0.1, { dolly: 0.08 });
    E.letterbox(0, true, 1, 0.01);
    E.letterbox(N.a.end - 0.2, false);
    E.cue("braam", 0.05, 1);
    const c1 = E.el(s1, "center", "", { bottom: "560px" });
    const t1 = E.text(c1, "QUANTO\nINVESTIR\nPOR [g-white:DIA]?", "t t-xl");
    E.wordsIn(t1, N.a.t, { stagger: 0.12, from: "up" });
    E.punch(N.a.t + 0.9, { amp: 14, flash: 0.25, cue: "boom" });
    const r = E.rng(3);
    for (let i = 0; i < 9; i++) {
      const co = E.el(s1, "abs badge", "", { left: 90 + i * 100 + "px", top: "-160px", width: "96px", height: "96px", borderRadius: "50%", background: "#ffd23f" });
      co.appendChild(E.icon("coin", 58));
      const t = N.a.t + 0.6 + r() * 1.2;
      tl.fromTo(co, { y: 0, rotate: 0 }, { y: 1300 + r() * 200, rotate: 360 * (r() > 0.5 ? 1 : -1), duration: 1.4, ease: "bounce.out", immediateRender: false }, t);
    }

    // 2 — não é mágica, é conta
    const s2 = E.scene(N.b.t - 0.1, N.c.t - 0.1, { enter: "whip", exit: "whip", dolly: 0.05 });
    E.bgTo(N.b.t - 0.2, "coral");
    const c2 = E.el(s2, "center", "", { bottom: "560px" });
    const t2a = E.text(c2, "NÃO É [mute:MÁGICA].", "t t-l");
    E.wordsIn(t2a, N.b.t + 0.05, { stagger: 0.08 });
    const t2b = E.text(c2, "É [g-white:CONTA].", "t t-xxl", { marginTop: "40px" });
    E.wordsIn(t2b, N.b.t + N.b.d * 0.55, { from: "pop", stagger: 0.1 });
    E.punch(N.b.t + N.b.d * 0.6, { amp: 16, flash: 0.3 });

    // 3 — 50 conversões pra sair do aprendizado
    const s3 = E.scene(N.c.t - 0.1, N.d.t - 0.1, { exit: "whip" });
    E.bgTo(N.c.t - 0.2, "sky");
    const k3 = E.el(s3, "abs", `<div class="kicker"><span class="dot"></span>Fase de aprendizado</div>`, { left: 0, right: 0, top: "330px", textAlign: "center" });
    E.in(k3, N.c.t, { from: "pop", cue: "pop" });
    const card = E.el(s3, "card abs", "", { left: "80px", right: "80px", top: "450px", padding: "40px" });
    const grid = E.el(card, "", "", { display: "grid", gridTemplateColumns: "repeat(10, 1fr)", gap: "14px" });
    const dots = Array.from({ length: 50 }, () => E.el(grid, "", "", { aspectRatio: "1", borderRadius: "50%", border: "4px solid #17171c", background: "#fff" }));
    E.in(card, N.c.t + 0.1, { from: "up", cue: "whoosh" });
    const fillT = N.c.t + 0.5, fillD = Math.max(1.5, N.c.d - 1.2);
    dots.forEach((d, i) => {
      const t = fillT + (i / 50) * fillD;
      tl.to(d, { background: "#b8f35a", scale: 1.15, duration: 0.08 }, t);
      tl.to(d, { scale: 1, duration: 0.1 }, t + 0.08);
      if (i % 5 === 0) E.cue("tick", t, 0.4);
    });
    const lbl = E.el(card, "", "", { display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginTop: "30px" });
    E.el(lbl, "lbl", "Conversões na semana");
    const cnt = E.el(lbl, "num", "0", { fontSize: "96px" });
    E.counter(cnt, fillT, fillD, 0, 50, (v) => Math.round(v), { cue: false });
    const st = E.el(s3, "abs", "", { left: 0, right: 0, top: "1110px", textAlign: "center" });
    const stc = E.el(st, "chip", `${E.icon("check", 40, "#1a9e55", 3.4).outerHTML}<span>Aprendizado concluído</span>`, { fontSize: "40px", background: "#b8f35a" });
    E.in(stc, fillT + fillD + 0.1, { from: "pop", cue: "ding" });

    // 4 — a conta
    const s4 = E.scene(N.d.t - 0.1, N.g.t - 0.1, { exit: "whip", dolly: 0.04 });
    E.bgTo(N.d.t - 0.2, "teal");
    const t4 = E.text(s4, "A *CONTA*", "t t-l", { position: "absolute", top: "320px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t4, N.d.t);
    const calc = E.el(s4, "card abs", "", { left: "80px", right: "80px", top: "520px", padding: "20px 48px 36px" });
    const row = (lb, op) => {
      const r = E.el(calc, "", "", { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "26px 0", borderBottom: "4px dashed rgba(23,23,28,.15)" });
      E.el(r, "p", `<b style="color:#ff5e5b">${op}</b> ${lb}`, { fontSize: "42px", color: "#17171c", fontWeight: 800 });
      const n = E.el(r, "num", "", { fontSize: "72px" });
      return { r, n };
    };
    const r1 = row("Custo por venda", "");
    const r2 = row("50 vendas na semana", "×");
    const r3 = row("7 dias", "÷");
    r3.r.style.borderBottom = "none";
    E.in(calc, N.d.t + 0.2, { from: "up", cue: "swish" });
    E.in(r1.r, N.d.t + N.d.d * 0.6, { from: "left" });
    E.counter(r1.n, N.d.t + N.d.d * 0.65, 0.6, 0, 30, brl);
    E.in(r2.r, N.e.t, { from: "left", cue: "whoosh" });
    E.counter(r2.n, N.e.t + N.e.d * 0.5, 0.9, 0, 1500, brl);
    E.in(r3.r, N.f.t, { from: "left", cue: "whoosh" });
    const tot = E.el(s4, "abs", "", { left: 0, right: 0, top: "1050px", textAlign: "center" });
    const tv = E.el(tot, "t g-green", "", { display: "inline-block", fontSize: "150px" });
    const per = E.el(tot, "p", "por dia", { fontSize: "48px", color: "#17171c", fontWeight: 800, marginTop: "10px" });
    E.in(tot, N.f.t + N.f.d * 0.45, { from: "zoom", dur: 0.5 });
    E.counter(tv, N.f.t + N.f.d * 0.45, 0.8, 0, 215, brl);
    E.punch(N.f.t + N.f.d * 0.45 + 0.8, { amp: 18, flash: 0.35, cue: "cash" });

    // 5 — orçamento menor: evento mais barato
    const s5 = E.scene(N.g.t - 0.1, N.h.t - 0.1, { exit: "whip" });
    E.bgTo(N.g.t - 0.2, "orange");
    const t5 = E.text(s5, "POUCA VERBA?\nSOBE MENOS NO *FUNIL*", "t t-m", { position: "absolute", top: "320px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t5, N.g.t);
    const evs = [["Compra", "cart", "mais caro", "#ff5e5b"], ["Adicionar ao carrinho", "cart", "intermediário", "#ffd23f"], ["Ver conteúdo", "eye", "mais barato", "#b8f35a"]];
    const evEls = evs.map(([n, ic, tag, c], i) => {
      const e = E.el(s5, "card abs", "", { left: "80px", right: "80px", top: 610 + i * 200 + "px", padding: "26px 36px", display: "flex", alignItems: "center", gap: "26px" });
      const b = E.el(e, "badge", "", { flex: "none", width: "96px", height: "96px", borderRadius: "28px", background: c });
      b.appendChild(E.icon(ic, 54));
      E.el(e, "", `<div style="font:900 46px 'Inter Display'">${n}</div><div class="p" style="font-size:32px">${tag}</div>`);
      E.in(e, N.g.t + 0.4 + i * 0.15, { from: "right", cue: i ? false : "whoosh" });
      return e;
    });
    tl.to(evEls[0], { opacity: 0.45, scale: 0.95, duration: 0.3 }, N.g.t + N.g.d * 0.5);
    tl.to(evEls[1], { background: "#fff6b0", scale: 1.05, duration: 0.3, ease: "back.out(2)" }, N.g.t + N.g.d * 0.5);
    E.cue("pop", N.g.t + N.g.d * 0.5, 0.8);
    const pick = E.el(evEls[1], "abs chip", "ESCOLHA ESSE", { right: "-20px", top: "-34px", fontSize: "28px", background: "#17171c", color: "#fff", padding: "8px 18px" });
    E.in(pick, N.g.t + N.g.d * 0.55, { from: "pop" });

    // 6 — sem dados, ele chuta
    const s6 = E.scene(N.h.t - 0.1, N.i.t - 0.15, { exit: "whip", dolly: 0.08 });
    E.bgTo(N.h.t - 0.2, "pink");
    const c6 = E.el(s6, "center", "", { bottom: "560px" });
    const dice = E.el(c6, "badge", "", { width: "220px", height: "220px", borderRadius: "56px", background: "#fff", marginBottom: "60px" });
    dice.innerHTML = `<svg viewBox="0 0 100 100" width="150" height="150">${[[25, 25], [75, 25], [50, 50], [25, 75], [75, 75]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="10" fill="#17171c"/>`).join("")}</svg>`;
    tl.fromTo(dice, { rotate: -540, y: -500, scale: 0.4 }, { rotate: 0, y: 0, scale: 1, duration: 1.0, ease: "bounce.out" }, N.h.t);
    E.cue("whoosh", N.h.t, 0.7);
    const t6 = E.text(c6, "SEM DADOS,\nELE [g-red:CHUTA].", "t t-l");
    E.wordsIn(t6, N.h.t + N.h.d * 0.5, { stagger: 0.09 });
    E.punch(N.h.t + N.h.d * 0.75, { amp: 16, flash: 0.25 });

    E.bgTo(N.i.t - 0.3, "yellow");
    E.cta(N.i.t - 0.15, N.i.end + 2.2, { text: "SALVA E FAZ\nA *SUA CONTA*", next: "EP 12: teste A/B do jeito certo" });
  },
};
