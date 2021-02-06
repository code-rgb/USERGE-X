"""Last FM"""

# Copyright (C) 2020 BY USERGE-X
# All rights reserved.
#
# Authors: 1. https://github.com/lostb053 [TG: @Lostb053]
#          2. https://github.com/code-rgb [TG: @DeletedUser420]
#
# API: https://www.last.fm/api


from userge import Config, Message, userge
from userge.utils import get_response, rand_array

API = "http://ws.audioscrobbler.com/2.0"

# In Case Song Does't have any Album Art.
PIC_URL = [
    "https://i.imgur.com/l772pcA.png",
    "https://i.imgur.com/KehK98D.png",
    "https://i.imgur.com/LuwSKeO.png",
    "https://i.imgur.com/EZ1S9cJ.png",
]


@userge.on_cmd(
    "lastfm",
    about={"header": "Get Lastfm now playing pic"},
)
async def last_fm_pic_(message: Message):
    """now playing"""
    await message.edit("<code>Getting info from last.fm ...</code>")
    if not await check_lastfmvar(message):
        return
    params = {
        "method": "user.getrecenttracks",
        "limit": 1,
        "extended": 1,
        "user": Config.LASTFM_USERNAME,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    try:
        view_data = await get_response.json(link=API, params=params)
    except ValueError:
        return await message.err("LastFm API is Down", del_in=5)
    if "error" in view_data:
        return await message.err(view_data["error"], del_in=5)
    recent_song = view_data["recenttracks"]["track"]
    if len(recent_song) == 0:
        return await message.err("No Recent Tracks found", del_in=5)
    rep = f"<b><a href=https://www.last.fm/user/{Config.LASTFM_USERNAME}>{Config.LASTFM_USERNAME}</a></b> is currently listening to:\n"
    song_ = recent_song[0]
    song_name = song_["name"]
    artist_name = song_["artist"]["name"]
    rep += f"🎧  <b><a href={song_['url']}>{song_name}</a></b> - <a href={song_['artist']['url']}>{artist_name}</a>"
    if song_["loved"] != "0":
        rep += " (♥️, loved)"
    # Trying to Fetch Album of the track
    params_ = {
        "method": "track.getInfo",
        "track": song_name,
        "artist": artist_name,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    try:
        view_data_ = await get_response.json(link=API, params=params_)
    except ValueError:
        return await message.err("LastFm API is Down", del_in=5)
    get_track = view_data_["track"]
    img = (
        (get_track["album"]["image"].pop())["#text"]
        if get_track.get("album")
        else rand_array(PIC_URL)
    )
    get_tags = "\n"
    # tags of the given track
    for tags in get_track["toptags"]["tag"]:
        get_tags += f"<a href={tags['url']}>#{tags['name']}</a>  "
    await message.edit(f"<a href={img}>\u200c</a>" + rep + get_tags, parse_mode="html")


@userge.on_cmd(
    "lastuser",
    about={
        "header": "Get Lastfm user info",
        "usage": "{tr}lastuser [lastfm username] (optional)",
    },
)
async def last_fm_user_info_(message: Message):
    """user info"""
    if not await check_lastfmvar(message):
        return
    lfmuser = message.input_str or Config.LASTFM_USERNAME
    await message.edit(f"<code>Getting info about last.fm User: {lfmuser}</code> ...")
    params = {
        "method": "user.getInfo",
        "user": lfmuser,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    try:
        view_data = await get_response.json(link=API, params=params)
    except ValueError:
        return await message.err("LastFm API is Down", del_in=5)
    if "error" in view_data:
        return await message.err(view_data["error"], del_in=5)
    lastuser = view_data["user"]
    if lastuser["gender"] == "m":
        gender = "🙎‍♂️ "
    elif lastuser["gender"] == "f":
        gender = "🙍‍♀️ "
    else:
        gender = "👤 "
    lastimg = lastuser["image"].pop() if len(lastuser["image"]) != 0 else None
    age = lastuser["age"]
    playlist = lastuser["playlists"]
    subscriber = lastuser["subscriber"]
    result = ""
    if lastimg:
        result += f"<a href={lastimg['#text']}>\u200c</a>"
    result += f"<b>LastFM User Info for <a href={lastuser['url']}>{lfmuser}</a></b>:\n"
    result += f" {gender}<b>Name:</b> {lastuser['realname']}\n"
    if age != "0":
        result += f" 🎂 <b>Age:</b> {age}\n"
    result += f" 🎵 <b>Total Scrobbles:</b> {lastuser['playcount']}\n"
    result += f" 🌍 <b>Country:</b> {lastuser['country']}\n"
    if playlist != "0":
        result += f" ▶️ <b>Playlists:</b> {playlist}\n"
    if subscriber != "0":
        result += f" ⭐️ <b>Subscriber:</b> {subscriber}"
    await message.edit(result, parse_mode="html")


@userge.on_cmd(
    "lastlove",
    about={
        "header": "Get Lastfm Loved Tracks",
        "usage": "{tr}lastlove [lastfm username] (optional)",
    },
)
async def last_fm_loved_tracks_(message: Message):
    """liked songs"""
    if not await check_lastfmvar(message):
        return
    user_ = message.input_str or Config.LASTFM_USERNAME
    await message.edit(f"♥️<code> Fetching favourite tracks of {user_} ...</code>")
    params = {
        "method": "user.getlovedtracks",
        "limit": 30,
        "page": 1,
        "user": user_,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    try:
        view_data = await get_response.json(link=API, params=params)
    except ValueError:
        return await message.err("LastFm API is Down", del_in=5)
    tracks = view_data["lovedtracks"]["track"]
    if "error" in view_data:
        return await message.err(view_data["error"], del_in=5)
    if len(tracks) == 0:
        return await message.edit("You Don't have any Loved tracks yet.")

    rep = f"♥️ <b>Favourite Tracks of <a href=https://www.last.fm/user/{user_}>{user_}'s</a></b>"
    for count, song_ in enumerate(tracks, start=1):
        song_name = song_["name"]
        artist_name = song_["artist"]["name"]
        rep += f"\n{count:02d}. 🎧  <b><a href={song_['url']}>{song_name}</a></b> - <a href={song_['artist']['url']}>{artist_name}</a>"
    await message.edit(rep, disable_web_page_preview=True, parse_mode="html")


@userge.on_cmd(
    "lastplayed",
    about={
        "header": "Get recently played LastFm Songs",
        "usage": "{tr}lastplayed [lastFM username] (optional)",
    },
)
async def last_fm_played_(message: Message):
    """recently played songs"""
    await message.edit(
        "<code> 🎵 Fetching recently played songs from last.fm ...</code>"
    )
    if not await check_lastfmvar(message):
        return
    user_ = message.input_str or Config.LASTFM_USERNAME
    params = {
        "method": "user.getrecenttracks",
        "limit": 30,
        "extended": 1,
        "user": user_,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    try:
        view_data = await get_response.json(link=API, params=params)
    except ValueError:
        return await message.err("LastFm API is Down", del_in=5)
    if "error" in view_data:
        return await message.err(view_data["error"], del_in=5)
    recent_song = view_data["recenttracks"]["track"]
    if len(recent_song) == 0:
        return await message.err("No Recent Tracks found", del_in=5)
    rep = f"<b><a href=https://www.last.fm/user/{user_}>{user_}'s</a></b> recently played songs:"
    for count, song_ in enumerate(recent_song, start=1):
        song_name = song_["name"]
        artist_name = song_["artist"]["name"]
        rep += f"\n{count:02d}. 🎧  <b><a href={song_['url']}>{song_name}</a></b> - <a href={song_['artist']['url']}>{artist_name}</a>"
        if song_["loved"] != "0":
            rep += " ♥️"
    await message.edit(rep, disable_web_page_preview=True, parse_mode="html")


async def check_lastfmvar(message: Message):
    if hasattr(Config, "LASTFM_API_KEY") and (
        Config.LASTFM_API_KEY and Config.LASTFM_USERNAME
    ):
        return True
    await message.edit(
        "**LastFm Config Vars not found !\n See [Guide](https://code-rgb.gitbook.io/userge-x/setting-up-environment-variables/extra-vars/lastfm_api_key-and-lastfm_user) for more info.**"
    )
    return False
