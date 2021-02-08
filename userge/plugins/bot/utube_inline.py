""" Download Youtube Video/ Audio in a User friendly interface """
# -------------------------- #
# Modded ytdl by code-rgb
# -------------------------- #

import glob
import os
from collections import defaultdict
from pathlib import Path
from re import search
from time import time

import ujson
import youtube_dl
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaPhoto,
    InputMediaVideo,
)
from wget import download
from youtube_dl.utils import DownloadError
from youtubesearchpython import VideosSearch

from userge import Config, Message, pool, userge
from userge.utils import (
    check_owner,
    get_file_id,
    get_response,
    humanbytes,
    post_to_telegraph,
    rand_key,
    sublists,
)

from ..misc.upload import upload

LOGGER = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)
BASE_YT_URL = "https://www.youtube.com/watch?v="
YOUTUBE_REGEX = r"(?:(?:https?:)?\/\/)?(?:(?:www|m)\.)?(?:(?:youtube\.com|youtu.be))(?:\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(?:\S+)?"
PATH = "./userge/xcache/ytsearch.json"


class YT_Search_X:
    def __init__(self):
        if not os.path.exists(PATH):
            with open(PATH, "w") as f_x:
                ujson.dump({}, f_x)
        with open(PATH) as yt_db:
            self.db = ujson.load(yt_db)

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
    input_url = input_url.strip()
    if message.client.is_bot:
        link = get_yt_video_id(input_url)
        if link is None:
            search_ = VideosSearch(input_url, limit=15)
            resp = (search_.result()).get("result")
            if len(resp) == 0:
                await message.err(f'No Results found for "{input_url}"', del_in=7)
                return
            outdata = await result_formatter(resp)
            key_ = rand_key()
            ytsearch_data.store_(key_, outdata)
            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"1 / {len(outdata)}",
                            callback_data=f"ytdl_next_{key_}_1",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="📜  List all",
                            callback_data=f"ytdl_listall_{key_}_1",
                        ),
                        InlineKeyboardButton(
                            text="⬇️  Download",
                            callback_data=f'ytdl_download_{outdata[1]["video_id"]}_0',
                        ),
                    ],
                ]
            )
            caption = outdata[1]["message"]
            photo = outdata[1]["thumb"]
        else:
            caption, buttons = await download_button(link, body=True)
            photo = await get_ytthumb(link)

        await userge.bot.send_photo(
            message.chat.id,
            photo=photo,
            caption=caption,
            reply_markup=buttons,
        )
        await message.delete()
    else:
        bot = await userge.bot.get_me()
        x = await userge.get_inline_bot_results(bot.username, f"ytdl {input_url}")
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
                await c_q.edit_message_reply_markup(
                    reply_markup=(await download_button(yt_code))
                )
                return
        else:
            choice_id = None
        startTime = time()
        downtype = c_q.matches[0].group(3)
        media_type = "Video" if downtype == "v" else "Audio"
        callback_continue = f"Downloading {media_type} Please Wait..."
        frmt_text = choice_id or (
            "bestaudio/best [mp4]" if downtype == "v" else "320 Kbps"
        )
        callback_continue += f"\n\nFormat Code : {frmt_text}"
        await c_q.answer(callback_continue, show_alert=True)
        upload_msg = await userge.send_message(Config.LOG_CHANNEL_ID, "Uploading...")
        yt_url = BASE_YT_URL + yt_code
        await c_q.edit_message_text(
            text=(
                f"**⬇️ Downloading {media_type} ...**"
                f"\n\n🔗  [<b>Link</b>]({yt_url})\n🆔  <b>Format Code</b> : {frmt_text}"
            ),
        )
        if downtype == "v":
            retcode = await _tubeDl(url=yt_url, starttime=startTime, uid=choice_id)
        else:
            retcode = await _mp3Dl(url=yt_url, starttime=startTime, uid=choice_id)
        if retcode != 0:
            return await upload_msg.edit(str(retcode))
        _fpath = ""
        thumb_pic = None
        for _path in glob.glob(os.path.join(Config.DOWN_PATH, str(startTime), "*")):
            if _path.lower().endswith((".jpg", ".png", ".webp")):
                thumb_pic = _path
            else:
                _fpath = _path
        if not _fpath:
            await upload_msg.err("nothing found !")
            return
        if not thumb_pic and downtype == "v":
            thumb_pic = str(download(await get_ytthumb(yt_code)))
        uploaded_media = await upload(
            upload_msg,
            path=Path(_fpath),
            callback=c_q,
            custom_thumb=thumb_pic,
            log=False,
        )
        refresh_vid = await userge.bot.get_messages(
            Config.LOG_CHANNEL_ID, uploaded_media.message_id
        )
        f_id = get_file_id(refresh_vid)
        if downtype == "v":
            await c_q.edit_message_media(
                media=(
                    InputMediaVideo(
                        media=f_id,
                        caption=f"📹  <b>[{uploaded_media.caption}]({yt_url})</b>",
                    )
                ),
            )
        else:  # Audio
            await c_q.edit_message_media(
                media=(
                    InputMediaAudio(
                        media=f_id,
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
            await c_q.edit_message_media(
                media=(
                    InputMediaPhoto(
                        media=back_vid.get("thumb"),
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
            await c_q.edit_message_media(
                media=(
                    InputMediaPhoto(
                        media=front_vid.get("thumb"),
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
            await c_q.edit_message_media(
                media=(
                    InputMediaPhoto(
                        media=search_data.get("1").get("thumb"),
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
            await c_q.edit_message_media(
                media=(
                    InputMediaPhoto(
                        media=first.get("thumb"),
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
        "format": f"{uid or 'bestvideo[ext=mp4]'}+bestaudio[ext=m4a]/best[ext=mp4]",
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
                "preferredquality": uid or "320",
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


def get_yt_video_id(url: str):
    # https://regex101.com/r/boXuXb/1
    match = search(YOUTUBE_REGEX, url)
    if match:
        return match.group(1)
    return


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
        v_deo_id = r.get("id")
        output[index] = dict(
            message=out,
            thumb=thumb,
            video_id=v_deo_id,
            list_view=f'<img src={thumb}><b><a href={r.get("link")}>{index}. {r.get("accessibility").get("title")}</a></b><br>',
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
    vid_data = youtube_dl.YoutubeDL({"no-playlist": True}).extract_info(
        BASE_YT_URL + vid, download=False
    )
    buttons = [
        [
            InlineKeyboardButton(
                "⭐️  BEST VIDEO", callback_data=f"ytdl_download_{vid}_best_v"
            ),
            InlineKeyboardButton(
                "⭐️  BEST AUDIO", callback_data=f"ytdl_download_{vid}_best_a"
            ),
        ]
    ]
    # ------------------------------------------------ #
    qual_dict = defaultdict(lambda: defaultdict(int))
    qual_list = ["144p", "360p", "720p", "1080p", "1440p"]
    audio_dict = {}
    # ------------------------------------------------ #
    for video in vid_data["formats"]:
        fr_note = video.get("format_note")
        fr_id = int(video.get("format_id"))
        fr_size = video.get("filesize")
        for frmt_ in qual_list:
            if fr_note in (frmt_, frmt_ + "60"):
                qual_dict[frmt_][fr_id] = fr_size
        if video.get("acodec") != "none":
            bitrrate = int(video.get("abr", 0))
            if bitrrate != 0:
                audio_dict[
                    bitrrate
                ] = f"🎵 {bitrrate}Kbps ({humanbytes(fr_size) or 'N/A'})"

    video_btns = []
    for frmt in qual_list:
        frmt_dict = qual_dict[frmt]
        if len(frmt_dict) != 0:
            frmt_id = sorted(list(frmt_dict))[-1]
            frmt_size = humanbytes(frmt_dict.get(frmt_id)) or "N/A"
            video_btns.append(
                InlineKeyboardButton(
                    f"📹 {frmt} ({frmt_size})",
                    callback_data=f"ytdl_download_{vid}_{frmt_id}_v",
                )
            )
    buttons += sublists(video_btns, width=2)
    buttons += sublists(
        [
            InlineKeyboardButton(
                audio_dict.get(key_), callback_data=f"ytdl_download_{vid}_{key_}_a"
            )
            for key_ in sorted(audio_dict.keys())
        ],
        width=2,
    )
    if body:
        vid_body = f"<b>[{vid_data.get('title')}]({vid_data.get('webpage_url')})</b>"
        return vid_body, InlineKeyboardMarkup(buttons)
    return InlineKeyboardMarkup(buttons)
