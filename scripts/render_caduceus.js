#!/usr/bin/env node
/* Writes docs/assets/caduceus.svg: one still frame of the caduceus (the living idle pose,
   time 0) as dots, for visitors without scripts. Same engine, same dither as the live piece.
   Run: node scripts/render_caduceus.js */
const fs = require("fs");
const path = require("path");
const C = require("../docs/assets/caduceus.js");

const engine = C.createEngine();
engine.frame(0, C.IDLE);
const pose = C.IDLE;
const tone = pose.tone ? C.SIGNAL[pose.tone] : null;
const colors = [
  C.mixc(C.INK, pose.wingInk),
  C.mixc(tone || C.INK, pose.snakeInk[0]),
  C.mixc(tone || C.INK, pose.snakeInk[1]),
  C.mixc(tone || C.ACCENT, pose.staffInk),
  C.mixc(C.SIGNAL.whisper, 1),
];
const paths = colors.map(() => "");
for (const [x, y, o] of C.dots(engine)) paths[o] += `M${x + 0.24} ${y + 0.24}h.52v.52h-.52z`;
const body = paths.map((d, i) => (d ? `<path fill="${colors[i]}" d="${d}"/>` : "")).join("");
const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${C.W} ${C.H}" width="${C.W}" height="${C.H}" role="img" aria-label="The Axiom caduceus drawn in braille dots: a staff with two serpents and open wings">${body}</svg>\n`;
fs.writeFileSync(path.join(__dirname, "../docs/assets/caduceus.svg"), svg);
console.log("caduceus.svg", svg.length, "bytes");
