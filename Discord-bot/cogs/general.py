# cogs/general.py
import discord
from discord.ext import commands
from utils.views import FrequentCommandsView
from typing import Optional
from datetime import datetime
from config.constants import HELP_TEXT, ERROR_MESSAGES
import traceback
import sys

class General(commands.Cog):
    """General commands and event handlers"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the bot is ready"""
        print(f'Logged in as {self.bot.user.name} (ID: {self.bot.user.id})')
        print('------')
        
        # Set custom status
        activity = discord.Activity(
            type=discord.ActivityType.competing,
            name="a music contest"
        )
        await self.bot.change_presence(activity=activity)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
            
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                ERROR_MESSAGES['no_permission']
            )
            return
            
        if isinstance(error, commands.CheckAnyFailure):
            await ctx.send(
                ERROR_MESSAGES['admin_only']
            )
            return
            
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                ERROR_MESSAGES['check_failure']
            )
            return
            
        if isinstance(error, commands.BadArgument):
            await ctx.send(
                f"❌ Bad argument: {str(error)}\n"
                "Please check the command usage with `!help`"
            )
            return
            
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"❌ Missing required argument: {error.param.name}\n"
                "Please check the command usage with `!help`"
            )
            return

        # Log unexpected errors
        print('Ignoring exception in command {}:'.format(ctx.command), 
              file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Welcome new members"""
        # Send welcome message in system channel
        if member.guild.system_channel:
            embed = discord.Embed(
                title="Welcome!",
                description=f"Welcome to the server, {member.mention}! 🎉",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(
                name="Getting Started",
                value="Check out our channels and don't forget to read the rules!"
            )
            await member.guild.system_channel.send(embed=embed)
        
        # Send private welcome message
        try:
            embed = discord.Embed(
                title=f"Welcome to {member.guild.name}!",
                description="We're glad to have you here! 👋",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Need Help?",
                value="Feel free to ask questions in the server!",
                inline=False
            )
            embed.add_field(
                name="Useful Commands",
                value="Use `!help` to see available commands",
                inline=False
            )
            await member.send(embed=embed)
        except discord.Forbidden:
            # User has DMs disabled
            pass

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle message events"""
        # Ignore messages from bots
        if message.author.bot:
            return

        # Handle specific messages
        if message.content == "!":
            await message.channel.send(HELP_TEXT)
            return

        # Custom responses
        responses = {
            "!hello": "Hello! 👋",
            "!vaporclub": "https://open.spotify.com/playlist/52cc4UPXBRFBHcrPFLbckf?si=90bff350651f4626",
            "!invite": "https://discord.gg/sRmsVRNNRv"
        }
        
        if message.content in responses:
            await message.channel.send(responses[message.content])

    @commands.command()
    async def ping(self, ctx):
        """Check bot's latency"""
        latency = round(self.bot.latency * 1000)  # Convert to ms
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: {latency}ms",
            color=discord.Color.green() if latency < 100 else discord.Color.orange()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def serverinfo(self, ctx):
        """Display server information"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"📊 {guild.name} Server Information",
            color=discord.Color.blue()
        )
        
        # Server icon
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # General information
        embed.add_field(
            name="Owner",
            value=guild.owner.mention,
            inline=True
        )
        embed.add_field(
            name="Created On",
            value=guild.created_at.strftime("%B %d, %Y"),
            inline=True
        )
        embed.add_field(
            name="Server ID",
            value=guild.id,
            inline=True
        )
        
        # Member counts
        total_members = len(guild.members)
        bot_count = len([m for m in guild.members if m.bot])
        human_count = total_members - bot_count
        
        embed.add_field(
            name="Members",
            value=f"👥 Total: {total_members}\n"
                  f"👤 Humans: {human_count}\n"
                  f"🤖 Bots: {bot_count}",
            inline=True
        )
        
        # Channel counts
        channels = guild.channels
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(
            name="Channels",
            value=f"📝 Text: {text_channels}\n"
                  f"🔊 Voice: {voice_channels}\n"
                  f"📁 Categories: {categories}",
            inline=True
        )
        
        # Role count
        embed.add_field(
            name="Roles",
            value=str(len(guild.roles) - 1),  # Subtract @everyone role
            inline=True
        )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        """Display user information"""
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"👤 User Information: {member.name}",
            color=member.color
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Basic information
        embed.add_field(
            name="User ID",
            value=member.id,
            inline=True
        )
        embed.add_field(
            name="Nickname",
            value=member.nick or "None",
            inline=True
        )
        
        # Dates
        embed.add_field(
            name="Account Created",
            value=member.created_at.strftime("%B %d, %Y"),
            inline=True
        )
        embed.add_field(
            name="Joined Server",
            value=member.joined_at.strftime("%B %d, %Y"),
            inline=True
        )
        
        # Roles
        roles = [role.mention for role in reversed(member.roles[1:])]  # Exclude @everyone
        embed.add_field(
            name=f"Roles [{len(roles)}]",
            value=" ".join(roles) or "No roles",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='help')
    async def help_command(self, ctx, command: str = None):
        """Show help information"""
        if command is None:
            await ctx.send(HELP_TEXT)
            return

        cmd = self.bot.get_command(command)
        if cmd is None:
            await ctx.send(f"❌ Command `{command}` not found.")
            return

        embed = discord.Embed(
            title=f"Help: {cmd.name}",
            description=cmd.help or "No description available.",
            color=discord.Color.blue()
        )
        
        if cmd.aliases:
            embed.add_field(
                name="Aliases",
                value=", ".join(cmd.aliases),
                inline=False
            )
            
        usage = f"{ctx.prefix}{cmd.name}"
        if cmd.signature:
            usage += f" {cmd.signature}"
        embed.add_field(
            name="Usage",
            value=f"`{usage}`",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def menu(self, ctx):
        """Display the frequent commands menu"""
        view = FrequentCommandsView()
        embed = discord.Embed(
            title="Frequently Used Commands",
            description="Select a command from the menu below:",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    """Setup function for loading the cog"""
    await bot.add_cog(General(bot))