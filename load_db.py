import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
from database import Database
from wordle import Wordle
load_dotenv()

year = 2025
start = datetime.datetime(year - 1, 12, 31)
end = datetime.datetime(year + 1, 1, 1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
database = Database("database.db")

def is_wordle_message(text: str) -> bool:
    return text.startswith("Wordle ") and len(text.splitlines()) >= 3 and (
        "⬛" in text or
        "🟨" in text or
        "🟩" in text or
        "⬜" in text
    )

@bot.command()
async def load_db(ctx: commands.Context):
    await ctx.message.delete()
    print(f"Loading messages from {ctx.channel.name} into db...")
    guild = await bot.fetch_guild(ctx.guild.id)
    user_ids = []
    count = 0
    async for message in ctx.channel.history(after=start, before=end, limit=None):
        if not is_wordle_message(message.content):
            continue
        print(message.content)
        wordle = Wordle(message.content)
        database.input_wordle(message.author.id, wordle)
        if message.author.id not in user_ids:
            try:
                member = await guild.fetch_member(message.author.id)
            except:
                member = message.author
            database.input_user(member.id, message.author.display_name, getattr(member, "nick", None), member.display_avatar.url, member.color.value)
            user_ids.append(member.id)
        count += 1
        print(count)
    database.commit()
    database.remove_less_than_twenty()
    print("Done!")

bot.run(os.environ.get("DISCORD_TOKEN"))