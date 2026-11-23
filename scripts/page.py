"""The catalog page, as markup. Imported by build.py; styles and behaviour live in docs/assets/.

Everything that states a fact about a plugin comes in through `ctx` (from data/plugins.json).
This file owns the expression: the hero, the Office diagram (two SVG layouts, drawn on a
character grid), the demo script and the flash sheet.
"""
import json
from html import escape

# ------------------------------------------------------------------ the Office diagram
CW, RH = 8, 16            # one terminal cell, in drawing units
BIT = [[0x01, 0x08], [0x02, 0x10], [0x04, 0x20], [0x40, 0x80]]   # braille dot bits, [row][col]
IDLE_MASK = 0x36          # the resting sigil, braille dots 2 3 5 6

SPECS = [  # id, label, side, row of the box's first line
    ("code-review", "CODE REVIEW", "L", 7),
    ("builder", "BUILDER", "L", 13),
    ("client-desk", "CLIENT DESK", "R", 7),
    ("tester", "TESTER", "R", 13),
]
LAYOUTS = {
    "wide": dict(margin=6, pad=3, sw=22, sp=9, ow=26),
    "narrow": dict(margin=1, pad=1, sw=13, sp=2, ow=14),
}
ROWS = 22
LABELS = {
    "wide": dict(held="held: specialists don't send", ask="approve 1 send?", approved="approved", sent="sent",
                 gate="permission prompt"),
    "narrow": dict(held="held", ask="approve?", approved="approved", sent="sent", gate="prompt"),
}
DIAGRAM_DESC = ("The owner connects only to the orchestrator, through the front door. The orchestrator "
                "connects to five specialists: code review, builder, client desk, tester and marketing. "
                "The specialists have no door to the outside. One gate, on the orchestrator's outbound line, "
                "is where a send leaves, through Claude Code's permission prompt.")


def _sigil(cx, cy, mask=IDLE_MASK):
    out = []
    for r in range(4):
        for c in range(2):
            on = " on" if mask & BIT[r][c] else ""
            out.append(f'<circle class="dot{on}" data-bit="{BIT[r][c]}" cx="{cx + (c - .5) * 4.4:.1f}" '
                       f'cy="{cy + (r - 1.5) * 3.6:.1f}" r="1.15"/>')
    return f'<g class="sigil">{"".join(out)}</g>'


def _frame_path(x0, y0, x1, y1, gaps):
    """A rectangle outline as separate segments so a side can have a gap (door, gate)."""
    segs = []

    def side(a, b, fixed, horizontal, gap):
        parts = [(a, b)]
        if gap:
            lo, hi = gap
            parts = [(a, lo), (hi, b)]
        for p, q in parts:
            segs.append(f"M{p:.1f} {fixed:.1f}H{q:.1f}" if horizontal else f"M{fixed:.1f} {p:.1f}V{q:.1f}")

    side(x0, x1, y0, True, gaps.get("top"))
    side(x0, x1, y1, True, gaps.get("bottom"))
    side(y0, y1, x0, False, gaps.get("left"))
    side(y0, y1, x1, False, gaps.get("right"))
    return "".join(segs)


