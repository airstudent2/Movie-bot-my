from pyrogram import Client, filters
from pyrogram.types import Message
from bot.database import Database
from bot.keyboards import Keyboards
from bot.config import ADMIN_IDS

db = Database()
kb = Keyboards()

@Client.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Start command handler"""
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username
    
    # Check for referral
    referred_by = None
    if len(message.command) > 1:
        try:
            referred_by = int(message.command[1])
        except:
            pass
    
    # Add user if new
    user = db.get_user(user_id)
    if not user:
        db.add_user(user_id, name, username, referred_by)
        user = db.get_user(user_id)
    
    # Update last active
    db.update_last_active(user_id)
    
    # Get welcome message from settings
    welcome_msg = db.get_setting('welcome_message')
    welcome_msg = welcome_msg.replace('{name}', name)
    
    # Get user stats
    points = user['points']
    level = user['level'].title()
    
    welcome_text = f"""
{welcome_msg}

━━━━━━━━━━━━━━━━━━━━
💰 পয়েন্ট: **{points}**
🏆 লেভেল: **{level}**
━━━━━━━━━━━━━━━━━━━━

🎯 **কিভাবে কাজ করে:**
• অ্যাড দেখে পয়েন্ট কামাও
• পয়েন্ট দিয়ে কন্টেন্ট আনলক করো
• রেফার করে বোনাস পাও

👇 **মেনু থেকে অপশন বেছে নাও:**
"""
    
    await message.reply(welcome_text, reply_markup=kb.main_menu(user_id))

@Client.on_message(filters.command("points"))
async def points_command(client: Client, message: Message):
    """Check points"""
    user_id = message.from_user.id
    points = db.get_points(user_id)
    
    await message.reply(f"💰 **Your Points:** {points}")

@Client.on_message(filters.command("ref") | filters.command("referral"))
async def referral_command(client: Client, message: Message):
    """Referral system"""
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    
    user = db.get_user(user_id)
    referrals = user['referrals']
    ref_bonus = int(db.get_setting('referral_bonus'))
    
    ref_link = f"https://t.me/{bot_username}?start={user_id}"
    
    ref_text = f"""
👥 **Referral Program**

🎁 **Your Earnings:**
• Total Referrals: **{referrals}**
• Earnings: **{referrals * ref_bonus} points**

💰 **How it works:**
• Share your link
• Friend joins via your link
• You get **{ref_bonus} points** instantly!

🔗 **Your Referral Link:**
`{ref_link}`

👆 Tap to copy and share!
"""
    
    await message.reply(ref_text)

@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Help command"""
    help_text = """
📚 **Available Commands:**

👤 **User Commands:**
/start - শুরু করুন
/points - পয়েন্ট চেক করুন
/ref - রেফারেল লিংক
/help - সাহায্য

💡 **How to use:**
1. অ্যাড দেখে পয়েন্ট কামান
2. পয়েন্ট দিয়ে মুভি আনলক করুন
3. বন্ধুদের রেফার করুন

❓ **Support:** @Mobile_nest_air_bot
"""
    await message.reply(help_text)
