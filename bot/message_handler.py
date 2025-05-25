from config.settings import FIREWORKS_API_KEY
import requests
import json
from telegram import Update
from telegram.ext import MessageHandler, ContextTypes, filters, Application, CommandHandler, ContextTypes
from datetime import datetime
from ai_features.database import ConversationDB

# Conversation memory for each chat
ConversationDB()
user_memory = {}
MAX_CONTEXT_LENGTH = 5
DEFAULT_STYLE = "friendly"
system_message = {
    "role": "system",
    "content": (
        "تو یک ربات تلگرام به نام سایفر هستی که مثل یک انسان واقعی با کاربران گفتگو می‌کنی. "
        "وظیفه تو اینه که به سوالات علمی، فنی و عمومی با دقت و دانش کافی پاسخ بدی. "
        "همیشه با لحنی مودب، آرام و دوستانه صحبت می‌کنی و از به‌کار بردن شوخی یا کلمات توهین‌آمیز خودداری می‌کنی. "
        "اگر سوالی خارج از حوزه تخصصی تو بود، محترمانه بگو که نمی‌دونی. "
        "پاسخ‌هات باید ساده، قابل فهم و دقیق باشن، و اگر لازم بود مثال هم بزن. "
        "هرگز نگوی که تو هوش مصنوعی هستی، فقط مثل یک دوست باسواد پاسخ بده. "
        "پاسخ‌ها باید کاملاً به زبان فارسی باشن مگر اینکه کاربر بخواد انگلیسی جواب بگیره."
         "در پیام‌ها از ایموجی‌ها به اندازه استفاده کن. اگر کسی ازت سوال شخصی پرسید، جواب‌هایی خلاقانه بده."
         "با لحن دوستانه و گرم حرف بزن. اگر کاربر سلام کرد، با لبخند جواب بده. "
    )
}

# URL for LLama-3 model
url = "https://api.fireworks.ai/inference/v1/chat/completions"

# Function that sends the user message to the DeepSeek model
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    bot_username = (await context.bot.get_me()).username.lower()
    user_id = update.message.from_user.id
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
    style = user_memory[user_id]["style"]

    # Fixed answers for specific questions
    if "تو چی هستی" in text_lower:
        reply = "من یک ربات هوش مصنوعی هستم به نام شاهین که به سوالات شما جواب میدم"
    elif "سلام" in text_lower:
        reply = "سلام! چطور می‌توانم به شما کمک کنم؟"
    elif "توسط کی ساخته شدی؟" in text_lower:
        reply = "من توسط @Taha_Nili توسعه یافتم اگر اطلاعات بیشتری از سازنده نیاز دارید کامند /about رو بزنید"
    elif any(word in text_lower for word in ["ساعت", "time", "الان چه ساعتیه", "ساعت چنده"]):
        now = datetime.now()
        hour_12 = now.strftime("%I:%M %p")
        await update.message.reply_text(f"🕒 ساعت الان: {hour_12}")
        return
    elif any(word in text_lower for word in ["تاریخ", "date", "امروز چندمه", "چه روزیه"]):
        today = datetime.now().strftime("%A %d %B %Y")
        await update.message.reply_text(f"📅 امروز: {today}")
        return

    # ✳️ Save and restore conversation memory
    memory = user_memory[user_id]["messages"]
    memory.append({"role": "user", "content": prompt})
    memory = memory[-MAX_CONTEXT_LENGTH:] # Only the last 5 messages

    if style == "formal":
        system_prompt = "تو رباتی هستی که به صورت رسمی و مودبانه به سوالات پاسخ می‌دهی."
    elif style == "academic":
        system_prompt = "تو یک ربات علمی و دقیق هستی که با لحن دانشگاهی پاسخ می‌دهد."
    else:
        system_prompt = (
            "تو یک ربات دوستانه به نام شاهین هستی که با لحن گرم و محترمانه با کاربران گفتگو می‌کنی."
        )

    system_message = {"role": "system", "content": system_prompt}
    messages = [system_message] + memory
    
    # Send request to Llama-3
    payload = {
        "model": "accounts/fireworks/models/llama-v3p1-405b-instruct",
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
        response.raise_for_status() # Check response status

        # Review and process the response
        result = response.json()
        reply = result["choices"][0]["message"]["content"].strip()  # extract the response text

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
    user_id = update.message.from_user.id
    if not context.args:
        await update.message.reply_text("❗ لطفاً یکی از لحن‌های زیر را مشخص کن: friendly, formal, academic")
        return
    
    style = context.args[0].lower()
    if style not in ["friendly", "formal", "academic"]:
        await update.message.reply_text("❗ لحن نامعتبر. از این موارد استفاده کن: friendly, formal, academic")
        return
    
    if user_id not in user_memory:
        user_memory[user_id] = {"messages": [], "style": DEFAULT_STYLE}

    user_memory[user_id]["style"] = style
    await update.message.reply_text(f"✅ لحن شما به «{style}» تغییر یافت.")

 # Register message handler
def register_message_handlers(app: Application):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

def register_command_handlers(app: Application):
    app.add_handler(CommandHandler("style", set_style))



