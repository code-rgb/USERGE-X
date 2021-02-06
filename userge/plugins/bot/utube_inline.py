import glob
import os
from pathlib import Path
from time import time
from urllib.parse import parse_qs, urlparse

import ujson
import youtube_dl
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from wget import download
from youtube_dl.utils import DownloadError

from userge import Config, Message, pool, userge
from userge.utils import (
    check_owner,
    get_file_id,
    get_response,
    humanbytes,
    post_to_telegraph,
    sublists,
    xbot,
    xmedia,
)

from ..misc.upload import upload

LOGGER = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)
BASE_YT_URL = "https://www.youtube.com/watch?v="
PATH = "./userge/xcache/ytsearch.json"


class YT_Search_X:
    def __init__(self):
        if not os.path.exists(PATH):
            d = {}
            ujson.dump(d, open(PATH, "w"))
        self.db = ujson.load(open(PATH))

    def store_(self, rnd_id: str, results: dict):
        self.db[rnd_id] = results
        self.save()

    def save(self):
        with open(PATH, "w") as outfile:
            ujson.dump(self.db, outfile, indent=4)


ytsearch_data = YT_Search_X()


async def get_ytthumb(videoid: str):
    thumb_quality = [
        "maxresdefault.jpg",  # Best quality
        "hqdefault.jpg",
        "sddefault.jpg",
        "mqdefault.jpg",
        "default.jpg",  # Worst quality
    ]

    thumb_link = "https://i.imgur.com/4LwPLai.png"
    for qualiy in thumb_quality:
        link = f"https://i.ytimg.com/vi/{videoid}/{qualiy}"
        if await get_response.status(link) == 200:
            thumb_link = link
            break
    return thumb_link


@userge.on_cmd(
    "iytdl",
    about={
        "header": "ytdl with inline buttons",
        "usage": "{tr}iytdl [URL / Text] or [Reply to URL / Text]",
    },
)
async def iytdl_inline(message: Message):
    reply = message.reply_to_message
    input_url = None
    if message.input_str:
        input_url = message.input_str
    elif reply:
        if reply.text:
            input_url = reply.text
        elif reply.caption:
            input_url = reply.caption

    if not input_url:
        return await message.err("Input or reply to a valid youtube URL", del_in=5)
    await message.edit(f"🔎 Searching Youtube for: <code>'{input_url}'</code>")
    bot = await userge.bot.get_me()
    x = await userge.get_inline_bot_results(bot.username, f"ytdl {input_url.strip()}")
    await message.delete()
    await userge.send_inline_bot_result(
        chat_id=message.chat.id, query_id=x.query_id, result_id=x.results[0].id
    )


