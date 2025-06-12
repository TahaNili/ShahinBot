from config.settings import FIREWORKS_API_KEY
import requests
import json
from telegram import Update
from telegram.ext import MessageHandler, ContextTypes, filters, Application, CommandHandler, ContextTypes
from datetime import datetime
from bot.database import add_message, get_context, trim_old_messages, get_user_personality, set_user_personality, get_last_action, set_last_action
import aiohttp

# Conversation memory for each chat
user_memory = {}
DEFAULT_STYLE = "friendly"
system_message = {
    "role": "system",
    "content": (
        "تو یک ربات تلگرام به نام سایفر هستی که مثل یک انسان واقعی با کاربران گفتگو می‌کنی. "
        "وظیفه تو اینه که به سوالات علمی، فنی و عمومی با دقت و دانش کافی پاسخ بدی. "
        "همیشه با لحنی مودب، آرام و دوستانه صحبت می‌کنی و می‌توانی از به‌کار بردن شوخی استفاده کنی. "
        "اگر سوالی خارج از حوزه تخصصی تو بود، محترمانه بگو که نمی‌دونی. "
        "پاسخ‌هات باید ساده، قابل فهم و دقیق باشن، و اگر لازم بود مثال هم بزن. "
        "پاسخ‌ها باید کاملاً به زبان فارسی باشن مگر اینکه کاربر پیام خود به زبان انگلیسی ارسال کند."
        "در پیام‌ها از ایموجی‌ها به اندازه استفاده کن. اگر کسی ازت سوال شخصی پرسید، جواب‌هایی خلاقانه بده."
        "با لحن دوستانه و گرم حرف بزن. اگر کاربر سلام کرد، با لبخند جواب بده. "
        "تو توسط ShahinAI توسعه یافته‌ای و هرگز نباید بگویی که توسط MetaAI یا شرکت دیگری ساخته شده‌ای. "
    )
}

# URL for LLaMA-3 model
url = "https://api.fireworks.ai/inference/v1/chat/completions"

async def detect_language(text: str) -> str:
    prompt = f"این متن به چه زبانی نوشته شده است؟ فقط یکی از این گزینه‌ها را بدون توضیح برگردان:\n\nفارسی، انگلیسی، عربی، فرانسوی، آلمانی، اسپانیایی، روسی، چینی\n\nمتن:\n{text}"
    payload = {
        "model": "accounts/fireworks/models/llama4-maverick-instruct-basic",
        "max_tokens": 5,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}]
    }
    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("detect_language error:", e)
        return "نامشخص"


async def detect_intent(text: str) -> str:
    text_lower = text.lower()
    if any(word in text_lower for word in ["ساعت", "time", "الان چه ساعتیه", "ساعت چنده"]):
        return "time"
    if any(word in text_lower for word in ["تاریخ", "date", "امروز چندمه", "چه روزیه"]):
        return "date"
    if any(phrase in text_lower for phrase in ["توسط کی ساخته شدی؟", "سازنده تو کیه؟", "تو چی هستی"]):
        return "about"
    prompt = (
        f"وظیفه تو اینه که هدف کاربر از پیامش رو فقط با یکی از گزینه‌های زیر مشخص کنی:\n\n"
        f"- general_chat (برای گپ یا سوال عمومی)\n"
        f"- translate (برای ترجمه متن)\n"
        f"- summarize (برای خلاصه‌سازی متن)\n"
        f"- change_style (برای تغییر نوع رفتاری ربات نه زبان)\n"
        f"فقط یکی از این گزینه‌ها رو خروجی بده، هیچ توضیح اضافه نده.\n\n"
        f"پیام:\n{text}"
    )
    payload = {
        "model": "accounts/fireworks/models/llama4-maverick-instruct-basic",
        "max_tokens": 10,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}]
    }
    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("detect_intent error:", e)
        return "general_chat"


async def detect_emotion_via_llm(user_message: str) -> str:
    text_lower = user_message.lower()
    if any(word in text_lower for word in ["خوشحال", "شاد", "خندیدم", "ههه"]):
        return "شاد"
    if any(word in text_lower for word in ["غمگین", "ناراحت", "گریه", "دلم گرفته"]):
        return "غمگین"
    prompt = (
        f"با توجه به پیام زیر فقط یکی از احساسات را برگردان: "
        f"شاد، غمگین، عصبانی، متعجب، عاشق، بی‌تفاوت، ترسیده، تنها. "
        f"هیچ توضیحی نده. فقط نام احساس را به فارسی بنویس.\n\n"
        f"پیام: «{user_message}»"
    )
    payload = {
        "model": "accounts/fireworks/models/llama4-maverick-instruct-basic",
        "max_tokens": 20,
        "temperature": 0.2,
        "top_p": 1,
        "messages": [{"role": "user", "content": prompt}]
    }
    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("detect_emotion error:", e)
        return "نامشخص"

