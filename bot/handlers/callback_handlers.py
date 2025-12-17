from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.database import Database
from bot.keyboards import Keyboards

db = Database()
kb = Keyboards()

# Main Menu
@Client.on_callback_query(filters.regex("^main_menu$"))
async def main_menu_callback(client: Client, callback: CallbackQuery):
    """Return to main menu"""
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    
    welcome_text = f"""
🎬 **Movie Nest**

━━━━━━━━━━━━━━━━━━━━
💰 পয়েন্ট: **{user['points']}**
🏆 লেভেল: **{user['level'].title()}**
━━━━━━━━━━━━━━━━━━━━

👇 **মেনু থেকে অপশন বেছে নাও:**
"""
    
    await callback.message.edit_text(welcome_text, reply_markup=kb.main_menu(user_id))

# Category Browsing
@Client.on_callback_query(filters.regex("^cat_"))
async def category_callback(client: Client, callback: CallbackQuery):
    """Browse category"""
    category = callback.data.replace("cat_", "")
    
    if category == "trending":
        contents = db.get_contents(limit=10)
    elif category == "new":
        contents = db.get_contents(limit=10)
    else:
        contents = db.get_contents(category=category, limit=10)
    
    if not contents:
        await callback.answer("❌ No content available yet!", show_alert=True)
        return
    
    category_name = {
        'movies': '🎬 Movies',
        'series': '📺 Series',
        'trending': '🔥 Trending',
        'new': '🆕 New Releases'
    }.get(category, category.title())
    
    text = f"{category_name}\n\n"
    
    buttons = []
    for content in contents:
        emoji = "🎬" if content['category'] == 'movies' else "📺"
        buttons.append([InlineKeyboardButton(
            f"{emoji} {content['title']} - {content['price_points']} pts",
            callback_data=f"view_{content['content_id']}"
        )])
    
    buttons.append([InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")])
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# View Content Detail
@Client.on_callback_query(filters.regex("^view_"))
async def view_content_callback(client: Client, callback: CallbackQuery):
    """View content details"""
    content_id = int(callback.data.replace("view_", ""))
    user_id = callback.from_user.id
    
    content = db.get_content(content_id)
    if not content:
        await callback.answer("❌ Content not found!", show_alert=True)
        return
    
    user_points = db.get_points(user_id)
    is_unlocked = db.is_unlocked(user_id, content_id)
    
    text = f"""
🎬 **{content['title']}**

{'⭐ ' + str(content['rating']) + '/10' if content['rating'] else ''}
{'⏱️ ' + content['duration'] if content['duration'] else ''}
{'🌐 ' + content['language'] if content['language'] else ''}
{'📀 ' + content['quality'] if content['quality'] else ''}

📄 {content['description'] if content['description'] else 'No description'}

━━━━━━━━━━━━━━━━━━━━

{'✅ **Already Unlocked!**' if is_unlocked else f'💰 **Price:** {content["price_points"]} points'}
{'📺 **Or watch ' + str(content['ads_required']) + ' ads**' if not is_unlocked else ''}

👁️ Views: {content['views']}
🔓 Unlocks: {content['unlocks']}
"""
    
    await callback.message.edit_text(
        text, 
        reply_markup=kb.content_detail(content_id, user_points, content['price_points'], is_unlocked)
    )

# Unlock with Points
@Client.on_callback_query(filters.regex("^unlock_points_"))
async def unlock_points_callback(client: Client, callback: CallbackQuery):
    """Unlock content with points"""
    content_id = int(callback.data.replace("unlock_points_", ""))
    user_id = callback.from_user.id
    
    result = db.unlock_content(user_id, content_id, method='points')
    
    if not result['success']:
        await callback.answer(f"❌ {result['message']}", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"✅ **Unlocked Successfully!**\n\n"
        f"💰 Remaining Points: {result['new_balance']}\n\n"
        f"🔗 **Download Link:**\n{result['download_link']}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ])
    )

# Unlock with Ads
@Client.on_callback_query(filters.regex("^unlock_ads_"))
async def unlock_ads_callback(client: Client, callback: CallbackQuery):
    """Unlock content by watching ads"""
    content_id = int(callback.data.replace("unlock_ads_", ""))
    user_id = callback.from_user.id
    
    content = db.get_content(content_id)
    ads_required = content['ads_required']
    
    from bot.config import SERVER_URL
    
    await callback.message.edit_text(
        f"📺 **Watch {ads_required} Ads to Unlock**\n\n"
        f"🎬 {content['title']}\n\n"
        f"Click below to start watching ads:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                f"📺 Watch Ads ({ads_required} required)", 
                web_app={"url": f"{SERVER_URL}/watch_ad.html?user_id={user_id}&content_id={content_id}&ads_required={ads_required}"}
            )],
            [InlineKeyboardButton("🔙 Back", callback_data=f"view_{content_id}")]
        ])
    )

# Earn Points Menu
@Client.on_callback_query(filters.regex("^earn_points$"))
async def earn_points_callback(client: Client, callback: CallbackQuery):
    """Show earn points menu"""
    user_id = callback.from_user.id
    points = db.get_points(user_id)
    points_per_ad = int(db.get_setting('points_per_ad'))
    
    text = f"""
💰 **Earn Points**

━━━━━━━━━━━━━━━━━━━━
💵 Current Balance: **{points}**
━━━━━━━━━━━━━━━━━━━━

📺 **Watch Ads:** +{points_per_ad} points/ad
🎁 **Daily Bonus:** +{db.get_setting('daily_bonus')} points
👥 **Refer Friends:** +{db.get_setting('referral_bonus')} points

👇 **Choose an option:**
"""
    
    await callback.message.edit_text(text, reply_markup=kb.earn_menu(user_id))

# My Wallet
@Client.on_callback_query(filters.regex("^my_wallet$"))
async def my_wallet_callback(client: Client, callback: CallbackQuery):
    """Show wallet"""
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    
    text = f"""
👛 **My Wallet**

━━━━━━━━━━━━━━━━━━━━
💰 Current Balance
────────────────────
🪙 {user['points']} Points

📊 **Statistics**
────────────────────
🎬 Total Unlocked: {user['total_unlocked']}
📺 Ads Watched: {user['total_ads_watched']}
👥 Referrals: {user['referrals']}

━━━━━━━━━━━━━━━━━━━━
"""
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Earn More", callback_data="earn_points")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]))

# Search
@Client.on_callback_query(filters.regex("^search$"))
async def search_callback(client: Client, callback: CallbackQuery):
    """Search prompt"""
    await callback.message.edit_text(
        "🔍 **Search Content**\n\n"
        "Send movie/series name to search:\n"
        "Example: `Pushpa`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ])
    )

# Admin Menu
@Client.on_callback_query(filters.regex("^admin_menu$"))
async def admin_menu_callback(client: Client, callback: CallbackQuery):
    """Return to admin menu"""
    from bot.config import ADMIN_IDS
    
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Access Denied!", show_alert=True)
        return
    
    stats = db.get_stats()
    
    admin_text = f"""
👑 **Admin Dashboard**

📊 **Today's Stats:**
👥 New Users: **{stats['today_users']}**
📺 Ad Views: **{stats['today_ads']}**

📈 **Total Stats:**
👥 Total Users: **{stats['total_users']}**
📺 Total Ads: **{stats['total_ads']}**
🎬 Contents: **{stats['total_contents']}**
🔓 Unlocks: **{stats['total_unlocks']}**

━━━━━━━━━━━━━━━━━━━━
"""
    
    await callback.message.edit_text(admin_text, reply_markup=kb.admin_menu())
