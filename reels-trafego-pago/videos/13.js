// EP 13 — Como escalar sem quebrar a campanha (narrado, trilha trap)
window.VIDEO = {
  ep: 13,
  slug: "escalar-sem-quebrar",
  title: "Como escalar sem quebrar a campanha",
  music: "trap",
  theme: { a1: "#ff8a3d", a2: "#ffd23f", bg: "orange" },
  narr: [
    { id: "a", text: "Sua campanha tá vendendo. E agora, como escalar sem estragar tudo?", gap: 0.5 },
    { id: "b", text: "Existem dois caminhos: escala vertical e escala horizontal." },
    { id: "c", text: "Vertical é aumentar o orçamento do que já funciona. Mas aos poucos: algo como vinte por cento a cada dois ou três dias.",
      cap: "Vertical é aumentar o orçamento do que já funciona. Mas aos poucos: algo como 20% a cada 2 ou 3 dias.", gap: 0.4 },
    { id: "d", text: "Exemplo: cem reais por dia vira cento e vinte. Depois, cento e quarenta e quatro. Sem susto pro algoritmo.",
      cap: "Exemplo: R$ 100 por dia vira R$ 120. Depois, R$ 144. Sem susto pro algoritmo." },
    { id: "e", text: "Dobrar tudo de uma vez pode jogar a campanha de volta pro aprendizado. E o custo sobe." },
    { id: "f", text: "Horizontal é multiplicar: novos criativos, novos públicos, novas ofertas. Em vez de só colocar mais dinheiro no mesmo lugar.", gap: 0.4 },
    { id: "g", text: "O caminho mais seguro? Os dois juntos, de olho no custo por venda todo dia." },
    { id: "h", text: "Salva e manda pra quem quer escalar.", gap: 0.5, nocap: true },
  ],
  build(E) {
    const { tl, N } = E;
    const brl = (v) => "R$ " + Math.round(v).toLocaleString("pt-BR");

    // 1 — abertura
    const s1 = E.scene(0, N.b.t - 0.1, { exit: "whip", dolly: 0.07 });
    E.letterbox(0, true, 1, 0.01);
    E.letterbox(N.a.t + N.a.d * 0.55, false);
    E.cue("braam", 0.05, 0.8);
    const ch = E.el(s1, "card abs", "", { left: "80px", right: "80px", top: "340px", height: "420px", padding: "30px" });
    ch.innerHTML = `<svg width="100%" height="100%" viewBox="0 0 820 360"><path d="M0 350 H820" stroke="#17171c" stroke-width="5"/>
      <path class="up" d="M10 320 L180 280 L320 250 L470 170 L620 120 L800 30" fill="none" stroke="#2bc46b" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
    E.in(ch, N.a.t, { from: "up", cue: "whoosh" });
    E.draw(ch.querySelector(".up"), N.a.t + 0.2, 1.2, { ease: "power2.in" });
    E.cue("riser", N.a.t + 0.1, 0.6);
    const t1 = E.text(s1, "ESCALAR SEM\n[g-red:QUEBRAR]", "t t-l", { position: "absolute", top: "830px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t1, N.a.t + N.a.d * 0.5, { stagger: 0.1 });
    E.punch(N.a.t + N.a.d * 0.6, { amp: 18, flash: 0.3, cue: "boom" });
    E.glitch(t1.words[2], N.a.t + N.a.d * 0.65);

    // 2 — dois caminhos (tela dividida)
    const s2 = E.scene(N.b.t - 0.1, N.c.t - 0.1, { enter: "whip", exit: "whip" });
    const top = E.el(s2, "abs", "", { left: 0, right: 0, top: 0, height: "960px", background: "#3da5ff", borderBottom: "8px solid #17171c",
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "flex-end", paddingBottom: "70px" });
    const bot = E.el(s2, "abs", "", { left: 0, right: 0, top: "960px", height: "960px", background: "#ffd23f",
      display: "flex", flexDirection: "column", alignItems: "center", paddingTop: "70px" });
    const upA = E.icon("trend", 200, "#17171c", 2.6); top.appendChild(upA);
    E.el(top, "t sticker", "VERTICAL", { fontSize: "130px" });
    E.el(bot, "t sticker", "HORIZONTAL", { fontSize: "120px" });
    const row = E.el(bot, "", "", { display: "flex", gap: "30px", marginTop: "24px" });
    for (let i = 0; i < 3; i++) { const b = E.el(row, "badge", "", { width: "110px", height: "110px", background: "#fff" }); b.appendChild(E.icon("users", 60)); }
    tl.fromTo(top, { yPercent: -100 }, { yPercent: 0, duration: 0.5, ease: "expo.out" }, N.b.t);
    tl.fromTo(bot, { yPercent: 100 }, { yPercent: 0, duration: 0.5, ease: "expo.out" }, N.b.t + N.b.d * 0.45);
    E.cue("whoosh", N.b.t); E.cue("whoosh", N.b.t + N.b.d * 0.45);
    E.in(row.children, N.b.t + N.b.d * 0.6, { from: "pop", stagger: 0.1, cue: "pop" });
    E.punch(N.b.t + 0.3, { amp: 12, flash: 0.2, cue: "hit", vol: 0.6 });

    // 3 — vertical em degraus de 20%
    const s3 = E.scene(N.c.t - 0.1, N.f.t - 0.1, { exit: "whip" });
    E.bgTo(N.c.t - 0.2, "sky");
    const t3 = E.text(s3, "VERTICAL: *+20%*\nA CADA 2–3 DIAS", "t t-m", { position: "absolute", top: "320px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t3, N.c.t + 0.15, { stagger: 0.07 });
    const base = 1250;
    const steps = [[100, N.d.t + N.d.d * 0.1], [120, N.d.t + N.d.d * 0.35], [144, N.d.t + N.d.d * 0.6]];
    steps.forEach(([v, t], i) => {
      const h = v * 3.2;
      const b = E.el(s3, "abs", "", { left: 110 + i * 230 + "px", top: base - h + "px", width: "190px", height: h + "px", borderRadius: "22px 22px 0 0",
        background: "#b8f35a", border: "5px solid #17171c", borderBottom: "none", transformOrigin: "bottom" });
      const lb = E.el(s3, "abs num", brl(v), { left: 110 + i * 230 + "px", width: "190px", top: base - h - 80 + "px", textAlign: "center", fontSize: "52px" });
      tl.fromTo(b, { scaleY: 0 }, { scaleY: 1, duration: 0.5, ease: "back.out(1.6)" }, t);
      E.in(lb, t + 0.2, { from: "pop", dur: 0.4, cue: "pop" });
      if (i) {
        const plus = E.el(s3, "abs chip", "+20%", { left: 110 + i * 230 - 40 + "px", top: base - h - 170 + "px", fontSize: "30px", padding: "6px 16px", background: "#ffd23f" });
        E.in(plus, t + 0.3, { from: "pop", dur: 0.4 });
      }
    });
    E.el(s3, "abs", "", { left: "80px", right: "80px", top: base + "px", height: "8px", background: "#17171c", borderRadius: "8px" });
    // dobrar de uma vez: barra vermelha estoura
    const big = E.el(s3, "abs", "", { left: "800px", top: base - 640 + "px", width: "190px", height: "640px", borderRadius: "22px 22px 0 0",
      background: "#ff5e5b", border: "5px solid #17171c", borderBottom: "none", transformOrigin: "bottom" });
    const bigL = E.el(s3, "abs t", `<span class="g-white">×2</span>`, { left: "800px", width: "190px", top: base - 760 + "px", textAlign: "center", fontSize: "70px" });
    const te = N.e.t + 0.2;
    tl.fromTo(big, { scaleY: 0 }, { scaleY: 1, duration: 0.35, ease: "expo.out" }, te);
    E.in(bigL, te + 0.2, { from: "pop", dur: 0.4 });
    E.punch(te + 0.3, { amp: 22, flash: 0.35, cue: "error" });
    E.cue("hit", te + 0.3, 0.8);
    E.bgTo(te + 0.3, "coral", 0.25);
    const warn = E.el(s3, "abs", "", { left: 0, right: 0, top: "260px", textAlign: "center", opacity: 0 });
    tl.to(t3, { opacity: 0, duration: 0.2 }, te + 0.3);
    const wc = E.el(warn, "chip", `${E.icon("alert", 40, "#17171c", 2.8, "#ffd23f").outerHTML}<span>Volta pro <b>aprendizado</b>, custo sobe</span>`, { fontSize: "38px", marginTop: "90px" });
    tl.to(warn, { opacity: 1, duration: 0.01 }, te + 0.45);
    E.in(wc, te + 0.45, { from: "pop", cue: "pop" });

    // 4 — horizontal: multiplica
    const s4 = E.scene(N.f.t - 0.1, N.g.t - 0.1, { exit: "whip", dolly: 0.04 });
    E.bgTo(N.f.t - 0.2, "yellow");
    const t4 = E.text(s4, "HORIZONTAL:\n*MULTIPLICA*", "t t-l", { position: "absolute", top: "320px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t4, N.f.t + 0.1);
    const colsH = [["Criativos", "play", "#ff5e5b"], ["Públicos", "users", "#3da5ff"], ["Ofertas", "coin", "#b8f35a"]];
    colsH.forEach(([n, ic, c], i) => {
      const x = 80 + i * 320;
      const hd = E.el(s4, "abs", n, { left: x + "px", width: "280px", top: "640px", textAlign: "center", font: "900 44px 'Inter Display'", textTransform: "uppercase" });
      const t = N.f.t + N.f.d * (0.18 + i * 0.14);
      E.in(hd, t, { from: "up", cue: "whoosh", vol: 0.5 });
      for (let k = 0; k < 3; k++) {
        const c2 = E.el(s4, "abs badge", "", { left: x + 60 + "px", top: 720 + k * 170 + "px", width: "160px", height: "140px", borderRadius: "30px", background: c });
        c2.appendChild(E.icon(ic, 70));
        tl.fromTo(c2, { y: -(k * 170), scale: k ? 0.6 : 0, opacity: k ? 0 : 1 }, { y: 0, scale: 1, opacity: 1, duration: 0.45, ease: "back.out(1.8)", immediateRender: true }, t + 0.15 + k * 0.18);
        E.cue("pop", t + 0.15 + k * 0.18, 0.4);
      }
    });

    // 5 — os dois juntos, de olho no CPA
    const s5 = E.scene(N.g.t - 0.1, N.h.t - 0.15, { exit: "whip", dolly: 0.06 });
    E.bgTo(N.g.t - 0.2, "teal");
    const c5 = E.el(s5, "center", "", { bottom: "560px" });
    const icons = E.el(c5, "", "", { display: "flex", gap: "40px", alignItems: "center", marginBottom: "50px" });
    const i1 = E.el(icons, "badge", "", { width: "170px", height: "170px", background: "#3da5ff" }); i1.appendChild(E.icon("trend", 100));
    E.el(icons, "t", "+", { fontSize: "120px" });
    const i2 = E.el(icons, "badge", "", { width: "170px", height: "170px", background: "#ffd23f" }); i2.appendChild(E.icon("users", 100));
    E.in(icons.children, N.g.t + N.g.d * 0.3, { from: "pop", stagger: 0.12, cue: "pop" });
    const t5 = E.text(c5, "OS DOIS\n*JUNTOS*", "t t-xl");
    E.wordsIn(t5, N.g.t + N.g.d * 0.35, { stagger: 0.1 });
    E.punch(N.g.t + N.g.d * 0.45, { amp: 16, flash: 0.3, cue: "boom" });
    const mon = E.el(c5, "chip", `${E.icon("eye", 40).outerHTML}<span>De olho no <b>custo por venda</b></span>`, { marginTop: "50px", fontSize: "40px" });
    E.in(mon, N.g.t + N.g.d * 0.7, { from: "up", cue: "ding" });

    E.bgTo(N.h.t - 0.3, "orange");
    E.cta(N.h.t - 0.15, N.h.end + 2.2, { text: "SALVA E\n*ESCALA CERTO*", next: "EP 14: dobre as vendas sem gastar mais" });
  },
};
