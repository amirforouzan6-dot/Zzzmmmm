import os
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from groq import Groq


BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

CREATOR = "امیر علی فروزان اصل"

client = Groq(api_key=GROQ_KEY)

DB_FILE = "database.json"


def load_db():
    try:
        with open(DB_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"users":{}}


def save_db(data):
    with open(DB_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ قبول قوانین",
                callback_data="ok"
            ),
            InlineKeyboardButton(
                "❌ رد",
                callback_data="no"
            )
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



async def button(update:Update, context:ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    uid = str(query.from_user.id)

    db = load_db()


    if query.data == "ok":

        db["users"][uid] = {
            "accepted":True
        }

        save_db(db)

        await query.edit_message_text(
            "✅ قوانین قبول شد\n🤖 حالا پیام بده"
        )


    elif query.data == "no":

        await query.edit_message_text(
            "❌ بدون قبول قوانین استفاده نمی‌شود"
        )



async def ai_chat(update:Update, context:ContextTypes.DEFAULT_TYPE):

    uid = str(update.message.from_user.id)

    db = load_db()

    if uid not in db["users"]:
        await update.message.reply_text(
            "❌ اول /start بزن و قوانین را قبول کن"
        )
        return


    try:

        res = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                "role":"user",
                "content":update.message.text
                }
            ]
        )


        await update.message.reply_text(
            res.choices[0].message.content
        )


    except Exception as e:

        await update.message.reply_text(
            "❌ خطا در هوش مصنوعی"
        )




def main():

    app = Application.builder().token(BOT_TOKEN).build()


    app.add_handler(
        CommandHandler("start",start)
    )


    app.add_handler(
        CallbackQueryHandler(button)
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            ai_chat
        )
    )


    print("RUNNING")

    app.run_polling()



if __name__=="__main__":
    main()
