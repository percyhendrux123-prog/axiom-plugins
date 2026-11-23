#!/usr/bin/env node
/* Writes docs/og.png (1200x630): graphite ground, the braille caduceus still, the title in Cinzel,
   the locked unseen-triangle mark (docs/mark.svg), the subtitle. Not part of the page build.
   NODE_PATH=<a node_modules that has playwright> node scripts/render_og.js */
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");
const os = require("os");
const ROOT = path.resolve(__dirname, "..");
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const U = (p) => "file://" + path.join(ROOT, p);

const html = `<!doctype html><meta charset="utf-8"><style>
@font-face{font-family:Cinzel;src:url(${U("docs/fonts/cinzel-latin-wght.woff2")}) format("woff2");font-weight:400 900}
@font-face{font-family:Plex;src:url(${U("docs/fonts/ibm-plex-mono-latin-400-normal.woff2")}) format("woff2");font-weight:400}
html,body{margin:0;width:1200px;height:630px;background:#0c0d0f;overflow:hidden}
.c{position:relative;width:1200px;height:630px;color:#f1ede4}
.mark{position:absolute;left:80px;top:64px;width:112px;height:auto}
.cad{position:absolute;right:60px;top:46%;transform:translateY(-50%);width:480px;height:auto}
.rule{position:absolute;left:80px;top:250px;width:56px;height:2px;background:#c2a874}
h1{position:absolute;left:80px;top:274px;margin:0;font:700 56px/1.18 Cinzel,serif;letter-spacing:.03em;width:640px;white-space:nowrap}
.sub{position:absolute;left:80px;top:430px;font:400 27px/1.3 Plex,monospace;color:#d9d5cb;letter-spacing:.01em}
.foot{position:absolute;left:80px;bottom:54px;font:400 20px/1 Plex,monospace;color:#8d8980;letter-spacing:.08em}
.line{position:absolute;left:80px;right:80px;bottom:100px;height:1px;background:#7a6540;opacity:.7}
</style><div class="c">
<img class="mark" src="${U("docs/mark.svg")}">
<img class="cad" src="${U("docs/assets/caduceus.svg")}">
<div class="rule"></div>
<h1>The Agent With<br>The Axiom Tattoo</h1>
<div class="sub">Axiom Office for Claude \u00b7 11 plugins</div>
<div class="line"></div>
<div class="foot">DEPLOY AXIOM</div>
</div>`;

(async () => {
  const b = await chromium.launch({ executablePath: CHROME });
  const p = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  const tmp = path.join(os.tmpdir(), "axiom-og.html");
  fs.writeFileSync(tmp, html);
  await p.goto("file://" + tmp);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(600);
  await p.screenshot({ path: path.join(ROOT, "docs", "og.png") });
  await b.close();
  console.log("og.png written");
})();
