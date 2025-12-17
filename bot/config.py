import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
API_ID = int(os.getenv('API_ID', '37081556'))
API_HASH = os.getenv('API_HASH', '61e4c99b0b400d0399ff96864aecab20')
BOT_TOKEN = os.getenv('BOT_TOKEN', '8331138127:AAHMMhcWUd1jHbirR_yrHfpYRK_X0VzinQU')

# Admin Configuration
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '8128572225').split(',') if x]

# Server Configuration
SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:10000')
FLASK_PORT = int(os.getenv('FLASK_PORT', '10000'))

# Database
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/bot_database.db')

# Monetag
MONETAG_ZONE_ID = os.getenv('MONETAG_ZONE_ID', '10337592')

# Bot Settings (Admin থেকে চেঞ্জ করা যাবে)
DEFAULT_SETTINGS = {
    'points_per_ad': '15',
    'ads_for_content': '3',
    'daily_bonus': '20',
    'referral_bonus': '50',
    'monetag_zone_id': MONETAG_ZONE_ID,
    'welcome_message': '🎬 স্বাগতম {name}!\n\n✨ Movie Nest এ আপনাকে স্বাগতম!\nমুভি দেখতে পয়েন্ট কামান!',
    'bot_status': 'active',
    'maintenance_message': '⚠️ বট রক্ষণাবেক্ষণে আছে। শীঘ্রই ফিরে আসছি।'
}
