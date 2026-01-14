# Discord Wordle Rewind

This is a pair of scripts that allow you to extract people's wordle answers from a Discord text channel and generate Spotify Rewind style stats

# Examples
![Average Guesses Example](/examples/avg_guesses.png)
![Biggest Loser Example](/examples/biggest_losers.png)
![Streak Example](/examples/streak.png)
![Hardest Example](/examples/hardest.png)

# Usage
1. Create a [Discord Bot](https://discord.com/developers/applications) and invite it to your server.
2. Copy your bot's token and create a file `.env` and write `DISCORD_TOKEN="Paste Token Here"` in this directory.
3. Run `load_db.py`
4. In the discord channel that contains the Wordle messages, send a message that says `!load_db`
5. After its done, you can manually stop the bot.
6. Run `create_charts.py`
7. Look in output folder!