def office_svg(kind):
    g = LAYOUTS[kind]
    m, pad, sw, sp, ow = g["margin"], g["pad"], g["sw"], g["sp"], g["ow"]
    fw = 2 + 2 * pad + 2 * sw + 2 * sp + ow
    cols = fw + 2 * m
    L = LABELS[kind]
    fl, fr, ft, fb = m, m + fw - 1, 5, 21
    lx = m + 1 + pad
    ox = lx + sw + sp
    rx = ox + ow + sp
    X = lambda c: c * CW            # left edge of a cell
    cx = lambda c: c * CW + CW / 2  # centre of a cell
    cy = lambda r: r * RH + RH / 2
    cxo = X(ox) + ow * CW / 2       # the centre line of the orchestrator column
    W, H = cols * CW, ROWS * RH

    def box(c0, r0, w, h):
        return f'x="{cx(c0):.1f}" y="{cy(r0):.1f}" width="{(w - 1) * CW}" height="{(h - 1) * RH}"'

    out = [f'<svg class="office-svg office-{kind}" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           f'role="img" aria-labelledby="od-{kind}-t od-{kind}-d" data-kind="{kind}" focusable="false">',
           f'<title id="od-{kind}-t">The Axiom Office: one orchestrator, five specialists, the owner outside</title>',
           f'<desc id="od-{kind}-d">{escape(DIAGRAM_DESC)}</desc>']
    # the wall: two thin lines, a door on top, a gate on the right
    door = (cxo - (3 if kind == "wide" else 2) * CW, cxo + (3 if kind == "wide" else 2) * CW)
    gate = (cy(11) - 14, cy(11) + 14)
    outer = _frame_path(cx(fl), cy(ft), cx(fr), cy(fb), {"top": door, "right": gate})
    inner = _frame_path(cx(fl) + 3, cy(ft) + 3, cx(fr) - 3, cy(fb) - 3, {"top": door, "right": gate})
    out.append(f'<path class="wall" d="{outer}"/><path class="wall wall2" d="{inner}"/>')

    # edges: orchestrator -> target (the page animates along this direction)
    def edge(eid, x1, y1, x2, y2, cls="edge"):
        return (f'<line class="{cls}" data-edge="{eid}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')

    out.append(edge("owner", cxo, cy(7), cxo, cy(2)))
    out.append(edge("marketing", cxo, cy(15), cxo, cy(17)))
    out.append(edge("out", cx(ox + ow - 1), cy(11), cx(cols - 1), cy(11)))
    for sid, _label, side, r0 in SPECS:
        y = cy(r0 + 1)
        if side == "L":
            out.append(edge(sid, cx(ox), y, cx(lx + sw - 1), y))
            out.append(edge("stub-" + sid, cx(lx), y, cx(fl), y, "stub"))
        else:
            out.append(edge(sid, cx(ox + ow - 1), y, cx(rx), y))
            out.append(edge("stub-" + sid, cx(rx + sw - 1), y, cx(fr), y, "stub"))
    out.append(edge("stub-marketing", cxo, cy(19), cxo, cy(fb), "stub"))

    # nodes
    def node(nid, label, c0, r0, w, h, sig=False, extra=""):
        mid = r0 + (h - 1) / 2
        tx = X(c0) + w * CW / 2
        s = _sigil(X(c0) + 17, cy(mid)) if sig else ""
        return (f'<g class="node" data-node="{nid}"><rect {box(c0, r0, w, h)}/>{s}'
                f'<text class="nm" x="{tx:.1f}" y="{cy(mid) + 4.6:.1f}" text-anchor="middle">{label}</text>{extra}</g>')

    out.append(node("owner", "OWNER", ox, 0, ow, 3))
    sub = ""
    if kind == "wide":
        sub = (f'<text class="sub" x="{cxo:.1f}" y="{cy(13) + 4.2:.1f}" text-anchor="middle">the one front door</text>'
               f'<text class="sub" x="{cxo:.1f}" y="{cy(14) + 4.2:.1f}" text-anchor="middle">alone holds sensitive data</text>')
    orch_label_y = cy(11) + 4.6
    orch = (f'<g class="node" data-node="orch"><rect {box(ox, 7, ow, 9)}/>{_sigil(cxo, cy(9))}'
            f'<text class="nm" x="{cxo:.1f}" y="{orch_label_y:.1f}" text-anchor="middle">ORCHESTRATOR</text>{sub}</g>')
    out.append(orch)
    for sid, label, side, r0 in SPECS:
        out.append(node(sid, label, lx if side == "L" else rx, r0, sw, 3, sig=(kind == "wide")))
    out.append(node("marketing", "MARKETING", ox, 17, ow, 3, sig=(kind == "wide")))

    # fixed labels and the places the demo writes to
    out.append(f'<text class="lbl dim" x="{cxo - 12:.1f}" y="{cy(4) + 4.2:.1f}" text-anchor="end">front door</text>')
    out.append(f'<text class="lbl dim" x="{cx(fr) - 14:.1f}" y="{cy(12) + 4.2:.1f}" text-anchor="end">{L["gate"]}</text>')
    out.append(f'<text class="lbl brass" data-label="ask" x="{cxo + 12:.1f}" y="{cy(4) + 4.2:.1f}">{escape(L["ask"])}</text>')
    out.append(f'<text class="lbl stone" data-label="approved" x="{cxo + 12:.1f}" y="{cy(4) + 4.2:.1f}">{escape(L["approved"])}</text>')
    out.append(f'<text class="lbl red" data-label="held" x="{cx(fr) - 8:.1f}" y="{cy(10) + 4.2:.1f}" text-anchor="end">{escape(L["held"])}</text>')
    if kind == "wide":
        out.append(f'<text class="lbl stone" data-label="sent" x="{cx(fr) + 10:.1f}" y="{cy(10) + 4.2:.1f}">{L["sent"]}</text>')
    else:
        out.append(f'<text class="lbl stone" data-label="sent" x="{cx(fr) - 8:.1f}" y="{cy(10) + 4.2:.1f}" text-anchor="end">{L["sent"]}</text>')
    # the red cross where a specialist's send meets the wall, and the gate
    sx, sy = cx(fr), cy(8)
    out.append(f'<path class="mark held-x" data-mark="held" d="M{sx - 5:.1f} {sy - 5:.1f}l10 10m0 -10l-10 10"/>')
    gx, gy = cx(fr), cy(11)
    out.append(f'<path class="mark gate" data-mark="gate" d="M{gx:.1f} {gy - 6:.1f}l6 6l-6 6l-6 -6z"/>')
    # arrow head on the outbound line
    ax, ay = cx(cols - 1), cy(11)
    out.append(f'<path class="arrow" d="M{ax - 5:.1f} {ay - 3.5:.1f}L{ax:.1f} {ay:.1f}L{ax - 5:.1f} {ay + 3.5:.1f}"/>')
    out.append('<g class="pulses"></g></svg>')
    return "".join(out)


