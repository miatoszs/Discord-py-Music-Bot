import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import re
import os

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

TOKEN = 'YOUR_DISCORD_BOT_TOKEN'  # Replace with your actual bot token
bot = commands.Bot(command_prefix="!", intents=intents)

# Global variables for queue and currently playing song
song_queue = []
current_song = None

# Regular expression to check if the input is a YouTube URL
YOUTUBE_URL_PATTERN = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')

# Emoji list for selecting songs from the search results and queue
emoji_numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

@bot.event
async def on_ready():
    await bot.tree.sync()  # Syncs the slash commands with Discord
    print(f'Bot {bot.user.name} has connected to Discord and slash commands are synced!')

@bot.tree.command(name="play", description="Plays a song from a YouTube URL or keyword.")
async def play(interaction: discord.Interaction, query: str):
    embed = discord.Embed(title="Play Command", description="Processing your request...", color=0x1E90FF)
    await interaction.response.send_message(embed=embed)

    if YOUTUBE_URL_PATTERN.match(query):
        song_queue.append({'title': query, 'url': query})
        embed.description = f"Added to queue: {query}"
        await interaction.edit_original_response(embed=embed)
    else:
        ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'nocheckcertificate': True}
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)
                top_result = info['entries'][0]
                song_queue.append({'title': top_result['title'], 'url': top_result['webpage_url']})
                embed.description = f"Added to queue: {top_result['title']}"
                await interaction.edit_original_response(embed=embed)
            except Exception as e:
                embed.description = "An error occurred while searching YouTube."
                await interaction.edit_original_response(embed=embed)
                print(e)
                return

    if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
        await play_next_song(interaction)

@bot.tree.command(name="skip", description="Skips the currently playing song.")
async def skip(interaction: discord.Interaction):
    embed = discord.Embed(title="Skip Command", color=0x1E90FF)
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        embed.description = "Song skipped."
    else:
        embed.description = "No song is currently playing."
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="search", description="Searches YouTube for videos based on a keyword.")
async def search(interaction: discord.Interaction, keyword: str):
    embed = discord.Embed(title="YouTube Search", description="Searching YouTube...", color=0x1E90FF)
    await interaction.response.send_message(embed=embed)

    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'nocheckcertificate': True}

    results = []
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch5:{keyword}", download=False)
            results = info['entries']
        except Exception as e:
            embed.description = "An error occurred while searching YouTube."
            await interaction.edit_original_response(embed=embed)
            print(e)
            return

    if not results:
        embed.description = "No results found."
        await interaction.edit_original_response(embed=embed)
        return

    embed = discord.Embed(title="YouTube Search Results", description=f"Results for: `{keyword}`", color=0x1E90FF)
    for i, result in enumerate(results):
        embed.add_field(name=f"{emoji_numbers[i]} {result['title']}", value=f"[Watch on YouTube]({result['webpage_url']})", inline=False)

    message = await interaction.edit_original_response(embed=embed)

    for i in range(len(results)):
        await message.add_reaction(emoji_numbers[i])

    def check_reaction(reaction, user):
        return (
            user == interaction.user and
            reaction.message.id == message.id and
            str(reaction.emoji) in emoji_numbers[:len(results)]
        )

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check_reaction)
        selected_index = emoji_numbers.index(str(reaction.emoji))
        selected_result = results[selected_index]

        song_queue.append({'title': selected_result['title'], 'url': selected_result['webpage_url']})
        embed.description = f"Added to queue: {selected_result['title']}"
        await interaction.edit_original_response(embed=embed)

        if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
            await play_next_song(interaction)
    except asyncio.TimeoutError:
        embed.description = "You didn't select a song in time. Please try again."
        await interaction.edit_original_response(embed=embed)

async def play_next_song(interaction):
    global current_song
    if song_queue:
        current_song = song_queue.pop(0)
        await play_selected_song(interaction, current_song['url'])
    else:
        current_song = None

