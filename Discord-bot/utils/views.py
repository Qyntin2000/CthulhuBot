# utils/views.py
import discord
from discord.ui import Button, View, Select
from typing import Optional, Callable

class VolumeSlider(Select):
    """Volume control dropdown menu"""
    def __init__(self):
        options = [
            discord.SelectOption(label=f"{i*10}%", value=str(i*10)) 
            for i in range(11)
        ]
        super().__init__(
            placeholder="Adjust volume",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        volume = int(self.values[0])
        if interaction.guild.voice_client:
            interaction.guild.voice_client.source.volume = volume / 100
            await interaction.response.send_message(
                f"Changed volume to {volume}%",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Not connected to a voice channel.",
                ephemeral=True
            )

class MusicControlView(View):
    """Music control panel with buttons"""
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.add_item(VolumeSlider())

    @discord.ui.button(label="▶️ Play/Pause", style=discord.ButtonStyle.primary, emoji="⏯️")
    async def play_pause(self, interaction: discord.Interaction, button: Button):
        if interaction.guild.voice_client is None:
            await interaction.response.send_message(
                "I'm not connected to a voice channel.",
                ephemeral=True
            )
            return
        
        if interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.pause()
            await interaction.response.send_message("Paused the music.", ephemeral=True)
        else:
            interaction.guild.voice_client.resume()
            await interaction.response.send_message("Resumed the music.", ephemeral=True)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.secondary, emoji="⏭️")
    async def skip(self, interaction: discord.Interaction, button: Button):
        if interaction.guild.voice_client is None:
            await interaction.response.send_message(
                "I'm not connected to a voice channel.",
                ephemeral=True
            )
            return
        
        if not interaction.guild.voice_client.is_playing():
            await interaction.response.send_message(
                "Nothing is playing right now.",
                ephemeral=True
            )
            return
        
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("Skipped the current song.")

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="⏹️")
    async def stop(self, interaction: discord.Interaction, button: Button):
        if interaction.guild.voice_client is None:
            await interaction.response.send_message(
                "Not connected to a voice channel.",
                ephemeral=True
            )
            return

        interaction.guild.voice_client.stop()
        self.ctx.bot.queue.clear()
        await interaction.response.send_message("Playback stopped and queue cleared.")

    @discord.ui.button(label="Queue", style=discord.ButtonStyle.secondary, emoji="📜")
    async def show_queue(self, interaction: discord.Interaction, button: Button):
        if (interaction.guild.voice_client is None or 
            not interaction.guild.voice_client.is_playing()):
            await interaction.response.send_message(
                "Nothing is currently playing.",
                ephemeral=True
            )
            return
        
        current_song = interaction.guild.voice_client.source.title
        queue_list = f"Currently playing: {current_song}\n\nUpcoming songs:\n"
        
        if len(self.ctx.bot.queue) == 0:
            queue_list += "No songs in the queue."
        else:
            queue_list += "\n".join(
                f"{i+1}. {song.title}" 
                for i, song in enumerate(self.ctx.bot.queue)
            )
        
        await interaction.response.send_message(queue_list, ephemeral=True)

    @discord.ui.button(label="Shuffle", style=discord.ButtonStyle.secondary, emoji="🔀")
    async def shuffle(self, interaction: discord.Interaction, button: Button):
        await self.ctx.bot.get_command('shuffle').callback(self.ctx)
        await interaction.response.send_message("Queue shuffled!", ephemeral=True)

class FrequentCommandsMenu(Select):
    """Dropdown menu for frequently used commands"""
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Play Music",
                value="play",
                description="Play a song or add to queue"
            ),
            discord.SelectOption(
                label="Show Controls",
                value="controls",
                description="Display music control panel"
            ),
            discord.SelectOption(
                label="Shuffle Queue",
                value="shuffle",
                description="Shuffle the current queue"
            ),
            discord.SelectOption(
                label="Set Birthday",
                value="setbirthday",
                description="Set your birthday"
            ),
            discord.SelectOption(
                label="Upcoming Birthdays",
                value="upcoming_birthdays",
                description="Show upcoming birthdays"
            ),
            discord.SelectOption(
                label="Upcoming Holidays",
                value="next_holiday",
                description="Show upcoming Holidays"
            ),
        ]
        super().__init__(
            placeholder="Select a command",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        if self.values[0] == "play":
            await interaction.followup.send(
                "Please use `!play <song>` to play a song.",
                ephemeral=True
            )
        elif self.values[0] == "controls":
            await interaction.client.get_command('controls').callback(
                await interaction.client.get_context(interaction.message)
            )
        elif self.values[0] == "shuffle":
            await interaction.client.get_command('shuffle').callback(
                await interaction.client.get_context(interaction.message)
            )
        elif self.values[0] == "setbirthday":
            await interaction.followup.send(
                "Please use `!setbirthday MM-DD` to set your birthday.",
                ephemeral=True
            )
        elif self.values[0] == "upcoming_birthdays":
            await interaction.client.get_command('upcoming_birthdays').callback(
                await interaction.client.get_context(interaction.message)
            )
        elif self.values[0] == "next_holiday":
            await interaction.client.get_command('next_holiday').callback(
                await interaction.client.get_context(interaction.message)
            )

class FrequentCommandsView(View):
    """View containing the frequent commands menu"""
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(FrequentCommandsMenu())