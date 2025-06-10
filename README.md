<!-- filepath: d:\TelegramBot\README.md -->
<div align="center">
  <h1>Sypher Telegram Bot</h1>
  <p>A smart, modular Telegram bot powered by Python and LLaMA-4</p>
</div>

---

Sypher is an intelligent and modular Telegram bot built with Python and the python-telegram-bot library (v22.1). It leverages the LLaMA-4 model via the Fireworks API to deliver advanced features like intelligent responses, text summarization, translation, sentiment analysis, and group joining. Sypher communicates in Persian with a friendly, professional tone, perfect for both private chats and groups.

## ✨ Features
- **Intelligent Responses**: Answers scientific, technical, and general questions using LLaMA-4.
- **Commands**:
  - `/start`: Welcome message
  - `/help`: List all commands
  - `/about`: Bot and creator info
  - `/style`: Change response tone (friendly, formal, academic, sarcastic)
  - `/summarize`: Summarize provided or replied text
  - `/translate`: Translate text
  - `/join`: Join groups via invite link
- **Sentiment Analysis**: Detects emotions and responds empathetically
- **Conversation Memory**: Maintains context using SQLite
- **Group Support**: Joins groups and responds to mentions/replies
- **Modular Design**: Clean, organized, and extensible

## 🚀 Quick Start
1. Configure your bot with @BotFather (enable groups, disable privacy, set commands)
2. Add your API keys in `config/settings.py`
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python main.py`

## 📝 Example Usage
- `/start` — Start the bot
- `/help` — Show help
- `/style formal` — Change tone
- `/summarize <text>` — Summarize text
- `/translate <text>` — Translate text
- `/join <invite link>` — Add bot to group
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

## 🌟 Advanced Features (Staged)
- **Persistent Multi-Turn Memory**: Context retention across restarts
- **Intent Detection**: LLM detects user intent (summarize, translate, etc.)
- **Persistent Personality**: User tone saved and applied
- **Follow-up Intelligence**: Bot tracks last action/output for follow-ups
- **Language Detection & Auto Translation**: Detects language and responds accordingly
- **User-Controlled Style via Message**: Recognizes natural language style-change requests
- **Per-User Behavioral Profiles**: Stores tone, mood, language, and custom name

## 🆕 Changelog
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