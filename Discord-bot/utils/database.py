# utils/database.py
import sqlite3
from datetime import datetime, timedelta
from config.settings import DATABASE_NAME

class Database:
    def __init__(self):
        self.db_name = DATABASE_NAME

    def init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            # Create birthdays table
            c.execute('''CREATE TABLE IF NOT EXISTS birthdays
                        (user_id INTEGER PRIMARY KEY, birthday TEXT)''')
            
            # Create birthday channels table
            c.execute('''CREATE TABLE IF NOT EXISTS birthday_channels
                        (guild_id INTEGER PRIMARY KEY, channel_id INTEGER)''')
            
            # Create birthday roles table
            c.execute('''CREATE TABLE IF NOT EXISTS birthday_roles
                        (guild_id INTEGER PRIMARY KEY, role_id INTEGER)''')

            # Create holiday channels table
            c.execute('''CREATE TABLE IF NOT EXISTS holiday_channels
                        (guild_id INTEGER PRIMARY KEY, channel_id INTEGER)''')
            conn.commit()

    def store_birthday(self, user_id: int, birthday: datetime):
        """Store user's birthday"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO birthdays VALUES (?, ?)", 
                     (user_id, birthday.strftime("%m-%d")))
            conn.commit()

    def set_birthday_channel(self, guild_id: int, channel_id: int):
        """Set birthday announcement channel for a guild"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO birthday_channels VALUES (?, ?)", 
                     (guild_id, channel_id))
            conn.commit()

    def get_birthday_channel(self, guild_id: int) -> int:
        """Get birthday announcement channel for a guild"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT channel_id FROM birthday_channels WHERE guild_id = ?", 
                     (guild_id,))
            result = c.fetchone()
            return result[0] if result else None

    def set_birthday_role(self, guild_id: int, role_id: int):
        """Set birthday role for a guild"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO birthday_roles VALUES (?, ?)", 
                     (guild_id, role_id))
            conn.commit()

    def get_birthday_role(self, guild_id: int) -> int:
        """Get birthday role for a guild"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT role_id FROM birthday_roles WHERE guild_id = ?", 
                     (guild_id,))
            result = c.fetchone()
            return result[0] if result else None

    def get_todays_birthdays(self) -> list:
        """Get list of user IDs who have birthdays today"""
        today = datetime.now().strftime("%m-%d")
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT user_id FROM birthdays WHERE birthday = ?", (today,))
            return [user_id for (user_id,) in c.fetchall()]

    def get_upcoming_birthdays(self, days: int = 30) -> list:
        """Get list of upcoming birthdays within specified days"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        today = datetime.now()
        upcoming = []
        
        for i in range(days):
            date = (today + timedelta(days=i)).strftime("%m-%d")
            c.execute("SELECT user_id, birthday FROM birthdays WHERE birthday = ?", 
                     (date,))
            results = c.fetchall()
            for user_id, birthday in results:
                birthday_date = datetime.strptime(birthday, "%m-%d").replace(
                    year=today.year)
                upcoming.append((user_id, birthday_date))
        
        conn.close()
        return sorted(upcoming, key=lambda x: x[1])

    def get_birthdays_for_date(self, date_str: str) -> list:
        """Get all user IDs who have birthdays on a specific date"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT user_id FROM birthdays WHERE birthday = ?", (date_str,))
            return [row[0] for row in c.fetchall()]

    def set_holiday_channel(self, guild_id: int, channel_id: int):
        """Set holiday announcement channel for a guild"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO holiday_channels VALUES (?, ?)",
                     (guild_id, channel_id))
            conn.commit()

    def get_holiday_channel(self, guild_id: int) -> int:
        """Get holiday announcement channel for a guild"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT channel_id FROM holiday_channels WHERE guild_id = ?",
                     (guild_id,))
            result = c.fetchone()
            return result[0] if result else None

# utils/__init__.py
"""
This file is intentionally empty to mark the directory as a Python package.
"""