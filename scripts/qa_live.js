/* Live checks with the real conductor: runs the demo, scrolls the page, measures layout shift,
   overflow and keyboard reach. NODE_PATH=<node_modules with playwright> node scripts/qa_live.js */
const { chromium } = require("playwright");
const path = require("path");
const ROOT = path.resolve(__dirname, "..");
const URL = process.env.QA_URL || "http://127.0.0.1:8765/index.html";
const OUT = path.join(ROOT, "review", "v2");
(async () => {
  const b = await chromium.launch({ executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" });
  for (const [w, h] of [[1440, 900], [390, 844]]) {
    const ctx = await b.newContext({ viewport: { width: w, height: h } });
    const p = await ctx.newPage();
    const errs = [];
    p.on("pageerror", (e) => errs.push(e.message));
    p.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
    await p.addInitScript(() => {
      window.__cls = 0;
      new PerformanceObserver((l) => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({ type: "layout-shift", buffered: true });
    });
    await p.goto(URL);
    await p.waitForTimeout(3000);
    // scroll the whole page
    const H = await p.evaluate(() => document.documentElement.scrollHeight);
    for (let y = 0; y < H; y += 300) { await p.evaluate((yy) => window.scrollTo(0, yy), y); await p.waitForTimeout(120); }
    await p.evaluate(() => document.querySelector("#office").scrollIntoView());
    await p.waitForTimeout(600);
    const before = await p.evaluate(() => { const r = document.querySelector("#term").getBoundingClientRect(); const f = document.querySelector(".office-fig").getBoundingClientRect(); return [r.height, f.height]; });
    await p.click("#run");
    await p.waitForTimeout(6200);
    await p.screenshot({ path: path.join(OUT, `live-${w}-run-6s.png`) });
    const mid = await p.evaluate(() => ({ btn: document.querySelector(".run-t").textContent, lines: document.querySelectorAll(".console li.on").length, rows: document.querySelectorAll(".ledger tbody tr.on").length, spin: document.querySelector(".spin").textContent }));
    await p.waitForTimeout(7000);
    const end = await p.evaluate(() => ({ btn: document.querySelector(".run-t").textContent, lines: document.querySelectorAll(".console li.on").length, rows: document.querySelectorAll(".ledger tbody tr.on").length, spin: document.querySelector(".spin").textContent, state: document.querySelector(".term-state").textContent }));
    await p.screenshot({ path: path.join(OUT, `live-${w}-run-end.png`) });
    const after = await p.evaluate(() => { const r = document.querySelector("#term").getBoundingClientRect(); const f = document.querySelector(".office-fig").getBoundingClientRect(); return [r.height, f.height]; });
    const m = await p.evaluate(() => ({ cls: window.__cls, sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
    // keyboard: tab through and count focusable stops with visible outline
    await p.evaluate(() => window.scrollTo(0, 0));
    await p.focus("body");
    let stops = 0, noRing = [];
    for (let i = 0; i < 60; i++) {
      await p.keyboard.press("Tab");
      const info = await p.evaluate(() => { const e = document.activeElement; if (!e || e === document.body) return null; const cs = getComputedStyle(e); return { tag: e.tagName, txt: (e.textContent || "").trim().slice(0, 24), ow: cs.outlineWidth, os: cs.outlineStyle }; });
      if (!info) break;
      stops++;
      if (info.os === "none" || info.ow === "0px") noRing.push(info.tag + ":" + info.txt);
    }
    console.log(w, "errors:", errs.length ? errs : "none", "| layout-shift sum:", m.cls.toFixed(4), "| overflow:", m.sw, "vs", m.cw,
      "| term/fig height before->after:", JSON.stringify(before), "->", JSON.stringify(after), "| mid:", JSON.stringify(mid), "| end:", JSON.stringify(end), "| tab stops:", stops, "no ring:", noRing);
    await ctx.close();
  }
  await b.close();
})();
