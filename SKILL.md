---
name: carousel-maker
description: Turn an article, tweet/X thread, or reel/video link (plus any notes) into a polished 8–10 slide Instagram carousel. Scrapes the source for text and visuals (screenshots for articles & tweets, ssstwitter.com for X GIFs/videos, yt-dlp for reels), picks a topic-appropriate colour palette, writes a cohesive slide-by-slide story, builds a self-contained 1080×1080 HTML deck, and renders Instagram-ready PNG + MP4 files. Use when the user wants to make a carousel, turn a link/article/tweet/reel into slides, or create an Instagram/LinkedIn carousel post.
version: 1.0.0
dependencies: ffmpeg, yt-dlp, and Python Playwright with the "chrome" channel (the chromium binary is usually absent — always launch channel="chrome"). All present on this machine.
---

# Carousel Maker

Turn one link (or a topic + notes) into a finished, postable Instagram carousel — scraped, designed, built, and rendered to files the user can upload directly.

## When to use
Trigger on: "make a carousel", "turn this article/tweet/reel into a carousel", "carousel from this link", "Instagram/LinkedIn carousel", or any request that hands you a source URL and asks for slides.

## The deliverable
Always two things:
1. A self-contained carousel deck: `carousel.html` (one `<section>` per slide, 1080×1080, palette in `:root`).
2. A folder of **postable files** in `~/Downloads/<slug>_IG/`, named `01…NN` in order — `.png` for static slides, `.mp4` for motion slides.

The HTML is the editable source of truth. The PNG/MP4s are what gets posted. Never hand the user raw HTML as "the carousel" — always render the files.

## Pipeline (run in order)

### 1 · Intake
- Identify the source type: **article** (URL), **tweet / X thread** (URL), **reel / short video** (IG/TikTok/YT/X URL), or **raw topic + notes**.
- Ask for (or infer) the few things that change the output, in ONE short message — don't interrogate:
  - **Angle / takeaway** the user wants front-and-centre (the hook).
  - **Audience & platform** (default: Instagram, square 1080×1080).
  - **Handle / CTA** (e.g. `@manikk.ai`, "follow for X daily").
  - **Slide count** (default 8–10).
- If the user already gave enough, skip the questions and proceed. Bias to action.

### 2 · Scrape & collect assets
Create a working dir (scratchpad). Pull text AND visuals. See `references/scraping.md` for exact commands.
- **Article** → extract the body text (WebFetch), then screenshot the key figures/charts/hero with Playwright.
- **Tweet / thread** → screenshot the tweet(s) for use as slide imagery; for any **video/GIF in the tweet**, copy the tweet link into **https://ssstwitter.com/**, download the MP4, and use that.
- **Reel / short video** → `yt-dlp` the video; pull caption/transcript for copy.
- **Prep every clip**: remux to faststart MP4 + strip audio (recipe in `references/scraping.md`). Instagram never animates a raw GIF — it MUST become an MP4.
- Save assets with clear names (`fig-1.png`, `demo-trading.mp4`, …) in the working dir next to where `carousel.html` will live (relative `./` paths must resolve).

### 3 · Story & design (the judgment step — do this well)
Three sub-steps, in this order:

**a. Understand the industry.** One short internal note: what field is this (AI, fintech, fashion, health, crypto…), who reads it, what tone fits. This sets vocabulary and restraint.

**b. Choose the palette from the topic.** Don't default to one look. Derive a 6–8 colour palette that *fits the subject* (brand colours of the company involved, or the mood of the field). Map them to the CSS variables in the template (`--bg --bg2 --text --muted --line --accent --accent-ink --warn`). See `references/design-system.md` for the variable system and ready-made light/dark palettes per industry.

**c. Simplify the topic into a story.** Distill the source to ONE spine a scroller can follow in 10 seconds, then expand to 8–10 slides. Default narrative arc:
`Hook → What it is (1 image/diagram) → How it works → Proof/receipts → 1–4 concrete use cases (with the scraped media) → How to access / pricing → CTA + follow`.
Write the copy hook-first and crisp (punchy, not consultant-y; short > long; one idea per slide; the outcome IS the headline). Each media slide gets a one-line **"The task / the point:"** so the viewer knows what they're looking at.

