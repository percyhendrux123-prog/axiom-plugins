#!/usr/bin/env python3
"""Regenerate marketplace.json, docs/index.html and README.md from data/plugins.json.

docs/index.html is assembled here and in scripts/page.py; the look lives in docs/assets/site.css
and site.js, which are hand-written and are not generated. Two optional helper scripts write
files that are committed: scripts/dither_icons.py (1-bit icons, needs Pillow) and
scripts/render_caduceus.js (the no-script caduceus still, needs node).

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
    "Discovery: an owner interview that writes the rulebook and the settings; you apply them yourself.",
    "One front door: you talk only to the orchestrator. Specialists cannot send outside or touch the data tier you list.",
    "A pane shows every agent: state, task, time, context use, and a mark when you are wanted.",
]
OFFICE_STATUS = "Version 0.1 \u00b7 free and open source \u00b7 runs in Claude Code and the Claude desktop app"
OFFICE_INSTALL = f"claude plugin install axiom-office@{DATA['marketplace']}"
OFFICE_CTA_NOTE = "Deploy Axiom runs discovery, writes your rules and sets up the team."
CTA_TEXT = "Talk to Deploy Axiom"
PARTS_INTRO = ("Eleven plugins for Claude Code: the Axiom Office, and ten that each have a Hermes Agent original. "
               "Each one installs on its own.")
TAG_LEGEND = [
    ("skill", "Instructions Claude loads when the task matches. No code runs."),
    ("hook", "A script Claude Code runs on an event, such as before a tool call."),
    ("mod", "JavaScript that runs inside Claude Code."),
]
NOTES = [
    "The Axiom Office is version 0.1, built against Claude Code 2.1.330 and proven live in the terminal and in the "
    "Code tab of the Claude Desktop app. VS Code is not proven live. Agent teams are an experimental Claude Code "
    "feature; the pane and the rules also work for plain subagents.",
    "Hook and mod plugins run code with your permissions. Each README says what the plugin "
    "reads, writes and calls.",
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
        "metadata": {"description": "Plugins for Claude Code from Deploy Axiom: the Axiom Office and ten plugins that each have a Hermes Agent original."},
        "plugins": entries,
    }
    (ROOT / ".claude-plugin" / "marketplace.json").write_text(json.dumps(doc, indent=2) + "\n")


# ---------------------------------------------------------------------- page
def build_page():
    """The page itself (markup in scripts/page.py; styles and behaviour in docs/assets/)."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from page import build_page as render
    ctx = {
        "data": DATA, "plugins": PLUGINS, "site": SITE, "base_url": BASE_URL,
        "h1": OFFICE_H1, "lede": OFFICE_LEDE, "lines": OFFICE_LINES, "status_line": OFFICE_STATUS, "install": OFFICE_INSTALL, "cta_note": OFFICE_CTA_NOTE,
        "cta": CTA_TEXT, "parts_intro": PARTS_INTRO, "tag_legend": TAG_LEGEND, "notes": NOTES,
        "status": status, "install_cmd": install_cmd, "repo_url": repo_url,
        "tree_url": tree_url, "readme_url": readme_url,
    }
    (ROOT / "docs" / "index.html").write_text(render(ctx))


# -------------------------------------------------------------------- README
def build_readme():
    L = []
    L.append("# Deploy Axiom plugins for Claude Code\n")
    L.append(f"**{OFFICE_H1}**: {OFFICE_LEDE}\n\n{OFFICE_STATUS}.\n")
    for x in OFFICE_LINES:
        L.append(f"- {x}")
    L.append(f"\nInstall the Office, after adding the catalog below:\n\n```\n{OFFICE_INSTALL}\n```\n")
    L.append(f"[{CTA_TEXT}]({SITE}). {OFFICE_CTA_NOTE}\n")
    L.append("## The plugins\n")
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
            L.append(f"- Hermes Agent original: [{p['repo']}]({repo_url(p)})" if p.get("original", True)
                     else f"- Source: [{p['repo']}]({repo_url(p)}) (MIT)")
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
    L.append("Fonts in `docs/fonts` are Cinzel, Geist and IBM Plex Mono, all SIL Open Font License; the licenses sit beside them. The page itself is `docs/index.html` with `docs/assets/` (plain CSS and JavaScript, no external requests).\n")
    L.append(f"{FOOTER}\n")
    (ROOT / "README.md").write_text("\n".join(L))


if __name__ == "__main__":
    build_marketplace()
    build_page()
    build_readme()
    print("built")
