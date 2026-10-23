# Caption Editor Bot

A Telegram bot that edits the caption of files you send it, using a button
panel under the file. Works with photos, videos, documents, audio, voice notes
and GIFs. It re-sends files by Telegram file ID, so nothing is downloaded and
big files work too.

## Use
Send or forward a file. The bot sends it back with these buttons:

- **Remove ID** - removes @usernames
- **Remove link** - removes links
- **Remove #** - removes hashtags
- **Default text** - adds your saved default text
- **Delete text** - removes the text you added
- **At Top / At Bottom** - where the added text goes
- **Add new text** - the bot asks for a text, then adds it
- **Done** - finishes and removes the buttons

Commands:
- `/settext <text>` saves your default text
- `/status` shows it, `/cancel` cancels "Add new text", `/reset` clears settings

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
- Settings and button panels are saved in `bot_data.pickle`. On Render this
  file resets on each deploy unless you attach a persistent disk. Old panels
  then stop working and users just send the file again.
