#!/usr/bin/env python3
"""Tile the demo frames into contact sheets. Run: env -u PYTHONPATH /usr/bin/python3 scripts/qa_contact.py"""
from pathlib import Path
from PIL import Image, ImageDraw
OUT = Path(__file__).resolve().parent.parent / "review" / "v2"
TS = ["1_5", "3_6", "5_9", "7_4", "10_3", "11_6"]
CAPS = {"1_5": "1.5 s  discovery prints the roster", "3_6": "3.6 s  specialists work", "5_9": "5.9 s  send attempt held at the wall",
        "7_4": "7.4 s  orchestrator asks the owner", "10_3": "10.3 s  one send leaves through the gate", "11_6": "11.6 s  receipt printed, wings open"}
def sheet(tag, cols, tile_w, crop):
    tiles = []
    for t in TS:
        im = Image.open(OUT / f"frame-{tag}-{t}.png").convert("RGB")
        im = im.crop(crop(im))
        h = int(im.height * tile_w / im.width)
        im = im.resize((tile_w, h), Image.LANCZOS)
        cap = Image.new("RGB", (tile_w, h + 26), (12, 13, 15))
        cap.paste(im, (0, 26))
        ImageDraw.Draw(cap).text((8, 7), "Demo run (simulated)  " + CAPS[t], fill=(205, 200, 189))
        tiles.append(cap)
    rows = (len(tiles) + cols - 1) // cols
    th = max(t.height for t in tiles)
    S = Image.new("RGB", (cols * tile_w + (cols + 1) * 10, rows * th + (rows + 1) * 10), (50, 52, 56))
    for i, t in enumerate(tiles):
        S.paste(t, (10 + (i % cols) * (tile_w + 10), 10 + (i // cols) * (th + 10)))
    return S
sheet("d", 2, 960, lambda im: (150, 0, 1290, im.height)).save(OUT / "contact-sheet-demo-desktop.png")
sheet("m", 3, 420, lambda im: (0, 0, im.width, im.height)).save(OUT / "contact-sheet-demo-390.png")
print("ok")
