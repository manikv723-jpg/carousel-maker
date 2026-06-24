#!/usr/bin/env python3
"""
Post a rendered carousel folder to a Telegram chat as album(s).

Usage:
  python3 send_telegram.py <outdir> --token <BOT_TOKEN> --chat <CHAT_ID> [--caption "text"]

Env fallback: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID (keep the token in env, never in the repo).

Sends the slides in 01..NN order as Telegram media groups (albums). Telegram caps a
group at 10 items, so an 11-slide carousel goes out as 10 + 1. Photos and videos can
share one album, so the static + motion slides post together in order.

Requires: requests  (pip install requests)
Built for headless agents (Hermes / OpenClaw / any Telegram bot) — see references/integration.md.
"""
import os, sys, json, glob, argparse
try:
    import requests
except ImportError:
    sys.exit("send_telegram.py needs `requests`  →  pip install requests")

ap = argparse.ArgumentParser()
ap.add_argument("dir", help="render output folder (contains 01.png/mp4 … and manifest.json)")
ap.add_argument("--token", default=os.environ.get("TELEGRAM_BOT_TOKEN"))
ap.add_argument("--chat",  default=os.environ.get("TELEGRAM_CHAT_ID"))
ap.add_argument("--caption", default="", help="caption on the first slide")
a = ap.parse_args()
if not a.token or not a.chat:
    sys.exit("need --token and --chat (or env TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID)")

# ordered files: prefer manifest.json, else sort numeric png/mp4
mf = os.path.join(a.dir, "manifest.json")
if os.path.exists(mf):
    files = [os.path.join(a.dir, s["file"]) for s in json.load(open(mf))["slides"]]
else:
    files = sorted(glob.glob(os.path.join(a.dir, "[0-9]*.png")) +
                   glob.glob(os.path.join(a.dir, "[0-9]*.mp4")))
files = [f for f in files if os.path.exists(f)]
if not files:
    sys.exit("no slides found in " + a.dir)

api = f"https://api.telegram.org/bot{a.token}/sendMediaGroup"
def chunks(lst, n):
    for i in range(0, len(lst), n): yield lst[i:i+n]

first = True
for group in chunks(files, 10):
    media, fh = [], {}
    for i, p in enumerate(group):
        key = f"f{i}"
        typ = "video" if p.lower().endswith(".mp4") else "photo"
        item = {"type": typ, "media": f"attach://{key}"}
        if first and i == 0 and a.caption:
            item["caption"] = a.caption
        media.append(item)
        fh[key] = open(p, "rb")
    r = requests.post(api, data={"chat_id": a.chat, "media": json.dumps(media)},
                      files=fh, timeout=180)
    for f in fh.values(): f.close()
    ok = False
    try: ok = r.json().get("ok")
    except Exception: pass
    print(f"sent {len(group)} ({os.path.basename(group[0])}…) -> {r.status_code} ok={ok}")
    if not ok:
        print(r.text[:300]); sys.exit(1)
    first = False
print("delivered", len(files), "slides to chat", a.chat)
