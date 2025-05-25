from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from config.settings import FIREWORKS_API_KEY
import json
import requests
from bot.message_handler import url, set_style

# Command /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"سلام کاربر {user.first_name} خوش آمدی"
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "این ربات سایفر هستش که توسط ShahinAI ساخته شده هنوز اطلاعات درستی درباره سازندگان ربات در دسترس نیست و اطلاعاتی درمورد برند ShahinAI در اینترنت نیست. هرگونه کپی برداری از این ربات پیگرد قانونی و غیر قانونی دارد!"
    )

# Command /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        " ... \n"
        "📚 لیست دستورات موجود:\n"
        "/start - شروع کار با ربات\n"
        "/help - نمایش این رهنما\n"
        "/about - اطلاعات درباره سازنده ربات\n"
        "/style - تغییر لحن ربات\n"
        "/summarize - خلاصه‌سازی متن یا پیام ریپلای‌شده\n"
        "/translate - ترجمه متن\n"
        " ... \n"
    )

async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get text: either from argument or from reply
    if context.args:
        text = " ".join(context.args)
    elif update.message.reply_to_message and update.message.reply_to_message.text:
        text = update.message.reply_to_message.text
    else:
        await update.message.reply_text("❗ لطفاً متنی را برای خلاصه‌سازی ارسال یا ریپلای کن.")
        return

    prompt = f"این متن را خلاصه کن:\n\n{text}"

    payload = {
        "model": "accounts/fireworks/models/llama-v3p1-405b-instruct",
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

    await update.message.reply_text(reply)

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = " ".join(context.args)
    elif update.message.reply_to_message and update.message.reply_to_message.text:
        text = update.message.reply_to_message.text
    else:
        await update.message.reply_text("❗ لطفاً متنی برای ترجمه بنویس یا روی پیام ریپلای کن.")
        return

    # Give clear instructions for translation
    prompt = f"این متن را به زبان دیگر ترجمه کن:\n{text}"

    # Give the message to the LLaMA-3 model (like all other messages)
    payload = {
        "model": "accounts/fireworks/models/llama-v3p1-405b-instruct",
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
        await update.message.reply_text(f"🌍 ترجمه:\n{translation}")
    except Exception as e:
        print("🔥 Translate error:", e)
        await update.message.reply_text("❗ مشکلی در ترجمه پیش آمد.")



# Register commands in the application
def register_command_handlers(app: Application):
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("style", set_style))
    app.add_handler(CommandHandler("summarize", summarize))
    app.add_handler(CommandHandler("translate", translate))
