#!/usr/bin/env python3
"""Regenerate marketplace.json, docs/index.html and README.md from data/plugins.json.

Run from anywhere:  python3 scripts/build.py
Every statement about a plugin lives in data/plugins.json and comes from that
plugin's own README. Edit the data file, not the generated files.
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "plugins.json").read_text())
GH = "https://github.com/percyhendrux123-prog"
SITE = "https://deployaxiom.com"
# Assumed GitHub Pages address; used only for the og:image URL.
BASE_URL = "https://percyhendrux123-prog.github.io/axiom-plugins/"
MP = DATA["marketplace"]
PLUGINS = DATA["plugins"]

OFFICE_H1 = "Axiom Office for Claude"
OFFICE_LEDE = ("One orchestrator, a team of specialists you can see but not talk past, "
               "and your rules enforced as code.")
OFFICE_LINES = [
    "Discovery decides the team.",
    "One front door: you talk only to the orchestrator, which alone holds sensitive data.",
    "Every send, refusal and run leaves a receipt.",
]
OFFICE_STATUS = "In build. Not released yet."
CTA_TEXT = "Talk to Deploy Axiom"
PARTS_INTRO = ("Ten plugins for Claude Code, each with a Hermes Agent original. "
               "Each one installs on its own.")
TAG_LEGEND = [
    ("skill", "Instructions Claude loads when the task matches. No code runs."),
    ("hook", "A script Claude Code runs on an event, such as before a tool call."),
    ("mod", "JavaScript that runs inside Claude Code."),
]
NOTES = [
    "Hook and mod plugins run code with your permissions. Each README has a \u201cBefore you install\u201d "
    "section that lists what the plugin reads, writes and calls.",
    "Plugins with hooks, scripts or mods are not eligible for Anthropic\u2019s plugin directory until the "
    "publisher is verified, so they install from GitHub.",
    "Not affiliated with or endorsed by Anthropic.",
]
FOOTER = "Deploy Axiom \u00b7 deployaxiom.com \u00b7 MIT licensed"


def install_cmd(name):
    return f"claude plugin install {name}@{MP}"


def status(p):
    return "Directory: in review" if p["directory"] else "Install from GitHub"


def readme_url(p):
    return f"{GH}/{p['repo']}/blob/main/claude-plugin/{p['folder']}/README.md"


def repo_url(p):
    return f"{GH}/{p['repo']}"


def tree_url(p):
    return f"{GH}/{p['repo']}/tree/main/claude-plugin/{p['folder']}"


# ---------------------------------------------------------------- marketplace
def build_marketplace():
    entries = []
    for name, p in PLUGINS.items():
        entries.append({
            "name": name,
            "displayName": p["display"],
            "source": {"source": "git-subdir", "url": f"https://github.com/percyhendrux123-prog/{p['repo']}.git",
                       "path": f"claude-plugin/{p['folder']}", "ref": "main"},
            "description": p["entry_description"],
            "homepage": repo_url(p),
            "license": "MIT",
            "category": next(g["id"] for g in DATA["groups"] if name in g["plugins"]),
            "tags": p["tags"],
        })
    doc = {
        "name": MP,
        "owner": {"name": "Deploy Axiom", "url": SITE},
        "metadata": {"description": "Plugins for Claude Code from Deploy Axiom. Each has a Hermes Agent original."},
        "plugins": entries,
    }
    (ROOT / ".claude-plugin" / "marketplace.json").write_text(json.dumps(doc, indent=2) + "\n")


# ---------------------------------------------------------------------- page
CSS = """
@font-face{font-family:Geist;src:url(fonts/geist-latin-wght-normal.woff2) format("woff2");font-weight:100 900;font-display:swap}
@font-face{font-family:"IBM Plex Mono";src:url(fonts/ibm-plex-mono-latin-400-normal.woff2) format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"IBM Plex Mono";src:url(fonts/ibm-plex-mono-latin-500-normal.woff2) format("woff2");font-weight:500;font-display:swap}
:root{--ink:#121316;--panel:#17181B;--rule:#2C2D31;--dim:#96928A;--mid:#CDC8BD;--text:#DEDAD1;--stone:#F2EEE6;--brass:#8C7350;
--sans:Geist,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
--mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
--gut:clamp(20px,5vw,56px)}
*{box-sizing:border-box}
html{background:var(--ink);color-scheme:dark;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--ink);color:var(--text);font:400 1rem/1.6 var(--sans);overflow-wrap:break-word}
.wrap{max-width:1180px;margin:0 auto;padding:0 var(--gut)}
a{color:var(--stone);text-decoration-thickness:1px;text-underline-offset:3px}
a:hover{text-decoration-thickness:2px}
:focus-visible{outline:2px solid var(--stone);outline-offset:3px}
.skip{position:absolute;left:-999px;top:8px;background:var(--stone);color:var(--ink);padding:10px 14px;z-index:9}
.skip:focus{left:8px}
.bar{border-bottom:1px solid var(--rule)}
.bar .wrap{display:flex;align-items:center;gap:10px;min-height:56px}
.bar img{width:22px;height:20px;display:block}
.bar span{font-weight:600;color:var(--stone);letter-spacing:-.01em}
.bar .sub{margin-left:auto;font:400 .75rem/1 var(--mono);color:var(--dim);text-transform:uppercase;letter-spacing:.08em}
.label{font:500 .75rem/1.4 var(--mono);color:var(--dim);text-transform:uppercase;letter-spacing:.1em;margin:0 0 14px}
.label::before{content:"";display:inline-block;width:18px;height:1px;background:var(--brass);vertical-align:middle;margin-right:10px}
h1,h2,h3{font-family:var(--sans);color:var(--stone);margin:0}
h1{font-weight:640;font-size:clamp(2.1rem,6.4vw,3.6rem);line-height:1.06;letter-spacing:-.035em}
h2{font-weight:640;font-size:clamp(1.5rem,3.6vw,2.1rem);line-height:1.15;letter-spacing:-.03em}
h3{font-weight:600;font-size:1.125rem;line-height:1.25;letter-spacing:-.01em}
.hero .wrap{position:relative}
.hero .big{display:none}
@media (min-width:900px){.hero .big{display:block;position:absolute;right:var(--gut);top:0;width:120px;height:auto}}
.hero{padding:clamp(40px,8vw,88px) 0 clamp(36px,6vw,64px);border-bottom:1px solid var(--rule)}
.hero .state{display:inline-block;font:500 .75rem/1 var(--mono);text-transform:uppercase;letter-spacing:.1em;color:var(--stone);border:1px solid var(--rule);border-left:3px solid var(--brass);padding:8px 12px;margin:0 0 22px}
.lede{font-size:clamp(1.125rem,2.4vw,1.4rem);line-height:1.45;color:var(--mid);max-width:36em;margin:20px 0 0}
.three{list-style:none;margin:28px 0 0;padding:0;max-width:44em;border-top:1px solid var(--rule)}
.three li{padding:14px 0;border-bottom:1px solid var(--rule);color:var(--text)}
.actions{display:flex;flex-wrap:wrap;gap:16px 24px;align-items:center;margin-top:30px}
.btn{display:inline-flex;align-items:center;min-height:48px;padding:0 22px;background:var(--stone);color:var(--ink);font:500 1rem/1 var(--sans);text-decoration:none;border:1px solid var(--stone)}
.btn:hover{background:#fff}
.note{font-size:.875rem;color:var(--dim);margin:0}
section.block{padding:clamp(36px,6vw,64px) 0 0}
.intro{color:var(--mid);max-width:40em;margin:12px 0 0}
.install{margin:24px 0 0;border:1px solid var(--rule);background:var(--panel);padding:16px 18px}
.install p{margin:0 0 10px;font-size:.9375rem;color:var(--mid)}
code,pre{font-family:var(--mono)}
pre{margin:0;white-space:pre-wrap;overflow-wrap:anywhere}
pre code{font-size:.875rem;line-height:1.55;color:var(--stone);user-select:all;-webkit-user-select:all}
.legend{display:grid;gap:10px;margin:22px 0 0;padding:0;list-style:none;font-size:.9375rem;color:var(--mid)}
.legend li{display:flex;gap:12px;align-items:baseline}
.tag{display:inline-block;font:500 .75rem/1 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--stone);border:1px solid var(--rule);border-left:3px solid var(--brass);padding:6px 9px;white-space:nowrap}
.group{padding-top:clamp(32px,5vw,52px)}
.group h2{font-size:clamp(1.3rem,3vw,1.7rem);padding-top:16px;border-top:1px solid var(--brass)}
.grid{display:grid;gap:16px;margin-top:22px;grid-template-columns:repeat(auto-fill,minmax(min(100%,320px),1fr))}
.card{background:var(--panel);border:1px solid var(--rule);padding:20px;display:flex;flex-direction:column;gap:14px;min-width:0}
.card header{display:flex;gap:14px;align-items:center}
.card img{width:56px;height:56px;flex:none;display:block;border:1px solid var(--rule)}
.card .id{margin:2px 0 0;font:400 .8125rem/1.3 var(--mono);color:var(--dim)}
.card p{margin:0}
.card .blurb{color:var(--text);flex:1}
.meta{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;margin:0;padding:0;list-style:none;font-size:.875rem;color:var(--mid)}
.card pre{background:var(--ink);border:1px solid var(--rule);padding:12px 14px}
.card .hermes{font-size:.875rem;color:var(--dim)}
.links{display:flex;flex-wrap:wrap;gap:0 20px;margin-top:auto !important}
.links a{display:inline-flex;align-items:center;min-height:44px;font-size:.9375rem}
.fine{margin:18px 0 0;padding:0;list-style:none;display:grid;gap:8px;color:var(--dim);font-size:.9375rem;max-width:46em}
footer{margin-top:clamp(44px,7vw,80px);border-top:1px solid var(--rule);padding:28px 0 40px;font:400 .8125rem/1.6 var(--mono);color:var(--dim)}
footer a{color:var(--mid)}
@media (max-width:520px){.legend li{flex-direction:column;gap:6px}.bar .sub{display:none}}
"""


def card(name):
    p = PLUGINS[name]
    d = escape(p["display"])
    return f"""      <article class="card" id="{escape(name)}">
        <header>
          <img src="icons/{escape(p['icon'])}" width="56" height="56" alt="" loading="lazy" decoding="async">
          <div><h3>{d}</h3><p class="id">{escape(name)}</p></div>
        </header>
        <p class="blurb">{escape(p['blurb'])}</p>
        <ul class="meta"><li class="tag">{escape(p['mechanism'])}</li><li>{escape(status(p))}</li></ul>
        <pre><code>{escape(install_cmd(name))}</code></pre>
        <p class="hermes">Hermes Agent original: <a href="{escape(repo_url(p))}">{escape(p['repo'])}</a></p>
        <p class="links"><a href="{escape(tree_url(p))}" aria-label="{d} repository folder">Repository</a><a href="{escape(readme_url(p))}" aria-label="{d} README">README</a></p>
      </article>"""


def build_page():
    desc = (f"{OFFICE_H1}: {OFFICE_LEDE} In build. Built from ten Claude Code plugins that "
            f"install from GitHub.")
    groups = []
    for g in DATA["groups"]:
        cards = "\n".join(card(n) for n in g["plugins"])
        groups.append(f"""    <section class="group" id="{g['id']}" aria-labelledby="h-{g['id']}">
      <h2 id="h-{g['id']}">{escape(g['title'])}</h2>
      <div class="grid">
{cards}
      </div>
    </section>""")
    legend = "\n".join(f'        <li><span class="tag">{t}</span><span>{escape(s)}</span></li>' for t, s in TAG_LEGEND)
    three = "\n".join(f"        <li>{escape(x)}</li>" for x in OFFICE_LINES)
    notes = "\n".join(f"        <li>{escape(x)}</li>" for x in NOTES)
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(OFFICE_H1)} \u00b7 Deploy Axiom</title>
<meta name="description" content="{escape(desc)}">
<meta name="theme-color" content="#121316">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Deploy Axiom">
<meta property="og:title" content="{escape(OFFICE_H1)} \u00b7 Deploy Axiom">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:image" content="{BASE_URL}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Axiom Office for Claude, in build, with the Deploy Axiom mark.">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="mark.svg">
<link rel="preload" href="fonts/geist-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="bar"><div class="wrap"><img src="mark.svg" alt="" width="22" height="20"><span>Deploy Axiom</span><span class="sub">Plugins for Claude Code and Hermes Agent</span></div></div>
<main id="main">
  <div class="hero"><div class="wrap">
    <img class="big" src="mark.svg" alt="" width="120" height="110">
    <p class="state">{escape(OFFICE_STATUS)}</p>
    <h1>{escape(OFFICE_H1)}</h1>
    <p class="lede">{escape(OFFICE_LEDE)}</p>
    <ul class="three">
{three}
    </ul>
    <div class="actions">
      <a class="btn" href="{SITE}">{escape(CTA_TEXT)}</a>
      <p class="note">The Office is in build. The parts below are released.</p>
    </div>
  </div></div>

  <div class="wrap">
    <section class="block" id="parts" aria-labelledby="h-parts">
      <p class="label">Parts</p>
      <h2 id="h-parts">The parts it is built from</h2>
      <p class="intro">{escape(PARTS_INTRO)}</p>
      <div class="install">
        <p>Add the whole catalog once, then install any part by name.</p>
        <pre><code>claude plugin marketplace add {escape(DATA['catalog_repo'])}</code></pre>
      </div>
      <ul class="legend" aria-label="What the tags mean">
{legend}
      </ul>
    </section>

{chr(10).join(groups)}

    <section class="group" aria-labelledby="h-notes">
      <h2 id="h-notes">Before you install</h2>
      <ul class="fine">
{notes}
      </ul>
    </section>
  </div>
</main>
<footer><div class="wrap">Deploy Axiom \u00b7 <a href="{SITE}">deployaxiom.com</a> \u00b7 MIT licensed</div></footer>
</body>
</html>
"""
    (ROOT / "docs" / "index.html").write_text(html)


