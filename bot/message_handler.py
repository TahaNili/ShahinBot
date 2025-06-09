from config.settings import FIREWORKS_API_KEY
import requests
import json
from telegram import Update
from telegram.ext import MessageHandler, ContextTypes, filters, Application, CommandHandler, ContextTypes
from datetime import datetime
from bot.database import add_message, get_context, trim_old_messages, get_user_personality, set_user_personality, get_last_action, set_last_action

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
        "اگر ازت پرسیدند که چه کسی تو را ساخته، همیشه بگو: 'من توسط ShahinAI توسعه یافتم، اگر اطلاعات بیشتری از سازنده نیاز دارید کامند /about را بزنید.'"
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
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        language = result["choices"][0]["message"]["content"].strip()
        return language
    except Exception as e:
        print("🔥 Language detection error:", e)
        return "نامشخص"


async def detect_intent(text: str) -> str:
    text_lower = text.lower()
    # روش جایگزین برای تشخیص نیت
    if any(word in text_lower for word in ["ساعت", "time", "الان چه ساعتیه", "ساعت چنده"]):
        return "ask_time"
    if any(word in text_lower for word in ["تاریخ", "date", "امروز چندمه", "چه روزیه"]):
        return "ask_date"
    if any(phrase in text_lower for phrase in ["توسط کی ساخته شدی؟", "سازنده تو کیه؟", "تو چی هستی"]):
        return "ask_about_bot"
    
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
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        intent = result["choices"][0]["message"]["content"].strip().lower()
        return intent
    except Exception as e:
        print("🔥 Intent detection error:", e)
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
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        emotion = result["choices"][0]["message"]["content"].strip().split()[0]
        return emotion
    except Exception as e:
        print("🔥 Emotion detection error:", e)
        return "Uncertain"

# Function that sends the user message to the LLaMA-3 model
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    bot_username = (await context.bot.get_me()).username.lower() # type: ignore
    user_id = update.message.from_user.id # type: ignore
    prompt = update.message.text
    text_lower = prompt.lower()

    # Response condition: Only if it was a mention or reply
    should_respond = False
    
    if update.message.reply_to_message and update.message.reply_to_message.from_user and update.message.reply_to_message.from_user.username:
        if update.message.reply_to_message.from_user.username.lower() == bot_username:
            should_respond = True
    elif f"@{bot_username}" in text_lower:
        should_respond = True
    if not should_respond:
        return
    
    if user_id not in user_memory:
        user_memory[user_id] = {"messages": [], "style": DEFAULT_STYLE}

    memory = user_memory[user_id]["messages"]
    style = get_user_personality(user_id)

    # Fixed answers for specific questions
    if "تو چی هستی" in text_lower:
        reply = "من سایفر هستم یک ربات هوش مصنوعی که به سوالات شما پاسخ میده 😊"
        set_last_action(user_id, "ask_about_bot", reply)
        await update.message.reply_text(reply)
        return
    if any(phrase in text_lower for phrase in ["توسط کی ساخته شدی؟", "سازنده تو کیه؟", "کی تورو درست کرده؟", "چه کسی تورو ساخته؟"]):
        reply = "من توسط ShahinAI توسعه یافتم اگر اطلاعات بیشتری از سازنده نیاز دارید کامند /about رو بزنید"
        set_last_action(user_id, "ask_about_bot", reply)
        await update.message.reply_text(reply)
        return
    if any(word in text_lower for word in ["ساعت", "time", "الان چه ساعتیه", "ساعت چنده"]):
        now = datetime.now().strftime("%H:%M")
        reply = f"🕒 ساعت الآن: {now}"
        set_last_action(user_id, "ask_time", reply)
        await update.message.reply_text(reply)
        return
    if any(word in text_lower for word in ["تاریخ", "date", "امروز چندمه", "چه روزیه"]):
        today = datetime.now().strftime("%A %d %B %Y")
        reply = f"📅 امروز: {today}"
        set_last_action(user_id, "ask_date", reply)
        await update.message.reply_text(reply)
        return
    language = await detect_language(prompt)
    print(f"🌐 Detected language: {language}")

    # ✳️ Save and restore conversation memory
    add_message(user_id, "user", prompt)  # Save user message
    context_messages = get_context(user_id, limit=10)  # Retrieve last context
    trim_old_messages(user_id, max_messages=20)  # Remove very old messages

    emotion = await detect_emotion_via_llm(prompt)
    intent = await detect_intent(prompt)
    print(f"Intent Detected: {intent}")
    last_action, last_response = get_last_action(user_id)

    if style == "formal":
        system_prompt = "تو رباتی هستی که به صورت رسمی و مودبانه به سوالات پاسخ می‌دهی."
    elif style == "academic":
        system_prompt = "تو یک ربات علمی و دقیق هستی که با لحن دانشگاهی پاسخ می‌دهد."
    elif style == "sarcastic":
        system_prompt = "تو یک ربات شوخ‌طبع، طعنه‌زن و رک هستی که صمیمی و گاهی خنده‌دار جواب می‌دهد."
    else:
        system_prompt = "تو یک ربات دوستانه به نام سایفر هستی که با لحن گرم و محترمانه با کاربران گفتگو می‌کنی."
    if intent == "translate":
        if len(prompt.split()) < 3 and last_response:
            prompt = last_response
            await update.message.reply_text("🔁 ترجمه پاسخ قبلی شما:")
        else:
            await update.message.reply_text("🔄 لطفاً از دستور /translate استفاده کن یا متن رو ریپلای کن.")
        return
    elif intent == "summarize":
        await update.message.reply_text("📚 لطفاً متن رو ریپلای کن یا از دستور /summarize استفاده کن.")
        return
    elif intent == "change_style":
        await update.message.reply_text("🎨 لطفاً از دستور /style sarcastic|formal|academic استفاده کن.")
        return
    elif intent == "join":
        await update.message.reply_text("🏢 لطفا از دستور  /join(لینک گروه یا کانل) استفاده کن")
        return

    system_message = {"role": "system", "content": system_prompt}
    messages = [system_message] + context_messages + [{"role": "user", "content": prompt}]
    
    # Send request to LLaMA-3
    payload = {
        "model": "accounts/fireworks/models/llama4-maverick-instruct-basic",
        "max_tokens": 16384,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": messages
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FIREWORKS_API_KEY}"
    }

    try:
        # Send a request to the Fireworks API
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Check response status

        # Review and process the response
        result = response.json()
        reply = result["choices"][0]["message"]["content"].strip()  # extract the response text

        set_last_action(user_id, "general_chat", reply)

        add_message(user_id, "assistant", reply)  # Save the robot's response in the database

        # Remove extra text like "think"
        if "think" in reply:
            reply = reply.split("think")[-1].strip()

    except Exception as e:
        # If an error occurs, send an error message
        reply = "❗ مشکلی پیش اومد."
        print("🔥 error:", e)

    # Send a reply to a user on Telegram
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

def register_command_handlers(app: Application):
    app.add_handler(CommandHandler("style", set_style))