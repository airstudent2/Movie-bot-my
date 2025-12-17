
import asyncio
import logging
from pyrogram import Client
from bot.config import API_ID, API_HASH, BOT_TOKEN
from bot.database import Database

# Add logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

# Initialize bot
app = Client(
    "movie_nest_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=1,
    in_memory=True
)

logger.info("🤖 Movie Nest Bot Starting...")
logger.info(f"API_ID: {API_ID}")
logger.info(f"BOT_TOKEN exists: {bool(BOT_TOKEN)}")

# Import handlers
from bot.handlers import user_handlers, admin_handlers, callback_handlers

if __name__ == "__main__":
    logger.info("✅ Bot is starting...")
    try:
        app.run()
    except Exception as e:
        logger.error(f"❌ Error: {e}")
