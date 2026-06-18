import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

CREATOR = "امیر علی فروزان اصل"
DB = "database.json"


def load_db():
    try:
        with open(DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"users": {}}


def save_db(data):
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton("✅ قبول قوانین", callback_data="accept"),
            InlineKeyboardButton("❌ رد", callback_data="reject")
        ]
    ]

    await update.message.reply_text(
        f"""
📜 قوانین ربات

👨‍💻 سازنده: {CREATOR}

قبل از استفاده قوانین را قبول کنید.

مسئولیت استفاده با کاربر است.
""",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    db = load_db()

    if query.data == "accept":

        db["users"][user_id] = {
            "accepted": True,
            "warnings": 0
        }

        save_db(db)

        await query.edit_message_text(
            "✅ قوانین قبول شد\n🤖 حالا می‌توانید از ربات استفاده کنید"
        )


    elif query.data == "reject":

        await query.edit_message_text(
            "❌ بدون قبول قوانین امکان استفاده نیست"
        )


def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
