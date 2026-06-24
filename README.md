# carousel-maker

A [Claude](https://claude.com/claude-code) **skill** that turns a link into a finished, postable Instagram carousel.

Hand it an **article, tweet/X thread, or reel** (plus any notes) and it will:

1. **Scrape** the source for text and visuals — screenshots for articles & tweets, [ssstwitter.com](https://ssstwitter.com/) for X GIFs/videos, `yt-dlp` for reels.
2. **Design** a colour palette that fits the topic and write a cohesive **8–10 slide story** (hook → what it is → how it works → proof → use cases → how to access → CTA).
3. **Build** a self-contained `1080×1080` HTML deck (one `<section>` per slide).
4. **Render** Instagram-ready files — `.png` for static slides, `.mp4` for motion slides — named `01…NN` in post order.
5. **Iterate** on your feedback.

On first run it asks for **your** brand — handle, CTA, colours/fonts/logo (or "derive from the topic"), and what the carousel is for — so the output is yours, not a template's. GIFs are auto-converted to looping MP4 (Instagram won't animate a raw GIF), media is shown full-frame so nothing gets cropped, and every clip is encoded faststart/yuv420p so IG accepts it.

## Requirements

- [Claude Code](https://claude.com/claude-code) (or any agent host that loads `SKILL.md` skills)
- `ffmpeg`
- `yt-dlp` (for reels)
- Python [Playwright](https://playwright.dev/python/) — launched with the **`chrome` channel** (uses your installed Google Chrome; no separate browser download needed)

```bash
brew install ffmpeg yt-dlp
pip install playwright            # Chrome channel uses your existing Chrome install
```

## Install

Clone into your Claude skills directory:

```bash
git clone https://github.com/manikv723-jpg/carousel-maker.git ~/.claude/skills/carousel-maker
```

Restart your session and the skill is available.

## Use

Just ask, in natural language:

> "Make a carousel from this article: <url>"
> "Turn this tweet into an 8-slide carousel, handle @yourname"

Or invoke it directly: `/carousel-maker <link>`.

The finished files land in `~/Downloads/<slug>_IG/` — open Instagram → new post → select multiple → add them in filename order.

## How it's organized

```
carousel-maker/
├── SKILL.md                     # the pipeline + when to use it
├── assets/
│   ├── template.html            # parametrized 1080×1080 deck (palette in :root)
│   └── render_ig.py             # HTML deck → Instagram-ready PNG/MP4 (auto-detects motion slides)
└── references/
    ├── design-system.md         # slide anatomy, palette presets, type & copy rules
    ├── scraping.md              # article/tweet/reel scraping + clip prep recipes
    └── rendering.md             # render usage, square vs 4:5, posting
```

## Use it inside an agent / Telegram bot

The scripts are plain CLIs, so a Telegram agent (e.g. on **Hermes** or **OpenClaw**) can run the whole pipeline and post the result:

```bash
# 1. render (writes NN.png/mp4 + manifest.json)
python3 assets/render_ig.py carousel.html out/ --palette violet-dark
# 2. deliver the album to a chat
python3 assets/send_telegram.py out/ --token "$TELEGRAM_BOT_TOKEN" --chat <chat_id> --caption "…"
```

In a bot, skip the interactive intake: read the brief from the message (`<url> brand:@x palette:violet-dark`) or a stored `brand.json`, render, deliver, then offer other palettes as a tap. `render_ig.py` emits `manifest.json` (ordered slides + types) so the agent knows what to send. Full playbook + brand-profile schema: [`references/integration.md`](references/integration.md).

## Customizing the look

The whole palette is 8 CSS variables in the template's `:root` (`--bg --bg2 --text --muted --line --accent --accent-ink --warn`). `references/design-system.md` ships ready-made palettes for AI, fintech, crypto, health, fashion, and editorial — or derive your own from the topic's brand colours. Render at `--size 1080x1350` for a 4:5 portrait set.

## License

MIT — see [LICENSE](LICENSE).

---

Built with [Claude Code](https://claude.com/claude-code).
