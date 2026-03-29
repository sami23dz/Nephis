import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
# =======================
# CONFIG
# =======================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found or empty")
OWNER_ID = 1043552279665573929  # put your Discord ID here

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True
	
bot = commands.Bot(command_prefix="!", intents=intents)

# =======================
# GLOBAL STATE
# =======================
pending_action = {}
	
COLOR_MAP = {
    "crimson": discord.Color.from_rgb(220, 20, 60),
    "scarlet": discord.Color.from_rgb(255, 36, 0),
    "ruby": discord.Color.from_rgb(224, 17, 95),
    "burgundy": discord.Color.from_rgb(128, 0, 32),
    "wine": discord.Color.from_rgb(114, 47, 55),
    "coral": discord.Color.from_rgb(255, 127, 80),
    "salmon": discord.Color.from_rgb(250, 128, 114),
    "peach": discord.Color.from_rgb(255, 218, 185),
    "tangerine": discord.Color.from_rgb(255, 153, 51),
    "orange": discord.Color.from_rgb(255, 140, 0),
    "amber": discord.Color.from_rgb(255, 191, 0),
    "gold": discord.Color.from_rgb(212, 175, 55),
    "lemon": discord.Color.from_rgb(255, 250, 205),
    "olive": discord.Color.from_rgb(128, 128, 0),
    "forest": discord.Color.from_rgb(34, 139, 34),
    "emerald": discord.Color.from_rgb(80, 200, 120),
    "mint": discord.Color.from_rgb(152, 255, 152),
    "teal": discord.Color.from_rgb(0, 128, 128),
    "cyan": discord.Color.from_rgb(0, 255, 255),
    "azure": discord.Color.from_rgb(0, 127, 255),
    "sky": discord.Color.from_rgb(135, 206, 235),
    "cobalt": discord.Color.from_rgb(0, 71, 171),
    "navy": discord.Color.from_rgb(0, 0, 128),
    "indigo": discord.Color.from_rgb(75, 0, 130),
    "violet": discord.Color.from_rgb(138, 43, 226),
    "plum": discord.Color.from_rgb(142, 69, 133),
    "magenta": discord.Color.from_rgb(255, 0, 255),
    "rose": discord.Color.from_rgb(255, 102, 178),
    "pink": discord.Color.from_rgb(255, 105, 180),
    "lavender": discord.Color.from_rgb(181, 126, 220),
    "slate": discord.Color.from_rgb(112, 128, 144),
    "graphite": discord.Color.from_rgb(54, 69, 79),
    "charcoal": discord.Color.from_rgb(54, 69, 79),
    "silver": discord.Color.from_rgb(192, 192, 192),
    "ivory": discord.Color.from_rgb(255, 255, 240),
    "white": discord.Color.from_rgb(255, 255, 255),
    "black": discord.Color.from_rgb(15, 15, 15),
    "brown": discord.Color.from_rgb(139, 69, 19),
    "tan": discord.Color.from_rgb(210, 180, 140),
    "beige": discord.Color.from_rgb(245, 245, 220),
    "maroon": discord.Color.from_rgb(128, 0, 0),
    "turquoise": discord.Color.from_rgb(64, 224, 208),
    "sea": discord.Color.from_rgb(46, 139, 87),
    "midnight": discord.Color.from_rgb(25, 25, 112),
    "storm": discord.Color.from_rgb(72, 61, 139),
    "neon": discord.Color.from_rgb(57, 255, 20),
}

def is_owner(ctx):
    return ctx.author.id == OWNER_ID

def request_confirmation(user_id, action):
    pending_action[user_id] = action
    bot.loop.call_later(10, lambda: pending_action.pop(user_id, None))

def parse_color(text):
    if not text:
        return None

    key = text.strip().lower()
    if key in COLOR_MAP:
        return COLOR_MAP[key]
        
    if key.startswith("#"):
        key = key[1:]

    if len(key) == 6:
        try:
            return discord.Color(int(key, 16))
        except ValueError:
            return None

    return None

async def resolve_member(ctx, member_text):
    converter = commands.MemberConverter()
    return await converter.convert(ctx, member_text)

# =======================
# EVENTS
# =======================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="The bot is online"))

# =======================
# TEST COMMAND
# =======================
@bot.command(name="nephis")
async def nephis(ctx):
    await ctx.send("I'm here")
# =======================
# SAFE DELETE FRAMEWORK
# =======================
# I am not including the bulk wipe logic here.
# This is only the confirmation shell so you can extend it later in a controlled way.

@bot.command()
async def delroles(ctx):
    if not is_owner(ctx):
        return
    request_confirmation(ctx.author.id, "roles")
    await ctx.send("Type `!confirm` within 10 seconds to continue role cleanup.")

@bot.command()
async def delchannels(ctx):
    if not is_owner(ctx):
        return
    request_confirmation(ctx.author.id, "channels")
    await ctx.send("Type `!confirm` within 10 seconds to continue channel cleanup.")

@bot.command()
async def delcategories(ctx):
    if not is_owner(ctx):
        return
    request_confirmation(ctx.author.id, "categories")
    await ctx.send("Type `!confirm` within 10 seconds to continue category cleanup.")

@bot.command()
async def confirm(ctx):
    if not is_owner(ctx):
        return

    action = pending_action.get(ctx.author.id)
    if not action:
        await ctx.send("No pending action.")
        return

    pending_action.pop(ctx.author.id, None)

    if action == "roles":
        await ctx.send("Role cleanup hook reached. Add your own targeted cleanup here.")
    elif action == "channels":
        await ctx.send("Channel cleanup hook reached. Add your own targeted cleanup here.")
    elif action == "categories":
        await ctx.send("Category cleanup hook reached. Add your own targeted cleanup here.")
    else:
        await ctx.send("Unknown action.")

