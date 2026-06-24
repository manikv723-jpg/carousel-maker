# Design system — anatomy, palette, type, copy, media

The look is driven by `assets/template.html`. Keep the structure; change the palette and copy per topic.

## Slide anatomy (every slide is identical scaffolding)
A `<section>` wraps `.slide`, a 1080×1080 grid: `60px header / 1fr middle / 52px footer`, padding `64px 68px`.
- **Header** — `● eyebrow label` on the left, `NN / TOTAL` counter on the right. Mono, uppercase, `--faint`.
- **Middle** — the content. Centered (`justify-content:center`) for text slides; `flex-start` for media slides so the clip fills cleanly.
- **Footer** — `— @handle` on the left, `swipe →` on the right; last slide uses `● END`.
- **Texture + glow** — a faint grid and a radial accent glow (decorative, z0). Disable the grid with `--grid-alpha:0`.

Consistency across slides is what makes a carousel feel designed: same header/footer, same type scale, same accent. Vary the *middle* only.

## Palette system — pick from the topic, don't default
Set these 8 variables in `:root`. Everything else references them.

| var | role | dark default | light example |
|---|---|---|---|
| `--bg` | slide background | `#06121A` | `#FAF7F2` |
| `--bg2` | card/panel bg | `#0C1E27` | `#FFFFFF` |
| `--text` | primary text | `#E6F1F3` | `#1A1A1A` |
| `--muted` | secondary text | `#A4BEC6` | `#5B5B5B` |
| `--faint` | labels/counters/lines | `#5E7A86` | `#9A9A9A` |
| `--line` | borders/dividers | `#1A3744` | `#E6E0D8` |
| `--accent` | highlight/brand pop | `#2FE3C8` | `#1463FF` |
| `--accent-ink` | text on an accent fill | `#06121A` | `#FFFFFF` |
| `--warn` | "loses / worse" accent | `#FF7E6B` | `#D7263D` |

**How to choose:** **if the user gave brand guidelines, use them — that overrides everything here** (map their colours/fonts to the vars, use their logo on the cover). Otherwise start from the subject: if a specific brand/company is central, pull its real brand colours (one dark base, one accent); else use the field's mood. Always check the accent has enough contrast on `--bg`, and that `--accent-ink` is readable on an `--accent` fill.

### Ready-made presets
These ship as named entries in `assets/palettes.json` (`aqua-dark`, `violet-dark`, `fintech-green`, `crypto-purple`, `editorial-amber`, `mono-light`, `warm-light`). Preview them all on your deck with `assets/palette_preview.py`, then render the chosen one with `render_ig.py … --palette <name>`. Add your own by editing `palettes.json`. The texture/glow derive from `--accent`, so a palette swap re-skins the whole slide. Hex reference (map left→right to the vars above):
- **AI / deep-tech (dark):** `#06121A · #0C1E27 · #E6F1F3 · #A4BEC6 · #5E7A86 · #1A3744 · #2FE3C8 · #06121A · #FF7E6B` (the default).
- **Fintech / markets (dark):** `#0A1A14 · #0F241B · #EAF6EF · #9DBDAC · #5E7E6C · #1C3A2C · #46E08A · #07140D · #FF6B6B`.
- **Crypto / web3 (near-black):** `#0B0B12 · #14141F · #ECEcFb · #A6A6C2 · #6A6A85 · #25253A · #8B5CFF · #0B0B12 · #FF4D6D`.
- **Health / wellness (light):** `#F3F6F2 · #FFFFFF · #1D2A22 · #5A6B60 · #9DB0A4 · #DDE6DD · #2F8F5B · #FFFFFF · #C2502F`.
- **Fashion / luxury (light):** `#F6F1EA · #FFFFFF · #161310 · #6B6258 · #A99E90 · #E6DDD0 · #B6892E · #161310 · #9E3B2E`.
- **Editorial / news (dark):** `#101114 · #1A1B20 · #F2F3F5 · #B7BAC2 · #74778099 · #2A2C33 · #FFC14D · #101114 · #FF6F61`.

## Typography
Three roles. Keep the pairing tight.
- **Display** (`--f-display`) — headlines + numbers. Space Grotesk default. Swap to a strong geometric/grotesk per brand.
- **Mono** (`--f-mono`) — eyebrows, labels, captions, counters. JetBrains Mono.
- **Serif accent** (`--f-serif`) — one italic phrase per headline for flavour (`.accent-i`). Instrument Serif.

Scale guide (square 1080): cover h1 56–60px; section h1 44–54px; lead 23–24px; task line 20px; card number 28–32px; labels/captions 12–15px. Drop a size if a headline wraps past 2 lines.

## Copy rules (hook-first, crisp)
- One idea per slide. Short > long. The **outcome is the headline** ("X beat the field at trading"), not the setup.
- Cover promises the payoff in one sentence. Each use-case slide gets a one-line **"The task:"** so the viewer knows what they're seeing.
- Eyebrow can pose the question ("can it trade?"), headline answers it.
- Last slide: a memorable line + a single clear CTA. No walls of text anywhere.
- Match the user's voice if known (e.g. punchy, not consultant-y).

## Media rules (do not crop the user's stuff)
- Put images/clips in `.media` (`flex:1 1 auto; min-height:0; object-fit:contain`) so the **whole frame** shows and the clip can't push text off-slide. Only switch to `object-fit:cover` if the user explicitly wants edge-to-edge/cropped.
- A landscape clip on a square slide will have quiet space above/below — it blends into `--bg`, reading as intentional. To fill instead, the user must approve cropping or supply a re-framed clip.
- Light diagram on a dark deck → frame it in a light rounded card (see template slide 2).
- Every motion asset is an MP4 with `autoplay loop muted playsinline`. Never place a raw `.gif` in a slot.

## Narrative arc (8–10 slides default)
`Hook → What it is (1 visual) → How it works → Proof/receipts → 1–4 use cases (scraped media) → How to access / pricing → CTA + follow`.
Adjust to the source: a tutorial may be `Hook → why → steps 1..n → result → CTA`; a product launch may be `Hook → problem → product → proof → pricing → CTA`.
