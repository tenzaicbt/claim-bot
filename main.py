import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
import re  # Importing the regex module for cleaning environment variable inputs

# Load environment variables from .env file
load_dotenv()

# Function to safely fetch and convert environment variables to integers
def safe_get_env_int(var_name):
    raw_value = os.getenv(var_name, "")
    if raw_value is None:
        print(f"Error: {var_name} is not set in the environment.")
        return None
    try:
        # Clean the value by removing any non-digit characters
        cleaned_value = re.sub("[^0-9]", "", raw_value)
        return int(cleaned_value)
    except ValueError:
        print(f"Error: {var_name} contains invalid characters or is not a valid integer.")
        return None

# Create bot instance with proper intents
intents = discord.Intents.default()
intents.message_content = True  # Enables content of messages to be read
intents.members = True  # Required for on_member_join event

bot = commands.Bot(command_prefix="/", intents=intents)

# Fetch channel IDs using the safe function
STATUS_CHANNEL_ID = safe_get_env_int('STATUS_CHANNEL_ID')  # Channel ID for logs
ROLE_ID = safe_get_env_int('ROLE_ID')  # Role ID
RULES_CHANNEL_ID = safe_get_env_int('RULES_CHANNEL_ID')  # Rules channel ID
TICKETS_CHANNEL_ID = safe_get_env_int('TICKETS_CHANNEL_ID')  # Tickets channel ID
ROLE_CLAIM_ID = safe_get_env_int('ROLE_CLAIM_ID')  # Mapping help channel ID

# Function to send logs to a specific channel
async def log_message(message: str):
    channel = bot.get_channel(STATUS_CHANNEL_ID)
    if channel:
        try:
            await channel.send(message)
            print(f"Log message sent to channel {STATUS_CHANNEL_ID}: {message}")
        except Exception as e:
            print(f"Failed to send log message: {e}")
    else:
        print(f"Channel with ID {STATUS_CHANNEL_ID} not found.")

# Function to send a welcome DM using an embed
async def send_welcome_dm(user: discord.User):
    embed = discord.Embed(
        title="Welcome to LordeFX",
        description=(
            f"Before doing anything, please read the <#{RULES_CHANNEL_ID}>.\n"
            f"To view all the maps, prices and purchase, please open Ticket <#{TICKETS_CHANNEL_ID}>.\n"
            f"Firstly, you need to verify and obtain the role .\n"
            f"Hope you enjoy your stay!"
        ),
        color=0xFFA500  # Orange color
    )
    embed.set_footer(text=f"LordeFX • {datetime.datetime.now():%d %b %Y %H:%M}")
    try:
        await user.send(embed=embed)
        print(f"Welcome embed message sent to {user}")
    except Exception as e:
        print(f"Failed to send welcome embed message to {user}: {e}")

# Slash command to claim roles
@bot.tree.command(name="claim", description="Manually claim your purchased product and get a role")
async def claim(interaction: discord.Interaction):
    user = interaction.user
    guild = interaction.guild

    # Simulating a verification process
    verified = True

    if verified:
        role = guild.get_role(ROLE_ID)
        if role:
            if role not in user.roles:
                await user.add_roles(role)
                response_message = f"Role `{role.name}` has been successfully assigned to you!"
                await interaction.response.send_message(response_message)
                await log_message(response_message)
            else:
                response_message = "You already have the role!"
                await interaction.response.send_message(response_message)
                await log_message(response_message)
        else:
            response_message = "Role not found."
            await interaction.response.send_message(response_message)
            await log_message(response_message)
    else:
        response_message = "You are not verified for this claim."
        await interaction.response.send_message(response_message)
        await log_message(response_message)

# Event to handle new member joining
@bot.event
async def on_member_join(member: discord.Member):
    await send_welcome_dm(member)

# Bot setup and run
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user} and slash commands synced.')
    # await log_message('Bot has started and is now online.')

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
