# Integrating into agents (Hermes / OpenClaw / Telegram bots)

Every step except the story/design judgment is a plain CLI, so any agent runtime
can drive this skill. The agent's LLM does the writing & layout (guided by
`SKILL.md`); the scripts do scrape-prep, render, and delivery.

## Two modes
- **Interactive** (a human in the chat): ask the brief intake questions (handle,
  brand, use case) as messages, then build. This is the default.
- **Non-interactive / headless** (bots, cron, queues): **do not block on
  questions.** Take inputs from the incoming message or a stored brand profile,
  fall back to defaults, auto-derive the palette, render, and deliver — then
  offer alternate palettes in a follow-up message the user can tap.

## Inputs the agent parses (from the message or its config)
- `url` — article / tweet / reel (required)
- `brand` — handle + CTA (from the per-user brand profile below)
- `palette` — a name from `assets/palettes.json` (optional; else auto-derive)
- `slides` (default 8–10), `aspect` (`1080x1080` | `1080x1350`)

A simple message convention works well:
`<url>  brand:@acme  palette:violet-dark  slides:9`

## Brand profile (so a bot serves one creator by default)
Store `brand.json` per user/bot and pass it into the build so the agent never
has to ask:
```json
{ "handle": "@acme", "cta": "follow for daily AI",
  "palette": "violet-dark", "logo": "assets/acme-logo.png",
  "colors": { "--bg":"#0E0A1A", "--accent":"#A675FF" } }
```
`colors` (optional) overrides specific palette vars; `logo` goes on the cover.

## Output contract
`render_ig.py <deck> <outdir> [--palette name]` writes `outdir/NN.png|mp4` **plus**
`outdir/manifest.json`:
```json
{ "size":"1080x1080", "palette":"violet-dark", "count":11,
  "slides":[ {"index":1,"file":"01.png","type":"image"},
             {"index":5,"file":"05.mp4","type":"video"}, ... ] }
```
The agent reads `manifest.json` to know exactly what to send, and in what order.

## Deliver to Telegram
```
python3 assets/send_telegram.py <outdir> \
  --token "$TELEGRAM_BOT_TOKEN" --chat <chat_id> --caption "Qwen-AgentWorld, explained"
```
Posts the slides as album(s) — 10 per group, photos + videos mixed, in order.
Reads `manifest.json` for ordering. (Or the agent uploads via its own Telegram
client; the manifest gives it the file list.)

## Minimal agent loop (pseudocode)
```
on_message(text):
    url, opts = parse(text)                      # url + brand/palette/slides
    wd = make_workdir()
    scrape(url, wd)                              # references/scraping.md
    deck = build_deck(wd, brand_profile, opts)   # template.html + the story
    run("render_ig.py", deck, wd/"out", "--palette", opts.palette or auto)
    run("send_telegram.py", wd/"out", "--token", TOKEN, "--chat", chat_id)
    reply("Want another look? aqua-dark · violet-dark · mono-light")
on_reply(palette):
    run("render_ig.py", deck, wd/("out_"+palette), "--palette", palette)
    run("send_telegram.py", wd/("out_"+palette), "--token", TOKEN, "--chat", chat_id)
```
Re-skinning is cheap: the deck never changes, only `--palette`. Offer the palette
chooser image (`palette_preview.py`) up front if the user wants to pick first.

## Runtime notes (headless hosts)
- Needs **Google Chrome** (Playwright `channel="chrome"`), **ffmpeg**, **yt-dlp** on the host.
  On a server: install Chrome; Playwright runs it headless (no display needed).
- `send_telegram.py` needs `requests`. The only network credential is the bot token.
- Keep the token in env (`TELEGRAM_BOT_TOKEN`) — never in the deck, manifest, or repo.
- One render of a 10-slide deck is seconds for statics, a few seconds per video slide.
- Everything is local files until `send_telegram.py` — safe to run in a sandbox.
