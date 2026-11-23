#!/usr/bin/env python3
"""Assemble docs/assets/caduceus.js: the panel's engine, copied verbatim, plus this page's glue.

Source of the engine: ~/dev/axiom-panel/index.html (same code as the hermes-axioma desktop
plugin). Run again only if the engine changes there. The page glue is the GLUE string below.
"""
import sys
from pathlib import Path

PANEL = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / "dev/axiom-panel/index.html")
OUT = Path(__file__).resolve().parent.parent / "docs/assets/caduceus.js"

HDR = '''/* The braille caduceus. The drawing engine below is ported without change from the
   Axiom panel (index.html) and the hermes-axioma desktop plugin: an 88 x 72 field of dots,
   hand-made wings, serpents as a helix round the staff, ordered dither into braille cells.
   Meaning: staff = the main agent, serpents = running workers, amber and still = waiting
   on the owner, wings open and green = something finished. Only the page glue after the
   "page glue" line is new (pose targets for this page, HTML painter, exports). */
(function(root){
"use strict";
'''

GLUE = r'''
// ------------------------------------------------------------ page glue (new)
// Wings at rest sit level, not hanging: 0 = closed and drooping, 1 = lifted open (the "finished" pose).
const REST_OPEN=0.6;
// Poses. IDLE is a living pose, not the panel's dimmed "standing by": the hero is never asleep.
const IDLE={wingMotion:0.5,open:REST_OPEN,snakeMotion:[0.45,0.4],snakeInk:[0.6,0.58],staffInk:1,wingInk:0.9,tone:null,wingTone:null};
// live = {waiting, workers, recent}; same rules as the panel's targetPose, with the living idle.
function targetPose(live){
 const workers=live.workers,active=workers>0,still=live.waiting>0,verified=live.recent;
 if(!active&&!still&&!verified)return {...IDLE,snakeMotion:IDLE.snakeMotion.slice(),snakeInk:IDLE.snakeInk.slice()};
 return {
  wingMotion:still?0:active?0.7:0.35,
  open:verified?1:REST_OPEN,
  snakeMotion:[still?0:workers>0?1:0.3,still?0:workers>1?1:0.3],
  snakeInk:[workers>0?1:still?0.85:0.6,workers>1?1:still?0.85:0.58],
  staffInk:1,
  wingInk:verified?1:still?0.85:0.9,
  tone:still?"caution":null,
  wingTone:verified?"go":null
 };
}
const BGC=[0x0c,0x0d,0x0f];
const hex2=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));
const mixc=(h,a)=>{const c=hex2(h);return "#"+c.map((v,i)=>Math.round(BGC[i]+(v-BGC[i])*a).toString(16).padStart(2,"0")).join("")};
const RANK=[0,1,1,2,3];
const CAD_ROWS=H/4,CAD_COLS=W/2;
// Dither the engine's field into braille cells and return the rows as HTML.
// ls = letter-spacing in px that puts a braille glyph on the same pitch as the letters.
function paintHTML(engine,pose,ls){
 const tone=pose.tone?SIGNAL[pose.tone]:null;
 const fills=[[pose.wingTone?SIGNAL[pose.wingTone]:tone||INK,pose.wingInk],[tone||INK,pose.snakeInk[0]],[tone||INK,pose.snakeInk[1]],[tone||ACCENT,pose.staffInk],[tone||SIGNAL.whisper,1]];
 const colors=fills.map(f=>mixc(f[0],f[1]));
 const {field,owner}=engine,lsAttr=ls?`;letter-spacing:${ls}px`:"";
 let html="";
 for(let cy=0;cy<CAD_ROWS;cy++){
  let row="",run="",rc=-2;
  const flush=()=>{if(run)row+=`<span style="${rc<0?"":"color:"+colors[rc]+";"}${lsAttr.slice(1)}">${run}</span>`;run=""};
  for(let cx=0;cx<CAD_COLS;cx++){
   let bits=0,best=-1;
   for(let dy=0;dy<4;dy++)for(let dx=0;dx<2;dx++){
    const x=cx*2+dx,y=cy*4+dy,i=y*W+x;
    if(field[i]*1.3<=BAYER[(y&3)*4+(x&3)])continue;
    bits|=BIT[dy][dx];const o=owner[i];if(best<0||RANK[o]>RANK[best])best=o;
   }
   const c=bits?best:-1;
   if(c!==rc){flush();rc=c}
   run+=String.fromCharCode(0x2800+bits);
  }
  flush();html+=`<div>${row}</div>`;
 }
 return html;
}
// The same dither as a list of lit dots [x, y, owner], for the no-script SVG (scripts/render_caduceus.js).
function dots(engine){
 const {field,owner}=engine,out=[];
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){
  const i=y*W+x;
  if(field[i]*1.3>BAYER[(y&3)*4+(x&3)])out.push([x,y,owner[i]]);
 }
 return out;
}
const api={W,H,CAD_ROWS,CAD_COLS,createEngine,targetPose,easePose,poseGap,paintHTML,dots,SIGNAL,INK,ACCENT,IDLE,mixc};
if(typeof module==="object"&&module.exports)module.exports=api;else root.AxiomCaduceus=api;
})(typeof window!=="undefined"?window:globalThis);
'''

src = PANEL.read_text()
core = src[src.index("const W=88,H=72"):src.index("// What the drawing should look like for the board")]
pose = src[src.index("function easePose"):src.index("// ------------------------------------------------------------ terminal grid")]
OUT.write_text(HDR + core + "\n" + pose + GLUE)
print("wrote", OUT)