# -------------------------------------------------------------------- README
def build_readme():
    L = []
    L.append("# Deploy Axiom plugins for Claude Code\n")
    L.append(f"**{OFFICE_H1}** ({OFFICE_STATUS.rstrip('.')}.) {OFFICE_LEDE}\n")
    for x in OFFICE_LINES:
        L.append(f"- {x}")
    L.append(f"\n[{CTA_TEXT}]({SITE})\n")
    L.append("## The parts it is built from\n")
    L.append(PARTS_INTRO + "\n")
    L.append("Add the whole catalog once, then install any part by name:\n")
    L.append(f"```\nclaude plugin marketplace add {DATA['catalog_repo']}\nclaude plugin install axiom-gatekeeper@{MP}\n```\n")
    L.append("Tags: " + " ".join(f"**{t}**: {s}" for t, s in TAG_LEGEND) + "\n")
    for g in DATA["groups"]:
        L.append(f"## {g['title']}\n")
        for n in g["plugins"]:
            p = PLUGINS[n]
            L.append(f"### {p['display']} (`{n}`)\n")
            L.append(p["blurb"] + "\n")
            L.append(f"- Mechanism: {p['mechanism']}")
            L.append(f"- {status(p)}")
            L.append(f"- Hermes Agent original: [{p['repo']}]({repo_url(p)})")
            L.append(f"- [Repository folder]({tree_url(p)}) \u00b7 [README]({readme_url(p)})\n")
            L.append(f"```\n{install_cmd(n)}\n```\n")
    L.append("## Before you install\n")
    for x in NOTES:
        L.append(f"- {x}")
    L.append("\n## About this repository\n")
    L.append("This repository holds only the catalog: `.claude-plugin/marketplace.json`, which lists each plugin "
             "from its own repository (a `git-subdir` source), and the catalog page in `docs/`. "
             "The plugins live in their own repositories. To regenerate the generated files after editing "
             "`data/plugins.json`, run `python3 scripts/build.py`.\n")
    L.append("Fonts in `docs/fonts` are Geist and IBM Plex Mono, both SIL Open Font License; the licenses sit beside them.\n")
    L.append(f"{FOOTER}\n")
    (ROOT / "README.md").write_text("\n".join(L))


if __name__ == "__main__":
    build_marketplace()
    build_page()
    build_readme()
    print("built")
