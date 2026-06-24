# Rendering & delivery

Turn the HTML deck into files the user can post.

## Run the renderer
```
python3 <skill>/assets/render_ig.py /path/to/carousel.html ~/Downloads/<slug>_IG
# 4:5 portrait instead of square (more feed real estate, often better reach):
python3 <skill>/assets/render_ig.py /path/to/carousel.html ~/Downloads/<slug>_IG --size 1080x1350
# re-skin to a named palette without editing the deck:
python3 <skill>/assets/render_ig.py /path/to/carousel.html ~/Downloads/<slug>_IG_mono --palette mono-light
```

## Palette options (let the user choose)
Preview one slide across every palette in `assets/palettes.json`, tiled into one image:
```
python3 <skill>/assets/palette_preview.py /path/to/carousel.html ~/Downloads/<slug>_palettes.png --slide 2
```
Show it to the user, then render the full deck with `--palette <name>`. `--palette` injects a `:root` override after the deck head (the deck file is never modified) and the texture/glow are `--accent`-derived, so the whole look swaps. To hand over every option as its own set, render once per palette into separate folders.
What it does automatically:
- One `<section>` → one slide, in order.
- Slide with a `<video>` → **screen-recorded MP4** (autoplay+loop, ~one source loop).
- Any other slide → **PNG** (rendered at 2×, downscaled with lanczos = crisp).
- Reuses the deck's `<head>` (fonts + `:root` palette) so output matches the deck.
- Clears the output dir first; names files `01.png/mp4 … NN.png/mp4`.

Requirements (all present here): Python Playwright launched with `channel="chrome"` (the chromium binary is usually absent), and ffmpeg. If Chrome is missing, install a browser with `python3 -m playwright install chromium` and change the launch in the script.

## Always spot-check before handing over
```
# a frame from a video slide:
ffmpeg -y -ss 4 -i ~/Downloads/<slug>_IG/05.mp4 -frames:v 1 /tmp/check.png
```
Then Read 1–2 PNGs and 1–2 video frames and confirm: fonts loaded (not system fallback), nothing clipped, media shows full frame, counters/handle correct. Fix in `carousel.html`, re-render.

## ffmpeg recipes (manual tweaks)
- Force a specific clip to fill edge-to-edge (cropping) instead of full-frame: change that slide's video to `object-fit:cover` in the HTML and re-render — don't post-process.
- Shorten a long clip: the renderer already trims to one source loop; to cap further, lower the per-clip cap in `render_ig.py` (`min(max(dur,5),16)`).
- Re-encode a stubborn output: `ffmpeg -i in.mp4 -an -vf format=yuv420p -c:v libx264 -movflags +faststart out.mp4`.

## Posting to Instagram
- Files live in `~/Downloads/<slug>_IG/`, ordered `01 → NN`.
- Move them to the phone (AirDrop / Photos sync) — IG posts from the phone.
- IG → new post → **Select multiple** → add in filename order. Mixing photos + videos is fine as long as **all slides share one aspect ratio** (the renderer guarantees this).
- Square = 1080×1080; portrait 4:5 = 1080×1350. Pick one for the whole set.

## Optional — publish to claude.ai/design (DesignSync MCP)
If the user keeps decks there, the HTML + assets can be pushed:
1. `DesignSync get_project` / `list_files` to confirm the target.
2. `finalize_plan` with the writes (the `.html` + any `.mp4`/`.png` assets), `deletes:[]`.
3. `write_files` with `localPath` for each (binary uploads stream from disk).
This is a distribution convenience; the postable PNG/MP4s come from `render_ig.py`, not from the design tool.
