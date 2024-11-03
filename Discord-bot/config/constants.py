# config/constants.py
from datetime import datetime
from discord import Color

# Holiday definitions
HOLIDAYS = {
    "New Year's Day": (1, 1),
    "Valentine's Day": (2, 14),
    "St. Patrick's Day": (3, 17),
    "April Fools' Day": (4, 1),
    "Easter": (4, 9),  # Note: Date changes yearly
    "Mother's Day": (5, 14),  # Second Sunday in May
    "Father's Day": (6, 18),  # Third Sunday in June
    "Independence Day": (7, 4),
    "Halloween": (10, 31),
    "Thanksgiving": (11, 23),  # Fourth Thursday in November
    "Christmas Eve": (12, 24),
    "Christmas": (12, 25),
    "New Year's Eve": (12, 31)
}

# Bot Colors
COLORS = {
    'success': Color.green(),
    'error': Color.red(),
    'warning': Color.orange(),
    'info': Color.blue(),
    'music': Color.purple(),
    'birthday': Color.gold(),
    'holiday': Color.teal()
}

# Music Settings
MUSIC_SETTINGS = {
    'default_volume': 0.5,
    'max_queue_size': 500,
    'timeout_duration': 300,  # 5 minutes of inactivity before bot leaves
    'allowed_file_types': ['.mp3', '.wav', '.m4a', '.flac'],
    'max_song_duration': 10800,  # 3 hours in seconds
}

# Help Messages
HELP_TEXT = """
**🤖 Bot Commands Guide**

🎵 Music Commands
------------------
`!play <song>` - Play a song or add to queue
`!pause` - Pause current playback
`!resume` - Resume playback
`!skip` - Skip current song
`!stop` - Stop playback and clear queue
`!queue` - Show current queue
`!shuffle` - Shuffle the queue
`!loop [off/single/queue]` - Set loop mode
`!volume <0-100>` - Adjust volume
`!controls` - Show music control panel

🎂 Birthday Commands
------------------
`!setbirthday MM-DD` - Set your birthday
`!upcoming_birthdays [days]` - Show upcoming birthdays
`!set_birthday_channel #channel` - Set birthday announcement channel (Admin only)
`!set_birthday_role @role` - Set birthday role (Admin only)

🎉 Holiday Commands
------------------
`!next_holiday` - Show next upcoming holiday

⚙️ General Commands
------------------
`!help [command]` - Show this help or command details
`!ping` - Check bot's latency
`!serverinfo` - Show server information
`!userinfo [@user]` - Show user information
`!menu` - Show quick access menu

For more detailed help, use `!help <command>` 
Example: `!help play`
"""

# Command Cooldowns (in seconds)
COOLDOWNS = {
    'play': 3,
    'queue': 5,
    'birthday_info': 10,
    'upcoming_birthdays': 30,
    'serverinfo': 60
}

# Error Messages
ERROR_MESSAGES = {
    'not_in_voice': "❌ You need to be in a voice channel to use this command!",
    'no_music_playing': "❌ No music is currently playing!",
    'no_permission': "❌ You don't have permission to use this command!",
    'invalid_date': "❌ Invalid date format! Please use MM-DD (e.g., 12-25)",
    'queue_empty': "Queue is empty!",
    'song_not_found': "❌ Could not find the requested song.",
    'invalid_volume': "❌ Volume must be between 0 and 100!",
    'admin_only': "❌ This command requires administrator permissions or server owner status.",
    'check_failure': "❌ You don't have permission to use this command. This command requires administrator permissions or server owner status.",
    'bot_no_permission': "❌ I don't have permission to perform this action!",
    'invalid_channel': "❌ Invalid channel specified.",
    'invalid_role': "❌ Invalid role specified.",
    'channel_not_found': "❌ Birthday announcement channel not set. Ask an admin to set it using !set_birthday_channel",
    'role_not_found': "❌ Birthday role not set. Ask an admin to set it using !set_birthday_role"
}

# Success Messages
SUCCESS_MESSAGES = {
    'joined_voice': "✅ Joined the voice channel!",
    'left_voice': "✅ Left the voice channel!",
    'queue_cleared': "✅ Queue has been cleared!",
    'volume_changed': "✅ Volume changed to {}%",
    'birthday_set': "✅ Birthday has been set to {}!",
    'role_set': "✅ Role has been set!",
    'channel_set': "✅ Birthday announcement channel has been set!",
    'birthday_role_set': "✅ Birthday role has been updated!",
    'permission_granted': "✅ Permission granted successfully!"
}

# Emoji Mappings
EMOJIS = {
    'play': '▶️',
    'pause': '⏸️',
    'stop': '⏹️',
    'skip': '⏭️',
    'shuffle': '🔀',
    'repeat': '🔁',
    'queue': '📜',
    'volume': '🔊',
    'birthday': '🎂',
    'holiday': '🎉',
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'admin': '👑',
    'settings': '⚙️',
    'permission': '🔒'
}

# Visualization Settings
VISUALIZER = {
    'bars': ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'],
    'update_interval': 1,  # seconds
    'length': 20  # number of bars
}

# Command Categories
CATEGORIES = {
    'Music': ['play', 'pause', 'resume', 'skip', 'stop', 'queue', 'shuffle', 'loop', 'volume', 'controls'],
    'Birthday': ['setbirthday', 'upcoming_birthdays', 'birthday_info', 'set_birthday_channel', 'set_birthday_role'],
    'Holiday': ['next_holiday', 'upcoming_holidays'],
    'General': ['help', 'ping', 'serverinfo', 'userinfo', 'menu']
}

# Database Tables
DB_TABLES = {
    'birthdays': """
        CREATE TABLE IF NOT EXISTS birthdays (
            user_id INTEGER PRIMARY KEY,
            birthday TEXT
        )
    """,
    'birthday_channels': """
        CREATE TABLE IF NOT EXISTS birthday_channels (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER
        )
    """,
    'birthday_roles': """
        CREATE TABLE IF NOT EXISTS birthday_roles (
            guild_id INTEGER PRIMARY KEY,
            role_id INTEGER
        )
    """
}

# API Timeouts (in seconds)
TIMEOUTS = {
    'voice_connection': 20,
    'api_request': 10,
    'database': 5
}

# Custom Welcome Messages
WELCOME_MESSAGES = [
    "Welcome to the server, {}! 🎉",
    "Hey {}! Glad you're here! 👋",
    "Welcome aboard, {}! 🚀",
    "Everyone welcome {} to the server! 🌟",
    "{} just joined! Make yourself at home! 🏠"
]

# Permission Levels
PERMISSION_LEVELS = {
    'user': 0,
    'moderator': 1,
    'admin': 2,
    'owner': 3
}

# Command Requirements (for help text and checks)
COMMAND_REQUIREMENTS = {
    'set_birthday_channel': {
        'permissions': ['administrator'],
        'description': 'Set the channel where birthday announcements will be sent',
        'usage': '!set_birthday_channel #channel',
        'example': '!set_birthday_channel #birthdays'
    },
    'set_birthday_role': {
        'permissions': ['administrator'],
        'description': 'Set the role that will be given to users on their birthday',
        'usage': '!set_birthday_role @role',
        'example': '!set_birthday_role @Birthday'
    }
}