# ------------------------------------------------------------------ the demo script
ROSTER = ["code-review", "builder", "client-desk", "tester", "marketing"]
DEMO = {
    "dur": 12.0, "tail": 4.0, "spin": [0.0, 11.1],
    "roster": [1.0, 1.35, 1.7, 2.05, 2.4],
    "discover": [0.5, 3.0], "work": [3.0, 10.8],
    "attempt": [5.0, 5.6], "held": [5.6, 8.0],
    "ask": [7.0, 9.0], "askPulse": [7.0, 7.8],
    "approve": [9.0, 9.7], "approved": [9.0, 10.0],
    "send": [9.8, 10.8], "gate": [10.1, 10.7], "sent": [10.3, 11.8],
    "done": 11.1,
    "steps": [0.5, 2.4, 3.0, 5.6, 7.0, 9.0, 10.3, 11.1],
    "order": ROSTER,
}
CONSOLE = [  # t, class, text
    (0.0, "dim", "demo run \u00b7 simulated \u00b7 nothing is sent"),
    (0.5, "", "example team assembled"),
] + [(t, "dim", f"  + {n}") for t, n in zip(DEMO["roster"], ROSTER)] + [
    (3.0, "", "orchestrator: work goes out to the team"),
    (5.0, "", "client-desk: tries to send a message"),
    (5.6, "red", "front door: held \u00b7 specialists don't send"),
    (7.0, "brass", "orchestrator: asks owner to approve 1 send"),
    (9.0, "", "owner: approved"),
    (9.8, "", "orchestrator: 1 approved send leaves"),
    (10.9, "", "run-receipts: receipt written"),
]
LEDGER = [  # t, ts, agent, kind, outcome, via
    (5.8, "00:05", "client-desk", "tool_blocked", "held", "tripwire"),
    (10.3, "00:10", "orchestrator", "send", "sent", "gatekeeper"),
    (11.1, "00:11", "orchestrator", "run", "completed", "run-receipts"),
]


def console_html():
    items = "\n".join(f'          <li data-t="{t}"{f" class={chr(34)}{c}{chr(34)}" if c else ""}>{escape(s)}</li>'
                      for t, c, s in CONSOLE)
    return f'<ol class="console" role="log" aria-label="Demo run output, simulated">\n{items}\n        </ol>'


def ledger_html():
    rows = "\n".join(
        f'            <tr data-t="{t}"><td>{ts}</td><td>{ag}</td><td>{k}</td><td>{o}</td><td class="via">{v}</td></tr>'
        for t, ts, ag, k, o, v in LEDGER)
    return f"""<table class="ledger">
          <caption class="sr">Ledger of the simulated run</caption>
          <thead><tr><th scope="col">ts</th><th scope="col">agent</th><th scope="col">kind</th><th scope="col">outcome</th><th scope="col" class="via">from</th></tr></thead>
          <tbody>
{rows}
          </tbody>
        </table>"""


