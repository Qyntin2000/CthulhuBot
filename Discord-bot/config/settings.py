# config/settings.py
import os
from dotenv import load_dotenv
import discord

# Load environment variables from .env file
load_dotenv()

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
BOT_PREFIX = '!'

# Discord Intents
INTENTS = discord.Intents.default()
INTENTS.voice_states = True
INTENTS.message_content = True
INTENTS.members = True

# Database configuration
DATABASE_NAME = 'birthdays.db'

# YTDL Options
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

# FFMPEG Options
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

# Verify token is loaded
if not DISCORD_TOKEN:
    raise ValueError("No Discord token found. Please check your .env file.")

# config/constants.py
from datetime import datetime, date

# Holiday definitions
HOLIDAYS = {
    "Christmas": (12, 25),
    "Thanksgiving": (11, 28),
    "Halloween": (10, 31)
}

# Help messages
HELP_TEXT = """
**Bot Commands:**

Channel Commands
-----------------
`!join` - Bot joins your current voice channel
`!leave` - Bot leaves the voice channel

Music Commands
---------------
`!play <song>` - Play a song or add it to the queue
`!controls` - Display the music control panel
`!shuffle` - Shuffle the current queue
`!loop [off/single/queue]` - Set loop mode (off, single track, or entire queue)

Birthday Commands
------------------
`!setbirthday MM-DD` - Set your birthday (e.g., !setbirthday 12-25 for December 25th)
`!upcoming_birthdays [days]` - Show upcoming birthdays (default: next 30 days)
`!set_birthday_role @role` - Set the role to be given on birthdays (Admin only)

Holiday Commands
-----------------
`!next_holiday` - Shows the next closest holiday

General Commands
-----------------
`!help` - Show this help message
"""

# Create empty __init__.py file in config directory
# config/__init__.py
"""
This file is intentionally empty to mark the directory as a Python package.
"""