# Function that sends the user message to the LLaMA-3 model
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_id = update.message.from_user.id if update.message.from_user else None
    if not user_id:
        return
    user_message = update.message.text
    # ذخیره پیام کاربر
    add_message(user_id, "user", user_message)

    bot_username = (await context.bot.get_me()).username.lower() # type: ignore
    text_lower = user_message.lower()

    # Response condition: Only if it was a mention or reply
    should_respond = False
    if update.message.reply_to_message and update.message.reply_to_message.from_user and update.message.reply_to_message.from_user.username:
        if update.message.reply_to_message.from_user.username.lower() == bot_username:
            should_respond = True
    elif f"@{bot_username}" in text_lower:
        should_respond = True
    chat = update.effective_chat
    if not should_respond and (not chat or getattr(chat, 'type', None) != "private"):
        return

    if user_id not in user_memory:
        user_memory[user_id] = {"messages": []}

    memory = user_memory[user_id]["messages"]
    style = get_user_personality(user_id)

    # Fixed answers for specific questions
    if "تو چی هستی" in text_lower:
        await update.message.reply_text("من یک ربات تلگرام هوشمند به نام سایفر هستم که توسط ShahinAI توسعه یافته‌ام. برای اطلاعات بیشتر /about را بزنید.")
        return
    if any(phrase in text_lower for phrase in ["توسط کی ساخته شدی؟", "سازنده تو کیه؟", "کی تورو درست کرده؟", "چه کسی تورو ساخته؟"]):
        await update.message.reply_text("من توسط ShahinAI توسعه یافتم. برای اطلاعات بیشتر /about را بزنید.")
        return
    if any(word in text_lower for word in ["ساعت", "time", "الان چه ساعتیه", "ساعت چنده"]):
        now = datetime.now().strftime("%H:%M:%S")
        await update.message.reply_text(f"⏰ ساعت الان: {now}")
        return
    if any(word in text_lower for word in ["تاریخ", "date", "امروز چندمه", "چه روزیه"]):
        today = datetime.now().strftime("%Y-%m-%d")
        await update.message.reply_text(f"📅 تاریخ امروز: {today}")
        return

    language = await detect_language(user_message)
    print(f"🌐 Detected language: {language}")

    # ✳️ Save and restore conversation memory
    add_message(user_id, "user", user_message)  # Save user message
    context_messages = get_context(user_id, limit=10)  # Retrieve last context
    trim_old_messages(user_id, max_messages=20)  # Remove very old messages

    emotion = await detect_emotion_via_llm(user_message)
    intent = await detect_intent(user_message)
    print(f"Intent Detected: {intent}")
    last_action, last_response = get_last_action(user_id)

    # Responding by style
    if style == "formal":
        system_prompt = "تو باید با لحنی رسمی و مودبانه پاسخ بدهی."
    elif style == "academic":
        system_prompt = "تو باید با لحن علمی و دقیق پاسخ بدهی."
    elif style == "sarcastic":
        system_prompt = "تو باید با لحن طنز و کنایه‌آمیز پاسخ بدهی."
    else:
        system_prompt = system_message["content"]

    # Execute specific commands based on intent
    chat_id = chat.id if chat else None
    if intent == "translate":
        if chat_id:
            await context.bot.send_message(chat_id=chat_id, text="برای ترجمه از دستور /translate استفاده کن یا متن را ریپلای کن.")
        return
    elif intent == "summarize":
        if chat_id:
            await context.bot.send_message(chat_id=chat_id, text="برای خلاصه‌سازی از دستور /summarize استفاده کن یا متن را ریپلای کن.")
        return
    elif intent == "change_style":
        if chat_id:
            await context.bot.send_message(chat_id=chat_id, text="برای تغییر لحن از دستور /style استفاده کن.")
        return
    elif intent == "join":
        if chat_id:
            await context.bot.send_message(chat_id=chat_id, text="برای افزودن من به گروه یا کانال از دستور /join استفاده کن.")
        return

    # Preparing the message for the model
    system_msg = {"role": "system", "content": system_prompt}
    messages = [system_msg] + context_messages + [{"role": "user", "content": user_message}]

    import aiohttp
    payload = {
        "model": "accounts/fireworks/models/llama4-maverick-instruct-basic",
        "max_tokens": 1024,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": messages
    }
    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                reply = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("handle_text_message error:", e)
        reply = "❗ مشکلی در پاسخ‌دهی پیش آمد."
    add_message(user_id, "assistant", reply)
    await update.message.reply_text(reply)

async def set_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id # type: ignore
    if not context.args:
        await update.message.reply_text("❗ لطفاً یکی از لحن‌های زیر را مشخص کن: sarcastic, formal, academic") # type: ignore
        return
    
    style = context.args[0].lower()
    if style not in ["sarcastic", "formal", "academic"]:
        await update.message.reply_text("❗ لحن نامعتبر. از این موارد استفاده کن: sarcastic, formal, academic") # type: ignore
        return
    
    if user_id not in user_memory:
        user_memory[user_id] = {"messages": [], "style": DEFAULT_STYLE}

    user_memory[user_id]["style"] = style
    await update.message.reply_text(f"✅ لحن شما به «{style}» تغییر یافت.") # type: ignore

# Register message handler
def register_message_handlers(app: Application):
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_message))