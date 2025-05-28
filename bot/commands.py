from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from config.settings import FIREWORKS_API_KEY
import json
import requests
import re
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

async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only process invite links in private chats
    if update.message.chat.type != "private":
        await update.message.reply_text("❗ این دستور فقط در چت خصوصی کار می‌کند.")
        return

    if not context.args:
        await update.message.reply_text("❗ لطفاً لینک دعوت گروه را وارد کنید (مثل /join t.me/+abc123)")
        return

    invite_link = context.args[0]
    # Regex to detect Telegram invite links (e.g., t.me/+abc123 or t.me/joinchat/abc123)
    invite_link_pattern = r"(?:https?://)?t\.me/(?:\+|joinchat/)([A-Za-z0-9_-]+)"
    match = re.search(invite_link_pattern, invite_link)

    if not match:
        await update.message.reply_text("❗ لطفاً یک لینک دعوت معتبر تلگرام (مثل t.me/+abc123) وارد کنید.")
        return

    invite_hash = match.group(1)

    try:
        # Join the group using the invite link
        result = await context.bot.join_chat(invite_hash)
        group_name = result.title if result.title else "گروه بدون نام"

        # Send a confirmation message to the user
        await update.message.reply_text(
            f"✅ با موفقیت به گروه «{group_name}» پیوستم!\n"
            "لطفاً من را به عنوان ادمین گروه تنظیم کنید و دسترسی‌های زیر را بدهید:\n"
            "📩 ارسال پیام\n"
            "📌 مدیریت پیام‌ها (در صورت نیاز)\n"
            "برای این کار، به تنظیمات گروه بروید، من را به عنوان ادمین اضافه کنید و دسترسی‌های لازم را فعال کنید."
        )

        # Send a welcome message to the group
        await context.bot.send_message(
            chat_id=result.id,
            text="سلام به همه! 😊 من سایفر هستم، ربات هوشمند شما. برای شروع، لطفاً من را به عنوان ادمین تنظیم کنید و دسترسی ارسال پیام را فعال کنید."
        )

    except Exception as e:
        print("🔥 Join group error:", e)
        await update.message.reply_text("❗ مشکلی در پیوستن به گروه پیش آمد. لطفاً مطمئن شوید لینک معتبر است و من اجازه پیوستن به گروه‌ها را دارم.")



# Register commands in the application
def register_command_handlers(app: Application):
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("style", set_style))
    app.add_handler(CommandHandler("summarize", summarize))
    app.add_handler(CommandHandler("translate", translate))
    app.add_handler(CommandHandler("join", join_command))