# ------------------------------------------------------------------ the page
def piece(ctx, name, n):
    P = ctx["plugins"][name]
    d = escape(P["display"])
    icon = P["icon"]
    return f"""        <article class="piece{" feature" if P.get("feature") else ""}" id="{escape(name)}" data-piece="{escape(name)}">
          <span class="inkrule" aria-hidden="true"></span>
          <div class="piece-top">
            <div class="mark" aria-hidden="true"><img src="icons/1bit/{escape(icon)}" width="128" height="128" alt="" loading="lazy" decoding="async"><canvas width="64" height="64"></canvas></div>
            <div class="who"><p class="no">No. {n:02d}</p><p class="slug">{escape(name)}</p><ul class="meta"><li class="tag">{escape(P['mechanism'])}</li><li>{escape(ctx['status'](P))}</li></ul></div>
          </div>
          <h4>{d}</h4>
          <p class="rule"><span class="rl">Inks in</span>{escape(P['rule'])}</p>
          <p class="blurb">{escape(P['blurb'])}</p>
          <div class="cmdbox"><pre><code>{escape(ctx['install_cmd'](name))}</code></pre><button class="copy" type="button" hidden aria-label="Copy the install command for {d}">Copy</button></div>
          <p class="hermes">{"Hermes Agent original" if P.get("original", True) else "Source"}: <a href="{escape(ctx['repo_url'](P))}">{escape(P['repo'])}</a></p>
          <p class="links"><a href="{escape(ctx['tree_url'](P))}" aria-label="{d} repository folder">Repository</a><a href="{escape(ctx['readme_url'](P))}" aria-label="{d} README">README</a></p>
        </article>"""


def build_page(ctx):
    D = ctx["data"]
    SITE = ctx["site"]
    desc = (f"{ctx['h1']}: {ctx['lede']} Version 0.1, free and open source (MIT). "
            f"Eleven plugins for Claude Code that install from GitHub.")
    og_alt = "The Agent With The Axiom Tattoo: a braille caduceus and the Deploy Axiom mark. Axiom Office for Claude, 11 plugins."
    n = 0
    sheets = []
    for g in D["groups"]:
        pcs = []
        for name in g["plugins"]:
            n += 1
            pcs.append(piece(ctx, name, n))
        count = len(g["plugins"])
        sheets.append(f"""      <section class="sheet" id="{g['id']}" aria-labelledby="h-{g['id']}">
        <span class="crop tl" aria-hidden="true"></span><span class="crop tr" aria-hidden="true"></span><span class="crop bl" aria-hidden="true"></span><span class="crop br" aria-hidden="true"></span>
        <header class="sheet-head"><h3 id="h-{g['id']}">{escape(g['title'])}</h3><p class="count">{count} {"piece" if count == 1 else "pieces"}</p></header>
        <div class="pieces">
{chr(10).join(pcs)}
        </div>
      </section>""")
    legend = "\n".join(f'        <li><span class="tag">{t}</span><span>{escape(s)}</span></li>' for t, s in ctx["tag_legend"])
    three = "\n".join(f"        <li>{escape(x)}</li>" for x in ctx["lines"])
    notes = "\n".join(f"        <li>{escape(x)}</li>" for x in ctx["notes"])
    demo_json = json.dumps(DEMO, separators=(",", ":")).replace("</", "<\\/")
    html = f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(ctx['h1'])} \u00b7 Deploy Axiom</title>
