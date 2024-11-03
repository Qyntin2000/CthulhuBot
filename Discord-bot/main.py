# main.py
import discord
from discord.ext import commands
import asyncio
import sys
import traceback
from typing import Optional
from datetime import datetime

# Import configurations
from config.settings import DISCORD_TOKEN, BOT_PREFIX, INTENTS
from utils.database import Database

class MusicBot(commands.Bot):
    """Custom bot class with additional functionality"""
    
    def __init__(self):
        # Initialize the bot with configured settings
        super().__init__(
            command_prefix=BOT_PREFIX,
            intents=INTENTS,
            help_command=None,  # Disable default help command
            activity=discord.Activity(
                type=discord.ActivityType.competing,
                name="a music contest"
            )
        )
        
        # Initialize bot attributes
        self.db = Database()
        self.start_time = datetime.utcnow()
        self.error_channel: Optional[discord.TextChannel] = None
        
        # Music-related attributes
        self.music_players = {}
        self.visualizer_messages = {}

    async def setup_hook(self):
        """Setup hook that runs before the bot starts"""
        print("Setting up bot...")
        
        # Initialize database
        print("Initializing database...")
        self.db.init_db()
        
        # Load all cogs
        print("Loading extensions...")
        initial_extensions = [
            'cogs.music',
            'cogs.birthday',
            'cogs.holiday',
            'cogs.general'
        ]
        
        for extension in initial_extensions:
            try:
                await self.load_extension(extension)
                print(f"Loaded {extension}")
            except Exception as e:
                print(f"Failed to load extension {extension}.", file=sys.stderr)
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)

    async def on_error(self, event_method: str, *args, **kwargs):
        """Global error handler for all events"""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        # Format the error message
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Print to console
        print(f'Unhandled error in {event_method}:', file=sys.stderr)
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
        
        # Log to error channel if available
        if self.error_channel:
            embed = discord.Embed(
                title=f"Error in {event_method}",
                description=f"```py\n{error_msg[:2000]}```",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            try:
                await self.error_channel.send(embed=embed)
            except discord.HTTPException:
                pass

    async def set_error_channel(self, channel_id: int):
        """Set the channel for error logging"""
        self.error_channel = self.get_channel(channel_id)

    async def close(self):
        """Clean up before the bot closes"""
        print("Shutting down bot...")
        
        # Disconnect from all voice channels
        for voice_client in self.voice_clients:
            try:
                await voice_client.disconnect(force=True)
            except:
                pass
        
        # Cancel all tasks and clean up
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        
        await super().close()

async def run_bot():
    """Initialize and run the bot"""
    try:
        # Create bot instance
        bot = MusicBot()
        
        # Add error handling for the initial connection
        try:
            print("Connecting to Discord...")
            await bot.start(DISCORD_TOKEN)
        except discord.LoginFailure:
            print("Failed to log in: Invalid token", file=sys.stderr)
            return
        except discord.HTTPException as e:
            print(f"Failed to log in: HTTP Exception: {e}", file=sys.stderr)
            return
        except Exception as e:
            print(f"Failed to log in: {type(e).__name__}: {e}", file=sys.stderr)
            return
            
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        print("\nShutdown requested...")
        await bot.close()
    finally:
        # Clean up any remaining resources
        print("Cleanup complete. Bot shut down.")

if __name__ == "__main__":
    # Set up logging configuration
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Create and run the event loop
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\nBot shutdown complete.")