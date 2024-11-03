# cogs/music.py
import discord
from discord.ext import commands, tasks
from utils.music_util import YTDLSource, MusicPlayer, QueueManager
from utils.views import MusicControlView
import asyncio
from typing import Optional
from collections import deque

class Music(commands.Cog):
    """Music commands and functionality"""
    
    def __init__(self, bot):
        self.bot = bot
        self.music_players = {}
        self.visualizer_messages = {}
        self.visualizer_loop.start()

    def cog_unload(self):
        """Cleanup when cog is unloaded"""
        self.visualizer_loop.cancel()

    async def get_player(self, ctx) -> MusicPlayer:
        """Get or create a MusicPlayer instance for a guild"""
        if ctx.guild.id not in self.music_players:
            player = MusicPlayer(self.bot)
            self.music_players[ctx.guild.id] = player
            return player
        return self.music_players[ctx.guild.id]

    @commands.command()
    async def join(self, ctx):
        """Join the user's voice channel"""
        if ctx.author.voice is None:
            return await ctx.send("You're not connected to a voice channel.")
        
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        
        await ctx.send(f"Joined {channel.name}")

    @commands.command()
    async def leave(self, ctx):
        """Leave the voice channel"""
        if ctx.voice_client is None:
            return await ctx.send("I'm not connected to a voice channel.")
        
        await ctx.voice_client.disconnect()
        
        # Cleanup
        if ctx.guild.id in self.music_players:
            self.music_players[ctx.guild.id].destroy(ctx.guild)
            
        await ctx.send("Left the voice channel")

    @commands.command()
    async def play(self, ctx, *, query: str):
        """Play a song or add it to the queue"""
        # Join voice channel if not already connected
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                return await ctx.send("You're not connected to a voice channel.")

        async with ctx.typing():
            try:
                player = await self.get_player(ctx)
                source = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
                
                await player.queue.put(source)
                
                if not ctx.voice_client.is_playing():
                    await self._play_next(ctx, player)
                    await ctx.send(f"Now playing: {source.title}")
                else:
                    await ctx.send(f"Added to queue: {source.title}")
                    
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")

    @commands.command()
    async def pause(self, ctx):
        """Pause the current song"""
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            return await ctx.send("Nothing is playing right now.")
            
        ctx.voice_client.pause()
        await ctx.send("Paused ⏸️")

    @commands.command()
    async def resume(self, ctx):
        """Resume the current song"""
        if ctx.voice_client is None:
            return await ctx.send("I'm not connected to a voice channel.")
            
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed ▶️")
        else:
            await ctx.send("The music is not paused.")

    @commands.command()
    async def stop(self, ctx):
        """Stop playing and clear the queue"""
        if ctx.voice_client is None:
            return await ctx.send("I'm not connected to a voice channel.")

        player = await self.get_player(ctx)
        player.queue._queue.clear()
        ctx.voice_client.stop()
        await ctx.send("Stopped playing and cleared the queue ⏹️")

    @commands.command()
    async def skip(self, ctx):
        """Skip the current song"""
        if ctx.voice_client is None:
            return await ctx.send("I'm not connected to a voice channel.")

        if not ctx.voice_client.is_playing():
            return await ctx.send("Nothing is playing right now.")

        ctx.voice_client.stop()
        await ctx.send("Skipped ⏭️")

    @commands.command()
    async def queue(self, ctx):
        """Display the current queue"""
        player = await self.get_player(ctx)
        
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            return await ctx.send("Nothing is playing right now.")

        # Create queue embed
        embed = discord.Embed(title="Music Queue", color=discord.Color.blue())
        
        # Add current song
        embed.add_field(
            name="Now Playing",
            value=player.current.title if player.current else "Nothing",
            inline=False
        )
        
        # Add upcoming songs
        upcoming = list(player.queue._queue)
        if upcoming:
            queue_text = "\n".join(f"{i+1}. {song.title}" for i, song in enumerate(upcoming))
            embed.add_field(name="Up Next", value=queue_text, inline=False)
        else:
            embed.add_field(name="Up Next", value="No songs in queue", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def shuffle(self, ctx):
        """Shuffle the queue"""
        player = await self.get_player(ctx)
        
        if player.queue.qsize() < 2:
            return await ctx.send("Need at least 2 songs in the queue to shuffle.")

        # Get all items from queue
        items = list(player.queue._queue)
        player.queue._queue.clear()
        
        # Shuffle and put back
        import random
        random.shuffle(items)
        for item in items:
            await player.queue.put(item)
            
        await ctx.send("Queue has been shuffled! 🔀")

    @commands.command()
    async def loop(self, ctx, mode: str = 'off'):
        """Set loop mode (off/single/queue)"""
        player = await self.get_player(ctx)
        
        mode = mode.lower()
        if mode not in ['off', 'single', 'queue']:
            return await ctx.send("Invalid loop mode. Use 'off', 'single', or 'queue'.")
        
        player.loop_mode = mode
        await ctx.send(f"Loop mode set to: {mode} 🔁")

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Change the player's volume"""
        if ctx.voice_client is None:
            return await ctx.send("I'm not connected to a voice channel.")

        if not 0 <= volume <= 100:
            return await ctx.send("Volume must be between 0 and 100.")

        player = await self.get_player(ctx)
        player.volume = volume / 100
        if ctx.voice_client.source:
            ctx.voice_client.source.volume = volume / 100

        await ctx.send(f"Volume set to {volume}%")

    @commands.command()
    async def controls(self, ctx):
        """Display the music control panel"""
        view = MusicControlView(ctx)
        embed = discord.Embed(title="🎵 Music Controls", color=discord.Color.purple())
        
        player = await self.get_player(ctx)
        current_song = "No song playing"
        if player.current:
            current_song = player.current.title
            
        embed.add_field(name="Current Song", value=current_song)
        await ctx.send(embed=embed, view=view)

    async def _play_next(self, ctx, player):
        """Helper method to play the next song"""
        if player.queue.empty():
            return
            
        # Get next song from queue
        source = await player.queue.get()
        ctx.voice_client.play(
            source, 
            after=lambda e: self.bot.loop.create_task(self._play_next(ctx, player))
        )
        player.current = source

    @tasks.loop(seconds=1)
    async def visualizer_loop(self):
        """Update the music visualizer for all active players"""
        for guild_id, player in self.music_players.items():
            if guild_id in self.visualizer_messages and player.current:
                message = self.visualizer_messages[guild_id]
                try:
                    embed = await player.create_embed()
                    await message.edit(embed=embed)
                except discord.errors.NotFound:
                    # Message was deleted
                    del self.visualizer_messages[guild_id]
                except Exception as e:
                    print(f"Error updating visualizer: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handle bot disconnection and cleanup"""
        if member == self.bot.user and after.channel is None:
            guild_id = before.channel.guild.id
            if guild_id in self.music_players:
                self.music_players[guild_id].destroy(before.channel.guild)
                if guild_id in self.visualizer_messages:
                    try:
                        await self.visualizer_messages[guild_id].delete()
                    except:
                        pass
                    del self.visualizer_messages[guild_id]

async def setup(bot):
    """Setup function for loading the cog"""
    await bot.add_cog(Music(bot))