if userge.has_bot:

    @userge.bot.on_callback_query(
        filters.regex(pattern=r"^ytdl_download_(.*)_([\d]+|best)(?:_(a|v))?")
    )
    @check_owner
    async def ytdl_download_callback(c_q: CallbackQuery):
        yt_code = c_q.matches[0].group(1)
        choice_id = c_q.matches[0].group(2)
        if str(choice_id).isdigit():
            choice_id = int(choice_id)
            if choice_id == 0:
                await c_q.answer("🔄  Processing...", show_alert=False)
                await xbot.edit_inline_reply_markup(
                    c_q.inline_message_id, reply_markup=(await download_button(yt_code))
                )
                return
        else:
            choice_id = None

        startTime = time()
        downtype = c_q.matches[0].group(3)
        media_type = "Video" if downtype == "v" else "Audio"
        callback_continue = f"Downloading {media_type} Please Wait..."
        callback_continue += f"\n\nFormat Code : {choice_id or 'bestaudio/best'}"
        await c_q.answer(callback_continue, show_alert=True)
        upload_msg = await userge.send_message(Config.LOG_CHANNEL_ID, "Uploading...")
        yt_url = BASE_YT_URL + yt_code
        await xbot.edit_inline_caption(
            c_q.inline_message_id,
            caption=(
                f"**⬇️ Downloading {media_type} ...**"
                f"\n\n🔗  [<b>Link</b>]({yt_url})\n🆔  <b>Format Code</b> : {choice_id or 'bestaudio/best'}"
            ),
        )
        if downtype == "v":
            retcode = await _tubeDl(url=yt_url, starttime=startTime, uid=choice_id)
        else:
            retcode = await _mp3Dl(url=yt_url, starttime=startTime, uid=choice_id)
        if retcode != 0:
            return await upload_msg.edit(str(retcode))
        _fpath = ""
        for _path in glob.glob(os.path.join(Config.DOWN_PATH, str(startTime), "*")):
            if not _path.lower().endswith((".jpg", ".png", ".webp")):
                _fpath = _path
        if not _fpath:
            await upload_msg.err("nothing found !")
            return
        thumb_ = str(download(await get_ytthumb(yt_code))) if downtype == "v" else None
        uploaded_media = await upload(
            upload_msg,
            Path(_fpath),
            logvid=False,
            custom_thumb=thumb_,
            inline_id=c_q.inline_message_id,
        )
        refresh_vid = await userge.bot.get_messages(
            Config.LOG_CHANNEL_ID, uploaded_media.message_id
        )
        f_id = get_file_id(refresh_vid)
        if downtype == "v":
            await xbot.edit_inline_media(
                c_q.inline_message_id,
                media=(
                    await xmedia.InputMediaVideo(
                        file_id=f_id,
                        caption=f"📹  <b>[{uploaded_media.caption}]({yt_url})</b>",
                    )
                ),
            )
        else:  # Audio
            await xbot.edit_inline_media(
                c_q.inline_message_id,
                media=(
                    await xmedia.InputMediaAudio(
                        file_id=f_id,
                        caption=f"🎵  <b>[{uploaded_media.caption}]({yt_url})</b>",
                    )
                ),
            )

    @userge.bot.on_callback_query(
        filters.regex(pattern=r"^ytdl_(listall|back|next|detail)_([a-z0-9]+)_(.*)")
    )
    @check_owner
    async def ytdl_callback(c_q: CallbackQuery):
        choosen_btn = c_q.matches[0].group(1)
        data_key = c_q.matches[0].group(2)
        page = c_q.matches[0].group(3)
        if os.path.exists(PATH):
            with open(PATH) as f:
                view_data = ujson.load(f)
            search_data = view_data.get(data_key)
            total = len(search_data)
        else:
            return await c_q.answer(
                "Search data doesn't exists anymore, please perform search again ...",
                show_alert=True,
            )
        if choosen_btn == "back":
            index = int(page) - 1
            del_back = index == 1
            await c_q.answer()
            back_vid = search_data.get(str(index))
            await xbot.edit_inline_media(
                c_q.inline_message_id,
                media=(
                    await xmedia.InputMediaPhoto(
                        file_id=back_vid.get("thumb"),
                        caption=back_vid.get("message"),
                    )
                ),
                reply_markup=yt_search_btns(
                    del_back=del_back,
                    data_key=data_key,
                    page=index,
                    vid=back_vid.get("video_id"),
                    total=total,
                ),
            )
        elif choosen_btn == "next":
            index = int(page) + 1
            if index > total:
                return await c_q.answer("That's All Folks !", show_alert=True)
            await c_q.answer()
            front_vid = search_data.get(str(index))
            await xbot.edit_inline_media(
                c_q.inline_message_id,
                media=(
                    await xmedia.InputMediaPhoto(
                        file_id=front_vid.get("thumb"),
                        caption=front_vid.get("message"),
                    )
                ),
                reply_markup=yt_search_btns(
                    data_key=data_key,
                    page=index,
                    vid=front_vid.get("video_id"),
                    total=total,
                ),
            )

        elif choosen_btn == "listall":
            await c_q.answer("View Changed to:  📜  List", show_alert=False)
            list_res = ""
            for vid_s in search_data:
                list_res += search_data.get(vid_s).get("list_view")
            telegraph = post_to_telegraph(
                a_title=f"Showing {total} youtube video results for the given query ...",
                content=list_res,
            )
            await xbot.edit_inline_media(
                c_q.inline_message_id,
                media=(
                    await xmedia.InputMediaPhoto(
                        file_id=search_data.get("1").get("thumb"),
                        # caption=f"<b>[Click to view]({})</b>",
                    )
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "↗️  Click To Open",
                                url=telegraph,
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "📰  Detailed View",
                                callback_data=f"ytdl_detail_{data_key}_{page}",
                            )
                        ],
                    ]
                ),
            )

        else:  # Detailed
            index = 1
            await c_q.answer("View Changed to:  📰  Detailed", show_alert=False)
            first = search_data.get(str(index))
            await xbot.edit_inline_media(
                c_q.inline_message_id,
                media=(
                    await xmedia.InputMediaPhoto(
                        file_id=first.get("thumb"),
                        caption=first.get("message"),
                    )
                ),
                reply_markup=yt_search_btns(
                    del_back=True,
                    data_key=data_key,
                    page=index,
                    vid=first.get("video_id"),
                    total=total,
                ),
            )


