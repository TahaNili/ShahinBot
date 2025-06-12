<!-- filepath: d:\TelegramBot\README.md -->
<div align="center">
  <h1>Sypher Telegram Bot</h1>
  <p>A smart, modular Telegram bot powered by Python and LLaMA-4</p>
</div>

---

Sypher is an intelligent and modular Telegram bot built with Python and the python-telegram-bot library (v22.1). It leverages the LLaMA-4 model via the Fireworks API to deliver advanced features like intelligent responses, text summarization, translation, sentiment analysis, and group joining. Sypher communicates in Persian with a friendly, professional tone, perfect for both private chats and groups.

## ✨ Features
- **Intelligent Responses**: Answers scientific, technical, and general questions using LLaMA-4.
- **Conversation Memory**: Stores and retrieves the last messages of each user for context-aware and personalized responses. View your recent chat history with `/history`.
- **Voice Message Support**: Send a voice message to the bot and receive an intelligent voice reply! The bot uses Whisper (speech-to-text) and gTTS (text-to-speech) for a fully AI-powered audio conversation.
- **Commands**:
  - `/start`: Welcome message
  - `/help`: List all commands
  - `/about`: Bot and creator info
  - `/style`: Change response tone (friendly, formal, academic, sarcastic)
  - `/summarize`: Summarize provided or replied text
  - `/translate`: Translate text
  - `/join`: Join groups via invite link
  - `/setgoal`: Set your personal goal (per-user agent)
  - `/getgoal`: Show your current goal
  - `/setpref`: Set your preferences (per-user agent)
  - `/getpref`: Show your current preferences
  - `/history`: Show your last 10 messages (conversation memory)
- **Sentiment Analysis**: Detects emotions and responds empathetically
- **Group Support**: Joins groups and responds to mentions/replies
- **Modular Design**: Clean, organized, and extensible

## 🗣️ Voice Message Usage
- Simply send a voice message (voice note) to the bot in private chat or group (with mention).
- The bot will transcribe your voice, generate an intelligent reply, and send the answer as a voice message back to you.
- Voice recognition is powered by Whisper (open-source, supports Persian and English). Voice reply is generated using gTTS.
- If the bot cannot recognize your voice, it will send a text error message.

## 🚀 Quick Start
1. Configure your bot with @BotFather (enable groups, disable privacy, set commands)
2. Add your API keys in `config/settings.py`
3. Install dependencies: `pip install -r requirements.txt`
   - For voice features, also install: `pip install git+https://github.com/openai/whisper.git gtts pydub`
4. Run: `python main.py`

## 📝 Example Usage
- `/start` — Start the bot
- `/help` — Show help
- `/style formal` — Change tone
- `/summarize <text>` — Summarize text
- `/translate <text>` — Translate text
- `/join <invite link>` — Add bot to group
- `/setgoal <your goal>` — Set your personal goal
- `/getgoal` — Show your current goal
- `/setpref <your preferences>` — Set your preferences
- `/getpref` — Show your current preferences
- `/history` — Show your last 10 messages (conversation memory)
- Send a voice message to get a voice reply!
- Mention `@Sypher` in a group to interact

## 📂 Project Structure
- `main.py`: Bot entry point
- `bot/commands.py`: Command handlers
- `bot/message_handler.py`: Text, sentiment, and LLM logic
- `bot/database.py`: SQLite conversation and profile storage
- `config/settings.py`: Environment variables
- `requirements.txt`: Dependencies
- `README.md`: Documentation
- `.gitignore`: Ignore files

## 🆕 Changelog
- 2025-06-12: Added voice message support: send a voice, get an AI-powered voice reply (Whisper + gTTS)
- 2025-06-12: Implemented conversation memory and /history command for viewing recent chat history
- 2025-06-12: Added per-user goal and preference commands (/setgoal, /getgoal, /setpref, /getpref) to Personal AI Agent system; updated help and command list
- 2025-06-10: Major bug fixes, /help and /style commands improved, intent and language detection logic refactored, README.md restructured

## 📞 Support
No direct contact. Use `/about` in the bot for info.

## 📜 License
No proprietary license. Do not change or remove the project.

---

<div align="center">
  <h1>ShahinAI</h1>
  <img src="https://i.imgur.com/ZiN21Dp.png" alt="ShahinAI" width="90"/>
</div>