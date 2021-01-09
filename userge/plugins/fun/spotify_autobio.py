"""Module to display Currenty Playing Spotify Songs in your bio"""


#  CREDITS:
# [Poolitzer](https://t.me/poolitzer)  (for creating spotify bio plugin)
#
# [Sunny](https://t.me/medevilofxd) and Others for spotify_userbot
# (https://github.com/anilchauhanxda/spotify_userbot/blob/master/bot.py)
#
#  Github.com/code-rgb [ TG - @DetetedUser420 ]
#  Ported it to Pyrogram and improved Heroku compatiblilty


import asyncio
import json
import os
import time

import requests
from pyrogram.errors import AboutTooLong, FloodWait

from userge import Config, Message, get_collection, userge
from userge.utils.spotify import Database

SPOTIFY_DB = get_collection("SPOTIFY_DB")
SAVED_SETTINGS = get_collection("CONFIGS")
LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)
USER_INITIAL_BIO = {}


KEY = "🎶"
BIOS = [
    KEY + " Vibing ; {interpret} - {title} {progress}/{duration}",
    KEY + " Vibing : {interpret} - {title}",
    KEY + " : {interpret} - {title}",
    KEY + " Vibing : {title}",
    KEY + " : {title}",
]
OFFSET = 1
# reduce the OFFSET from our actual 70 character limit
LIMIT = 70 - OFFSET


