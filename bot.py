import os
import google.generativeai as genai

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from database import *

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    "gemini-1.5-pro"
)

RULES = """
📜 قوانین ربات

1- سوال سیاسی ممنوع
2- فحاشی ممنوع
3- بعد از 3 اخطار دسترسی قطع می‌شود

مسئولیت استفاده بر عهده کاربر است.
"""

political_words = [
    "سیاست",
    "politics",
    "election",
    "president"
]

bad_words = [
    "fuck",
    "shit",
    "کص",
    "حروم"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    create_user(uid)

    keyboard = [
        [InlineKeyboardButton(
            "📜 مشاهده قوانین",
            callback_data="rules"
        )],
        [InlineKeyboardButton(
            "✅ قبول قوانین",
            callback_data="accept"
        )]
    ]

    await update.message.reply_text(
        "🤖 به ربات Gemini خوش آمدید",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query

    await q.answer()

    uid = q.from_user.id

    create_user(uid)

    if q.data == "rules":
        await q.message.reply_text(RULES)

    elif q.data == "accept":
        accept_rules(uid)

        await q.message.reply_text(
            "✅ قوانین قبول شد"
        )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    create_user(uid)

    accepted, warns, banned = get_user(uid)

    if banned:
        await update.message.reply_text(
            "🚫 شما بن شده‌اید"
        )
        return

    if not accepted:
        await update.message.reply_text(
            "❌ ابتدا قوانین را قبول کنید"
        )
        return

    text = update.message.text.lower()

    if any(x in text for x in political_words):
        add_warn(uid)

        accepted, warns, banned = get_user(uid)

        if warns >= 3:
            ban_user(uid)

            await update.message.reply_text(
                "🚫 به علت تکرار تخلف بن شدید"
            )
            return

        await update.message.reply_text(
            f"⚠️ اخطار سیاسی ({warns}/3)"
        )
        return

    if any(x in text for x in bad_words):
        add_warn(uid)

        accepted, warns, banned = get_user(uid)

        if warns >= 3:
            ban_user(uid)

            await update.message.reply_text(
                "🚫 به علت تکرار تخلف بن شدید"
            )
            return

        await update.message.reply_text(
            f"⚠️ اخطار فحاشی ({warns}/3)"
        )
        return

    try:
        response = model.generate_content(
            update.message.text
        )

        await update.message.reply_text(
            response.text
        )

    except Exception:
        await update.message.reply_text(
            "❌ خطا در ارتباط با Gemini"
        )

def main():
    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(buttons)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    app.run_polling()

if __name__ == "__main__":
    main()
