// EP 01 — O que é tráfego pago (orgânico x pago, a jornada do clique à venda)
window.VIDEO = {
  ep: 1,
  slug: "o-que-e-trafego-pago",
  title: "Tráfego pago em 30 segundos",
  theme: { a1: "#ff5e5b", a2: "#ffffff", bg: "yellow" },
  build(E) {
    const { tl } = E;

    // 1 — gancho
    const h = E.hook(0, 3.4, { kicker: "Pare de torcer", text: "POSTAR E\n*TORCER*\nNÃO É\n[g-red:ESTRATÉGIA]", cls: "t t-l", stagger: 0.09 });
    E.punch(0.95, { amp: 16 });
    E.glitch(h.tx.words[5], 1.0, 0.45);

    // 2 — orgânico x pago
    const s2 = E.scene(3.4, 9.6);
    const chart = (parent, y, label, sub, color, pts, chip) => {
      const card = E.el(parent, "card abs", "", { left: "80px", right: "80px", top: y + "px", height: "500px" });
      const head = E.el(card, "", "", { display: "flex", alignItems: "center", gap: "26px" });
      const b = E.el(head, "badge", "", { width: "96px", height: "96px", borderRadius: "28px", background: color });
      b.appendChild(E.icon(label === "ORGÂNICO" ? "heart" : "rocket", 52));
      const tt = E.el(head, "", `<div class="t t-s" style="font-size:66px">${label}</div>`);
      const ch = E.el(head, "chip", chip, { marginLeft: "auto", fontSize: "30px", padding: "10px 22px" });
      const sv = E.el(card, "", `
        <svg width="824" height="250" viewBox="0 0 824 250" style="margin-top:22px;overflow:visible">
                    <path d="M0 240 H824" stroke="#17171c" stroke-width="4" stroke-linecap="round"/>
          <path class="ln" d="${pts}" fill="none" stroke="${color}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>`);
      const p = E.el(card, "p", sub, { fontSize: "38px", marginTop: "16px" });
      return { card, ln: sv.querySelector(".ln"), ch, p };
    };
    const org = chart(s2, 330, "ORGÂNICO", "Alcance limitado. <b>Depende do algoritmo.</b>", "#b9bec7",
      "M0 225 C120 215 180 228 260 205 S420 214 500 190 S650 200 824 165", "lento");
    const pag = chart(s2, 880, "PAGO", "Você escolhe <b>quem vê, quando e quanto</b> investe.", "#ff5e5b",
      "M0 225 C140 220 220 200 330 160 S520 80 600 55 S760 10 824 4", "previsível");
    E.in(org.card, 3.5, { from: "left", cue: "whoosh" });
    E.draw(org.ln, 3.9, 1.6, { ease: "power1.inOut" });
    E.in(pag.card, 5.2, { from: "right", cue: "whoosh" });
    E.draw(pag.ln, 5.6, 1.1, { ease: "expo.in" });
    E.punch(6.7, { amp: 14, flash: 0.25 });
    E.in(pag.ch, 6.7, { from: "pop", cue: "pop" });
    tl.to(org.card, { opacity: 0.45, scale: 0.96, duration: 0.6 }, 6.9);
    E.bgTo(6.7, "sky");

    // 3 — definição
    const s3 = E.scene(9.6, 14.2);
    const c3 = E.el(s3, "center");
    const k3 = E.el(c3, "kicker", `<span class="dot"></span>Definição simples`, { marginBottom: "60px" });
    E.in(k3, 9.7, { from: "pop" });
    const t3 = E.text(c3, "TRÁFEGO PAGO É\n*COMPRAR*\n*ATENÇÃO*\nDE QUEM PODE\n[g-green:COMPRAR DE VOCÊ]", "t t-m");
    E.wordsIn(t3, 9.8, { stagger: 0.07 });
    E.punch(10.45, { amp: 14, flash: 0.3 });
    E.bgTo(9.5, "coral");
    const eye = E.icon("eye", 150, "#17171c", 2.2, "#fff");
    E.el(s3, "abs", "", { right: "70px", top: "330px", opacity: 0.0 }).appendChild(eye);
    E.in(eye.parentNode, 10.4, { from: "pop", cue: false });
    tl.to(eye.parentNode, { opacity: 1, duration: 0.01 }, 10.4);
    E.draw(eye, 10.4, 0.8);
    E.float(eye.parentNode, 10.8, 14, 12, 1.6);

    // 4 — a jornada
    const s4 = E.scene(14.2, 20.6);
    E.bgTo(14.1, "yellow");
    const ttl = E.text(s4, "O CAMINHO DO *DINHEIRO*", "t t-s", { position: "absolute", top: "320px", left: "80px", right: "80px", textAlign: "center" });
    E.wordsIn(ttl, 14.3, { stagger: 0.06 });
    const steps = [["megaphone", "Anúncio", "aparece pra pessoa certa"], ["cursor", "Clique", "ela se interessa"], ["globe", "Página", "entende a oferta"], ["coin", "Venda", "dinheiro no caixa"]];
    const y0 = 520, gap = 250;
    const rail = E.el(s4, "abs", "", { left: "196px", top: y0 + 65 + "px", width: "8px", height: gap * 3 + "px", borderRadius: "9px", background: "rgba(23,23,28,.15)" });
    const fill = E.el(rail, "abs", "", { inset: 0, borderRadius: "9px", background: "#17171c", transformOrigin: "top" });
    tl.fromTo(fill, { scaleY: 0 }, { scaleY: 1, duration: 4.2, ease: "none" }, 15.0);
    steps.forEach(([ic, a, b], i) => {
      const y = y0 + i * gap;
      const bd = E.el(s4, "badge abs", "", { left: "135px", top: y + "px", width: "130px", height: "130px", borderRadius: "38px",
        background: "#fff" });
      const icn = E.icon(ic, 66); bd.appendChild(icn);
      const lb = E.el(s4, "abs", `<div class="t" style="font-size:78px">${a}</div><div class="p" style="font-size:38px;margin-top:6px">${b}</div>`,
        { left: "310px", top: y + 8 + "px" });
      const tin = 14.6 + i * 0.12;
      E.in([bd, lb], tin, { from: "left", dur: 0.6 });
      const lit = 15.0 + i * 1.4;
      tl.to(bd, { background: ["#ff5e5b", "#3da5ff", "#00c2a8", "#b8f35a"][i], duration: 0.2 }, lit);
      E.pulse(bd, lit, 1.18, 0.35);
      E.cue(i === 3 ? "cash" : "pop", lit, 0.8);
    });
    E.punch(19.2, { amp: 12, flash: 0.25, cue: "hit" });
    const plats = E.el(s4, "abs", "", { left: "80px", right: "80px", top: "1520px", display: "flex", gap: "18px", justifyContent: "center" });
    ["Meta Ads", "Google Ads", "TikTok Ads"].forEach((n) => E.el(plats, "chip", n, { fontSize: "32px" }));
    E.in(plats.children, 19.4, { from: "up", stagger: 0.08, dur: 0.5 });

    // 5 — medir
    const s5 = E.scene(20.6, 24.6);
    const c5 = E.el(s5, "center");
    E.bgTo(20.5, "coral");
    const a5 = E.text(c5, "SEM MEDIR,\nÉ SÓ [g-white:GASTO].", "t t-l");
    E.wordsIn(a5, 20.7, { stagger: 0.08 });
    E.punch(21.25, { amp: 12, flash: 0.2 });
    const b5 = E.text(c5, "MEDINDO, É\n[g-green:INVESTIMENTO].", "t t-l", { marginTop: "70px" });
    E.wordsIn(b5, 22.2, { stagger: 0.08 });
    E.punch(22.75, { amp: 16, flash: 0.35, cue: "cash" });
    E.bgTo(22.2, "green");

    // 6 — chamada final
    E.bgTo(24.4, "yellow");
    E.cta(24.6, 29.4, { text: "SALVA PRA\n*NÃO ESQUECER*", next: "EP 02: as 5 métricas que importam" });
  },
};
