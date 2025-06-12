from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, Application
from config.settings import FIREWORKS_API_KEY
import json
import requests
import re
from bot.message_handler import url, set_style
from bot.database import set_user_personality, set_user_agent, get_user_goal, get_user_pref, get_context

# Command /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text( # type: ignore
        f"سلام کاربر {user.first_name} خوش آمدی" # type: ignore
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text( # type: ignore
        "ربات سایفر توسط ShahinAI ساخته شده است برای اینکه اطلاعات بیشتری درباره ربات به دست بیاورید حتما به ریپازیتوری گیت هاب ما مراجعه کنید: https://github.com/TahaNili/Sypher.Bot.git | ضمنا هرگونه کپی برداری از این ربات از نظر شرعی و قانونی جایز نیست.! \n\n"
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
        "model": "accounts/fireworks/models/llama4-maverick-instruct-basic",
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
    if update.effective_chat.type != "private":        # type: ignore # This command only works in private chat
        await update.message.reply_text("❗ این دستور فقط در چت خصوصی کار می‌کند.") # type: ignore
        return

    bot_username = (await context.bot.get_me()).username
    keyboard = [
        [InlineKeyboardButton("افزودن به گروه یا کانال", url=f"https://t.me/{bot_username}?startgroup=true")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(        "برای اضافه کردن من به گروه یا کانال، روی دکمه زیر بزن و گروه موردنظرت رو انتخاب کن:", # type: ignore
        reply_markup=reply_markup
    )

async def setgoal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    if not context.args:
        await update.message.reply_text("لطفاً هدف خود را بعد از دستور وارد کنید.")
        return
    goal_text = " ".join(context.args)
    set_user_agent(user_id, goals=goal_text)
    await update.message.reply_text("✅ هدف شما ثبت شد.")

async def getgoal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    goal = get_user_goal(user_id)
    if goal:
        await update.message.reply_text(f"🎯 هدف فعلی شما: {goal}")
    else:
        await update.message.reply_text("شما هنوز هدفی ثبت نکرده‌اید.")

async def setpref_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    if not context.args:
        await update.message.reply_text("لطفاً ترجیحات خود را بعد از دستور وارد کنید.")
        return
    pref_text = " ".join(context.args)
    set_user_agent(user_id, preferences=pref_text)
    await update.message.reply_text("✅ ترجیحات شما ثبت شد.")

async def getpref_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    pref = get_user_pref(user_id)
    if pref:
        await update.message.reply_text(f"⚙️ ترجیحات فعلی شما: {pref}")
    else:
        await update.message.reply_text("شما هنوز ترجیحاتی ثبت نکرده‌اید.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "\u2753 راهنمای ربات سایفر:\n"
        "/start - شروع ربات\n"
        "/help - نمایش راهنما و دستورات\n"
        "/about - اطلاعات درباره ربات\n"
        "/style [academic|formal||sarcastic] - تغییر لحن پاسخ‌دهی\n"
        "/summarize [متن یا ریپلای] - خلاصه‌سازی متن\n"
        "/translate [متن یا ریپلای] - ترجمه متن\n"
        "/join - افزودن ربات به گروه یا کانال\n"
        "/setgoal [هدف] - ثبت هدف شخصی\n"
        "/getgoal - نمایش هدف فعلی\n"
        "/setpref [ترجیحات] - ثبت ترجیحات شخصی\n"
        "/getpref - نمایش ترجیحات فعلی\n"
        "/history - نمایش ۱۰ پیام آخر شما\n"
    )
    if update.message:
        await update.message.reply_text(help_text)

async def set_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    if not context.args or not context.args[0]:
        await update.message.reply_text("\u26a0\ufe0f لطفاً یکی از سبک‌های زیر را انتخاب کن: formal, academic, sarcastic")
        return
    style = context.args[0].lower()
    if style not in ["friendly", "formal", "academic", "sarcastic"]:
        await update.message.reply_text("\u26a0\ufe0f سبک نامعتبر است. فقط یکی از این گزینه‌ها: formal, academic, sarcastic")
        return
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        await update.message.reply_text("خطا در شناسایی کاربر.")
        return
    set_user_personality(user_id, style)
    await update.message.reply_text(f"\u2705 سبک پاسخ‌دهی شما به '{style}' تغییر کرد.")

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        if update.message:
            await update.message.reply_text("خطا در شناسایی کاربر.") # type: ignore
        return
    history = get_context(user_id, limit=10)
    if not history:
        if update.message:
            await update.message.reply_text("هیچ پیامی در حافظه شما ثبت نشده است.") # type: ignore
        return
    text = "\n".join([
        f"{i+1}. {'👤' if msg['role']=='user' else '🤖'}: {msg['content']}" for i, msg in enumerate(history)
    ])
    if update.message:
        await update.message.reply_text(f"🕑 ۱۰ پیام آخر شما:\n\n{text}") # type: ignore

# Register commands in the application
def register_command_handlers(app: Application):
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("style", set_style))
    app.add_handler(CommandHandler("summarize", summarize))
    app.add_handler(CommandHandler("translate", translate))
    app.add_handler(CommandHandler("join", join_command))
    app.add_handler(CommandHandler("setgoal", setgoal_command))
    app.add_handler(CommandHandler("getgoal", getgoal_command))
    app.add_handler(CommandHandler("setpref", setpref_command))
    app.add_handler(CommandHandler("getpref", getpref_command))
    app.add_handler(CommandHandler("history", history_command))
