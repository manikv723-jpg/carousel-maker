#!/usr/bin/env python3
"""
Render ONE slide of a deck across all curated palettes into a single labelled
comparison image, so the user can pick a look before the full render.

Usage:
  python3 palette_preview.py <carousel.html> <preview.png> [--slide N] [--names a,b,c]

- --slide N : which slide to preview (1-based; default 2, usually a content slide
              that shows text + accent + cards). Avoid the cover if it has media.
- --names   : comma-separated subset of palette names from palettes.json
              (default: all of them).

Then render the chosen palette full-deck with:
  python3 render_ig.py <carousel.html> <outdir> --palette <name>

Requires: Playwright (chrome channel), Pillow.
"""
import re, os, json, argparse
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("html"); ap.add_argument("out")
ap.add_argument("--slide", type=int, default=2)
ap.add_argument("--names", default=None)
ap.add_argument("--size", default="1080x1080")
args = ap.parse_args()
W, H = (int(x) for x in args.size.lower().split("x"))

here = os.path.dirname(os.path.abspath(__file__))
book = json.load(open(os.path.join(here, "palettes.json")))
names = args.names.split(",") if args.names else list(book)

doc = open(os.path.abspath(args.html), encoding="utf-8").read()
base_dir = os.path.dirname(os.path.abspath(args.html))
head = (re.search(r"<head\b[^>]*>(.*?)</head>", doc, re.DOTALL) or [None, ""])[1]
sections = re.findall(r"<section\b[^>]*>.*?</section>", doc, re.DOTALL)
sec = sections[max(0, min(args.slide-1, len(sections)-1))]

def wrap(palette_vars):
    ov = "<style>:root{" + "".join(f"{k}:{v};" for k,v in palette_vars.items()) + "}</style>"
    return (f"<!DOCTYPE html><html><head>{head}"
            f"<style>html,body{{margin:0;background:#000}}#stage{{width:{W}px;height:{H}px;overflow:hidden;position:relative}}"
            f"section{{display:block;width:100%;height:100%}}</style>{ov}</head>"
            f"<body><div id='stage'>{sec}</div></body></html>")

thumbs = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", args=["--hide-scrollbars"])
    pg = b.new_page(viewport={"width":W,"height":H}, device_scale_factor=1)
    os.makedirs(os.path.join(base_dir, "_pal"), exist_ok=True)
    for n in names:
        f = os.path.join(base_dir, "_pal", f"{n}.html")
        open(f,"w",encoding="utf-8").write(wrap(book[n].get("vars", book[n])))
        pg.goto("file://"+f)
        try: pg.evaluate("document.fonts.ready")
        except Exception: pass
        pg.wait_for_timeout(900)
        shot = os.path.join(base_dir, "_pal", f"{n}.png")
        pg.screenshot(path=shot, clip={"x":0,"y":0,"width":W,"height":H})
        thumbs.append((n, shot))
    b.close()

# tile: 3 columns, label each with the palette name + note
cols = 3; tw = 460; lab = 30; pad = 22
th = int(tw*H/W)
rows = (len(thumbs)+cols-1)//cols
sheet = Image.new("RGB", (cols*tw + (cols+1)*pad, rows*(th+lab) + (rows+1)*pad), (12,12,14))
d = ImageDraw.Draw(sheet)
for i,(n,shot) in enumerate(thumbs):
    r,c = divmod(i, cols)
    x = pad + c*(tw+pad); y = pad + r*(th+lab)
    d.text((x, y), f"{n}  —  {book[n].get('note','')}"[:64], fill=(235,235,245))
    im = Image.open(shot).convert("RGB").resize((tw, th))
    sheet.paste(im, (x, y+lab-6))
sheet.save(args.out)

import shutil; shutil.rmtree(os.path.join(base_dir, "_pal"), ignore_errors=True)
print("wrote", args.out, "with palettes:", ", ".join(names))
