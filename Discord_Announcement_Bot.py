import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

ALLOWED_ROLE_NAME = "Security"

# Helper function to simulate bigger heading using bold full-width Unicode
def big_text(text: str):
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    fullwidth = "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９"
    table = str.maketrans(normal, fullwidth)
    return f"**{text.translate(table)}**"

@bot.tree.command(name="announce", description="Send an announcement with optional image upload.")
@app_commands.describe(
    role="The role to mention and DM members of.",
    channel="The channel to post the announcement in.",
    header="The main header of the announcement (simulated big font).",
    message="The announcement content.",
    image="Optional image file to attach."
)
async def announce(
    interaction: discord.Interaction,
    role: discord.Role,
    channel: discord.TextChannel,
    header: str,
    sub_header: str,
    message: str,
    game_link: str = None,
    vc_link: str = None,
    image: discord.Attachment = None
):
    # Check if user has allowed role
    if ALLOWED_ROLE_NAME not in [r.name for r in interaction.user.roles]:
        await interaction.response.send_message(
            f"❌ You must have the `{ALLOWED_ROLE_NAME}` role to use this command.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    # Combine header and message
    full_message= None

    if game_link and vc_link != None:
        full_message = f"{big_text(header)}\n{big_text(sub_header)}\n\n{message}\n\nGame:{game_link}\nVC:{vc_link}"
    elif game_link != None:
        full_message = f"{big_text(header)}\n{big_text(sub_header)}\n\n{message}\n\nGame:{game_link}"
    elif vc_link != None:
        full_message = f"{big_text(header)}\n{big_text(sub_header)}\n\n{message}\n\nVC:{vc_link}"
    else:
        full_message = f"{big_text(header)}\n{big_text(sub_header)}\n\n{message}"

    # 1️⃣ Send to public channel
    try:
        if image:
            await channel.send(content=f"{role.mention}\n{full_message}", file=await image.to_file())
        else:
            await channel.send(content=f"{role.mention}\n{full_message}")
    except discord.Forbidden:
        await interaction.followup.send(
            f"❌ I don’t have permission to send messages in {channel.mention}.",
            ephemeral=True
        )
        return

    # 2️⃣ DM each member with the role
    count = 0
    failed = []
    for member in role.members:
        if member.bot:
            continue
        try:
            if image:
                await member.send(content=full_message, file=await image.to_file())
            else:
                await member.send(content=full_message)
            count += 1
        except discord.Forbidden:
            failed.append(member.name)
            print(f"⚠️ Cannot DM {member.name} (DMs closed).")

    # 3️⃣ Feedback
    response_msg = f"✅ Announcement sent in {channel.mention} and DMed to **{count}** member(s) with role {role.mention}."
    if failed:
        response_msg += f"\n⚠️ Could not DM: {', '.join(failed)}"

    await interaction.followup.send(response_msg, ephemeral=True)

app = Flask(__name__)

@app.route('/')

def home():
    return "Bot is running", 200

def run_flask():
    app.run(host = "0.0.0.0", port = 8000)

bot.run(TOKEN)