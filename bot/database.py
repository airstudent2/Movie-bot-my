import sqlite3
import os
from datetime import datetime
from bot.config import DATABASE_PATH, DEFAULT_SETTINGS

class Database:
    def __init__(self):
        # Create data directory if not exists
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize all tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                username TEXT,
                points INTEGER DEFAULT 0,
                level TEXT DEFAULT 'bronze',
                total_unlocked INTEGER DEFAULT 0,
                total_ads_watched INTEGER DEFAULT 0,
                referrals INTEGER DEFAULT 0,
                referred_by INTEGER,
                is_vip INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_active TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Contents Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contents (
                content_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                tags TEXT,
                thumbnail_url TEXT,
                download_link TEXT NOT NULL,
                price_points INTEGER DEFAULT 50,
                ads_required INTEGER DEFAULT 3,
                rating REAL DEFAULT 0,
                duration TEXT,
                language TEXT,
                quality TEXT,
                views INTEGER DEFAULT 0,
                unlocks INTEGER DEFAULT 0,
                added_by INTEGER,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Transactions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                source TEXT,
                description TEXT,
                balance_before INTEGER,
                balance_after INTEGER,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Unlocked Contents Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unlocked_contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content_id INTEGER NOT NULL,
                unlock_method TEXT,
                unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ad Views Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ad_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ad_type TEXT,
                points_earned INTEGER,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bot Settings Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_by INTEGER
            )
        ''')
        
        # Insert default settings
        for key, value in DEFAULT_SETTINGS.items():
            cursor.execute('''
                INSERT OR IGNORE INTO bot_settings (setting_key, setting_value)
                VALUES (?, ?)
            ''', (key, str(value)))
        
        conn.commit()
        conn.close()
    
    # ==================== USER FUNCTIONS ====================
    
    def add_user(self, user_id, name, username=None, referred_by=None):
        """Add new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (user_id, name, username, referred_by)
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, username, referred_by))
            
            if referred_by:
                referral_bonus = int(self.get_setting('referral_bonus'))
                self.add_points(referred_by, referral_bonus, 'referral_bonus')
                cursor.execute('UPDATE users SET referrals = referrals + 1 WHERE user_id = ?', (referred_by,))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_user(self, user_id):
        """Get user data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def update_last_active(self, user_id):
        """Update user last active time"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
    
    def get_points(self, user_id):
        """Get user points"""
        user = self.get_user(user_id)
        return user['points'] if user else 0
    
    def add_points(self, user_id, points, source='manual'):
        """Add points to user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        current_points = self.get_points(user_id)
        new_points = current_points + points
        
        cursor.execute('UPDATE users SET points = ? WHERE user_id = ?', (new_points, user_id))
        cursor.execute('''
            INSERT INTO transactions (user_id, type, amount, source, balance_before, balance_after)
            VALUES (?, 'earn', ?, ?, ?, ?)
        ''', (user_id, points, source, current_points, new_points))
        
        conn.commit()
        conn.close()
        return new_points
    
    def deduct_points(self, user_id, points, source='unlock_content'):
        """Deduct points from user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        current_points = self.get_points(user_id)
        if current_points < points:
            conn.close()
            return False
        
        new_points = current_points - points
        cursor.execute('UPDATE users SET points = ? WHERE user_id = ?', (new_points, user_id))
        cursor.execute('''
            INSERT INTO transactions (user_id, type, amount, source, balance_before, balance_after)
            VALUES (?, 'spend', ?, ?, ?, ?)
        ''', (user_id, points, source, current_points, new_points))
        
        conn.commit()
        conn.close()
        return new_points
    
    # ==================== CONTENT FUNCTIONS ====================
    
    def add_content(self, data):
        """Add new content"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contents 
            (title, description, category, tags, thumbnail_url, download_link,
             price_points, ads_required, rating, duration, language, quality, added_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['title'], data.get('description'), data['category'],
            data.get('tags'), data.get('thumbnail_url'), data['download_link'],
            data.get('price_points', 50), data.get('ads_required', 3),
            data.get('rating', 0), data.get('duration'), data.get('language'),
            data.get('quality'), data.get('added_by')
        ))
        
        content_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return content_id
    
    def get_contents(self, category=None, limit=10, offset=0, search=None):
        """Get contents list"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM contents WHERE is_active = 1'
        params = []
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        if search:
            query += ' AND (title LIKE ? OR tags LIKE ?)'
            params.extend([f'%{search}%', f'%{search}%'])
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        contents = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in contents]
    
    def get_content(self, content_id):
        """Get single content"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contents WHERE content_id = ?', (content_id,))
        content = cursor.fetchone()
        conn.close()
        return dict(content) if content else None
    
    def unlock_content(self, user_id, content_id, method='points'):
        """Unlock content for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM unlocked_contents WHERE user_id = ? AND content_id = ?', (user_id, content_id))
        if cursor.fetchone():
            conn.close()
            return {'success': False, 'message': 'Already unlocked'}
        
        content = self.get_content(content_id)
        if not content:
            conn.close()
            return {'success': False, 'message': 'Content not found'}
        
        if method == 'points':
            new_balance = self.deduct_points(user_id, content['price_points'], f'unlock_content_{content_id}')
            if new_balance is False:
                conn.close()
                return {'success': False, 'message': 'Insufficient points'}
        
        cursor.execute('INSERT INTO unlocked_contents (user_id, content_id, unlock_method) VALUES (?, ?, ?)', 
                      (user_id, content_id, method))
        cursor.execute('UPDATE contents SET unlocks = unlocks + 1, views = views + 1 WHERE content_id = ?', (content_id,))
        cursor.execute('UPDATE users SET total_unlocked = total_unlocked + 1 WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'download_link': content['download_link'],
            'new_balance': self.get_points(user_id)
        }
    
    def is_unlocked(self, user_id, content_id):
        """Check if content is unlocked"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM unlocked_contents WHERE user_id = ? AND content_id = ?', (user_id, content_id))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    # ==================== AD FUNCTIONS ====================
    
    def log_ad_view(self, user_id, ad_type, points_earned):
        """Log ad view"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO ad_views (user_id, ad_type, points_earned) VALUES (?, ?, ?)', 
                      (user_id, ad_type, points_earned))
        cursor.execute('UPDATE users SET total_ads_watched = total_ads_watched + 1 WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
    
    # ==================== SETTINGS FUNCTIONS ====================
    
    def get_setting(self, key):
        """Get bot setting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT setting_value FROM bot_settings WHERE setting_key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result['setting_value'] if result else None
    
    def update_setting(self, key, value, updated_by=None):
        """Update bot setting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE bot_settings 
            SET setting_value = ?, updated_at = CURRENT_TIMESTAMP, updated_by = ?
            WHERE setting_key = ?
        ''', (str(value), updated_by, key))
        conn.commit()
        conn.close()
    
    def get_all_settings(self):
        """Get all settings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bot_settings')
        settings = cursor.fetchall()
        conn.close()
        return {row['setting_key']: row['setting_value'] for row in settings}
    
    # ==================== STATS FUNCTIONS ====================
    
    def get_stats(self):
        """Get bot statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM users')
        total_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = DATE('now')")
        today_users = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM ad_views')
        total_ads = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM ad_views WHERE DATE(timestamp) = DATE('now')")
        today_ads = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM contents WHERE is_active = 1')
        total_contents = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM unlocked_contents')
        total_unlocks = cursor.fetchone()['count']
        
        conn.close()
        
        return {
            'total_users': total_users,
            'today_users': today_users,
            'total_ads': total_ads,
            'today_ads': today_ads,
            'total_contents': total_contents,
            'total_unlocks': total_unlocks
        }
    
    def get_all_users(self, limit=50, offset=0):
        """Get all users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?', (limit, offset))
        users = cursor.fetchall()
        conn.close()
        return [dict(row) for row in users]
