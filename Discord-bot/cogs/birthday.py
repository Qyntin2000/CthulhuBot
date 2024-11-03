# cogs/birthday.py
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import sqlite3
from utils.database import Database

def is_admin_or_owner():
    async def predicate(ctx):
        # Check if user is the server owner
        if ctx.guild.owner_id == ctx.author.id:
            return True
        # Check if user has administrator permissions
        if ctx.author.guild_permissions.administrator:
            return True
        return False
    return commands.check(predicate)

class Birthday(commands.Cog):
    """Birthday commands and automatic notifications"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.birthday_check.start()
        self.role_manager.start()

    def cog_unload(self):
        """Cleanup when cog is unloaded"""
        self.birthday_check.cancel()
        self.role_manager.cancel()

    @commands.command()
    async def setbirthday(self, ctx, date: str):
        """Set your birthday (format: MM-DD)"""
        try:
            # Parse the date string
            birthday = datetime.strptime(date, "%m-%d")
            
            # Store in database
            self.db.store_birthday(ctx.author.id, birthday)
            
            # Send confirmation
            embed = discord.Embed(
                title="Birthday Set!",
                description=f"Your birthday has been set to {birthday.strftime('%B %d')}",
                color=discord.Color.green()
            )
            embed.set_footer(text="You will receive birthday wishes on your special day!")
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ Invalid date format. Please use MM-DD (e.g., 12-25 for December 25th)")

    @commands.command()
    @is_admin_or_owner()
    async def set_birthday_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the channel for birthday announcements
        
        Only server administrators and the server owner can use this command.
        """
        channel = channel or ctx.channel
        
        try:
            self.db.set_birthday_channel(ctx.guild.id, channel.id)
            
            embed = discord.Embed(
                title="Birthday Channel Set",
                description=f"Birthday announcements will be sent to {channel.mention}",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")

    @commands.command()
    @is_admin_or_owner()
    async def set_birthday_role(self, ctx, role: discord.Role):
        """Set the role to be given on birthdays
        
        Only server administrators and the server owner can use this command.
        """
        try:
            self.db.set_birthday_role(ctx.guild.id, role.id)
            
            embed = discord.Embed(
                title="Birthday Role Set",
                description=f"Birthday role set to {role.mention}",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Note",
                value="This role will be automatically assigned on members' birthdays"
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")

    @commands.command()
    async def upcoming_birthdays(self, ctx, days: int = 365):
        """Show upcoming birthdays within specified days"""
        if not 0 < days <= 365:
            return await ctx.send("❌ Please specify a number of days between 1 and 365.")

        upcoming = self.db.get_upcoming_birthdays(days)
        
        if not upcoming:
            return await ctx.send(f"No upcoming birthdays in the next {days} days.")

        embed = discord.Embed(
            title=f"🎂 Upcoming Birthdays (Next {days} days)",
            color=discord.Color.blue()
        )
        
        current_month = None
        today = datetime.now()
        
        for user_id, birthday in upcoming:
            user = ctx.guild.get_member(user_id)
            if user:
                # Calculate the next birthday occurrence
                next_birthday = birthday.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = birthday.replace(year=today.year + 1)
                
                # Calculate days until birthday
                days_until = (next_birthday - today).days
                date_str = birthday.strftime("%B %d")
                
                # Only show if within the requested range
                if days_until <= days:
                    # Group by month
                    month = next_birthday.strftime("%B")
                    if month != current_month:
                        current_month = month
                        embed.add_field(
                            name=f"\n{month}",
                            value="",
                            inline=False
                        )
                    
                    # Add birthday entry
                    if days_until == 0:
                        value = f"**Today!** 🎉"
                    elif days_until == 1:
                        value = f"**Tomorrow!** 🎈"
                    else:
                        value = f"In {days_until} days"
                        
                    embed.add_field(
                        name=user.display_name,
                        value=f"{date_str} ({value})",
                        inline=True
                    )

        if len(embed.fields) == 0:
            return await ctx.send(f"No upcoming birthdays in the next {days} days.")
            
        await ctx.send(embed=embed)

    @tasks.loop(hours=24)
    async def birthday_check(self):
        """Check for birthdays and send notifications"""
        today = datetime.now().strftime("%m-%d")
        birthday_users = self.db.get_todays_birthdays()

        for guild in self.bot.guilds:
            channel_id = self.db.get_birthday_channel(guild.id)
            if not channel_id:
                continue
                
            channel = guild.get_channel(channel_id)
            if not channel:
                continue

            for user_id in birthday_users:
                member = guild.get_member(user_id)
                if member:
                    embed = discord.Embed(
                        title="🎉 Happy Birthday!",
                        description=f"Everyone wish {member.mention} a happy birthday!",
                        color=discord.Color.gold()
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    
                    # Add a random birthday message
                    messages = [
                        "Hope your day is filled with joy and cake! 🎂",
                        "Another year of awesome! Have a great day! 🎈",
                        "Time to celebrate! Happy Birthday! 🎊",
                        "Wishing you the happiest of birthdays! 🎁",
                        "Have an amazing birthday celebration! 🎉"
                    ]
                    import random
                    embed.add_field(
                        name="Message",
                        value=random.choice(messages)
                    )
                    
                    await channel.send(embed=embed)

    @tasks.loop(hours=1)
    async def role_manager(self):
        """Manage birthday roles"""
        now = datetime.now()
        today = now.strftime("%m-%d")
        yesterday = (now - timedelta(days=1)).strftime("%m-%d")

        for guild in self.bot.guilds:
            role_id = self.db.get_birthday_role(guild.id)
            if not role_id:
                continue
                
            role = guild.get_role(role_id)
            if not role:
                continue

            # Remove role from yesterday's birthday users
            yesterday_birthdays = self.db.get_birthdays_for_date(yesterday)
            for user_id in yesterday_birthdays:
                member = guild.get_member(user_id)
                if member and role in member.roles:
                    try:
                        await member.remove_roles(role)
                    except discord.HTTPException:
                        continue

            # Add role to today's birthday users
            today_birthdays = self.db.get_birthdays_for_date(today)
            for user_id in today_birthdays:
                member = guild.get_member(user_id)
                if member and role not in member.roles:
                    try:
                        await member.add_roles(role)
                    except discord.HTTPException:
                        continue

    @birthday_check.before_loop
    @role_manager.before_loop
    async def before_loops(self):
        """Wait until the bot is ready before starting loops"""
        await self.bot.wait_until_ready()

async def setup(bot):
    """Setup function for loading the cog"""
    await bot.add_cog(Birthday(bot))