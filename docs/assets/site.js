/* Deploy Axiom plugin catalog: one conductor, no libraries, no network.
   One requestAnimationFrame loop owns every moving thing: the chrome drift, the typed command,
   the caduceus, the Office pulses and demo, the ink-in reveals and the small timers.
   The loop sleeps when nothing is active and stops while the tab is hidden.
   Reduced motion, ?settled and ?demo=frame&t=N render the same states without any loop. */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
  var $ = function (s, r) { return (r || doc).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || doc).querySelectorAll(s)); };
  var qp = new URLSearchParams(location.search);
  // QA hooks: ?settled finishes every reveal; ?demo=frame&t=6.1 shows the Office at demo time 6.1 s, still.
  var FRAME = qp.get("demo") === "frame" ? parseFloat(qp.get("t") || "0") : null;
  var SETTLED = FRAME !== null || qp.has("settled");
  if (FRAME !== null) root.classList.add("frame");
  var mq = window.matchMedia("(prefers-reduced-motion: reduce)");
  var isStatic = function () { return mq.matches || SETTLED; };

  /* ------------------------------------------------------------ the conductor */
  var tasks = [], timers = [], raf = 0, last = 0, clock = 0;
  function wake() { if (!raf && !doc.hidden) { last = 0; raf = requestAnimationFrame(tick); } }
  function tick(ts) {
    raf = 0;
    if (doc.hidden) { last = 0; return; }
    if (!last) last = ts;
    var dt = Math.min(0.1, (ts - last) / 1000);
    last = ts; clock += dt;
    for (var i = timers.length - 1; i >= 0; i--) {
      if (clock >= timers[i].at) { var f = timers[i].fn; timers.splice(i, 1); f(); }
    }
    var busy = timers.length > 0;
    for (var k = 0; k < tasks.length; k++) {
      if (tasks[k].active()) { tasks[k].run(clock, dt); busy = true; }
    }
    if (busy) raf = requestAnimationFrame(tick); else last = 0;
  }
  function after(sec, fn) { timers.push({ at: clock + sec, fn: fn }); wake(); }
  doc.addEventListener("visibilitychange", function () { if (!doc.hidden) wake(); });
  function watch(el, cb, margin) {
    if (!("IntersectionObserver" in window)) { cb(true); return; }
    new IntersectionObserver(function (es) {
      es.forEach(function (e) { cb(e.isIntersecting); });
      wake();
    }, { rootMargin: margin || "80px" }).observe(el);
  }
  function announce(msg) { var l = $("#live"); if (l) l.textContent = msg; }

  /* ------------------------------------------------------------ chrome title + typed command */
  var h1 = $("h1.chrome"), hero = $(".hero"), heroIn = true;
  watch(hero, function (v) { heroIn = v; });
  var chromeAcc = 0;
  tasks.push({
    active: function () { return heroIn && !isStatic(); },
    run: function (t, dt) {
      chromeAcc += dt;
      if (chromeAcc > 0.06) { chromeAcc = 0; h1.style.setProperty("--chrome", ((t * 3.8) % 100).toFixed(2) + "%"); }
    }
  });

  var typedEl = $(".typed"), cursor = $(".cursor");
  var cmdFull = typedEl.textContent, cmdI = 0, cmdDone = isStatic(), cmdNext = 0.7, blinkAt = 0, parts = null;
  if (!cmdDone) {
    typedEl.innerHTML = "<span></span><span style=\"visibility:hidden\"></span>";
    parts = typedEl.children;
    parts[1].textContent = cmdFull;
  }
  tasks.push({
    active: function () { return heroIn && !isStatic(); },
    run: function (t) {
      if (!cmdDone && t >= cmdNext) {
        cmdI++;
        parts[0].textContent = cmdFull.slice(0, cmdI);
        parts[1].textContent = cmdFull.slice(cmdI);
        cmdNext = t + 0.05 + ((cmdI * 37) % 5) * 0.014;
        if (cmdI >= cmdFull.length) { cmdDone = true; blinkAt = t + 0.6; }
        cursor.classList.remove("off");
      } else if (cmdDone && t >= blinkAt) {
        cursor.classList.toggle("off");
        blinkAt = t + 0.53;
      }
    }
  });

  /* ------------------------------------------------------------ the caduceus */
  var C = window.AxiomCaduceus, engine = C.createEngine();
  var live = { waiting: 0, workers: 0, recent: false };
  var pose = C.targetPose(live);
  var cads = $$("[data-cad]").map(function (el) {
    return { el: el, box: $(".cad-box", el), pre: $("pre.cad", el), inView: false, html: "", ls: 0 };
  });
  function measureCad() {
    var cv = doc.createElement("canvas").getContext("2d");
    cads.forEach(function (c) {
      var fs = parseFloat(getComputedStyle(c.box).fontSize);
      cv.font = fs + "px " + getComputedStyle(c.pre).fontFamily;
      var d = 0.6 * fs - cv.measureText("\u28ff").width;   // put a braille glyph on the letters' pitch
      c.ls = Math.abs(d) < 0.05 ? 0 : Math.round(d * 100) / 100;
      c.html = "";
    });
  }
  function cadStep(t, instant, force) {
    var target = C.targetPose(live);
    pose = instant ? target : C.easePose(pose, target, 0.12);
    engine.frame(t, pose);
    cads.forEach(function (c) {
      if (!c.inView && !force) return;
      var h = C.paintHTML(engine, pose, c.ls);
      if (h !== c.html) { c.pre.innerHTML = h; c.html = h; }
      if (!c.box.classList.contains("live")) c.box.classList.add("live");
    });
  }
  cads.forEach(function (c) { watch(c.el, function (v) { c.inView = v; }, "120px"); });
  var cadNext = 0;
  tasks.push({
    active: function () { return !isStatic() && cads.some(function (c) { return c.inView; }); },
    run: function (t) {
      if (t < cadNext) return;
      cadNext = t + 1 / 24;
      cadStep(t, false, false);
    }
  });

  /* ------------------------------------------------------------ the Office: diagram, demo, terminal */
  var S = JSON.parse($("#demo-script").textContent);
  var SPIN = [0x0b, 0x19, 0x39, 0x38, 0x3c, 0x34, 0x26, 0x27, 0x07, 0x0f];   // braille "dots" spinner frames
  var SPIN_CH = "\u280b\u2819\u2839\u2838\u283c\u2834\u2826\u2827\u2807\u280f";
  var IDLE_MASK = 0x36;
  var NS = "http://www.w3.org/2000/svg";
  var SPOKES = ["code-review", "builder", "client-desk", "tester", "marketing"];
  var LIS = $$(".console li"), TRS = $$(".ledger tbody tr"), termEl = $("#term");

  function buildSvg(svg) {
    var layer = $(".pulses", svg), edges = {}, nodes = {}, labels = {};
    $$("line[data-edge]", svg).forEach(function (l) {
      var e = {
        x1: +l.getAttribute("x1"), y1: +l.getAttribute("y1"), x2: +l.getAttribute("x2"), y2: +l.getAttribute("y2"),
        dots: [], buf: []
      };
      e.len = Math.hypot(e.x2 - e.x1, e.y2 - e.y1);
      for (var i = 0; i < 6; i++) {
        var c = doc.createElementNS(NS, "circle");
        c.setAttribute("r", "1.4"); c.setAttribute("class", "pd"); c.setAttribute("opacity", "0");
        layer.appendChild(c); e.dots.push(c);
      }
      edges[l.getAttribute("data-edge")] = e;
    });
    $$("g[data-node]", svg).forEach(function (g) {
      nodes[g.getAttribute("data-node")] = { g: g, mode: "", mask: -1, dots: $$(".dot", g) };
    });
    $$("[data-label]", svg).forEach(function (t) { labels[t.getAttribute("data-label")] = t; });
    return { svg: svg, edges: edges, nodes: nodes, labels: labels, held: $(".held-x", svg), gate: $(".gate", svg) };
  }
  var svgs = $$(".office-svg").map(buildSvg);
  var officeEl = $("#office"), officeIn = false;
  watch(officeEl, function (v) { officeIn = v; });

  function within(t, r) { return t >= r[0] && t < r[1]; }
  var idleState = { nodes: {}, pulses: [], labels: {}, marks: {}, live: { waiting: 0, workers: 0, recent: false } };

  // The scripted run, as a pure function of demo time t (seconds). Every state on the page comes from here.
  function stateAt(t) {
    var st = { nodes: {}, pulses: [], labels: {}, marks: {}, live: { waiting: 0, workers: 0, recent: false } };
    if (t < 0) return st;
    var on = t < S.dur;
    st.nodes.orch = on ? (within(t, S.ask) ? "ask" : "lit") : "idle";
    st.nodes.owner = within(t, [S.askPulse[1], S.ask[1]]) ? "ask" : (within(t, S.approved) ? "lit" : "idle");
    S.order.forEach(function (id, i) {
      var m = "idle";
      if (on && t >= S.roster[i]) m = within(t, S.work) ? "work" : "lit";
      if (id === "client-desk" && within(t, S.held)) m = "held";
      st.nodes[id] = m;
      // discovery: one pulse out to each specialist as its name prints
      if (t >= S.roster[i] - 0.3 && t < S.roster[i] + 0.2) st.pulses.push({ e: id, s: (t - (S.roster[i] - 0.3)) / 0.5, rev: false, c: "" });
    });
    // work going out, evidence coming back
    if (within(t, S.work)) {
      SPOKES.forEach(function (id, i) {
        var ph = ((t - S.work[0] + i * 0.37) % 1.8) / 1.8;
        if (ph < 0.75) st.pulses.push({ e: id, s: ph / 0.75, rev: i % 2 === 1, c: "" });
      });
    }
    if (within(t, S.attempt)) st.pulses.push({ e: "stub-client-desk", s: (t - S.attempt[0]) / (S.attempt[1] - S.attempt[0]), rev: false, c: "red" });
    if (within(t, S.askPulse)) st.pulses.push({ e: "owner", s: (t - S.askPulse[0]) / (S.askPulse[1] - S.askPulse[0]), rev: false, c: "brass" });
    if (within(t, S.approve)) st.pulses.push({ e: "owner", s: (t - S.approve[0]) / (S.approve[1] - S.approve[0]), rev: true, c: "" });
    if (within(t, S.send)) st.pulses.push({ e: "out", s: (t - S.send[0]) / (S.send[1] - S.send[0]), rev: false, c: "" });
    st.labels.held = within(t, S.held);
    st.labels.ask = within(t, S.ask);
    st.labels.approved = within(t, S.approved);
    st.labels.sent = within(t, S.sent);
    st.marks.held = within(t, S.held);
    st.marks.gate = within(t, S.gate);
    st.live.workers = t >= S.discover[0] && t < S.work[0] ? 1 : (within(t, S.work) ? 2 : 0);
    st.live.waiting = within(t, S.ask) ? 1 : 0;
    st.live.recent = t >= S.done && t < S.dur + S.tail;
    return st;
  }

  function setMode(n, mode, spinIdx) {
    if (n.mode !== mode) { n.mode = mode; n.g.setAttribute("class", "node" + (mode && mode !== "idle" ? " " + mode : "")); }
    var mask = mode === "work" ? SPIN[spinIdx % SPIN.length] : IDLE_MASK;
    if (n.mask !== mask) {
      n.mask = mask;
      n.dots.forEach(function (d) {
        var b = +d.getAttribute("data-bit");
        d.setAttribute("class", "dot" + (mask & b ? " on" : ""));
      });
    }
  }
  // A pulse: a bright head with a short fading tail behind it. s runs 0..1 along the travel direction;
  // rev travels from the edge's end to its start.
  function pulse(e, s, rev, cls, a) {
    var step = 7 / e.len;
    for (var k = 0; k < 4; k++) {
      var back = s - k * step;
      if (back < 0 || back > 1) continue;
      var u = rev ? 1 - back : back;
      e.buf.push({ x: e.x1 + (e.x2 - e.x1) * u, y: e.y1 + (e.y2 - e.y1) * u, a: a * (1 - k * 0.24), c: cls, r: k === 0 ? 1.7 : 1.25 });
    }
  }
  function flush(model) {
    for (var id in model.edges) {
      var e = model.edges[id];
      for (var i = 0; i < e.dots.length; i++) {
        var d = e.dots[i], b = e.buf[i];
        if (b) {
          d.setAttribute("cx", b.x.toFixed(1)); d.setAttribute("cy", b.y.toFixed(1)); d.setAttribute("r", b.r);
          d.setAttribute("class", "pd" + (b.c ? " " + b.c : "")); d.setAttribute("opacity", b.a.toFixed(2));
        } else if (d.getAttribute("opacity") !== "0") d.setAttribute("opacity", "0");
      }
      e.buf.length = 0;
    }
  }
  var AMB = ["owner", "code-review", "client-desk", "builder", "tester", "marketing", "out"].map(function (id, k) {
    return { e: id, P: 6.2 + k * 0.85, ph: k * 1.7, rev: k % 2 === 1 };
  });
  var demoOn = false;

  function renderOffice(t, tr, clk, withPulses) {
    // t = demo time for the diagram (<0 = at rest); tr = demo time for the terminal (Infinity = everything)
    var st = t >= 0 ? stateAt(t) : idleState;
    var spinIdx = Math.floor(clk * 12.5);
    svgs.forEach(function (m) {
      if (!m.svg.getClientRects().length) return;
      for (var id in m.nodes) setMode(m.nodes[id], st.nodes[id] || "idle", spinIdx);
      for (var l in m.labels) m.labels[l].classList.toggle("on", !!st.labels[l]);
      m.held.classList.toggle("on", !!st.marks.held);
      m.gate.classList.toggle("on", !!st.marks.gate);
      if (withPulses) {
        var amb = demoOn ? 0.35 : 0.55;
        AMB.forEach(function (a) {
          var u = ((clk + a.ph) / a.P) % 1;
          if (u < 0.6 && m.edges[a.e]) pulse(m.edges[a.e], u / 0.6, a.rev, "", amb);
        });
        st.pulses.forEach(function (p) {
          if (m.edges[p.e]) pulse(m.edges[p.e], p.s, p.rev, p.c, 1);
        });
        flush(m);
      }
    });
    // the terminal
    LIS.forEach(function (li) { li.classList.toggle("on", +li.getAttribute("data-t") <= tr); });
    TRS.forEach(function (r) { r.classList.toggle("on", +r.getAttribute("data-t") <= tr); });
    if (termEl) termEl.classList.toggle("idle", tr < 0);
    // the caduceus follows the run
    live.waiting = st.live.waiting; live.workers = st.live.workers; live.recent = st.live.recent;
  }

  var runBtn = $("#run"), runT = runBtn ? $(".run-t", runBtn) : null, controls = $(".controls");
  var spinEl = $(".spin"), stateEl = $(".term-state");
  var demo = { t: -1, phase: "idle" };    // phase: idle | run | tail
  var trT = isStatic() ? Infinity : -1;   // how much of the transcript is showing
  function setUi(label, state, spinning) {
    if (runT) runT.textContent = label;
    if (stateEl) stateEl.textContent = state;
    if (controls) controls.classList.toggle("live", spinning);
  }
  var offAcc = 0;
  tasks.push({
    active: function () { return !isStatic() && (demo.phase !== "idle" || officeIn); },
    run: function (t, dt) {
      if (demo.phase !== "idle") {
        demo.t += dt;
        trT = Math.min(demo.t, S.dur);
        if (demo.phase === "run" && demo.t >= S.dur) {
          demo.phase = "tail"; demoOn = false;
          setUi("Run again", "done", false);
          if (spinEl) spinEl.textContent = "";
          announce("Demo run finished. The owner approved one send, it left through the gate, and a receipt was written. Simulated.");
        }
        if (demo.t >= S.dur + S.tail) { demo.phase = "idle"; demo.t = -1; }
      }
      offAcc += dt;
      if (offAcc < 1 / 30) return;
      offAcc = 0;
      if (spinEl && demo.phase === "run") spinEl.textContent = SPIN_CH.charAt(Math.floor(t * 12.5) % SPIN_CH.length);
      renderOffice(demo.t, trT, t, true);
    }
  });
  function startDemo() {
    demo.t = 0; demo.phase = "run"; demoOn = true; trT = 0;
    setUi("Stop", "running", true);
    announce("Demo run started. Simulated. Nothing is sent.");
    wake();
  }
  function stopDemo() {
    demo.t = -1; demo.phase = "idle"; demoOn = false; trT = -1;
    if (spinEl) spinEl.textContent = "";
    setUi("Run the demo", "ready", false);
    renderOffice(-1, -1, clock, true);
  }
  // Reduced motion: no timer, no travel. The whole transcript is showing; the button steps through it by hand.
  var stepI = -1;
  function stepTo(i) {
    stepI = i;
    var t = i < 0 ? -1 : S.steps[i];
    var lastStep = S.steps.length - 1;
    renderOffice(t, i < 0 ? Infinity : t, 0, false);
    cadStep(0, true, true);
    setUi(i < 0 ? "Step through" : (i === lastStep ? "Show it all" : "Next step"), i < 0 ? "done" : "step " + (i + 1) + " of " + S.steps.length, false);
    var shown = LIS.filter(function (li) { return li.classList.contains("on"); });
    if (shown.length) announce(shown[shown.length - 1].textContent);
  }
  if (runBtn) {
    runBtn.disabled = false;
    runBtn.addEventListener("click", function () {
      if (isStatic()) { stepTo(stepI >= S.steps.length - 1 ? -1 : stepI + 1); return; }
      if (demo.phase === "run") stopDemo(); else startDemo();
    });
  }

  /* ------------------------------------------------------------ the flash sheet: copy and ink-in */
  var copyFallback = function (text) {
    var ta = doc.createElement("textarea");
    ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
    doc.body.appendChild(ta); ta.select();
    var ok = false; try { ok = doc.execCommand("copy"); } catch (e) { ok = false; }
    doc.body.removeChild(ta); return ok;
  };
  $$(".copy").forEach(function (b) {
    b.hidden = false;
    b.addEventListener("click", function () {
      var code = $("code", b.parentNode), text = code.textContent;
      var done = function (ok) {
        b.textContent = ok ? "Copied" : "Select";
        announce(ok ? "Copied to the clipboard." : "Copy was blocked. The command is selected for you to copy.");
        if (!ok) { var r = doc.createRange(); r.selectNodeContents(code); var s = getSelection(); s.removeAllRanges(); s.addRange(r); }
        after(1.8, function () { b.textContent = "Copy"; });
      };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(copyFallback(text)); });
      else done(copyFallback(text));
    });
  });

  // Each piece's mark is a 64 x 64 one-bit image (assets/bits.js). Inking it in = switching its pixels on
  // in the order of a Bayer matrix biased top to bottom, so it reads as a dither pass that settles.
  var BAY8 = (function b(n) {
    if (n === 1) return [[0]];
    var m = b(n / 2), o = [], i, j, h = n / 2;
    for (i = 0; i < n; i++) o.push([]);
    for (i = 0; i < h; i++) for (j = 0; j < h; j++) {
      var v = 4 * m[i][j];
      o[i][j] = v; o[i][j + h] = v + 2; o[i + h][j] = v + 3; o[i + h][j + h] = v + 1;
    }
    return o;
  })(8);
  var BITS = window.AXIOM_BITS || {};
  var pieces = $$(".piece").map(function (el, idx) {
    var id = el.getAttribute("data-piece"), cv = $("canvas", el), px = [];
    if (BITS[id]) {
      var bin = atob(BITS[id]);
      for (var i = 0; i < 64 * 64; i++) {
        if ((bin.charCodeAt(i >> 3) << (i & 7)) & 0x80) {
          var x = i & 63, y = i >> 6;
          px.push([x, y, Math.min(0.999, (y / 64) * 0.55 + ((BAY8[y & 7][x & 7] + 0.5) / 64) * 0.45)]);
        }
      }
    }
    return { el: el, cv: cv, ctx: cv.getContext("2d"), px: px, rule: $(".inkrule", el), p: 0, state: 0, delay: 0 };
  });
  function drawPiece(pc, p) {
    var c = pc.ctx; c.clearRect(0, 0, 64, 64); c.fillStyle = "#121316";
    for (var i = 0; i < pc.px.length; i++) if (pc.px[i][2] <= p) c.fillRect(pc.px[i][0], pc.px[i][1], 1, 1);
  }
  pieces.forEach(function (pc, i) {
    if (!pc.px.length || isStatic()) {
      if (pc.px.length) drawPiece(pc, 1);
      else { pc.cv.style.display = "none"; $("img", pc.el).style.visibility = "visible"; }
      pc.state = 2; pc.el.classList.add("inked");
      return;
    }
    drawPiece(pc, 0);
    pc.rule.style.transform = "scaleX(0)";
    watch(pc.el, function (v) {
      if (v && pc.state === 0) { pc.state = 1; pc.delay = (i % 3) * 0.14; }
    }, "-60px 0px -60px 0px");
  });
  tasks.push({
    active: function () { return pieces.some(function (p) { return p.state === 1; }); },
    run: function (t, dt) {
      pieces.forEach(function (pc) {
        if (pc.state !== 1) return;
        if (pc.delay > 0) { pc.delay -= dt; return; }
        pc.p = Math.min(1, pc.p + dt / 1.15);
        drawPiece(pc, pc.p);
        var e = 1 - Math.pow(1 - Math.min(1, pc.p * 1.25), 3);
        pc.rule.style.transform = "scaleX(" + e.toFixed(3) + ")";
        if (pc.p >= 1) { pc.state = 2; pc.rule.style.transform = ""; pc.el.classList.add("inked"); }
      });
    }
  });

  /* ------------------------------------------------------------ start */
  var rt = 0;
  window.addEventListener("resize", function () {
    clearTimeout(rt);
    rt = setTimeout(function () { measureCad(); cadStep(clock, true, true); }, 150);
  });
  function init() {
    measureCad();
    if (FRAME !== null) {
      demo.t = FRAME; trT = FRAME;
      renderOffice(FRAME, FRAME, FRAME, true);
      cadStep(FRAME, true, true);
      setUi("Run the demo", "t " + FRAME.toFixed(1) + " s", FRAME >= 0 && FRAME < S.done);
      if (spinEl && FRAME < S.done) spinEl.textContent = SPIN_CH.charAt(Math.floor(FRAME * 12.5) % SPIN_CH.length);
      return;
    }
    renderOffice(-1, trT, clock, false);
    cadStep(0, true, true);
    if (isStatic()) setUi("Step through", "done", false); else setUi("Run the demo", "ready", false);
    wake();
  }
  if (mq.addEventListener) mq.addEventListener("change", function () { location.reload(); });
  (doc.fonts && doc.fonts.ready ? doc.fonts.ready : Promise.resolve()).then(init, init);
})();