<meta name="description" content="{escape(desc)}">
<meta name="theme-color" content="#0c0d0f">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Deploy Axiom">
<meta property="og:title" content="{escape(ctx['h1'])} \u00b7 Deploy Axiom">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:image" content="{ctx['base_url']}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{escape(og_alt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(ctx['h1'])} \u00b7 Deploy Axiom">
<meta name="twitter:description" content="{escape(desc)}">
<meta name="twitter:image" content="{ctx['base_url']}og.png">
<meta name="twitter:image:alt" content="{escape(og_alt)}">
<link rel="canonical" href="{ctx['base_url']}">
<link rel="icon" type="image/svg+xml" href="mark.svg">
<link rel="preload" href="fonts/cinzel-latin-wght.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/ibm-plex-mono-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/site.css">
<script>document.documentElement.className="js"</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="bar"><div class="wrap"><img src="mark.svg" alt="" width="22" height="20"><span class="brand">Deploy Axiom</span><span class="sub">Plugins for Claude Code and Hermes Agent</span></div></header>
<main id="main">
  <section class="hero" aria-labelledby="h-hero">
    <div class="wrap hero-grid">
      <div class="hero-cad" data-cad="hero"><div class="cad-box"><img class="cad-still" src="assets/caduceus.svg" alt="" width="88" height="72"><pre class="cad" aria-hidden="true"></pre></div></div>
      <div class="hero-copy">
        <p class="state">{escape(ctx['status_line'])}</p>
        <h1 id="h-hero" class="chrome">{escape(ctx['h1'])}</h1>
        <p class="label axiom-label">The axiom</p>
        <p class="axiom">Nothing sends, spends, or spins without the one who holds the gate.</p>
        <p class="cmd" aria-label="python deploy.py axiom"><span class="prompt" aria-hidden="true">$</span> <span class="typed" aria-hidden="true">python deploy.py axiom</span><span class="cursor" aria-hidden="true"></span></p>
        <p class="lede">{escape(ctx['lede'])}</p>
        <div class="install">
          <p class="label">Install the Office</p>
          <div class="cmdbox"><pre><code>claude plugin marketplace add {escape(D['catalog_repo'])}
{escape(ctx['install'])}</code></pre><button class="copy" type="button" hidden aria-label="Copy the install commands for the Axiom Office">Copy</button></div>
        </div>
        <div class="actions">
          <a class="btn" href="{SITE}">{escape(ctx['cta'])}</a>
          <p class="note">{escape(ctx['cta_note'])}</p>
        </div>
      </div>
    </div>
  </section>

  <section class="office" id="office" aria-labelledby="h-office">
    <div class="wrap">
      <p class="label">The Office</p>
      <h2 id="h-office">One front door.</h2>
      <div class="controls">
        <button class="run" type="button" id="run" disabled aria-describedby="run-note"><span class="run-t">Run the demo</span></button>
        <p class="chip"><span class="chip-dot" aria-hidden="true"></span>Demo run \u00b7 simulated</p>
        <p class="note" id="run-note">An example team and an example run. Nothing is sent.</p>
      </div>
      <figure class="office-fig">
        {office_svg('wide')}
        {office_svg('narrow')}
      </figure>
      <div class="office-low">
        <div class="status-cad" data-cad="office"><div class="cad-box"><img class="cad-still" src="assets/caduceus.svg" alt="" width="88" height="72"><pre class="cad" aria-hidden="true"></pre></div><p class="cad-cap">Serpents light while the team works. Amber and still: waiting on the owner. Wings open: a run finished.</p></div>
        <div class="term" id="term">
          <div class="term-head"><span class="term-t">axiom office \u00b7 demo</span><span class="term-s"><span class="spin" aria-hidden="true"></span><span class="term-state">ready</span></span></div>
          <div class="console-wrap">{console_html()}<p class="hint" aria-hidden="true">Press Run the demo. About twelve seconds, simulated.</p></div>
          {ledger_html()}
          <p class="term-note">Simulated rows, shaped like Tripwire and Run Receipts lines (those are separate plugins; the Office itself writes nothing to disk). The words are from their READMEs. Nothing here is a real send.</p>
        </div>
      </div>
      <p class="realrule"><span class="rl">The rule is real</span>Specialists cannot send outside. A subagent or teammate is refused send-like tools, and shell lines that send. Only the orchestrator can, and its sends still go through Claude Code\u2019s normal permission prompt. It is not a sandbox: the shell check cannot follow a script or code in another language. <a href="{ctx['readme_url'](ctx['plugins']['axiom-office'])}">Office README</a></p>
      <ul class="three">
{three}
      </ul>
      <script type="application/json" id="demo-script">{demo_json}</script>
    </div>
  </section>

  <section class="parts" id="parts" aria-labelledby="h-parts">
    <div class="wrap">
      <p class="label">Plugins</p>
      <h2 id="h-parts">The flash sheet</h2>
      <p class="intro">Rules, inked in, not instructed. {escape(ctx['parts_intro'])}</p>
      <div class="stencil">
        <p class="label">The stencil</p>
        <p>Add the whole catalog once, then install any part by name.</p>
        <div class="cmdbox"><pre><code>claude plugin marketplace add {escape(D['catalog_repo'])}</code></pre><button class="copy" type="button" hidden aria-label="Copy the catalog command">Copy</button></div>
      </div>
      <ul class="legend" aria-label="What the tags mean">
{legend}
      </ul>
{chr(10).join(sheets)}
      <section class="notes" aria-labelledby="h-notes">
        <h3 id="h-notes">Before you install</h3>
        <ul class="fine">
{notes}
        </ul>
      </section>
    </div>
  </section>
</main>
<footer>
  <div class="wrap">
    <img class="lockup" src="assets/deploy-axiom-lockup-stone-on-ink.svg" alt="Deploy Axiom" width="1059" height="220">
    <p class="foot-line"><a href="{SITE}">deployaxiom.com</a> \u00b7 MIT licensed</p>
    <p class="foot-line dim">Not affiliated with or endorsed by Anthropic.</p>
  </div>
</footer>
<p class="sr" id="live" role="status" aria-live="polite"></p>
<script src="assets/bits.js"></script>
<script src="assets/caduceus.js"></script>
<script src="assets/site.js"></script>
</body>
</html>
"""
    return html
