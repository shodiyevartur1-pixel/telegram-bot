import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes   
)
from yt_dlp import YoutubeDL

# ---------------- CONFIG ----------------
BOT_TOKEN = "7440221707:AAFFYF9QuP1DyDAqGe232Z7tkOvsOolDn-4"
DOWNLOADS = "downloads"
os.makedirs(DOWNLOADS, exist_ok=True)
logging.basicConfig(level=logging.ERROR)

# ---------------- TEMP STORAGE ----------------
USER_LANG = {}     # user_id -> lang
LAST_VIDEO = {}    # user_id -> (url, vid_id)

# ---------------- TEXTS ----------------
TEXT = {
    "uz": {
        "start": (
            "🔥 Assalomu alaykum! @songsavedinsta_bot ga xush kelibsiz.\n\n"
            "🚀 Yuklab olish imkoniyatlari:\n"
            "• Instagram (Post, Reels, Story)\n"
            "• TikTok (Suv belgisiz, HD)\n"
            "• YouTube (Video, Shorts, Audio)\n"
            "• Pinterest, Likee, Snapchat, Threads\n\n"
            "🎵 Shazam & Qidiruv:\n"
            "• Qo‘shiq nomi yoki ijrochi\n"
            "• Audio / Video / Voice yuboring\n\n"
            "🔗 Havolani yuboring yoki musiqa nomini yozing!"
        ),
        "wait": "⏳ Yuklanmoqda...",
        "sending": "📤 Telegramga yuborilmoqda...",
        "done": "✅ Video yuklandi",
        "mp3": "🎵 Musiqani yuklab olish",
        "error": "❌ Yuklab bo‘lmadi",
        "help": "☎ Yordam uchun admin bilan bog‘laning: @shodiyeevv",
        "choose_lang": "🌍 Tilni tanlang:"
    },
    "ru": {
        "start": (
            "🔥 Здравствуйте! Добро пожаловать в @songsavedinsta_bot.\n\n"
            "🚀 Возможности загрузки:\n"
            "• Instagram (Посты, Reels, Stories)\n"
            "• TikTok (Без водяного знака, HD)\n"
            "• YouTube (Видео, Shorts, Аудио)\n"
            "• Pinterest, Likee, Snapchat, Threads\n\n"
            "🎵 Shazam и поиск:\n"
            "• Название песни или исполнитель\n"
            "• Отправьте Audio / Video / Voice\n\n"
            "🔗 Отправьте ссылку или название музыки!"
        ),
        "wait": "⏳ Подготовка...",
        "sending": "📤 Отправка...",
        "done": "✅ Готово",
        "mp3": "🎵 Скачать музыку",
        "error": "❌ Ошибка при загрузке",
        "help": "💡 Для помощи свяжитесь с администратором: @shodiyeevv",
        "choose_lang": "🌍 Выберите язык:"
    }
}

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in USER_LANG:
        kb = [[
            InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
        ]]
        await update.message.reply_text(TEXT["uz"]["choose_lang"], reply_markup=InlineKeyboardMarkup(kb))
        return
    lang = USER_LANG[user_id]
    await update.message.reply_text(TEXT[lang]["start"])

# ---------------- LANGUAGE CALLBACK ----------------
async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    USER_LANG[query.from_user.id] = lang
    await query.message.delete()
    # Til tanlangan zahoti darhol start xabari chiqadi
    await context.bot.send_message(query.from_user.id, TEXT[lang]["start"])

# ---------------- LANGUAGE COMMAND ----------------
async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[
        InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang_uz"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    ]]
    await update.message.reply_text(TEXT["uz"]["choose_lang"], reply_markup=InlineKeyboardMarkup(kb))

# ---------------- HELP ----------------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = USER_LANG.get(user_id, "uz")
    await update.message.reply_text(TEXT[lang]["help"])

# ---------------- DOWNLOAD VIDEO ----------------
def download_video(url: str):
    # ✅ Instagram postlarni ham yuklash uchun cookies/login opsiyasi
    opts = {
        "format": "bestvideo[height<=720]+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": f"{DOWNLOADS}/%(id)s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        # Agar xohlasang login qo‘shish mumkin:
        # "username": "INSTAGRAM_USERNAME",
        # "password": "INSTAGRAM_PASSWORD",
        # yoki "cookies": "cookies.txt"
    }
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info), info["id"]

# ---------------- DOWNLOAD AUDIO ----------------
def download_audio(url: str, vid: str):
    opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOADS}/{vid}.mp3",
        "postprocessors": [{"key": "FFmpegExtractAudio","preferredcodec": "mp3","preferredquality": "192"}],
        "quiet": True
    }
    with YoutubeDL(opts) as ydl:
        ydl.download([url])
    return f"{DOWNLOADS}/{vid}.mp3"

# ---------------- HANDLE MESSAGE ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text or ""
    if user_id not in USER_LANG:
        return await start(update, context)
    lang = USER_LANG[user_id]
    if not text.startswith("http"):
        return
    wait = await update.message.reply_text(TEXT[lang]["wait"])
    try:
        path, vid = await asyncio.to_thread(download_video, text)
        LAST_VIDEO[user_id] = (text, vid)
        kb = [[InlineKeyboardButton(TEXT[lang]["mp3"], callback_data=f"mp3_{vid}")]]
        await wait.edit_text(TEXT[lang]["sending"])
        with open(path, "rb") as f:
            await update.message.reply_video(
                video=InputFile(f),
                caption=f"{TEXT[lang]['done']}\n\n🤖 @songsavedinsta_bot",
                reply_markup=InlineKeyboardMarkup(kb)
            )
        os.remove(path)
        await wait.delete()
    except:
        await wait.edit_text(TEXT[lang]["error"])

# ---------------- MP3 CALLBACK ----------------
async def mp3_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = USER_LANG.get(user_id, "uz")
    if user_id not in LAST_VIDEO:
        return
    url, vid = LAST_VIDEO[user_id]
    msg = await context.bot.send_message(user_id, TEXT[lang]["wait"])
    try:
        mp3 = await asyncio.to_thread(download_audio, url, vid)
        with open(mp3, "rb") as f:
            await context.bot.send_audio(chat_id=user_id, audio=InputFile(f),
                                         caption=f"🎵 @songsavedinsta_bot")
        os.remove(mp3)
        await msg.delete()
    except:
        await msg.edit_text(TEXT[lang]["error"])

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("language", language_command))

    # Callback (MP3 + Language)
    app.add_handler(CallbackQueryHandler(mp3_callback, pattern="^mp3_"))
    app.add_handler(CallbackQueryHandler(lang_callback, pattern="^lang_"))

    # Video links
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 @songsavedinsta_bot ishga tushdi")
    app.run_polling()

if __name__ == "__main__":
    main()