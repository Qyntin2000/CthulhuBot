# utils/music_utils.py
import discord
import yt_dlp
import asyncio
from typing import Optional, Dict, Any
from config.settings import YTDL_OPTIONS, FFMPEG_OPTIONS
import random

class YTDLSource(discord.PCMVolumeTransformer):
    """A custom audio source class for handling YouTube downloads and streaming"""
    
    def __init__(self, source: discord.AudioSource, *, data: Dict[str, Any], volume: float = 0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')
        self.webpage_url = data.get('webpage_url')
        self.uploader = data.get('uploader')

    @classmethod
    async def from_url(cls, url: str, *, loop: Optional[asyncio.AbstractEventLoop] = None, stream: bool = False):
        """Creates a YTDLSource from a URL"""
        loop = loop or asyncio.get_event_loop()
        ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
            if 'entries' in data:
                # Take first item from a playlist
                data = data['entries'][0]

            filename = data['url'] if stream else ytdl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)
        except Exception as e:
            raise Exception(f"Error processing URL: {str(e)}")

class MusicPlayer:
    """Helper class for managing music playback and queue"""
    
    def __init__(self, bot):
        self.bot = bot
        self.queue = asyncio.Queue()
        self.next_event = asyncio.Event()
        self.current = None
        self.volume = 0.5
        self.loop_mode = 'off'  # Can be 'off', 'single', or 'queue'
        self.voice = None
        self._task = None

    def generate_visualizer(self) -> str:
        """Generates a simple ASCII visualizer"""
        bars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        return ''.join(random.choice(bars) for _ in range(20))

    async def create_embed(self) -> discord.Embed:
        """Creates an embed for the currently playing song"""
        if not self.current:
            return discord.Embed(title="No song playing", color=discord.Color.red())

        embed = discord.Embed(title="Now Playing", color=discord.Color.blue())
        embed.add_field(name="Song", value=self.current.title)
        
        if self.current.uploader:
            embed.add_field(name="Uploader", value=self.current.uploader)
        
        if self.current.duration:
            minutes, seconds = divmod(self.current.duration, 60)
            embed.add_field(name="Duration", value=f"{minutes}:{seconds:02d}")
        
        if self.current.webpage_url:
            embed.add_field(name="URL", value=f"[Click here]({self.current.webpage_url})")
        
        if self.current.thumbnail:
            embed.set_thumbnail(url=self.current.thumbnail)

        visualizer = self.generate_visualizer()
        embed.description = f"```{visualizer}```"
        
        return embed

    async def player_loop(self):
        """Main player loop that handles queue and playback"""
        await self.bot.wait_until_ready()

        while True:
            self.next_event.clear()

            # Handle loop mode
            if self.loop_mode == 'single' and self.current:
                await self.queue.put(self.current)
            elif self.loop_mode == 'queue' and self.current:
                await self.queue.put(self.current)

            try:
                async with asyncio.timeout(180):  # 3 minute timeout
                    self.current = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self.voice.guild)

            self.current.source.volume = self.volume
            self.voice.play(self.current.source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next_event.set))
            await self.create_embed()
            await self.next_event.wait()

    def destroy(self, guild: discord.Guild):
        """Cleanup resources"""
        return self.bot.loop.create_task(self._cleanup(guild))

    async def _cleanup(self, guild: discord.Guild):
        """Internal cleanup method"""
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.bot.music_players[guild.id]
        except KeyError:
            pass

    @staticmethod
    def parse_duration(duration: str) -> int:
        """Convert duration string to seconds"""
        try:
            # Handle MM:SS format
            if ':' in duration:
                minutes, seconds = duration.split(':')
                return int(minutes) * 60 + int(seconds)
            # Handle seconds format
            return int(duration)
        except ValueError:
            return 0

class QueueManager:
    """Helper class for managing the music queue"""
    
    @staticmethod
    def shuffle_queue(queue):
        """Shuffles the queue while preserving the currently playing song"""
        if len(queue) < 2:
            return queue
            
        current = queue.popleft()  # Remove the currently playing song
        items = list(queue)
        random.shuffle(items)
        queue.clear()
        queue.append(current)  # Put the current song back
        queue.extend(items)
        return queue

    @staticmethod
    def format_queue(queue, current_song) -> str:
        """Formats the queue for display"""
        if not current_song:
            return "Nothing is currently playing."
            
        output = [f"🎵 Now Playing: {current_song.title}"]
        
        if not queue:
            output.append("\nQueue is empty.")
        else:
            output.append("\n📃 Queue:")
            for i, song in enumerate(queue, 1):
                output.append(f"{i}. {song.title}")
                
        return "\n".join(output)