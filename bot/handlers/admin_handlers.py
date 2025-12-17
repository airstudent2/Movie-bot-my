from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from bot.database import Database
from bot.keyboards import Keyboards
from bot.config import ADMIN_IDS

db = Database()
kb = Keyboards()

# Admin command
@Client.on_message(filters.command("admin") & filters.user(ADMIN_IDS))
async def admin_command(client: Client, message: Message):
    """Admin panel command"""
    stats = db.get_stats()
    
    admin_text = f"""
👑 **Admin Dashboard**

📊 **Today's Stats:**
👥 New Users: **{stats['today_users']}**
📺 Ad Views: **{stats['today_ads']}**

📈 **Total Stats:**
👥 Total Users: **{stats['total_users']}**
📺 Total Ads: **{stats['total_ads']}**
🎬 Total Contents: **{stats['total_contents']}**
🔓 Total Unlocks: **{stats['total_unlocks']}**

━━━━━━━━━━━━━━━━━━━━

👇 **Admin Options:**
"""
    
    await message.reply(admin_text, reply_markup=kb.admin_menu())

# Admin Stats Callback
@Client.on_callback_query(filters.regex("^admin_stats$") & filters.user(ADMIN_IDS))
async def admin_stats_callback(client: Client, callback: CallbackQuery):
    """Show detailed stats"""
    stats = db.get_stats()
    
    stats_text = f"""
📊 **Detailed Statistics**

👥 **Users:**
• Total: {stats['total_users']}
• Today: {stats['today_users']}

📺 **Ads:**
• Total Views: {stats['total_ads']}
• Today: {stats['today_ads']}

🎬 **Contents:**
• Total: {stats['total_contents']}
• Total Unlocks: {stats['total_unlocks']}

💰 **Estimated Revenue:**
• Today: ${stats['today_ads'] * 0.003:.2f}
• Total: ${stats['total_ads'] * 0.003:.2f}
"""
    
    await callback.message.edit_text(stats_text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
    ]))

# Admin Settings
@Client.on_callback_query(filters.regex("^admin_settings$") & filters.user(ADMIN_IDS))
async def admin_settings_callback(client: Client, callback: CallbackQuery):
    """Show settings menu"""
    settings = db.get_all_settings()
    
    settings_text = f"""
⚙️ **Bot Settings**

🎯 Points Per Ad: **{settings.get('points_per_ad', '15')}**
📺 Ads Required: **{settings.get('ads_for_content', '3')}**
🎁 Daily Bonus: **{settings.get('daily_bonus', '20')}**
👥 Referral Bonus: **{settings.get('referral_bonus', '50')}**

━━━━━━━━━━━━━━━━━━━━

👇 Click to change:
"""
    
    await callback.message.edit_text(settings_text, reply_markup=kb.admin_settings_menu())

# Admin Ad Settings
@Client.on_callback_query(filters.regex("^admin_ads$") & filters.user(ADMIN_IDS))
async def admin_ads_callback(client: Client, callback: CallbackQuery):
    """Show ad settings"""
    settings = db.get_all_settings()
    zone_id = settings.get('monetag_zone_id', 'Not Set')
    
    ad_text = f"""
💰 **Monetag Ad Settings**

🆔 **Current Zone ID:** `{zone_id}`

📊 **Ad Performance:**
• Total Ad Views: {db.get_stats()['total_ads']}
• Estimated Earnings: ${db.get_stats()['total_ads'] * 0.003:.2f}

━━━━━━━━━━━━━━━━━━━━

👇 Manage Settings:
"""
    
    await callback.message.edit_text(ad_text, reply_markup=kb.admin_ad_settings())

# Change Zone ID
@Client.on_callback_query(filters.regex("^setting_zone_id$") & filters.user(ADMIN_IDS))
async def setting_zone_id(client: Client, callback: CallbackQuery):
    """Prompt to change zone ID"""
    await callback.message.edit_text(
        "🆔 **Change Monetag Zone ID**\n\n"
        "Send new Zone ID in format:\n"
        "`/setzone YOUR_ZONE_ID`\n\n"
        "Example: `/setzone 10337592`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="admin_ads")]
        ])
    )