@pool.run_in_thread
def _tubeDl(url: str, starttime, uid=None):
    ydl_opts = {
        "addmetadata": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "outtmpl": os.path.join(
            Config.DOWN_PATH, str(starttime), "%(title)s-%(format)s.%(ext)s"
        ),
        "logger": LOGGER,
        "format": "{}+bestaudio/best".format(uid or "bestvideo"),
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "postprocessors": [
            {"key": "FFmpegMetadata"}
            # ERROR R15: Memory quota vastly exceeded
            # {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
        ],
        "quiet": True,
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            x = ydl.download([url])
    except DownloadError as e:
        CHANNEL.log(str(e))
    else:
        return x


@pool.run_in_thread
def _mp3Dl(url: str, starttime, uid):
    _opts = {
        "outtmpl": os.path.join(Config.DOWN_PATH, str(starttime), "%(title)s.%(ext)s"),
        "logger": LOGGER,
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "format": "bestaudio/best",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": str(uid),
            },
            {"key": "EmbedThumbnail"},  # ERROR: Conversion failed!
            {"key": "FFmpegMetadata"},
        ],
        "quiet": True,
    }
    try:
        with youtube_dl.YoutubeDL(_opts) as ytdl:
            dloader = ytdl.download([url])
    except Exception as y_e:
        LOGGER.exception(y_e)
        return y_e
    else:
        return dloader


#  initial version: http://stackoverflow.com/a/7936523/617185 \
#  by Mikhail Kashkin (http://stackoverflow.com/users/85739/mikhail-kashkin)
#
# Returns Video_ID extracting from the given url of Youtube
# Examples of URLs:
#     Valid:
#     'http://youtu.be/_lOT2p_FCvA',
#     'www.youtube.com/watch?v=_lOT2p_FCvA&feature=feedu',
#     'http://www.youtube.com/embed/_lOT2p_FCvA',
#     'http://www.youtube.com/v/_lOT2p_FCvA?version=3&amp;hl=en_US',
#     'https://www.youtube.com/watch?v=rTHlyTphWP0&index=6&list=PLjeDyYvG6-40qawYNR4juzvSOg-ezZ2a6',
#     'youtube.com/watch?v=_lOT2p_FCvA',
#
#     Invalid:
#     'youtu.be/watch?v=_lOT2p_FCvA'


def get_yt_video_id(url: str):
    if url.startswith(("youtu", "www")):
        url = "http://" + url
    yt_link = None
    try:
        query = urlparse(url)
        if "youtube" in query.hostname:
            if query.path == "/watch":
                yt_link = parse_qs(query.query)["v"][0]
            if query.path.startswith(("/embed/", "/v/")):
                yt_link = query.path.split("/")[2]
        elif "youtu.be" in query.hostname:
            yt_link = query.path[1:]
    except TypeError:
        pass
    return yt_link


async def result_formatter(results: list):
    output = {}
    for index, r in enumerate(results, start=1):
        thumb = (r.get("thumbnails").pop()).get("url")
        upld = r.get("channel")
        title = f'<a href={r.get("link")}><b>{r.get("title")}</b></a>\n'
        out = title
        if r.get("descriptionSnippet"):
            out += "<code>{}</code>\n\n".format(
                "".join(x.get("text") for x in r.get("descriptionSnippet"))
            )
        out += f'<b>❯  Duration:</b> {r.get("accessibility").get("duration")}\n'
        views = f'<b>❯  Views:</b> {r.get("viewCount").get("short")}\n'
        out += views
        out += f'<b>❯  Upload date:</b> {r.get("publishedTime")}\n'
        if upld:
            out += "<b>❯  Uploader:</b> "
            out += f'<a href={upld.get("link")}>{upld.get("name")}</a>'
        output[index] = dict(
            message=out,
            thumb=thumb,
            video_id=r.get("id"),
            list_view=f'<img src={thumb}><b><a href={r.get("link")}>{index}. {r.get("accessibility").get("title")}</a></b><br><br>',
        )
    return output


