import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import Command
from aiogram.enums import ChatMemberStatus
import yt_dlp

# ================= CONFIG =================

BOT_TOKEN = "7440221707:AAFFYF9QuP1DyDAqGe232Z7tkOvsOolDn-4"
ADMIN_USERNAME = "@shodiyeevv"
CHANNEL_ID = -1003896595389
CHANNEL_LINK = "https://t.me/+aLw1BSpmn_k0N2Ni"

# ==========================================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ============ KEYBOARDS ===================

def subscribe_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📢 Obuna bo‘lish", url=CHANNEL_LINK)
        ],
        [
            InlineKeyboardButton(text="✅ Obuna bo‘ldim", callback_data="check_sub")
        ]
    ])

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Video yuklash", callback_data="download")
        ],
        [
            InlineKeyboardButton(text="🌐 Language", callback_data="language")
        ],
        [
            InlineKeyboardButton(text="❓ Help", callback_data="help")
        ]
    ])

# ============ SUBSCRIBE CHECK ==============

async def check_subscription(user_id):
    member = await bot.get_chat_member(CHANNEL_ID, user_id)
    return member.status in [
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR
    ]

# ============== START ======================

@dp.message(Command("start"))
async def start_handler(message: Message):
    is_subscribed = await check_subscription(message.from_user.id)

    if not is_subscribed:
        await message.answer(
            "👋 Assalomu alaykum!\n\n"
            "Botdan foydalanish uchun avval kanalga obuna bo‘ling.",
            reply_markup=subscribe_keyboard()
        )
        return

    await message.answer(
        "🎉 Xush kelibsiz!\n\n"
        "Instagram, TikTok, YouTube, Pinterest va boshqa platformalardan video yuklab beraman.\n\n"
        "👇 Quyidagilardan birini tanlang:",
        reply_markup=main_menu()
    )

# ============= CHECK BUTTON ===============

@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
    is_subscribed = await check_subscription(callback.from_user.id)

    if not is_subscribed:
        await callback.answer("❌ Avval kanalga obuna bo‘ling!", show_alert=True)
        return

    await callback.message.edit_text(
        "✅ Obuna tasdiqlandi!\n\n"
        "Botdan bemalol foydalanishingiz mumkin.",
        reply_markup=main_menu()
    )

# ============= HELP ========================

@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "❓ Botdan foydalanish:\n\n"
        "1️⃣ Video linkini yuboring\n"
        "2️⃣ Bot yuklab beradi\n\n"
        f"👨‍💻 Admin: {ADMIN_USERNAME}"
    )

# ============= LANGUAGE ====================

@dp.message(Command("language"))
async def language_handler(message: Message):
    await message.answer(
        "🌐 Hozircha til: 🇺🇿 O‘zbek\n"
        "Tez orada boshqa tillar qo‘shiladi."
    )

# ============= VIDEO DOWNLOAD ==============

@dp.message(F.text)
async def download_video(message: Message):
    url = message.text

    if not url.startswith("http"):
        return

    is_subscribed = await check_subscription(message.from_user.id)
    if not is_subscribed:
        await message.answer(
            "❌ Avval kanalga obuna bo‘ling!",
            reply_markup=subscribe_keyboard()
        )
        return

    await message.answer("⏳ Yuklab olinmoqda...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        await message.answer_video(
            video=open(file_name, 'rb'),
            caption="🎬 Mana siz so‘ragan video!"
        )

        os.remove(file_name)

    except Exception:
        await message.answer(
            "❌ Video yuklab bo‘lmadi.\n"
            "Link to‘g‘riligini tekshiring."
        )

# ===========================================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
