<div align="center">
  <h1>Sypher Telegram Bot</h1>
  <p>A smart, modular Telegram bot powered by Python and LLaMA-3</p>
</div>

---

**Sypher** is an intelligent and modular Telegram bot built with **Python** and the `python-telegram-bot` library (version 22.1). It leverages the **LLaMA-3 model** via the Fireworks API to deliver advanced features like intelligent responses, text summarization, translation, sentiment analysis, and group joining capabilities. Sypher communicates in **Persian** with a friendly, professional tone, making it perfect for both private chats and group interactions.

## ✨ Key Features

- **Intelligent Responses** 🧠: Answers scientific, technical, and general questions using LLaMA-3.
- **Diverse Commands** 📜:
  - `/start`: Greets users with a personalized welcome message.
  - `/help`: Lists all available commands.
  - `/about`: Shares details about the bot and its creator, ShahinAI.
  - `/style`: Switches response tone (friendly, formal, academic).
  - `/summarize`: Condenses provided or replied text.
  - `/translate`: Translates text into various languages.
  - `/join`: Joins Telegram groups via invite links.
- **Sentiment Analysis** 😊: Detects emotions (e.g., happy, sad, angry) and responds empathetically.
- **Conversation Memory** 📚: Maintains context in long conversations using a SQLite database.
- **Group Support** 👥: Joins groups via invite links and responds to mentions or replies.
- **Modular Design** 🛠️: Clean, organized code for easy expansion.

## ⚙️ BotFather Setup

To configure Sypher with `@BotFather`:

1. Send `/mybots` to `@BotFather` and select your bot.
2. Enable **Allow Groups** in the settings.
3. Disable **Group Privacy** (Bot Settings > Group Privacy > Turn off).
4. Set the bot commands with:
   ```plaintext
   /setcommands
   start - Start the bot
   style - Change response tone
   translate - Translate text or replied message
   summarize - Summarize text or replied message
   about - Information about the bot
   help - Guide to using the bot
   join - Join a group via invite link
   ```

## 🚀 Usage

### Private Chats
- Start the bot: `/start`
- View commands: `/help`
- Change tone: `/style friendly` (or `formal`, `academic`)
- Summarize text: `/summarize Your text here`
- Translate text: `/translate Your text here`
- Join a group: `/join t.me/+abc123`

### Groups
- Add Sypher to a group using `/join t.me/+abc123` in a private chat.
- Grant admin privileges with **Send Messages** permission.
- Interact by mentioning `@Sypher` or replying to its messages.

### Example Commands
- Summarize: `/summarize Hi, this is a long text I want summarized...`
- Translate: `/translate Hello, how are you?`
- Time query: `@Sypher What's the time?`
- Join group: `/join t.me/+abc123`

## 📂 Project Structure

- **`main.py`**: Entry point for initializing the bot and commands.
- **`bot/commands.py`**: Handles commands like `/start`, `/help`, `/summarize`, etc.
- **`bot/message_handler.py`**: Manages text messages, sentiment analysis, and intelligent responses.
- **`bot/handlers.py`**: Placeholder for additional handlers (currently empty).
- **`config/settings.py`**: Manages environment variables (e.g., bot token, API key).
- **`requirements.txt`**: Lists project dependencies.
- **`README.md`**: Project documentation (you're reading it!).
- **`.gitignore`**: Excludes unnecessary files like `__pycache__` and `.env`.

## 🌟 Advanced Features (In Progress)

### ✅ Stage 1: Persistent Multi-Turn Memory
Conversations are stored in a SQLite database, enabling context retention across restarts. Old messages are automatically trimmed to maintain efficiency.

### 🎯 Stage 2: Intent Detection
Sypher uses LLaMA-3 to detect user intent (e.g., summarize, translate, ask time) and responds without needing explicit commands.

### 🧠 Stage 3: Persistent Personality
Users can set a preferred response tone (friendly, formal, academic, sarcastic), which is saved permanently for personalized interactions.

## 📞 Support
Currently, no contact information is available for the bot's creators (ShahinAI). For details, use the `/about` command in the bot.

## 📜 License
No license has been specified yet. Run `/about` in the bot for copyright information.

---

<div align="center">
  <p><em>Built with ❤️ by ShahinAI</em></p>
  <img src="https://img.icons8.com/?size=50&id=108792&format=png&color=000000" alt="Python Logo" width="30"/>
  <img src="D:\TelegramBot\img\shahinai.png" alt=Sypher Logo" width="30"/>
</div>