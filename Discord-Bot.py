# Help Playlist Pytube: https://stackoverflow.com/questions/54710982/using-pytube-to-download-playlist-from-youtube

import json
import discord
from discord.ext import commands 
import yt_dlp as youtube_dl
from pytube import YouTube
import asyncio

# Pfad zur JSON-Datei
json_file = "Path from the config file"  

# JSON-Datei öffnen und Inhalte a
# uslesen
with open(json_file, "r") as file:
    data = json.load(file)

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)
chat = client.get_channel(data["chat"])
key = data["token"]

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-v'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename


@client.event
async def on_ready():
    #information
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    channel = client.get_channel(data["chat"])
    if channel:
        await channel.send("@everyone \n I am Online \n Commands: \n        !join \n        !leave \n        !play \n        !resume \n        !stop")

# Join voice channel
@client.command(pass_context = True)
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You are not in a voice channel, you most be in a voice channel to run this command!")

#Leave voice channel
@client.command(pass_context = True)
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("I left the voice channel")
    else:
        await ctx.send("I am not in a voice channel")

#Play Song       
@client.command(pass_context = True)
async def play(ctx,url):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        video = YouTube(url)
        stream = video.streams.filter(only_audio=True).first()
        audio = stream.download(filename=f"{video.title}.mp3")
        print(video.title)

        async with ctx.typing():
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=audio))
        await ctx.send('**Now playing:** {}'.format(video.title))
    except:
        await ctx.send("The bot is not connected to a voice channel.")

# Pause Song
@client.command(pass_context = True)
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
        
# resume song   
@client.command(pass_context = True)
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

#Stop song
@client.command(pass_context = True)
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

#Clear Chat
@client.command()
async def clear(ctx, amount=0):
  await ctx.channel.purge(limit=amount)

client.run(key)