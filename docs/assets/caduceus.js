/* The braille caduceus. The drawing engine below is ported without change from the
   Axiom panel (index.html) and the hermes-axioma desktop plugin: an 88 x 72 field of dots,
   hand-made wings, serpents as a helix round the staff, ordered dither into braille cells.
   Meaning: staff = the main agent, serpents = running workers, amber and still = waiting
   on the owner, wings open and green = something finished. Only the page glue after the
   "page glue" line is new (pose targets for this page, HTML painter, exports). */
(function(root){
"use strict";
const W=88,H=72,CX=43.5,SOURCE_W=68,WING_BOTTOM=23;
const WING_ART=["⠀⣠⣤⣤⣄⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣠⣤⣤⣄⠀", "⠀⢹⣛⡿⢿⣿⣿⣿⣿⣶⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣶⣿⣿⣿⣿⡿⢿⣛⡏⠀", "⠀⠀⠿⢿⣿⣾⣭⣿⣿⣿⣿⣿⣷⣦⡀⠀⢿⡿⠀⢀⣴⣾⣿⣿⣿⣿⣿⣭⣷⣿⡿⠿⠀⠀", "⠀⠀⠀⠘⢷⣶⣿⣽⣿⣿⣿⣿⣿⣿⣿⣦⢸⡇⣴⣿⣿⣿⣿⣿⣿⣿⣿⣯⣿⣶⡾⠃⠀⠀⠀", "⠀⠀⠀⠀⠀⠀⠲⢶⡶⠿⣿⣿⣿⣿⣿⣿⢻⡟⣿⣿⣿⣿⣿⣿⠿⢶⡶⠖⠀⠀⠀⠀⠀⠀", "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠋⠚⠿⠛⠁⢸⡇⠈⠛⠿⠓⠙⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀"];
const BIT=[[0x01,0x08],[0x02,0x10],[0x04,0x20],[0x40,0x80]];
const BAYER=[0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5].map(v=>(v+0.5)/16);
const TAU=Math.PI*2;
const KY=[27,40,53,64,69.5],KP=[0,1,2,3,3.5],KR=[10,9,7.5,5.5,0.6];
const SNAKES=[
 {side:-1,wave:4.3,lambda:17,phase:0.0,breath:6.1,bphase:0.0,glint:8.3,gphase:0.0},
 {side:1,wave:5.2,lambda:19,phase:2.1,breath:7.3,bphase:1.7,glint:9.7,gphase:0.46}];
// Who owns a dot: 0 wings, 1 left serpent, 2 right serpent, 3 staff, 4 glint.
const WINGS=0,STAFF=3,GLINT=4;
const SIGNAL={stop:"#d9675b",caution:"#e0a43a",go:"#6fbf8a",whisper:"#eadfb8"};
const INK="#cfcdc5",ACCENT="#f0eee8";
const clamp01=x=>x<0?0:x>1?1:x;
const smooth=(a,b,x)=>{const u=clamp01((x-a)/(b-a));return u*u*(3-2*u)};
function knot(arr,y){
 if(y<=KY[0])return arr[0];
 for(let i=1;i<KY.length;i++){
  if(y<=KY[i]){let u=(y-KY[i-1])/(KY[i]-KY[i-1]);u=u*u*(3-2*u);return arr[i-1]+(arr[i]-arr[i-1])*u}
 }
 return arr[arr.length-1];
}
function parseArt(){
 const g=new Float32Array(SOURCE_W*H);
 WING_ART.forEach((row,r)=>{
  Array.from(row).forEach((ch,c)=>{
   const v=ch.codePointAt(0)-0x2800;
   if(v<=0||v>255||c>=SOURCE_W/2)return;
   for(let dy=0;dy<4;dy++)for(let dx=0;dx<2;dx++)if(v&BIT[dy][dx])g[(r*4+dy)*SOURCE_W+c*2+dx]=1;
  });
 });
 return g;
}
function createEngine(){
 const art=parseArt(),field=new Float32Array(W*H),owner=new Uint8Array(W*H);
 const px=(x,y)=>(x<0||y<0||x>=SOURCE_W||y>WING_BOTTOM?0:art[y*SOURCE_W+x]);
 function artAt(x,y){
  const x0=Math.floor(x),y0=Math.floor(y),fx=x-x0,fy=y-y0;
  return (px(x0,y0)*(1-fx)+px(x0+1,y0)*fx)*(1-fy)+(px(x0,y0+1)*(1-fx)+px(x0+1,y0+1)*fx)*fy;
 }
 function wings(t,amt,open){
  for(let y=0;y<=WING_BOTTOM;y++){
   for(let x=0;x<W;x++){
    const side=x<CX?-1:1,u=Math.min(1,Math.abs(x-CX)/44),lag=side<0?0:0.55,k=side<0?1.25:1.4;
    const breath=amt*2.1*Math.pow(u,1.5)*Math.sin(TAU*t/7.4-lag-k*u);
    const riffle=amt*0.35*u*Math.sin(TAU*t/2.9+y*0.45+side*0.9);
    // Closed wings hang a little; open wings lift toward the tips.
    const spread=(open*2.4-(1-open)*3.4)*Math.pow(u,1.3);
    let sx=33.5+(x-CX)/1.29;
    if(Math.abs(x-CX)<=1)sx=33.5+x-CX;
    const i=y*W+x;
    field[i]=artAt(sx,y+breath+riffle+spread);
    owner[i]=WINGS;
   }
  }
 }
 function strandX(s,y,t,amt){
  const r=knot(KR,y)*(1+amt*0.04*Math.sin(TAU*t/s.breath+s.bphase));
  const env=0.25+0.75*smooth(27,69,y);
  const wig=amt*1.15*env*Math.sin(TAU*y/s.lambda-TAU*t/s.wave+s.phase);
  return CX+s.side*r*Math.cos(Math.PI*knot(KP,y))+wig;
 }
 function snakes(t,amts){
  for(let i=(WING_BOTTOM+1)*W;i<W*H;i++){field[i]=0;owner[i]=WINGS}
  const glintY=SNAKES.map((s,k)=>{
   const g=((t/s.glint+s.gphase)%1+1)%1;
   return amts[k]>0.5&&g<0.45?69-(g/0.45)*44:-99;
  });
  for(let y=24;y<H;y++){
   const layers=[];
   for(let k=0;k<2;k++){
    if(y<27||y>69.5)continue;
    const s=SNAKES[k],xs=strandX(s,y,t,amts[k]);
    const slope=strandX(s,y+0.5,t,amts[k])-strandX(s,y-0.5,t,amts[k]);
    layers.push({xs,norm:Math.sqrt(1+slope*slope),z:Math.sin(Math.PI*knot(KP,y))*-s.side,hw:2.45-1.25*smooth(27,69,y),k});
   }
   layers.sort((a,b)=>a.z-b.z);
   for(let x=0;x<W;x++){
    let v=0,own=WINGS,staffDone=false;
    const staff=(x===CX-0.5||x===CX+0.5)&&y<=70;
    // Back to front: the serpent behind, the staff, the serpent in front.
    for(let o=0;o<=layers.length;o++){
     const L=layers[o];
     if(staff&&!staffDone&&(!L||L.z>0)){v=1;own=STAFF;staffDone=true}
     if(!L)break;
     const d=Math.abs(x-L.xs)/L.norm;
     if(d<L.hw){
      v=clamp01(L.hw-d+0.35)*(0.8+0.2*smooth(-0.35,0.35,L.z))*(1-0.12*(d/L.hw)*(d/L.hw));
      own=Math.abs(y-glintY[L.k])<2.6&&L.z>-0.2?GLINT:L.k+1;
     }else if(L.z>0&&d<L.hw+0.75){v=0}
    }
    const i=y*W+x;field[i]=v;owner[i]=own;
   }
  }
  // Heads, just under the wings, facing each other across the staff.
  for(let h=0;h<2;h++){
   const S=SNAKES[h],hx=strandX(S,27,t,amts[h])-S.side*0.6,hy=26+amts[h]*0.35*Math.sin(TAU*t/S.breath+S.bphase+1.2);
   for(let yy=23;yy<=29;yy++){
    for(let xx=Math.floor(hx-6);xx<=Math.ceil(hx+6);xx++){
     if(xx<0||xx>=W)continue;
     const ax=(xx-hx)*-S.side,rx=ax>0?4.1:3.4,ry=ax>0?1.9-0.25*(ax/4.1):2.2;
     const e=(ax/rx)*(ax/rx)+((yy-hy)/ry)*((yy-hy)/ry),i=yy*W+xx;
     const onStaff=xx===CX-0.5||xx===CX+0.5;
     if(e<1){field[i]=1;owner[i]=h+1}
     else if(e<1.5&&field[i]>0&&!onStaff)field[i]=0;
    }
   }
   const ex=Math.round(hx-S.side*0.9),ey=Math.round(hy);
   if(ex>=0&&ex<W)field[ey*W+ex]=0; // eye
  }
 }
 return {field,owner,frame(t,pose){wings(t,pose.wingMotion,pose.open);snakes(t,pose.snakeMotion)}};
}


function easePose(cur,to,k){
 const mix=(a,b)=>a+(b-a)*k;
 return {...to,
  wingMotion:mix(cur.wingMotion,to.wingMotion),open:mix(cur.open,to.open),
  snakeMotion:[mix(cur.snakeMotion[0],to.snakeMotion[0]),mix(cur.snakeMotion[1],to.snakeMotion[1])],
  snakeInk:[mix(cur.snakeInk[0],to.snakeInk[0]),mix(cur.snakeInk[1],to.snakeInk[1])],
  staffInk:mix(cur.staffInk,to.staffInk),wingInk:mix(cur.wingInk,to.wingInk)};
}
function poseGap(a,b){
 return Math.abs(a.wingMotion-b.wingMotion)+Math.abs(a.open-b.open)+Math.abs(a.snakeMotion[0]-b.snakeMotion[0])+Math.abs(a.snakeMotion[1]-b.snakeMotion[1])
  +Math.abs(a.snakeInk[0]-b.snakeInk[0])+Math.abs(a.snakeInk[1]-b.snakeInk[1])+Math.abs(a.staffInk-b.staffInk)+Math.abs(a.wingInk-b.wingInk);
}


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
