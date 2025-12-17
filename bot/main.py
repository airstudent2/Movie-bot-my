import asyncio
from pyrogram import Client
from bot.config import API_ID, API_HASH, BOT_TOKEN
from bot.database import Database

# Initialize database
db = Database()

# Initialize bot
app = Client(
    "movie_nest_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

print("🤖 Movie Nest Bot Starting...")

# Import handlers (this will register them)
from bot.handlers import user_handlers, admin_handlers, callback_handlers

if __name__ == "__main__":
    print("✅ Bot is running!")
    app.run()
