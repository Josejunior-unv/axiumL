// EP 07 — Anatomia de um anúncio que vende (gancho, problema, solução, prova, chamada)
window.VIDEO = {
  ep: 7,
  slug: "anatomia-do-anuncio",
  title: "Anatomia de um anúncio que vende",
  theme: { a1: "#00c2a8", a2: "#ffd23f", bg: "teal" },
  build(E) {
    const { tl } = E;

    // 1 — gancho com contagem regressiva
    const s1 = E.scene(0, 4.2);
    const c1 = E.el(s1, "center");
    const k = E.el(c1, "kicker", `<span class="dot"></span>Seu anúncio tem`, { marginBottom: "40px" });
    E.in(k, 0.05, { from: "pop" });
    const nums = E.el(c1, "", "", { position: "relative", width: "600px", height: "520px" });
    ["3", "2", "1"].forEach((n, i) => {
      const d = E.el(nums, "abs t sticker", n, { inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "520px",
        lineHeight: 1, WebkitTextStroke: "14px #17171c", color: ["#ffd23f", "#ff5e5b", "#ffffff"][i] });
      const t = 0.15 + i * 0.62;
      tl.fromTo(d, { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "expo.out" }, t);
      tl.to(d, { scale: 0.6, opacity: 0, filter: "blur(20px)", duration: 0.25, ease: "power2.in" }, t + 0.42);
      E.cue("hit", t, 0.6);
      E.shake(t, 12, 0.25);
    });
    const sg = E.text(c1, "SEGUNDOS PRA\n*PRENDER* ALGUÉM", "t t-m", { marginTop: "-380px" });
    E.wordsIn(sg, 2.1, { stagger: 0.07 });
    E.punch(2.5, { amp: 16, flash: 0.3 });

    // 2 — anatomia (celular + linha do tempo)
    const s2 = E.scene(4.2, 24.0);
    const ph = E.el(s2, "abs", "", { left: "320px", top: "300px", width: "440px", height: "800px", borderRadius: "64px", padding: "14px",
      background: "#17171c", boxShadow: "14px 14px 0 rgba(23,23,28,.35)" });
    const scr = E.el(ph, "", "", { position: "relative", width: "100%", height: "100%", borderRadius: "52px", background: "#fff", overflow: "hidden" });
    E.el(scr, "abs", "", { top: "22px", left: "50%", width: "110px", height: "30px", marginLeft: "-55px", borderRadius: "20px", background: "#000", zIndex: 5 });
    E.in(ph, 4.3, { from: "up", dur: 0.8, cue: "whoosh" });
    E.float(ph, 5.0, 23.5, 8, 3);

    // barra do vídeo (0 a 30s)
    const tlw = E.el(s2, "abs", "", { left: "80px", right: "80px", top: "1150px" });
    const segs = [["Gancho", "0–3s", 3, "#ff5e5b", "coral"], ["Problema", "3–8s", 5, "#ff8a3d", "orange"], ["Solução", "8–20s", 12, "#3da5ff", "sky"], ["Prova", "20–25s", 5, "#b8f35a", "lime"], ["Chamada", "25–30s", 5, "#ffd23f", "yellow"]];
    const bar = E.el(tlw, "", "", { display: "flex", gap: "8px", height: "26px" });
    const segEls = segs.map(([, , w, c]) => {
      const s = E.el(bar, "", "", { flex: w, borderRadius: "9px", background: "#fff", border: "4px solid #17171c", overflow: "hidden", position: "relative" });
      const f = E.el(s, "abs", "", { inset: 0, background: c, transformOrigin: "left", transform: "scaleX(0)" });
      return f;
    });
    E.in(tlw, 4.6, { from: "fade" });

    const card = E.el(s2, "card abs", "", { left: "80px", right: "80px", top: "1230px", height: "290px", padding: "0", overflow: "hidden" });
    E.in(card, 4.8, { from: "up", cue: "swish" });

    // conteúdo de cada etapa: tela do celular + explicação
    const screens = [
      () => `<div style="position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:40px;background:#ffd23f">
        <div class="t" style="font-size:66px;line-height:.95">PARE DE<br>PERDER<br>DINHEIRO<br>COM ADS</div><div style="margin-top:24px;font:800 26px Inter;opacity:.9">(e faça isso em vez disso)</div></div>`,
      () => `<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px;background:#fff6e5">
        ${E.icon("alert", 150, "#17171c", 2.2, "#ff8a3d").outerHTML}<div class="t" style="font-size:52px;text-align:center">CPA SUBINDO,<br>VENDA PARADA</div></div>`,
      () => `<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px;background:#e6f3ff">
        <svg width="320" height="220" viewBox="0 0 320 220"><path d="M10 200 L90 150 L150 170 L220 80 L310 20" fill="none" stroke="#3da5ff" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <div class="t" style="font-size:52px;text-align:center">O MÉTODO<br>NA PRÁTICA</div></div>`,
      () => `<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;background:#f1ffdc;padding:30px">
        <div style="display:flex;gap:8px">${Array(5).fill(E.icon("star", 54, "#17171c", 2.2, "#ffd23f").outerHTML).join("")}</div>
        <div style="font:700 32px/1.3 Inter;text-align:center;color:#17171c">"Meu custo por venda caiu pela metade."</div>
        <div style="font:800 24px Inter;color:#1a9e55">— depoimento de cliente</div></div>`,
      () => `<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:40px;background:#e6f3ff">
        <div class="t" style="font-size:56px;text-align:center">VAGAS<br>LIMITADAS</div>
        <div class="cta-btn" style="padding:26px 60px;border-radius:99px;background:#ff5e5b;color:#fff;border:5px solid #17171c;font:900 38px Inter;box-shadow:6px 6px 0 #17171c">SAIBA MAIS</div></div>`,
    ];
    const infos = [
      ["GANCHO", "Uma frase ou imagem que <b>para a rolagem</b>. Sem enrolar."],
      ["PROBLEMA", "Mostra que você <b>entende a dor</b> de quem assiste."],
      ["SOLUÇÃO", "Demonstra <b>como resolve</b>. Mostre, não só fale."],
      ["PROVA", "Depoimento, número, antes e depois. <b>Gera confiança.</b>"],
      ["CHAMADA", "Diz <b>exatamente o que fazer</b> agora: clicar, chamar, comprar."],
    ];
    const T0 = 5.2, ST = 3.7;
    segs.forEach(([n, rng, , c, bgp], i) => {
      const t = T0 + i * ST;
      const sc = E.el(scr, "abs", screens[i](), { inset: 0 });
      tl.set(sc, { opacity: 0 }, 0);
      tl.fromTo(sc, { opacity: 0, scale: 1.15 }, { opacity: 1, scale: 1, duration: 0.45, ease: "expo.out" }, t);
      if (i < 4) tl.to(sc, { opacity: 0, duration: 0.2 }, t + ST - 0.1);
      tl.to(segEls[i], { scaleX: 1, duration: ST * 0.9, ease: "none" }, t);
      const inf = E.el(card, "abs", "", { inset: 0, padding: "40px 46px" });
      const hd = E.el(inf, "", "", { display: "flex", alignItems: "center", justifyContent: "space-between" });
      E.el(hd, "t", `<span class="g-white" style="background:${c}">${n}</span>`, { fontSize: "70px" });
      E.el(hd, "chip", rng, { fontSize: "34px" });
      E.el(inf, "p", infos[i][1], { fontSize: "42px", marginTop: "20px" });
      tl.set(inf, { opacity: 0 }, 0);
      E.in(inf, t + 0.05, { from: "right", dur: 0.5, cue: "whoosh", vol: 0.6 });
      if (i < 4) E.out(inf, t + ST - 0.25, { to: "left", dur: 0.25 });
      E.bgTo(t, bgp);
      E.cue("pop", t, 0.5);
      if (i === 0) E.punch(t + 0.1, { amp: 10, flash: 0.15, vol: 0.6 });
      if (i === 4) {
        const btn = sc.querySelector(".cta-btn");
        const cur = E.el(scr, "abs", "", { left: "300px", top: "640px" });
        cur.appendChild(E.icon("cursor", 70, "#17171c", 2.4, "#fff"));
        tl.fromTo(cur, { opacity: 0, x: 80, y: 80 }, { opacity: 1, x: -60, y: -150, duration: 0.8, ease: "power2.inOut" }, t + 0.7);
        tl.to(btn, { scale: 0.9, duration: 0.08, yoyo: true, repeat: 1 }, t + 1.5);
        E.cue("click", t + 1.5, 1);
        E.punch(t + 1.55, { amp: 10, flash: 0.25, cue: "cash" });
      }
    });

    // 3 — fechamento
    const s3 = E.scene(24.0, 27.4);
    E.bgTo(23.8, "teal");
    const c3 = E.el(s3, "center");
    const a3 = E.text(c3, "SE O GANCHO\nFALHA, O RESTO\n[g-red:NINGUÉM VÊ].", "t t-l");
    E.wordsIn(a3, 24.1, { stagger: 0.07 });
    E.punch(24.9, { amp: 18, flash: 0.3 });

    E.cta(27.4, 32.0, { text: "SALVA ESSE\n*ROTEIRO*", next: "EP 08: o algoritmo está cego?" });
  },
};
