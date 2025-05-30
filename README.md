# Sypher Telegram Bot


**Sypher** is a smart and modular Telegram bot developed with **Python** and the `python-telegram-bot` library (version 20.x). This bot leverages LLaMA-3 models (via the Fireworks API) to provide advanced features such as intelligent responses, text summarization, translation, sentiment analysis, and joining Telegram groups via invite links. Sypher responds in Persian with a friendly and professional tone and is designed for use in private chats and groups.

## Key Features
- **Intelligent Responses**: Answers scientific, technical, and general questions using the LLaMA-3 model.
- **Diverse Commands**:
  - `/start`: Sends a welcome message with the user's name.
  - `/help`: Displays the list of commands.
  - `/about`: Information about the bot and its creator (ShahinAI).
  - `/style`: Changes the response tone (friendly, formal, academic).
  - `/summarize`: Summarizes provided or replied text.
  - `/translate`: Translates text into other languages.
  - `/join`: Joins a Telegram group via an invite link.
- **Sentiment Analysis**: Detects user emotions (e.g., happy, sad, angry) and responds empathetically.
- **Conversation Memory**: Advanced multi-turn memory to accurately maintain context in long conversations.
- **Group Support**: Ability to join groups via invite links and respond to mentioned or replied messages.
- **Modular Design**: Clean and organized code for easy expansion.

## BotFather Settings
   - Go to `@BotFather` and send `/mybots`.
   - Select your bot.
   - Ensure **Allow Groups** is enabled.
   - Turn off **Group Privacy** (Bot Settings > Group Privacy > Turn off).
   - Set the commands:
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

## Usage
1. **Private Chat**:
   - Start with the bot: `/start`
   - View commands: `/help`
   - Change response tone: `/style friendly` (or `formal`, `academic`)
   - Summarize text: `/summarize Your text here`
   - Translate text: `/translate Your text here`
   - Join a group: `/join t.me/+abc123`

2. **Groups**:
   - Add the bot to a group via invite link: `/join t.me/+abc123` (in private chat).
   - Make the bot an admin and enable the **Send Messages** permission.
   - Interact with the bot by mentioning it (e.g., `@Sypher`) or replying to its messages.

3. **Examples**:
   - Summarization: `/summarize Hi, this is a long text I want summarized...`
   - Translation: `/translate Hello, how are you?`
   - Time query: `@Sypher What's the time?`
   - Joining a group: `/join t.me/+abc123`

## Project Structure
- `main.py`: Entry point of the bot, sets up commands and initializes.
- `bot/commands.py`: Handlers for commands (`/start`, `/help`, `/about`, `/style`, `/summarize`, `/translate`, `/join`).
- `bot/message_handler.py`: Manages text messages, sentiment analysis, and intelligent responses.
- `bot/handlers.py`: Currently empty, intended for additional handlers.
- `config/settings.py`: Manages environment variables (bot token and API key).
- `requirements.txt`: List of dependencies (currently needs to be created manually).
- `README.md`: Project documentation (this file).
- `.gitignore`: Excludes unnecessary files like `__pycache__` and `.env`.

## Advanced Features (Ongoing Enhancements)

### ✅ Stage 1 — Persistent Multi-Turn Memory
User conversations are stored in a SQLite database, allowing the bot to retain context even after restarts. The bot trims old messages automatically and uses recent history when generating responses with LLaMA-3.

### 🎯 Stage 2 — Intent Detection
The bot uses LLaMA-3 to detect the user's intent behind each message (e.g., summarize, translate, ask date/time) and responds accordingly—no need for explicit commands.

### 🧠 Stage 3 — Persistent Personality per User
Each user can choose their preferred response tone (e.g., friendly, formal, academic, sarcastic), and the bot will store this setting permanently. This personality is used in all interactions.

## Support
Unfortunately, there is currently no way to contact the bot's creators. No information about ShahinAI is available on the internet.

## License
No license has been specified yet. For more information about copyright, run the `/about` command in the bot.

---

*Built by ShahinAI with ❤️*