if (
    Config.SPOTIFY_CLIENT_ID
    and Config.SPOTIFY_CLIENT_SECRET
    and Config.SPOTIFY_INITIAL_TOKEN
):

    async def _init() -> None:
        global database
        data = await SAVED_SETTINGS.find_one({"_id": "SPOTIFY_MODE"})
        if data:
            Config.SPOTIFY_MODE = bool(data["is_active"])
        if not os.path.exists("./userge/xcache/spotify_database.json"):
            await spotify_db_loader()
            await asyncio.sleep(5)
            database = Database()

    @userge.on_cmd(
        "spotify_bio",
        about={"header": "enable / disable Spotify Bio"},
        allow_channels=False,
    )
    async def spotify_bio_(message: Message):
        """Toggle Spotify BIO"""
        if Config.SPOTIFY_MODE:
            Config.SPOTIFY_MODE = False
            if USER_INITIAL_BIO:
                await userge.update_profile(bio=USER_INITIAL_BIO["bio"])
                USER_INITIAL_BIO.clear()
            await message.edit(" `Spotify Bio disabled !`", del_in=3)
        else:
            await message.edit(
                "✅ `Spotify Bio enabled` \nCurrent Spotify playback will updated in BIO",
                del_in=5,
            )
            USER_INITIAL_BIO["bio"] = (
                await userge.get_chat((await userge.get_me()).id)
            ).bio or ""
            Config.SPOTIFY_MODE = True
            await spotify_biox()
        await SAVED_SETTINGS.update_one(
            {"_id": "SPOTIFY_MODE"},
            {"$set": {"is_active": Config.SPOTIFY_MODE}},
            upsert=True,
        )

    def ms_converter(millis):
        millis = int(millis)
        seconds = (millis / 1000) % 60
        seconds = int(seconds)
        if str(seconds) == "0":
            seconds = "00"
        if len(str(seconds)) == 1:
            seconds = "0" + str(seconds)
        minutes = (millis / (1000 * 60)) % 60
        minutes = int(minutes)
        return str(minutes) + ":" + str(seconds)

    async def spotify_db_loader():
        sdb = await SPOTIFY_DB.find_one({"_id": "SPOTIFY_DB"})
        if sdb:
            sdb_msgid = sdb["database_id"]
            sdb_get = await userge.get_messages(Config.LOG_CHANNEL_ID, int(sdb_msgid))
            await userge.download_media(
                sdb_get.document, file_name="userge/xcache/spotify_database.json"
            )

        else:
            body = {
                "client_id": Config.SPOTIFY_CLIENT_ID,
                "client_secret": Config.SPOTIFY_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": "https://example.com/callback",
                "code": Config.SPOTIFY_INITIAL_TOKEN,
            }
            r = requests.post("https://accounts.spotify.com/api/token", data=body)
            save = r.json()
            try:
                to_create = {
                    "bio": "",
                    "access_token": save["access_token"],
                    "refresh_token": save["refresh_token"],
                    "telegram_spam": False,
                    "spotify_spam": False,
                }
                with open("./userge/xcache/spotify_database.json", "w+") as outfile:
                    json.dump(to_create, outfile, indent=4, sort_keys=True)
            except KeyError:
                await CHANNEL.log("SPOTIFY_INITIAL_TOKEN expired recreate one")
            except FileNotFoundError:
                await CHANNEL.log("Database not found")
            else:
                s_database = await userge.send_document(
                    Config.LOG_CHANNEL_ID,
                    "userge/xcache/spotify_database.json",
                    disable_notification=True,
                    caption="#SPOTIFY_DB Don't Delete",
                )
                await SPOTIFY_DB.update_one(
                    {"_id": "SPOTIFY_DB"},
                    {"$set": {"database_id": s_database.message_id}},
                    upsert=True,
                )

    # to stop unwanted spam, we sent these type of message only once. So we have a variable in our database which we check
    # for in return_info. When we send a message, we set this variable to true. After a successful update
    # (or a closing of spotify), we reset that variable to false.

    def save_spam(which, what):
        global database
        # see below why

        # this is if False is inserted, so if spam = False, so if everything is good.
        if not what:
            # if it wasn't normal before, we proceed
            if database.return_spam(which):
                # we save that it is normal now
                database.save_spam(which, False)
                # we return True so we can test against it and if it this function returns, we can send a fitting message
                return True
        # this is if True is inserted, so if spam = True, so if something went wrong
        else:
            # if it was normal before, we proceed
            if not database.return_spam(which):
                # we save that it is not normal now
                database.save_spam(which, True)
                # we return True so we can send a message
                return True
        # if True wasn't returned before, we can return False now so our test fails and we dont send a message
        return False

    async def spotify_biox():
        global database
        while Config.SPOTIFY_MODE:
            # SPOTIFY
            skip = False
            to_insert = {}
            oauth = {"Authorization": "Bearer " + database.return_token()}
            r = requests.get(
                "https://api.spotify.com/v1/me/player/currently-playing", headers=oauth
            )
            # 200 means user plays smth
            if r.status_code == 200:
                received = r.json()
                if received["currently_playing_type"] == "track":
                    to_insert["title"] = received["item"]["name"]
                    to_insert["progress"] = ms_converter(received["progress_ms"])
                    to_insert["interpret"] = received["item"]["artists"][0]["name"]
                    to_insert["duration"] = ms_converter(
                        received["item"]["duration_ms"]
                    )
                    to_insert["link"] = received["item"]["external_urls"]["spotify"]
                    to_insert["image"] = received["item"]["album"]["images"][1]["url"]
                    if save_spam("spotify", False):
                        stringy = (
                            "**[INFO]**\n\nEverything returned back to normal, the previous spotify issue has been "
                            "resolved."
                        )
                        await CHANNEL.log(stringy)

                else:
                    if save_spam("spotify", True):
                        # currently item is not passed when the user plays a podcast
                        string = (
                            f"**[INFO]**\n\nThe playback {received['currently_playing_type']}"
                            " didn't gave me any additional information, so I skipped updating the bio."
                        )
                        await CHANNEL.log(string)

            # 429 means flood limit, we need to wait
            elif r.status_code == 429:
                to_wait = r.headers["Retry-After"]
                LOG.error(f"Spotify, have to wait for {str(to_wait)}")
                await CHANNEL.log(
                    "**[WARNING]**\n\nI caught a spotify api limit. I shall sleep for "
                    f"{str(to_wait)} seconds until I refresh again"
                )
                skip = True
                await asyncio.sleep(int(to_wait))
            # 204 means user plays nothing, since to_insert is false, we dont need to change anything
            elif r.status_code == 204:
                if save_spam("spotify", False):
                    stringy = (
                        "**[INFO]**\n\nEverything returned back to normal, the previous spotify issue has been "
                        "resolved."
                    )
                    await CHANNEL.log(stringy)
            # 401 means our access token is expired, so we need to refresh it
            elif r.status_code == 401:
                data = {
                    "client_id": Config.SPOTIFY_CLIENT_ID,
                    "client_secret": Config.SPOTIFY_CLIENT_SECRET,
                    "grant_type": "refresh_token",
                    "refresh_token": database.return_refresh(),
                }
                r = requests.post("https://accounts.spotify.com/api/token", data=data)
                received = r.json()
                # if a new refresh is token as well, we save it here
                try:
                    database.save_refresh(received["refresh_token"])
                except KeyError:
                    pass
                database.save_token(received["access_token"])
                # since we didnt actually update our status yet, lets do this without the 30 seconds wait
                skip = True
            # 502 means bad gateway, its an issue on spotify site which we can do nothing about. 30 seconds wait shouldn't
            # put too much pressure on the spotify server, so we are just going to notify the user once

            elif r.status_code == 502:
                if save_spam("spotify", True):
                    string = (
                        "**[WARNING]**\n\nSpotify returned a Bad gateway, which means they have a problem on their "
                        "servers. The bot will continue to run but may not update the bio for a short time."
                    )
                    await CHANNEL.log(string)
            # 503 means service unavailable, its an issue on spotify site which we can do nothing about. 30 seconds wait
            # shouldn't put too much pressure on the spotify server, so we are just going to notify the user once
            elif r.status_code == 503:
                if save_spam("spotify", True):
                    string = (
                        "**[WARNING]**\n\nSpotify said that the service is unavailable, which means they have a "
                        "problem on their servers. The bot will continue to run but may not update the bio for a "
                        "short time."
                    )
                    await CHANNEL.log(string)
            # 404 is a spotify error which isn't supposed to happen (since our URL is correct). Track the issue here:
            # https://github.com/spotify/web-api/issues/1280
            elif r.status_code == 404:
                if save_spam("spotify", True):
                    string = "**[INFO]**\n\nSpotify returned a 404 error, which is a bug on their side."
                    await CHANNEL.log(string)
            # catch anything else
            else:
                await CHANNEL.log(
                    "**[ERROR]**\n\nOK, so something went reeeally wrong with spotify. The bot "
                    "was stopped.\nStatus code: "
                    + str(r.status_code)
                    + "\n\nText: "
                    + r.text
                )
                LOG.error(f"Spotify, error {str(r.status_code)}, text: {r.text}")
                # stop the whole program since I dont know what happens here and this is the safest thing we can do
                Config.SPOTIFY_MODE = False  # TODO check this
            # TELEGRAM
            try:
                # full needed, since we dont get a bio with the normal request
                full = await userge.get_chat((await userge.get_me()).id)
                bio = full.bio
                # to_insert means we have a successful playback
                if to_insert:
                    # putting our collected information's into nice variables

                    title = to_insert["title"]
                    interpret = to_insert["interpret"]
                    progress = to_insert["progress"]
                    duration = to_insert["duration"]
                    spotify_biox.interpret = to_insert["interpret"]
                    spotify_biox.progress = to_insert["progress"]
                    spotify_biox.duration = to_insert["duration"]
                    spotify_biox.title = to_insert["title"]
                    spotify_biox.link = to_insert["link"]
                    spotify_biox.image = to_insert["image"]
                    # we need this variable to see if actually one of the BIOS is below the character limit
                    new_bio = ""
                    for bio in BIOS:
                        temp = bio.format(
                            title=title,
                            interpret=interpret,
                            progress=progress,
                            duration=duration,
                        )
                        # we try to not ignore for telegrams character limit here

                        if len(temp) < LIMIT:
                            # this is short enough, so we put it in the variable and break our for loop
                            new_bio = temp
                            break
                    # if we have a bio, one bio was short enough
                    if new_bio:
                        # test if the user changed his bio to blank, we save it before we override
                        if not bio:
                            database.save_bio(bio)
                        # test if the user changed his bio in the meantime, if yes, we save it before we override
                        elif "🎶" not in bio:
                            database.save_bio(bio)
                        # test if the bio isn't the same, otherwise updating it would be stupid
                        if not new_bio == bio:
                            try:
                                await userge.update_profile(bio=new_bio)
                                spotify_biox.lrt = time.time()

                                if save_spam("telegram", False):
                                    stringy = (
                                        "**[INFO]**\n\nEverything returned back to normal, the previous telegram "
                                        "issue has been resolved."
                                    )
                                    await CHANNEL.log(stringy)
                            # this can happen if our LIMIT check failed because telegram counts emojis twice and python
                            # doesnt. Refer to the constants file to learn more about this
                            except AboutTooLong:
                                if save_spam("telegram", True):
                                    stringy = (
                                        "**[WARNING]**\n\nThe biography I tried to insert was too long. In order "
                                        "to not let that happen again in the future, please read the part about OFFSET "
                                        f"in the constants. Anyway, here is the bio I tried to insert:\n\n{new_bio}"
                                    )
                                    await CHANNEL.log(stringy)
                    # if we dont have a bio, everything was too long, so we tell the user that
                    if not new_bio:
                        if save_spam("telegram", True):
                            to_send = (
                                "**[INFO]**\n\nThe current track exceeded the character limit, so the bio wasn't "
                                f"updated.\n\n Track: {title}\nInterpret: {interpret}"
                            )
                            await CHANNEL.log(to_send)
                # not to_insert means no playback
                else:
                    if save_spam("telegram", False):
                        stringy = (
                            "**[INFO]**\n\nEverything returned back to normal, the previous telegram issue has "
                            "been resolved."
                        )
                        await CHANNEL.log(stringy)
                    old_bio = database.return_bio()
                    # this means the bio is blank, so we save that as the new one
                    if not bio:
                        database.save_bio(bio)
                    # this means an old playback is in the bio, so we change it back to the original one
                    elif "🎶" in bio:
                        await userge.update_profile(bio=database.return_bio())

                    # this means a new original is there, lets save it
                    elif not bio == old_bio:
                        database.save_bio(bio)
                    # this means the original one we saved is still valid
                    else:
                        pass
            except FloodWait as e:
                to_wait = e.seconds
                LOG.error(f"to wait for {str(to_wait)}")
                await CHANNEL.log(
                    "**[WARNING]**\n\nI caught a telegram api limit. I shall sleep "
                    f"{str(to_wait)} seconds until I refresh again"
                )
                skip = True
                await asyncio.sleep(int(to_wait))
            # skip means a flood error stopped the whole program, no need to wait another 30 seconds after that
            if not skip:
                await asyncio.sleep(30)

    @userge.on_cmd("now_playing", about={"header": "Now Playing Spotify Song"})
    async def now_playing_(message: Message):
        """Spotify Now Playing"""
        global database
        oauth = {"Authorization": "Bearer " + database.return_token()}
        r = requests.get(
            "https://api.spotify.com/v1/me/player/currently-playing", headers=oauth
        )
        if r.status_code == 204:
            spolink = "\n**I'm not listening anything right now :)**"
        else:
            spolink = f"🎶 Vibing ; [{spotify_biox.title}]({spotify_biox.link}) - {spotify_biox.interpret}"

        await message.edit(spolink)

    @userge.on_cmd("sp_info", about={"header": "Get Info about Your Songs and Device"})
    async def sp_info_(message: Message):
        """Spotify Device Info"""
        global database
        # =====================================GET_204=====================================================#
        oauth = {"Authorization": "Bearer " + database.return_token()}
        getplay = requests.get(
            "https://api.spotify.com/v1/me/player/currently-playing", headers=oauth
        )

        # =====================================GET_DEVICE_INFO==============================================#
        device = requests.get(
            "https://api.spotify.com/v1/me/player/devices", headers=oauth
        )

        # =====================================GET_FIVE_RECETLY_PLAYED_SONGS=================================#
        oauth = {"Authorization": "Bearer " + database.return_token()}
        recetly_pl = requests.get(
            "https://api.spotify.com/v1/me/player/recently-played?type=track&limit=5",
            headers=oauth,
        )
        if getplay.status_code == 204:
            status_pn = "\n**I'm not listening anything right now :)**"
        else:
            # ==========START_RECETLY_FIVE_SONGS_EXTRATIONS============================================================#
            recent_play = recetly_pl.json()
            get_rec = recent_play["items"]
            for for_rec in get_rec:
                track = for_rec["track"]
                get_name = track["name"]
                with open("status_recent_played_song.txt", "a") as sf:
                    sf.write("• __" + get_name + "__" + "\n")
            with open("status_recent_played_song.txt", "r+") as f:
                recent_p = f.read()
                f.truncate(0)
            device_info = device.json()
            g_dlist = device_info["devices"][0]
            device_name = g_dlist["name"]
            device_type = g_dlist["type"]
            device_vol = g_dlist["volume_percent"]
            # ==================PLAYING_SONGS_INFO=======================================#
            currently_playing_song = f"{spotify_biox.title} - {spotify_biox.interpret}"
            currently_playing_song_dur = (
                f"{spotify_biox.progress}/{spotify_biox.duration}"
            )
            # ==================ASSINGING_VAR_VLAUE=======================================#
            status_pn = f"""
        **Device name:** {device_name} ({device_type}) 
        **Device volume:** {device_vol}% 
        **Currently playing song:** {currently_playing_song} 
        **Duration:** {currently_playing_song_dur} 
        **Recently played songs:** \n{recent_p}"""

        await message.edit(status_pn)

    @userge.on_cmd("sp_profile", about={"header": "Get Your Spotify Account Info"})
    async def sp_profile_(message: Message):
        """Spotify Profile"""
        global database
        oauth = {"Authorization": "Bearer " + database.return_token()}
        me = requests.get("https://api.spotify.com/v1/me", headers=oauth)
        a_me = me.json()
        name = a_me["display_name"]
        country = a_me["country"] if hasattr(a_me, "country") else ""
        me_img = a_me["images"][0]["url"] if hasattr(a_me, "images") else ""
        me_url = a_me["external_urls"]["spotify"]
        profile_text = (
            f"**Spotify name**: [{name}]({me_img})\n**Profile link:** [here]({me_url})"
        )
        if country:
            profile_text += f"\n**Country:** {country}"
        await message.edit(profile_text)

    @userge.on_cmd("sp_recents", about={"header": "Get Recently Played Spotify Songs"})
    async def sp_recents_(message: Message):
        """Spotify Recent Songs"""
        global database
        oauth = {"Authorization": "Bearer " + database.return_token()}
        await message.edit("`Getting recent played songs...`")
        r = requests.get(
            "https://api.spotify.com/v1/me/player/recently-played", headers=oauth
        )
        recent_play = r.json()
        get_rec = recent_play["items"]
        recent = "🎵 **Recently played songs:**\n"
        for for_rec in get_rec:
            track = for_rec["track"]
            get_name = track["name"]
            ex_link = track["external_urls"]
            get_link = ex_link["spotify"]
            recent += "• [" + get_name + "]" + "(" + get_link + ")" + "\n"
        await message.edit(recent, disable_web_page_preview=True)
