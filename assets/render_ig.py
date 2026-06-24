#!/usr/bin/env python3
"""
Render a carousel HTML deck into Instagram-ready files.

Usage:
  python3 render_ig.py <carousel.html> <output_dir> [--size 1080x1080]

How it works:
  - Each top-level <section> in the deck becomes one slide, in document order.
  - A slide that contains a <video> is screen-recorded to MP4 (autoplay + loop).
  - Every other slide is screenshotted to PNG (rendered at 2x, downscaled = crisp).
  - The deck's <head> (font links + :root palette + <style>) is reused for each
    standalone slide, so the output looks identical to the deck.
  - Outputs are named by order: 01.png/mp4 ... NN.png/mp4

Requires: Python Playwright (launched with channel="chrome") and ffmpeg.
Relative ./media paths inside the deck resolve against the deck's own folder,
so keep carousel.html next to its images/clips.
"""
import re, os, sys, glob, json, shutil, subprocess, argparse
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("html", help="path to the carousel .html deck")
ap.add_argument("outdir", help="folder to write 01.png/mp4 ... into")
ap.add_argument("--size", default="1080x1080", help="slide size WxH (e.g. 1080x1350 for 4:5)")
ap.add_argument("--palette", default=None,
                help="re-skin without editing the deck: a name in assets/palettes.json, or a path to a JSON file of CSS var overrides")
args = ap.parse_args()
W, H = (int(x) for x in args.size.lower().split("x"))

def load_palette(ref):
    """Return a {'--bg':'#..',...} dict from a palettes.json key or a JSON file path."""
    if not ref: return None
    here = os.path.dirname(os.path.abspath(__file__))
    book = {}
    pj = os.path.join(here, "palettes.json")
    if os.path.exists(pj): book = json.load(open(pj))
    if ref in book: return book[ref].get("vars", book[ref])
    if os.path.exists(ref):
        d = json.load(open(ref)); return d.get("vars", d)
    raise SystemExit(f"--palette '{ref}' not found in palettes.json or as a file. Options: {', '.join(book)}")

PAL = load_palette(args.palette)
OVERRIDE = ("<style>:root{" + "".join(f"{k}:{v};" for k,v in PAL.items()) + "}</style>") if PAL else ""

html_path = os.path.abspath(args.html)
base_dir  = os.path.dirname(html_path)            # ./media paths resolve here
OUT = os.path.abspath(args.outdir)
REC = os.path.join(base_dir, "_rec")
os.makedirs(OUT, exist_ok=True); os.makedirs(REC, exist_ok=True)
for f in glob.glob(os.path.join(OUT, "*")):       # clear stale output
    if os.path.isfile(f): os.remove(f)

doc  = open(html_path, encoding="utf-8").read()
m    = re.search(r"<head\b[^>]*>(.*?)</head>", doc, re.DOTALL)
head = m.group(1) if m else ""
sections = re.findall(r"<section\b[^>]*>.*?</section>", doc, re.DOTALL)
assert sections, "no <section> elements found in the deck"
print(f"{len(sections)} slides @ {W}x{H}")

TPL = ("<!DOCTYPE html><html><head>{head}"
       "<style>html,body{{margin:0;padding:0;background:#000;}}"
       "#stage{{width:{W}px;height:{H}px;overflow:hidden;position:relative;}}"
       "section{{display:block;width:100%;height:100%;}}</style>"
       "{override}"  # palette override comes AFTER the deck head, so it wins
       "</head><body><div id=\"stage\">{inner}</div></body></html>")

def dur(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","default=nk=1:nw=1", path], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except Exception: return 8.0

def first_video_src(html):
    m = re.search(r'<video[^>]*\bsrc="([^"]+)"', html)
    return m.group(1) if m else None

slides = []  # (idx, file, is_motion, video_src)
for i, sec in enumerate(sections, 1):
    p = os.path.join(base_dir, f"_slide-{i:02d}.html")
    open(p, "w", encoding="utf-8").write(TPL.format(head=head, W=W, H=H, inner=sec, override=OVERRIDE))
    slides.append((i, p, "<video" in sec, first_video_src(sec)))

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome",
              args=["--autoplay-policy=no-user-gesture-required", "--hide-scrollbars"])

    # ---- static slides: 2x screenshot -> lanczos downscale ----
    sctx = browser.new_context(viewport={"width":W,"height":H}, device_scale_factor=2)
    spage = sctx.new_page()
    for i, path, motion, vsrc in slides:
        if motion: continue
        spage.goto("file://"+path)
        try: spage.evaluate("document.fonts.ready")
        except Exception: pass
        spage.wait_for_timeout(1600)             # let webfonts paint
        big = os.path.join(REC, f"_big-{i:02d}.png")
        spage.screenshot(path=big, clip={"x":0,"y":0,"width":W,"height":H})
        out = os.path.join(OUT, f"{i:02d}.png")
        subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",big,
                        "-vf",f"scale={W}:{H}:flags=lanczos", out], check=True)
        print("image:", os.path.basename(out))
    sctx.close()

    # ---- motion slides: record page (one loop) -> clean square mp4 ----
    for i, path, motion, vsrc in slides:
        if not motion: continue
        rec_s = 8.0
        if vsrc:
            vp = os.path.join(base_dir, vsrc.lstrip("./"))
            if os.path.exists(vp): rec_s = min(max(dur(vp), 5.0), 16.0)
        ctx = browser.new_context(viewport={"width":W,"height":H}, device_scale_factor=1,
              record_video_dir=REC, record_video_size={"width":W,"height":H})
        page = ctx.new_page()
        page.goto("file://"+path)
        try: page.evaluate("document.fonts.ready")
        except Exception: pass
        page.evaluate("document.querySelectorAll('video').forEach(v=>{v.muted=true;v.loop=true;v.play();})")
        page.wait_for_timeout(int((rec_s+0.8)*1000))
        vpath = page.video.path()
        ctx.close()                               # finalizes the webm
        out = os.path.join(OUT, f"{i:02d}.mp4")
        subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-ss","0.6","-i",vpath,
                        "-t",f"{rec_s:.2f}",
                        "-vf",f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30,format=yuv420p",
                        "-c:v","libx264","-profile:v","high","-pix_fmt","yuv420p","-an",
                        "-movflags","+faststart", out], check=True)
        os.remove(vpath)
        print("video:", os.path.basename(out))

    browser.close()

shutil.rmtree(REC, ignore_errors=True)
for f in glob.glob(os.path.join(base_dir, "_slide-*.html")): os.remove(f)

print("\nDONE ->", OUT)
for f in sorted(os.listdir(OUT)):
    print("  ", f, os.path.getsize(os.path.join(OUT, f))//1024, "KB")