# =======================
# CREATE ROLE + GIVE IT + COLOR
# Syntax:
# !createrolegive Role Name | @person | color
# Example:
# !createrolegive Knight | @User | crimson
# !createrolegive Knight | @User | #ff44aa
# =======================
@bot.command()
async def giverole(ctx, *, raw):
    if not is_owner(ctx):
        return

    parts = [p.strip() for p in raw.split("-")]
    if len(parts) < 2:
        await ctx.send("Use: `!giverole Role Name - @person - color(optional)`")
        return

    role_name = parts[0]
    member_text = parts[1]
    color_text = parts[2] if len(parts) >= 3 else None

    try:
        member = await resolve_member(ctx, member_text)
    except Exception:
        await ctx.send("I couldn't find that person. Mention them directly.")
        return

    role = discord.utils.get(ctx.guild.roles, name=role_name)

    # ===== ROLE EXISTS → ONLY GIVE (NO EDIT) =====
    if role:
        if role >= ctx.guild.me.top_role:
            await ctx.send("I can't manage this role because it is above my top role.")
            return

        try:
            await member.add_roles(role, reason=f"Assigned by {ctx.author}")
            await ctx.send(f"Gave existing role `{role.name}` to {member.mention}.")
        except:
            await ctx.send("Failed to assign role.")
        return

    # ===== ROLE DOES NOT EXIST → CREATE =====
    color = parse_color(color_text) if color_text else None

    if color_text and color is None:
        await ctx.send("Invalid color. Use a name or hex like #ff44aa.")
        return

    try:
        role = await ctx.guild.create_role(
            name=role_name,
            color=color if color else discord.Color.default(),
            reason=f"Created by {ctx.author}"
        )
    except:
        await ctx.send("Failed to create role.")
        return

    try:
        await member.add_roles(role, reason=f"Assigned by {ctx.author}")
    except:
        await ctx.send("Role created but couldn't assign it.")
        return

    await ctx.send(f"Created role `{role.name}` and gave it to {member.mention}.")
# =======================
# MODIFY A ROLE THE PERSON ALREADY HAS
# Syntax:
# !customrole Existing Role | New Name | color
# New Name and color are both optional, but keep the separators.
# Examples:
# !customrole Knight | Elite Knight | neon
# !customrole Knight | Elite Knight | #ff44aa
# !customrole Knight | | crimson
# =======================
@bot.command()
async def customrole(ctx, *, raw):
    parts = [p.strip() for p in raw.split("-")]

    if len(parts) < 1 or not parts[0]:
        await ctx.send("Use: `!customrole Existing Role - New Name - color`")
        return

    role_name = parts[0]
    new_name = parts[1] if len(parts) >= 2 and parts[1] else None
    color_text = parts[2] if len(parts) >= 3 and parts[2] else None

    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        await ctx.send(f"Role `{role_name}` not found.")
        return

    if not is_owner(ctx) and role not in ctx.author.roles:
        await ctx.send("You need to already have that role.")
        return

    if role >= ctx.guild.me.top_role:
        await ctx.send("I can't edit that role because it is above my top role.")
        return

    color = parse_color(color_text) if color_text else None
    if color_text and color is None:
        await ctx.send("Invalid color. Use a name like `violet` or a hex code like `#ff44aa`.")
        return

    try:
        await role.edit(
            name=new_name if new_name else role.name,
            color=color if color else role.color,
            reason=f"Customized by {ctx.author}"
        )
    except discord.Forbidden:
        await ctx.send("I don't have permission to edit that role.")
        return
    except discord.HTTPException as e:
        await ctx.send(f"Failed to edit role: {e}")
        return

    msg = f"Role `{role_name}` updated"
    if new_name:
        msg += f" to `{new_name}`"
    if color:
        msg += f" with a new color"
    await ctx.send(msg + ".")
#=======================
#======================°
@bot.command()
async def colors(ctx):
    names = ", ".join(sorted(COLOR_MAP.keys()))
    await ctx.send(f"Available colors:\n{names}")
# =======================
# AUTO REPLIES (NO PREFIX)
# =======================

AUTO_REPLIES = {
    "nephis": "I'm here",
    "السلام عليكم": "•• ۆعلـِْ♡̨̐ـِْيگمَ آلسَـِْ♡̨̐ـِْلامَ••",
    "سلام عليكم": "•• ۆعلـِْ♡̨̐ـِْيگمَ آلسَـِْ♡̨̐ـِْلامَ••",
}

RESTRICTED_REPLIES = {
    "i love you": {
        1043552279665573929: "me too, sunny"
    },

    "hey": {
        1247268420739928125: "what do you want zoro",
        1043552279665573929: "Yes love?",
        984074589082640464: "What's up wael?"
    },
    "kiss me": {
        1043552279665573929: "Muah~"
    
    }

    # ===== INSTRUCTIONS =====
    # "trigger": {
    #     USER_ID: "response",
    #     USER_ID2: "another response"
    # }
}
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower().strip()

    # ===== RESTRICTED FIRST =====
    if content in RESTRICTED_REPLIES:
        user_map = RESTRICTED_REPLIES[content]

        if message.author.id in user_map:
            await message.channel.send(user_map[message.author.id])

        return  # stop here (important)

    # ===== PUBLIC =====
    if content in AUTO_REPLIES:
        await message.channel.send(AUTO_REPLIES[content])

    await bot.process_commands(message) #=======================
# RUN
# =======================
bot.run(TOKEN)