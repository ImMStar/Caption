# Caption Editor Bot

A Telegram bot that edits or removes the caption of files you send it.
Works with photos, videos, documents, audio, voice notes and GIFs. It re-sends
files by Telegram file ID, so nothing is downloaded and big files work too.

## Use
- Send or forward a file: the bot returns it with the caption changed.
- `/mode remove|replace|append|prepend` picks what happens (default: remove).
- `/caption <text>` sets the text for replace/append/prepend.
- `/status` shows settings, `/reset` restores defaults.

## Create the bot
1. Chat with @BotFather on Telegram, send `/newbot`, copy the token.

## Run locally
```bash
pip install -r requirements.txt
export BOT_TOKEN="123456:ABC..."
python bot.py
```

## Deploy on Render
1. Push this folder to a GitHub repo.
2. Render: New > Background Worker > connect the repo.
3. Build: `pip install -r requirements.txt`  Start: `python bot.py`
4. Add the environment variable `BOT_TOKEN`, then deploy.

Notes:
- Render's free tier has no background workers. Use a paid worker or a Web
  Service with a small health endpoint.
- User settings are saved in `bot_data.pickle`. On Render this file resets on
  each deploy unless you attach a persistent disk. If it resets, users simply
  start again with the default mode.