@Client.on_message(filters.command("setzone") & filters.user(ADMIN_IDS))
async def set_zone_command(client: Client, message: Message):
    """Set new zone ID"""
    if len(message.command) < 2:
        await message.reply("❌ Usage: `/setzone YOUR_ZONE_ID`")
        return
    
    new_zone = message.command[1]
    db.update_setting('monetag_zone_id', new_zone, message.from_user.id)
    
    await message.reply(f"✅ **Zone ID Updated!**\n\nNew Zone ID: `{new_zone}`")

# Change Points Per Ad
@Client.on_callback_query(filters.regex("^setting_points_per_ad$") & filters.user(ADMIN_IDS))
async def setting_points_per_ad(client: Client, callback: CallbackQuery):
    """Prompt to change points per ad"""
    current = db.get_setting('points_per_ad')
    await callback.message.edit_text(
        f"🎯 **Change Points Per Ad**\n\n"
        f"Current: **{current} points**\n\n"
        f"Send new value:\n"
        f"`/setpoints NUMBER`\n\n"
        f"Example: `/setpoints 20`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="admin_settings")]
        ])
    )

@Client.on_message(filters.command("setpoints") & filters.user(ADMIN_IDS))
async def set_points_command(client: Client, message: Message):
    """Set new points per ad"""
    if len(message.command) < 2:
        await message.reply("❌ Usage: `/setpoints NUMBER`")
        return
    
    try:
        new_points = int(message.command[1])
        db.update_setting('points_per_ad', new_points, message.from_user.id)
        await message.reply(f"✅ **Points Per Ad Updated!**\n\nNew Value: **{new_points} points**")
    except ValueError:
        await message.reply("❌ Please provide a valid number!")

# Broadcast
@Client.on_callback_query(filters.regex("^admin_broadcast$") & filters.user(ADMIN_IDS))
async def admin_broadcast_callback(client: Client, callback: CallbackQuery):
    """Broadcast message"""
    await callback.message.edit_text(
        "📢 **Broadcast Message**\n\n"
        "Send your message in format:\n"
        "`/broadcast Your message here`\n\n"
        "It will be sent to all users.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
        ])
    )

@Client.on_message(filters.command("broadcast") & filters.user(ADMIN_IDS))
async def broadcast_command(client: Client, message: Message):
    """Broadcast message to all users"""
    if len(message.command) < 2:
        await message.reply("❌ Usage: `/broadcast Your message`")
        return
    
    broadcast_text = message.text.replace("/broadcast ", "")
    users = db.get_all_users(limit=10000)
    
    sent = 0
    failed = 0
    
    status_msg = await message.reply(f"📤 Broadcasting to {len(users)} users...")
    
    for user in users:
        try:
            await client.send_message(user['user_id'], broadcast_text)
            sent += 1
        except:
            failed += 1
    
    await status_msg.edit_text(
        f"✅ **Broadcast Complete!**\n\n"
        f"✅ Sent: {sent}\n"
        f"❌ Failed: {failed}"
    )

# Add Content Command
@Client.on_message(filters.command("addcontent") & filters.user(ADMIN_IDS))
async def add_content_command(client: Client, message: Message):
    """Add new content via command"""
    help_text = """
📤 **Add Content**

Usage:
`/addcontent Title | Category | Download_Link | Points | Description`

Example:
`/addcontent Pushpa 2 | movies | https://example.com/video.mp4 | 50 | Action movie`

Categories: movies, series, music, tutorials
"""
    
    if len(message.command) < 2:
        await message.reply(help_text)
        return
    
    try:
        # Parse content data
        parts = message.text.replace("/addcontent ", "").split(" | ")
        
        if len(parts) < 3:
            await message.reply("❌ Invalid format! Check example.")
            return
        
        content_data = {
            'title': parts[0].strip(),
            'category': parts[1].strip().lower(),
            'download_link': parts[2].strip(),
            'price_points': int(parts[3].strip()) if len(parts) > 3 else 50,
            'description': parts[4].strip() if len(parts) > 4 else '',
            'added_by': message.from_user.id
        }
        
        content_id = db.add_content(content_data)
        
        await message.reply(
            f"✅ **Content Added Successfully!**\n\n"
            f"🎬 Title: {content_data['title']}\n"
            f"📁 Category: {content_data['category']}\n"
            f"💰 Price: {content_data['price_points']} points\n"
            f"🆔 ID: {content_id}"
        )
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}\n\nCheck format and try again.")
