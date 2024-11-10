

---

# Discord Music Bot

A Discord music bot built with Python and `discord.py` that allows users to play songs from YouTube, search for videos, and manage a song queue. The bot uses `yt_dlp` to extract and download audio from YouTube videos.

## Features

- Play music from a YouTube URL or search keyword.
- Display the current song with details like title, thumbnail, and duration.
- Skip the currently playing song.
- Display and manage a song queue.
- Display the currently playing song and source information.

## Requirements

- Python 3.8+
- A Discord bot token (you can create a bot and get a token from the [Discord Developer Portal](https://discord.com/developers/applications))
- `discord.py` and `yt_dlp` Python packages
- A `cookies.txt` file (optional but recommended, especially for age-restricted videos)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/miatoszs/Discord-py-Music-Bot
   cd Discord-py-Music-Bot
   ```

2. **Install required packages:**

   It's recommended to use a virtual environment.

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

   If you don't have a `requirements.txt`, create one with the following dependencies:

   ```plaintext
   discord.py
   yt-dlp
   ```

   Then, run:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Discord bot token:**

   Open the `bot.py` file (or whatever you named your bot file) and replace `YOUR_DISCORD_BOT_TOKEN` with your actual Discord bot token.

   ```python
   TOKEN = 'YOUR_DISCORD_BOT_TOKEN'
   ```

4. **Set up a `cookies.txt` file (optional but recommended):**

   Some YouTube videos, especially age-restricted or region-restricted content, require cookies to be accessed. To allow the bot to play such videos, you can provide a `cookies.txt` file.

   - **Download Cookies**: Use a browser extension like [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/oknfoidjnjfofmieeigfakfgkkkeffeb) (for Chrome) to export your YouTube cookies.
   - **Save the File**: Save the file as `cookies.txt` in the same folder as your bot script.
   - **Update the Code**: The bot is already configured to look for a `cookies.txt` file, so no further code changes are needed.

5. **Run the bot:**

   Make sure you’re in the virtual environment if you created one, then start the bot:

   ```bash
   python bot.py
   ```

## Usage

Once the bot is running and invited to your server, you can use the following commands in Discord:

### Commands

- **`/play <URL or keyword>`** - Plays a song from a YouTube URL or searches by keyword. If a song is already playing, it adds the song to the queue.

- **`/search <keyword>`** - Searches YouTube for videos and displays the top 5 results. React to the results with emojis to add a song to the queue.

- **`/skip`** - Skips the currently playing song.

- **`/queue`** - Displays the current song queue with song titles and links.

- **`/nowplaying`** - Shows the currently playing song with details like title, thumbnail, and duration.

- **`/stop`** - Stops the currently playing song and disconnects the bot from the voice channel.

- **`/help`** - Displays help information with a list of available commands.

## Example Usage

1. **Play a song by URL:**
   ```
   /play https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```

2. **Play a song by keyword:**
   ```
   /play Never Gonna Give You Up
   ```

3. **Search for a song:**
   ```
   /search Lofi hip hop
   ```

4. **View the current queue:**
   ```
   /queue
   ```

5. **Show the currently playing song:**
   ```
   /nowplaying
   ```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have suggestions or find any bugs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

### Notes

- The `cookies.txt` file is optional but recommended for unrestricted access to all YouTube videos.
- if you see this ```ERROR: [youtube] vDtfJ47QDi4: Sign in to confirm you’re not a bot. This helps protect our community. Learn more``` you need a cookie

