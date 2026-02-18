import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.enums import ChatMemberStatus
import yt_dlp

# ================= CONFIG =================

BOT_TOKEN = "7440221707:AAFFYF9QuP1DyDAqGe232Z7tkOvsOolDn-4"
ADMIN_ID = 8059999086
ADMIN_USERNAME = "@shodiyeevv"
CHANNEL_ID = -1003896595389
CHANNEL_LINK = "https://t.me/+aLw1BSpmn_k0N2Ni"

# ==========================================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ====== MEMORY (til saqlash uchun) ======

user_languages = {}

# ============ KEYBOARD ===================

def subscribe_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Obuna bo‘lish", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Obuna bo‘ldim", callback_data="check_sub")]
    ])

def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O‘zbek", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
    ])

# ============ SUB CHECK ==================

async def check_subscription(user_id):
    member = await bot.get_chat_member(CHANNEL_ID, user_id)
    return member.status in [
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR
    ]

# ============= START =====================

@dp.message(Command("start"))
async def start_handler(message: Message):
    is_subscribed = await check_subscription(message.from_user.id)

    if not is_subscribed:
        await message.answer(
            "📢 Botdan foydalanish uchun kanalga obuna bo‘ling.",
            reply_markup=subscribe_keyboard()
        )
        return

    await message.answer(
        "🎉 Xush kelibsiz!\n\n"
        "🔗 Video link yuboring (Instagram, TikTok, YouTube, Pinterest)\n\n"
        "Tilni o‘zgartirish: /language"
    )

# ============= LANGUAGE ==================

@dp.message(Command("language"))
async def language_command(message: Message):
    await message.answer("🌐 Tilni tanlang:", reply_markup=language_keyboard())

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_languages[callback.from_user.id] = lang

    if lang == "uz":
        text = "🇺🇿 Til o‘zbek tiliga o‘zgartirildi!"
    else:
        text = "🇷🇺 Язык изменен на русский!"

    await callback.answer("✅ Saqlandi!")
    await callback.message.edit_text(text)

# ============= HELP ======================

@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "❓ Foydalanish:\n\n"
        "1️⃣ Video link yuboring\n"
        "2️⃣ Bot yuklab beradi\n\n"
        f"👨‍💻 Admin: {ADMIN_USERNAME}"
    )

# ============= ADMIN =====================

@dp.message(Command("admin"))
async def admin_command(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Siz admin emassiz.")
        return

    await message.answer("👑 Admin panel ishlayapti ✅")

# ============= SUB CHECK BUTTON ==========

@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
    is_subscribed = await check_subscription(callback.from_user.id)

    if not is_subscribed:
        await callback.answer("❌ Avval obuna bo‘ling!", show_alert=True)
        return

    await callback.message.edit_text(
        "✅ Obuna tasdiqlandi!\n\n"
        "Endi link yuborishingiz mumkin 🚀"
    )

# ============= VIDEO DOWNLOAD ============

@dp.message(F.text)
async def download_video(message: Message):
    url = message.text.strip()

    if not url.startswith("http"):
        return

    is_subscribed = await check_subscription(message.from_user.id)
    if not is_subscribed:
        await message.answer("❌ Avval kanalga obuna bo‘ling!", reply_markup=subscribe_keyboard())
        return

    waiting = await message.answer("⏳ Yuklanmoqda...")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await message.answer_video(
            video=open(filename, 'rb'),
            caption="🎬 Tayyor!"
        )

        os.remove(filename)
        await waiting.delete()

    except Exception as e:
        await waiting.edit_text("❌ Video yuklab bo‘lmadi.")

# =========================================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