async def play_selected_song(interaction, url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}],
        'outtmpl': 'song', 'quiet': True, 'nocheckcertificate': True
    }

    def _download():
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            current_song['title'] = info.get('title')
            current_song['url'] = info.get('webpage_url')
            current_song['thumbnail'] = info.get('thumbnail')  # Get thumbnail URL
            current_song['duration'] = info.get('duration')  # Duration in seconds

            ydl.download([url])  # Download the audio

    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, _download)
        
        if not os.path.exists("song.mp3"):
            embed = discord.Embed(title="Playback Error", description="Download failed. Could not find the audio file.", color=0xFF0000)
            await interaction.edit_original_response(embed=embed)
            return

        if not interaction.guild.voice_client:
            await interaction.user.voice.channel.connect()

        interaction.guild.voice_client.play(
            discord.FFmpegPCMAudio(os.path.abspath("song.mp3")),
            after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(interaction), bot.loop)
        )
    except youtube_dl.utils.ExtractorError as e:
        embed = discord.Embed(title="Playback Error", description="Unable to download the video. It may be age-restricted or require sign-in.", color=0xFF0000)
        await interaction.edit_original_response(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Playback Error", description="An error occurred during playback.", color=0xFF0000)
        await interaction.edit_original_response(embed=embed)
        print(e)

@bot.tree.command(name="stop", description="Stops the currently playing song and disconnects the bot")
async def stop(interaction: discord.Interaction):
    embed = discord.Embed(title="Stop Command", color=0x1E90FF)
    if interaction.guild.voice_client:
        interaction.guild.voice_client.stop()
        await interaction.guild.voice_client.disconnect()
        embed.description = "Music stopped and bot disconnected."
    else:
        embed.description = "I'm not in a voice channel."
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="queue", description="Displays the current song queue.")
async def queue(interaction: discord.Interaction):
    if song_queue:
        embed = discord.Embed(title="Current Song Queue", color=0x1E90FF)
        for i, song in enumerate(song_queue):
            embed.add_field(name=f"{emoji_numbers[i]} {song['title']}", value=f"[Watch on YouTube]({song['url']})", inline=False)
    else:
        embed = discord.Embed(title="Current Song Queue", description="The queue is currently empty.", color=0x1E90FF)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="nowplaying", description="Shows the currently playing song.")
async def nowplaying(interaction: discord.Interaction):
    if current_song:
        # Format duration in mm:ss
        duration_minutes = current_song['duration'] // 60
        duration_seconds = current_song['duration'] % 60
        duration_text = f"{duration_minutes:02}:{duration_seconds:02}"

        embed = discord.Embed(
            title="🎶 Now Playing",
            description=f"[{current_song['title']}]({current_song['url']})",
            color=0x1E90FF
        )
        
        embed.add_field(name="Source", value="YouTube", inline=True)
        embed.add_field(name="Duration", value=duration_text, inline=True)
        
        embed.set_thumbnail(url=current_song['thumbnail'])  # Set video thumbnail
        embed.set_footer(text="Requested by " + interaction.user.display_name, icon_url=interaction.user.avatar.url)

        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="Now Playing",
            description="No song is currently playing.",
            color=0x1E90FF
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Displays the help message with available commands.")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Help", description="Available Commands:", color=0x1E90FF)
    embed.add_field(name="/play <URL or keyword>", value="Plays a song from a YouTube URL or searches by keyword.", inline=False)
    embed.add_field(name="/skip", value="Skips the currently playing song.", inline=False)
    embed.add_field(name="/search <keyword>", value="Searches YouTube for videos and lets you select one to add to the queue.", inline=False)
    embed.add_field(name="/queue", value="Displays the current song queue.", inline=False)
    embed.add_field(name="/nowplaying", value="Shows the currently playing song.", inline=False)
    embed.add_field(name="/stop", value="Stops the current song and disconnects the bot.", inline=False)
    embed.add_field(name="/help", value="Displays this help message.", inline=False)
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
