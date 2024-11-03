# cogs/holiday.py
import discord
from discord.ext import commands, tasks
from datetime import datetime, date, timedelta
from typing import Optional, Tuple, Dict
from config.constants import HOLIDAYS
from utils.database import Database

class Holiday(commands.Cog):
    """Holiday commands and automatic notifications"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.check_holidays.start()
        self.last_triggered = {}

    def cog_unload(self):
        """Cleanup when cog is unloaded"""
        self.check_holidays.cancel()

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def set_holiday_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the channel for holiday announcements"""
        channel = channel or ctx.channel
        
        try:
            self.db.set_holiday_channel(ctx.guild.id, channel.id)
            
            embed = discord.Embed(
                title="Holiday Channel Set",
                description=f"Holiday announcements will now be sent to {channel.mention}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")

    def get_holiday_channel(self, guild_id: int) -> Optional[int]:
        """Get the configured holiday announcement channel for a guild"""
        return self.db.get_holiday_channel(guild_id)

    def get_next_holiday(self) -> Tuple[str, date]:
        """Get the next upcoming holiday"""
        today = date.today()
        next_holiday = None
        days_until = 366  # Max days to look ahead

        for holiday, date_tuple in HOLIDAYS.items():
            # Create a date object for this year
            holiday_date = date(today.year, date_tuple[0], date_tuple[1])
            
            # If the holiday has already passed this year, use next year's date
            if holiday_date < today:
                holiday_date = date(today.year + 1, date_tuple[0], date_tuple[1])
            
            delta = (holiday_date - today).days
            
            if delta < days_until:
                next_holiday = (holiday, holiday_date)
                days_until = delta

        return next_holiday

    @commands.command(name='next_holiday')
    async def next_holiday(self, ctx):
        """Show the next upcoming holiday"""
        holiday, holiday_date = self.get_next_holiday()
        days_until = (holiday_date - date.today()).days

        embed = discord.Embed(
            title="🎉 Next Holiday",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="Holiday",
            value=holiday,
            inline=False
        )
        
        embed.add_field(
            name="Date",
            value=holiday_date.strftime("%B %d, %Y"),
            inline=True
        )
        
        embed.add_field(
            name="Days Until",
            value=f"{days_until} days",
            inline=True
        )

        holiday_emojis = {
            "Christmas": "🎄",
            "Thanksgiving": "🦃",
            "Halloween": "🎃",
            "New Year's Day": "🎊",
            "Valentine's Day": "❤️",
            "St. Patrick's Day": "☘️",
            "Easter": "🐰",
            "Mother's Day": "💐",
            "Father's Day": "👔",
            "Independence Day": "🎆",
            "New Year's Eve": "✨",
            "Christmas Eve": "🎄"
        }
        
        if holiday in holiday_emojis:
            embed.description = f"{holiday_emojis[holiday]} {holiday_emojis[holiday]} {holiday_emojis[holiday]}"

        await ctx.send(embed=embed)

    @tasks.loop(hours=5)
    async def check_holidays(self):
        """Check for holidays and send notifications"""
        today = date.today()
        
        for holiday, holiday_date in HOLIDAYS.items():
            if today.month == holiday_date[0] and today.day == holiday_date[1]:
                if holiday not in self.last_triggered or self.last_triggered[holiday] != today:
                    for guild in self.bot.guilds:
                        try:
                            # Try to get the configured holiday channel
                            channel_id = self.get_holiday_channel(guild.id)
                            if channel_id:
                                channel = guild.get_channel(channel_id)
                            else:
                                # Try to find the general channel
                                channel = discord.utils.get(guild.text_channels, name='general')
                                
                            # If still no channel found, use system channel as last resort
                            if not channel:
                                channel = guild.system_channel
                            
                            if channel and channel.permissions_for(guild.me).send_messages:
                                embed = discord.Embed(
                                    title=f"Happy {holiday}! 🎉",
                                    description=self._get_holiday_message(holiday),
                                    color=self._get_holiday_color(holiday)
                                )
                                self._customize_holiday_embed(embed, holiday)
                                await channel.send(embed=embed)
                                
                        except Exception as e:
                            print(f"Error sending holiday message in guild {guild.name}: {e}")
                            continue

                    self.last_triggered[holiday] = today

    @commands.command()
    async def holiday_channel(self, ctx):
        """Show the current holiday announcement channel"""
        channel_id = self.get_holiday_channel(ctx.guild.id)
        if channel_id:
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                await ctx.send(f"Holiday announcements are being sent to {channel.mention}")
            else:
                await ctx.send("The configured holiday channel no longer exists. "
                             "Please set a new one with `!set_holiday_channel`")
        else:
            await ctx.send("No holiday channel has been set. "
                         "Announcements will be sent to the general channel if available, "
                         "or the system channel as a fallback. "
                         "Use `!set_holiday_channel #channel` to set a specific channel.")

    def _get_holiday_message(self, holiday: str) -> str:
        """Get a custom message for each holiday"""
        messages = {
            "Christmas": "🎄 Wishing everyone a Merry Christmas! May your day be filled with joy and celebration! 🎁",
            "Thanksgiving": "🦃 Happy Thanksgiving! Time to gather with loved ones and give thanks! 🍽️",
            "Halloween": "🎃 Happy Halloween! Have a spooktacular time! 👻",
            "New Year's Day": "🎊 Happy New Year! Here's to new beginnings and amazing adventures ahead! 🎉",
            "Valentine's Day": "❤️ Happy Valentine's Day! Spread love and joy! 💝",
            "St. Patrick's Day": "☘️ Happy St. Patrick's Day! May the luck of the Irish be with you! 🍀",
            "Easter": "🐰 Happy Easter! Hope your day is filled with joy and chocolate! 🥚",
            "Mother's Day": "💐 Happy Mother's Day to all the amazing moms out there! 🌸",
            "Father's Day": "👔 Happy Father's Day to all the wonderful dads! 🎉",
            "Independence Day": "🎆 Happy Independence Day! Celebrate freedom! 🇺🇸",
            "New Year's Eve": "✨ Happy New Year's Eve! Ready to welcome the new year! 🎊",
            "Christmas Eve": "🎄 Merry Christmas Eve! The magic of Christmas is in the air! 🎅"
        }
        return messages.get(holiday, f"Happy {holiday} everyone! 🎉")

    def _get_holiday_color(self, holiday: str) -> discord.Color:
        """Get a themed color for each holiday"""
        colors = {
            "Christmas": discord.Color.red(),
            "Thanksgiving": discord.Color.orange(),
            "Halloween": discord.Color.purple(),
            "New Year's Day": discord.Color.blue(),
            "Valentine's Day": discord.Color.from_rgb(255, 192, 203),  # Pink
            "St. Patrick's Day": discord.Color.green(),
            "Easter": discord.Color.from_rgb(255, 223, 196),  # Pastel Orange
            "Independence Day": discord.Color.blue(),
            "New Year's Eve": discord.Color.gold()
        }
        return colors.get(holiday, discord.Color.gold())

    def _customize_holiday_embed(self, embed: discord.Embed, holiday: str):
        """Add holiday-specific customization to embeds"""
        customizations = {
            "Christmas": {
                "name": "🎄 Season's Greetings! 🎄",
                "value": "May your holiday be filled with warmth and cheer!"
            },
            "Thanksgiving": {
                "name": "🦃 Time for Thanks 🦃",
                "value": "Grateful for our wonderful community!"
            },
            "Halloween": {
                "name": "🎃 Trick or Treat! 🎃",
                "value": "Have a safe and spooky Halloween!"
            },
            "New Year's Day": {
                "name": "🎊 New Beginnings 🎊",
                "value": "May this year bring you success and happiness!"
            },
            "Valentine's Day": {
                "name": "❤️ Love is in the Air ❤️",
                "value": "Spreading love and joy to everyone!"
            },
            "Easter": {
                "name": "🐰 Easter Joy 🐰",
                "value": "Hop into spring with joy and renewal!"
            },
            "Independence Day": {
                "name": "🎆 Celebrate Freedom 🎆",
                "value": "United in celebration of our independence!"
            }
        }
        
        if holiday in customizations:
            embed.add_field(
                name=customizations[holiday]["name"],
                value=customizations[holiday]["value"]
            )

    @check_holidays.before_loop
    async def before_check_holidays(self):
        """Wait until the bot is ready before starting the holiday check loop"""
        await self.bot.wait_until_ready()

async def setup(bot):
    """Setup function for loading the cog"""
    await bot.add_cog(Holiday(bot))