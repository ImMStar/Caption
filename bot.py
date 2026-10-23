import html
import logging
import os

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters,
)

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s", level=logging.INFO
)
log = logging.getLogger("captionbot")

BOT_TOKEN = os.environ["BOT_TOKEN"]
DATA_FILE = os.environ.get("DATA_FILE", "bot_data.pickle")

MODES = {
    "remove": "Remove the caption",
    "replace": "Replace the caption with your text",
    "append": "Add your text after the original caption",
    "prepend": "Add your text before the original caption",
}

HELP = (
    "Send or forward any photo, video, document, audio, voice or GIF and I'll "
    "send it back with the caption changed.\n\n"
    "Commands:\n"
    "/mode remove|replace|append|prepend - choose what I do (default: remove)\n"
    "/caption <text> - set the text used by replace/append/prepend\n"
    "/status - show your current settings\n"
    "/reset - go back to defaults\n\n"
    "Tip: send several files in a row and I'll process each one."
)


def settings(context: ContextTypes.DEFAULT_TYPE) -> dict:
    ud = context.user_data
    ud.setdefault("mode", "remove")
    ud.setdefault("text", "")
    return ud


def build_caption(mode: str, text: str, original_html: str) -> str | None:
    """Return the new caption as HTML, or None for no caption."""
    safe = html.escape(text)
    if mode == "remove":
        return None
    if mode == "replace":
        return safe or None
    if mode == "append":
        return (original_html + "\n\n" + safe).strip() or None
    if mode == "prepend":
        return (safe + "\n\n" + original_html).strip() or None
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings(context)
    await update.message.reply_text(HELP)


async def mode_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = settings(context)
    if not context.args or context.args[0].lower() not in MODES:
        lines = [f"/mode {k} - {v}" for k, v in MODES.items()]
        await update.message.reply_text("Choose a mode:\n" + "\n".join(lines))
        return
    s["mode"] = context.args[0].lower()
    note = ""
    if s["mode"] != "remove" and not s["text"]:
        note = "\nNow set your text with /caption <text>."
    await update.message.reply_text(f"Mode set to: {s['mode']}.{note}")


async def caption_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = settings(context)
    text = update.message.text.partition(" ")[2].strip()
    if not text:
        await update.message.reply_text("Usage: /caption Your text here")
        return
    if len(text) > 1024:
        await update.message.reply_text("Telegram captions can be at most 1024 characters.")
        return
    s["text"] = text
    await update.message.reply_text("Caption text saved.")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = settings(context)
    shown = s["text"] if s["text"] else "(not set)"
    await update.message.reply_text(
        f"Mode: {s['mode']} - {MODES[s['mode']]}\nText: {shown}"
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    settings(context)
    await update.message.reply_text("Settings reset. Mode is now: remove.")


async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = update.message
    s = settings(context)
    cap = build_caption(s["mode"], s["text"], m.caption_html or "")
    kw = {"caption": cap, "parse_mode": ParseMode.HTML if cap else None}
    chat = m.chat_id

    try:
        # Animation must be checked before document (a GIF is also a document).
        if m.animation:
            await context.bot.send_animation(chat, m.animation.file_id, **kw)
        elif m.photo:
            await context.bot.send_photo(chat, m.photo[-1].file_id, **kw)
        elif m.video:
            await context.bot.send_video(
                chat, m.video.file_id, supports_streaming=True, **kw
            )
        elif m.audio:
            await context.bot.send_audio(chat, m.audio.file_id, **kw)
        elif m.voice:
            await context.bot.send_voice(chat, m.voice.file_id, **kw)
        elif m.document:
            await context.bot.send_document(chat, m.document.file_id, **kw)
    except BadRequest as e:
        log.warning("BadRequest: %s", e)
        await m.reply_text(
            "Telegram rejected the new caption (it may be longer than 1024 "
            "characters). Try a shorter text."
        )
    except Exception:
        log.exception("Unexpected error")
        await m.reply_text("Something went wrong. Please try again.")


def main():
    persistence = PicklePersistence(filepath=DATA_FILE)
    app = Application.builder().token(BOT_TOKEN).persistence(persistence).build()

    app.add_handler(CommandHandler(["start", "help"], start))
    app.add_handler(CommandHandler("mode", mode_cmd))
    app.add_handler(CommandHandler("caption", caption_cmd))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("reset", reset))

    media = (
        filters.PHOTO
        | filters.VIDEO
        | filters.ANIMATION
        | filters.AUDIO
        | filters.VOICE
        | filters.Document.ALL
    )
    app.add_handler(MessageHandler(media & ~filters.COMMAND, handle_media))

    log.info("Caption editor bot started (polling)")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
