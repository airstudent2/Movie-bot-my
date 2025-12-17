from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from bot.config import SERVER_URL

class Keyboards:
    
    @staticmethod
    def main_menu(user_id):
        """Main menu keyboard"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎬 Movies", callback_data="cat_movies"),
                InlineKeyboardButton("📺 Series", callback_data="cat_series")
            ],
            [
                InlineKeyboardButton("🔥 Trending", callback_data="cat_trending"),
                InlineKeyboardButton("🆕 New", callback_data="cat_new")
            ],
            [
                InlineKeyboardButton("🔍 Search", callback_data="search"),
                InlineKeyboardButton("💰 Earn Points", callback_data="earn_points")
            ],
            [
                InlineKeyboardButton("👛 My Wallet", callback_data="my_wallet"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ]
        ])
    
    @staticmethod
    def earn_menu(user_id):
        """Earn points menu"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "📺 Watch Ads (+15 pts)", 
                web_app=WebAppInfo(url=f"{SERVER_URL}/watch_ad.html?user_id={user_id}")
            )],
            [
                InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus"),
                InlineKeyboardButton("👥 Refer Friends", callback_data="referral")
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ])
    
    @staticmethod
    def content_list(category):
        """Back button for content list"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ])
    
    @staticmethod
    def content_detail(content_id, user_points, price, is_unlocked=False):
        """Content detail keyboard"""
        if is_unlocked:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Download", callback_data=f"download_{content_id}")],
                [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
            ])
        
        buttons = []
        
        if user_points >= price:
            buttons.append([InlineKeyboardButton(
                f"🔓 Unlock ({price} pts)", 
                callback_data=f"unlock_points_{content_id}"
            )])
        
        buttons.append([InlineKeyboardButton(
            "📺 Watch Ads to Unlock (Free)", 
            callback_data=f"unlock_ads_{content_id}"
        )])
        
        buttons.append([
            InlineKeyboardButton("❤️ Favorite", callback_data=f"fav_{content_id}"),
            InlineKeyboardButton("📤 Share", callback_data=f"share_{content_id}")
        ])
        
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def admin_menu():
        """Admin menu keyboard"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📤 Add Content", callback_data="admin_add_content"),
                InlineKeyboardButton("👥 Users", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
                InlineKeyboardButton("⚙️ Bot Settings", callback_data="admin_settings")
            ],
            [
                InlineKeyboardButton("💰 Ad Settings", callback_data="admin_ads"),
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
            ],
            [InlineKeyboardButton("🌐 Web Dashboard", 
                                  web_app=WebAppInfo(url=f"{SERVER_URL}/admin_dashboard.html"))]
        ])
    
    @staticmethod
    def admin_settings_menu():
        """Admin settings submenu"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎯 Points Per Ad", callback_data="setting_points_per_ad")],
            [InlineKeyboardButton("📺 Ads Required", callback_data="setting_ads_required")],
            [InlineKeyboardButton("🎁 Daily Bonus", callback_data="setting_daily_bonus")],
            [InlineKeyboardButton("👥 Referral Bonus", callback_data="setting_referral_bonus")],
            [InlineKeyboardButton("💬 Welcome Message", callback_data="setting_welcome")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
        ])
    
    @staticmethod
    def admin_ad_settings():
        """Admin ad settings"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🆔 Change Zone ID", callback_data="setting_zone_id")],
            [InlineKeyboardButton("📊 View Ad Stats", callback_data="admin_ad_stats")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
        ])
