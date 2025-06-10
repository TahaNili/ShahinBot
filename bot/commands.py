from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, Application
from config.settings import FIREWORKS_API_KEY
import json
import requests
import re
from bot.message_handler import url, set_style

# Command /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text( # type: ignore
        f"سلام کاربر {user.first_name} خوش آمدی" # type: ignore
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text( # type: ignore
        "این ربات سایفر هستش که توسط ShahinAI ساخته شده هنوز اطلاعات درستی درباره سازندگان ربات در دسترس نیست و اطلاعاتی درمورد برند ShahinAI در اینترنت نیست. هرگونه کپی برداری از این ربات پیگرد قانونی و غیر قانونی دارد!"
    )

async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get text: either from argument or from reply
    if context.args:
        text = " ".join(context.args)
    elif update.message.reply_to_message and update.message.reply_to_message.text: # type: ignore
        text = update.message.reply_to_message.text # type: ignore
    else:
        await update.message.reply_text("❗ لطفاً متنی را برای خلاصه‌سازی ارسال یا ریپلای کن.") # type: ignore
        return

    prompt = f"این متن را خلاصه کن:\n\n{text}"

    payload = {
        "model": "accounts/fireworks/models/llama4-maverick-instruct-basic",
        "max_tokens": 500,
        "temperature": 0.5,
        "messages": [
            {"role": "system", "content": "تو یک ربات خلاصه‌ساز هستی که متن‌ها را کوتاه و مفید می‌کنی."},
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        reply = result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        reply = "❗ مشکلی در خلاصه‌سازی پیش اومد."
        print("🔥 summarize error:", e)

    await update.message.reply_text(reply) # type: ignore

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = " ".join(context.args)
    elif update.message.reply_to_message and update.message.reply_to_message.text: # type: ignore
        text = update.message.reply_to_message.text # type: ignore
    else:
        await update.message.reply_text("❗ لطفاً متنی برای ترجمه بنویس یا روی پیام ریپلای کن.") # type: ignore
        return

    # Give clear instructions for translation
    prompt = f"این متن را به زبان دیگر ترجمه کن:\n{text}"

    # Give the message to the LLaMA-3 model (like all other messages)
    payload = {
        "model": "accounts/fireworks/models/qwen3-235b-a22b",
        "max_tokens": 1024,
        "temperature": 0.5,
        "messages": [
            {"role": "system", "content": "تو یک مترجم دقیق و حرفه‌ای هستی که متون را به فارسی و انگلیسی ترجمه می‌کنی."},
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post("https://api.fireworks.ai/inference/v1/chat/completions", headers=headers, data=json.dumps(payload))
        res.raise_for_status()
        result = res.json()
        translation = result["choices"][0]["message"]["content"].strip()
        await update.message.reply_text(f"🌍 ترجمه:\n{translation}") # type: ignore
    except Exception as e:
        print("🔥 Translate error:", e)
        await update.message.reply_text("❗ مشکلی در ترجمه پیش آمد.") # type: ignore

async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private": # type: ignore
        await update.message.reply_text("❗ این دستور فقط در چت خصوصی کار می‌کند.") # type: ignore
        return

    bot_username = (await context.bot.get_me()).username
    keyboard = [
        [InlineKeyboardButton("افزودن به گروه یا کانال", url=f"https://t.me/{bot_username}?startgroup=true")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text( # type: ignore
        "برای اضافه کردن من به گروه یا کانال، روی دکمه زیر بزن و گروه موردنظرت رو انتخاب کن:",
        reply_markup=reply_markup
    )

# Register commands in the application
def register_command_handlers(app: Application):
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("style", set_style))
    app.add_handler(CommandHandler("summarize", summarize))
    app.add_handler(CommandHandler("translate", translate))
    app.add_handler(CommandHandler("join", join_command))
