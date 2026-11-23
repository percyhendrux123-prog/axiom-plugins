/* QA screenshots with Playwright + the installed Chrome. Not part of the page build.
   NODE_PATH=<a node_modules that has playwright> node scripts/qa_shots.js
   Writes review/$QA_OUT (default v3)/*.png (review/ is git-ignored). */
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");
const ROOT = path.resolve(__dirname, "..");
const URL = process.env.QA_URL || "http://127.0.0.1:8765/index.html";
const OUT = path.join(ROOT, "review", process.env.QA_OUT || "v3");
fs.mkdirSync(OUT, { recursive: true });
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

(async () => {
  const b = await chromium.launch({ executablePath: CHROME });
  const log = (...a) => console.log(...a);
  async function page(w, h, opts = {}) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: opts.dpr || 1, reducedMotion: opts.reduced ? "reduce" : "no-preference", javaScriptEnabled: opts.js !== false });
    const p = await ctx.newPage();
    p.on("console", (m) => { if (m.type() === "error") log("console error:", m.text()); });
    p.on("pageerror", (e) => log("pageerror:", e.message));
    return p;
  }
  const which = process.argv.slice(2);
  const want = (n) => !which.length || which.includes(n);

  if (want("desktop")) {
    const p = await page(1440, 900);
    await p.goto(URL);
    await p.waitForTimeout(4500);       // typed command, caduceus, cursor
    await p.screenshot({ path: path.join(OUT, "desktop-1440x900.png") });
    // full page: scroll through so every piece inks in, then capture
    const h = await p.evaluate(() => document.documentElement.scrollHeight);
    for (let y = 0; y < h; y += 500) { await p.evaluate((yy) => window.scrollTo(0, yy), y); await p.waitForTimeout(450); }
    await p.waitForTimeout(1800);
    await p.evaluate(() => window.scrollTo(0, 0));
    await p.waitForTimeout(500);
    await p.screenshot({ path: path.join(OUT, "desktop-full.png"), fullPage: true });
    log("desktop height", h);
    await p.context().close();
  }
  if (want("mobile")) {
    const p = await page(390, 844);
    await p.goto(URL);
    await p.waitForTimeout(4500);
    await p.screenshot({ path: path.join(OUT, "mobile-390x844.png") });
    const h = await p.evaluate(() => document.documentElement.scrollHeight);
    for (let y = 0; y < h; y += 400) { await p.evaluate((yy) => window.scrollTo(0, yy), y); await p.waitForTimeout(400); }
    await p.waitForTimeout(1800);
    await p.evaluate(() => window.scrollTo(0, 0));
    await p.waitForTimeout(400);
    await p.screenshot({ path: path.join(OUT, "mobile-full.png"), fullPage: true });
    const ov = await p.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
    log("mobile overflow check", JSON.stringify(ov), "height", h);
    await p.context().close();
  }
  if (want("frames")) {
    for (const [w, tag] of [[1440, "d"], [390, "m"]]) {
      for (const t of [1.5, 3.6, 5.9, 7.4, 10.3, 11.6]) {
        const p = await page(w, w === 1440 ? 1330 : 1700);
        await p.goto(URL + "?demo=frame&t=" + t);
        await p.waitForTimeout(700);
        await p.screenshot({ path: path.join(OUT, `frame-${tag}-${String(t).replace(".", "_")}.png`) });
        await p.context().close();
      }
    }
  }
  if (want("reduced")) {
    const p = await page(1440, 900, { reduced: true });
    await p.goto(URL); await p.waitForTimeout(800);
    await p.screenshot({ path: path.join(OUT, "reduced-1440x900.png") });
    await p.context().close();
  }
  if (want("nojs")) {
    const p = await page(1440, 900, { js: false });
    await p.goto(URL); await p.waitForTimeout(500);
    await p.screenshot({ path: path.join(OUT, "nojs-full.png"), fullPage: true });
    await p.context().close();
  }
  await b.close();
})();