Use this internal prompt for steps a–c:
> "Source: <link/notes>. (1) Name the industry, audience, and tone in one line. (2) Propose a 7-colour palette that fits this topic, as hex mapped to --bg/--bg2/--text/--muted/--line/--accent/--accent-ink/--warn, and say why it fits. (3) Lay out N slides: for each give the eyebrow label, the headline (outcome-first), the supporting line, and which scraped asset (if any) it uses. Keep every headline under ~8 words."

### 4 · Build the deck
- Copy `assets/template.html` to the working dir as `carousel.html`.
- Set the palette in `:root`. Build one `<section>` per slide following the template's anatomy: **header** (eyebrow + `NN / TOTAL` counter), **middle** (content), **footer** (handle + "swipe →"; last slide = "● END").
- Place scraped images/clips in their slots. **Media rule (non-negotiable):** show the full frame — `object-fit:contain` inside a `flex:1 1 auto; min-height:0` box so the clip can never crop the chart or push text off-slide. Videos: `<video autoplay loop muted playsinline preload="auto">`.
- Keep all slides the SAME aspect ratio (IG requires it).
- Verify before rendering: `grep -c '</section>' carousel.html` equals the slide count (use the closing tag — comments can mention `<section>`); counters read `01 / NN … NN / NN`; every `src="./…"` asset exists.

### 5 · Render to Instagram-ready files
- Run the bundled renderer (auto-detects motion vs static slides, reuses the deck's fonts + palette, names outputs by order):
  ```
  python3 <skill>/assets/render_ig.py /path/to/carousel.html ~/Downloads/<slug>_IG
  ```
- It produces `01.png/mp4 … NN.png/mp4` at 1080×1080. Details + flags in `references/rendering.md`.
- **Always spot-check**: grab a frame from 1–2 video slides (`ffmpeg -ss … -frames:v 1`) and Read a couple of PNGs to confirm fonts loaded, nothing is clipped, and media shows in full.

### 6 · Share & iterate
- Tell the user the files are in `~/Downloads/<slug>_IG/`, posted in `01→NN` order (IG → new post → select multiple → add in filename order; square keeps aspect consistent across photo+video slides).
- Invite specific edits (a headline, a palette shift, a slide reorder, swap a clip's framing to `contain`/crop). Edit `carousel.html`, re-render, re-show.

## Non-negotiables (hard-won)
- **GIFs don't animate on Instagram.** Convert every GIF/clip to MP4 (autoplay/loop/muted/playsinline). Raw GIF in a slot = frozen first frame.
- **Never crop the user's media by accident.** Full frame via `object-fit:contain` + flex. Only crop if the user asks.
- **Playwright: launch `channel="chrome"`** — the bundled chromium binary is typically not installed here.
- **Faststart + yuv420p** on every output MP4 or IG may reject/stutter it.
- **One source of truth:** edit `carousel.html`, then re-render. Don't hand-edit the exported files.

## Optional: publish to claude.ai/design
If the user keeps decks in claude.ai/design, the deck can be pushed/pulled with the DesignSync MCP (`list_files` → `finalize_plan` → `write_files`). This is an optional distribution step, not required to produce the postable files.

## Reference files
- `references/design-system.md` — slide anatomy, palette variable system, industry palette presets, typography, copy + media rules.
- `references/scraping.md` — exact recipes: article text + screenshots, tweet screenshots, ssstwitter GIF/video download, yt-dlp reels, ffmpeg clip prep.
- `references/rendering.md` — render_ig.py usage, ffmpeg recipes, square vs 4:5, IG posting, optional design-sync.
- `assets/template.html` — the parametrized 1080×1080 carousel template.
- `assets/render_ig.py` — HTML deck → Instagram-ready PNG/MP4 renderer.
