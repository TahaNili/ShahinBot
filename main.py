from telegram.ext import ApplicationBuilder
from config.settings import BOT_TOKEN
from bot.commands import register_command_handlers
from bot.message_handler import register_message_handlers
from telegram import BotCommand
from bot.database import init_db

init_db()

async def set_commands(application):
    commands = [
        BotCommand("start", "استارت ربات"),
        BotCommand("style", "تغییر لحن پاسخ‌دهی"),
        BotCommand("translate", "ترجمه متن یا پیام ریپلای‌شده"),
        BotCommand("summarize", "خلاصه‌سازی متن یا پیام ریپلای‌شده"),
        BotCommand("about", "اطلاعات درباره ربات"),
        BotCommand("help", "راهنمای استفاده از ربات"),
        BotCommand("join", "برای افزودن به کانال یا گروه"),
        BotCommand("setgoal", "ثبت هدف شخصی"),
        BotCommand("getgoal", "نمایش هدف فعلی"),
        BotCommand("setpref", "ثبت ترجیحات شخصی"),
        BotCommand("getpref", "نمایش ترجیحات فعلی"),
        BotCommand("history", "نمایش ۱۰ پیام آخر شما"),
        BotCommand("news", "دریافت اخبار روز دنیا")
    ]
    await application.bot.set_my_commands(commands)

def main():

    # Building a robot application using tokens
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(set_commands).build() # type: ignore

    # Register all command handlers
    register_command_handlers(app)

    # Register a text message handler
    register_message_handlers(app)

    print("🤖 THE ROBOT WAS SUCESSFULLY LAUNCHED...")

    app.run_polling()

if __name__ == '__main__':
    main()