def yt_search_btns(
    data_key: str, page: int, vid: str, total: int, del_back: bool = False
):
    buttons = [
        [
            InlineKeyboardButton(
                text="⬅️  Back",
                callback_data=f"ytdl_back_{data_key}_{page}",
            ),
            InlineKeyboardButton(
                text=f"{page} / {total}",
                callback_data=f"ytdl_next_{data_key}_{page}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📜  List all",
                callback_data=f"ytdl_listall_{data_key}_{page}",
            ),
            InlineKeyboardButton(
                text="⬇️  Download",
                callback_data=f"ytdl_download_{vid}_0",
            ),
        ],
    ]
    if del_back:
        buttons[0].pop(0)
    return InlineKeyboardMarkup(buttons)


@pool.run_in_thread
def download_button(vid: str, body: bool = False):
    x = youtube_dl.YoutubeDL({"no-playlist": True}).extract_info(
        BASE_YT_URL + vid, download=False
    )
    ###
    (
        format_144,
        format_240,
        format_360,
        format_720,
        format_1080,
        format_1440,
        format_2160,
    ) = [0 for _ in range(7)]
    btn = [
        [
            InlineKeyboardButton(
                "⭐️  BEST (Video + Audio)", callback_data=f"ytdl_download_{vid}_best_v"
            )
        ]
    ]
    audio, format_data = {}, {}
    ###
    for video in x["formats"]:
        if video.get("ext") == "mp4":
            f_note = video.get("format_note")
            fr_id = int(video.get("format_id"))
            if f_note in ("2160p", "2160p60") and fr_id > format_2160:
                format_2160 = fr_id
            if f_note in ("1440p", "1440p60") and fr_id > format_1440:
                format_1440 = fr_id
            if f_note in ("1080p", "1080p60") and fr_id > format_1080:
                format_1080 = fr_id
            if f_note in ("720p", "720p60") and fr_id > format_720:
                format_720 = fr_id
            if f_note in ("360p", "360p60") and fr_id > format_360:
                format_360 = fr_id
            if f_note in ("240p", "240p60") and fr_id > format_240:
                format_240 = fr_id
            if f_note in ("144p", "144p60") and fr_id > format_144:
                format_144 = fr_id
            format_data[
                fr_id
            ] = f'📹 {f_note} ({humanbytes(video.get("filesize")) or "N/A"})'

        if video.get("acodec") != "none":
            bitrrate = int(video.get("abr"))
            # if bitrrate >= 70:
            audio[
                bitrrate
            ] = f'🎵 {bitrrate}Kbps ({humanbytes(video.get("filesize")) or "N/A"})'

    btn += sublists(
        [
            InlineKeyboardButton(
                format_data.get(qual_), callback_data=f"ytdl_download_{vid}_{qual_}_v"
            )
            for qual_ in [
                format_144,
                format_240,
                format_360,
                format_720,
                format_1080,
                format_1440,
                format_2160,
            ]
            if qual_ != 0
        ],
        width=2,
    )
    btn += sublists(
        [
            InlineKeyboardButton(
                audio.get(key_), callback_data=f"ytdl_download_{vid}_{key_}_a"
            )
            for key_ in sorted(audio.keys())
        ],
        width=2,
    )
    if body:
        vid_body = f"<b>[{x.get('title')}]({x.get('webpage_url')})</b>"

        # ERROR Media Caption Too Long
        # <code>{x.get("description")}</code>
        # ❯  <b>Duration:</b> {x.get('duration')}
        # ❯  <b>Views:</b> {x.get('view_count')}
        # ❯  <b>Upload date:</b> {x.get('upload_date')}
        # ❯  <b>Uploader:</b> [{x.get('uploader')}]({x.get('uploader_url')})

        return vid_body, InlineKeyboardMarkup(btn)
    return InlineKeyboardMarkup(btn)
