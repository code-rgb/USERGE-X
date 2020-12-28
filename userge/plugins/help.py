import json
import os
import random
import re
from math import ceil
from typing import Any, Callable, Dict, List, Union

import requests
from html_telegraph_poster import TelegraphPoster
from pymediainfo import MediaInfo
from pyrogram import filters
from pyrogram.errors import BadRequest, MessageIdInvalid, MessageNotModified
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultAnimation,
    InlineQueryResultArticle,
    InlineQueryResultCachedDocument,
    InlineQueryResultCachedPhoto,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)
from youtubesearchpython import VideosSearch

from userge import Config, Message, get_collection, get_version, userge, versions
from userge.core.ext import RawClient
from userge.utils import get_file_id_and_ref
from userge.utils import parse_buttons as pb
from userge.utils import rand_key, xbot

from .bot.alive import check_media_link
from .bot.utube_inline import (
    download_button,
    get_yt_video_id,
    get_ytthumb,
    result_formatter,
    ytsearch_data,
)
from .fun.stylish import font_gen
from .misc.redditdl import reddit_thumb_link

CHANNEL = userge.getCLogger(__name__)
MEDIA_TYPE, MEDIA_URL = None, None
PATH = "userge/xcache"
_CATEGORY = {
    "admin": "🙋🏻‍♂️",
    "fun": "🎨",
    "misc": "🧩",
    "tools": "🧰",
    "utils": "🗂",
    "unofficial": "➕",
    "temp": "♻️",
    "plugins": "💎",
    "bot": "💠",
}
# Database
SAVED_SETTINGS = get_collection("CONFIGS")
REPO_X = InlineQueryResultArticle(
    title="Repo",
    input_message_content=InputTextMessageContent("**Here's how to setup USERGE-X** "),
    url="https://github.com/code-rgb/USERGE-X",
    description="Setup Your Own",
    thumb_url="https://i.imgur.com/1xsOo9o.png",
    reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔥 USERGE-X Repo", url="https://github.com/code-rgb/USERGE-X"
                ),
                InlineKeyboardButton(
                    "🚀 Deploy USERGE-X",
                    url=(
                        "https://heroku.com/deploy?template="
                        "https://github.com/code-rgb/USERGE-X/tree/alpha"
                    ),
                ),
            ]
        ]
    ),
)
# Thanks boi @FLAMEPOSEIDON
ALIVE_IMGS = [
    "https://telegra.ph/file/11123ef7dff2f1e19e79d.jpg",
    "https://i.imgur.com/uzKdTXG.jpg",
    "https://telegra.ph/file/6ecab390e4974c74c3764.png",
    "https://telegra.ph/file/995c75983a6c0e4499b55.png",
    "https://telegra.ph/file/86cc25c78ad667ca5e691.png",
]


def _get_mode() -> str:
    if RawClient.DUAL_MODE:
        return "↕️  **DUAL**"
    if Config.BOT_TOKEN:
        return "🤖  **BOT**"
    return "👤  **USER**"


async def _init() -> None:
    data = await SAVED_SETTINGS.find_one({"_id": "CURRENT_CLIENT"})
    if data:
        Config.USE_USER_FOR_CLIENT_CHECKS = bool(data["is_user"])


@userge.on_cmd(
    "help", about={"header": "Guide to use USERGE commands"}, allow_channels=False
)
async def helpme(
    message: Message,
) -> None:  # pylint: disable=missing-function-docstring
    plugins = userge.manager.enabled_plugins
    if not message.input_str:
        out_str = (
            f"""⚒ <b><u>(<code>{len(plugins)}</code>) Plugin(s) Available</u></b>\n\n"""
        )
        cat_plugins = userge.manager.get_plugins()
        for cat in sorted(cat_plugins):
            if cat == "plugins":
                continue
            out_str += (
                f"    {_CATEGORY.get(cat, '📁')} <b>{cat}</b> "
                f"(<code>{len(cat_plugins[cat])}</code>) :   <code>"
                + "</code>    <code>".join(sorted(cat_plugins[cat]))
                + "</code>\n\n"
            )
        out_str += (
            f"""📕 <b>Usage:</b>  <code>{Config.CMD_TRIGGER}help [plugin_name]</code>"""
        )
    else:
        key = message.input_str
        if (
            not key.startswith(Config.CMD_TRIGGER)
            and key in plugins
            and (
                len(plugins[key].enabled_commands) > 1
                or plugins[key].enabled_commands[0].name.lstrip(Config.CMD_TRIGGER)
                != key
            )
        ):
            commands = plugins[key].enabled_commands
            out_str = f"""<b><u>(<code>{len(commands)}</code>) Command(s) Available</u></b>

🔧 <b>Plugin:</b>  <code>{key}</code>
📘 <b>Doc:</b>  <code>{plugins[key].doc}</code>\n\n"""
            for i, cmd in enumerate(commands, start=1):
                out_str += (
                    f"    🤖 <b>cmd(<code>{i}</code>):</b>  <code>{cmd.name}</code>\n"
                    f"    📚 <b>info:</b>  <i>{cmd.doc}</i>\n\n"
                )
            out_str += f"""📕 <b>Usage:</b>  <code>{Config.CMD_TRIGGER}help [command_name]</code>"""
        else:
            commands = userge.manager.enabled_commands
            key = key.lstrip(Config.CMD_TRIGGER)
            key_ = Config.CMD_TRIGGER + key
            if key in commands:
                out_str = f"<code>{key}</code>\n\n{commands[key].about}"
            elif key_ in commands:
                out_str = f"<code>{key_}</code>\n\n{commands[key_].about}"
            else:
                out_str = f"<i>No Module or Command Found for</i>: <code>{message.input_str}</code>"
    await message.edit(
        out_str, del_in=0, parse_mode="html", disable_web_page_preview=True
    )


if userge.has_bot:

    def check_owner(func):
        async def wrapper(_, c_q: CallbackQuery):
            if c_q.from_user and c_q.from_user.id in Config.OWNER_ID:
                try:
                    await func(c_q)
                except MessageNotModified:
                    await c_q.answer("Nothing Found to Refresh 🤷‍♂️", show_alert=True)
                except MessageIdInvalid:
                    await c_q.answer(
                        "Sorry, I Don't Have Permissions to edit this 😔",
                        show_alert=True,
                    )
            else:
                user_dict = await userge.bot.get_user_dict(Config.OWNER_ID[0])
                await c_q.answer(
                    f"Only {user_dict['flname']} Can Access this...! Build Your USERGE-X",
                    show_alert=True,
                )

        return wrapper

    @userge.bot.on_callback_query(
        filters.regex(pattern=r"\((.+)\)(next|prev)\((\d+)\)")
    )
    @check_owner
    async def callback_next_prev(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        n_or_p = str(callback_query.matches[0].group(2))
        p_num = int(callback_query.matches[0].group(3))
        p_num = p_num + 1 if n_or_p == "next" else p_num - 1
        pos_list = cur_pos.split("|")
        if len(pos_list) == 1:
            buttons = parse_buttons(
                p_num,
                cur_pos,
                lambda x: f"{_CATEGORY.get(x, '📁')} {x}",
                userge.manager.get_all_plugins(),
            )
        elif len(pos_list) == 2:
            buttons = parse_buttons(
                p_num,
                cur_pos,
                lambda x: f"🔹 {x}",
                userge.manager.get_all_plugins()[pos_list[-1]],
            )
        elif len(pos_list) == 3:
            _, buttons = plugin_data(cur_pos, p_num)
        await xbot.edit_inline_reply_markup(
            callback_query.inline_message_id,
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        # await callback_query.edit_message_reply_markup(
        #     reply_markup=InlineKeyboardMarkup(buttons)
        # )

    @userge.bot.on_callback_query(filters.regex(pattern=r"back\((.+)\)"))
    @check_owner
    async def callback_back(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split("|")
        if len(pos_list) == 1:
            await callback_query.answer("you are in main menu", show_alert=True)
            return
        if len(pos_list) == 2:
            text = " 𝐔𝐒𝐄𝐑𝐆𝐄-𝐗  𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨"
            buttons = main_menu_buttons()
        elif len(pos_list) == 3:
            text, buttons = category_data(cur_pos)
        elif len(pos_list) == 4:
            text, buttons = plugin_data(cur_pos)

        await xbot.edit_inline_text(
            callback_query.inline_message_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons),
        )

        # await callback_query.edit_message_text(
        #     text, reply_markup=InlineKeyboardMarkup(buttons)
        # )

    @userge.bot.on_callback_query(filters.regex(pattern=r"enter\((.+)\)"))
    @check_owner
    async def callback_enter(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split("|")
        if len(pos_list) == 2:
            text, buttons = category_data(cur_pos)
        elif len(pos_list) == 3:
            text, buttons = plugin_data(cur_pos)
        elif len(pos_list) == 4:
            text, buttons = filter_data(cur_pos)

        await xbot.edit_inline_text(
            callback_query.inline_message_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons),
        )

        # await callback_query.edit_message_text(
        #     text, reply_markup=InlineKeyboardMarkup(buttons)
        # )

    @userge.bot.on_callback_query(
        filters.regex(pattern=r"((?:un)?load|(?:en|dis)able)\((.+)\)")
    )
    @check_owner
    async def callback_manage(callback_query: CallbackQuery):
        task = str(callback_query.matches[0].group(1))
        cur_pos = str(callback_query.matches[0].group(2))
        pos_list = cur_pos.split("|")
        if len(pos_list) == 4:
            if is_filter(pos_list[-1]):
                flt = userge.manager.filters[pos_list[-1]]
            else:
                flt = userge.manager.commands[pos_list[-1]]
            await getattr(flt, task)()
            text, buttons = filter_data(cur_pos)
        else:
            plg = userge.manager.plugins[pos_list[-1]]
            await getattr(plg, task)()
            text, buttons = plugin_data(cur_pos)
        await xbot.edit_inline_text(
            callback_query.inline_message_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        # await callback_query.edit_message_text(
        #     text, reply_markup=InlineKeyboardMarkup(buttons)
        # )

    @userge.bot.on_callback_query(filters.regex(pattern=r"^mm$"))
    @check_owner
    async def callback_mm(callback_query: CallbackQuery):

        await xbot.edit_inline_text(
            callback_query.inline_message_id,
            text=" 𝐔𝐒𝐄𝐑𝐆𝐄-𝐗  𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨 ",
            reply_markup=InlineKeyboardMarkup(main_menu_buttons()),
        )

        # await callback_query.edit_message_text(
        #     " 𝐔𝐒𝐄𝐑𝐆𝐄-𝐗  𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨 ",
        #     reply_markup=InlineKeyboardMarkup(main_menu_buttons()),
        # )

    @userge.bot.on_callback_query(filters.regex(pattern=r"^chgclnt$"))
    @check_owner
    async def callback_chgclnt(callback_query: CallbackQuery):
        if Config.USE_USER_FOR_CLIENT_CHECKS:
            Config.USE_USER_FOR_CLIENT_CHECKS = False
        else:
            Config.USE_USER_FOR_CLIENT_CHECKS = True
        await SAVED_SETTINGS.update_one(
            {"_id": "CURRENT_CLIENT"},
            {"$set": {"is_user": Config.USE_USER_FOR_CLIENT_CHECKS}},
            upsert=True,
        )

        await xbot.edit_inline_reply_markup(
            callback_query.inline_message_id,
            reply_markup=InlineKeyboardMarkup(main_menu_buttons()),
        )

        # await callback_query.edit_message_reply_markup(
        #     reply_markup=InlineKeyboardMarkup(main_menu_buttons())
        # )

    @userge.bot.on_callback_query(filters.regex(pattern=r"refresh\((.+)\)"))
    @check_owner
    async def callback_exit(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split("|")
        if len(pos_list) == 4:
            text, buttons = filter_data(cur_pos)
        else:
            text, buttons = plugin_data(cur_pos)

        response = await xbot.edit_inline_text(
            callback_query.inline_message_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        errors = response.get("description", None)
        if errors:
            if "not modified:" in errors:
                raise MessageNotModified
            if "MESSAGE_ID_INVALID" in errors:
                raise MessageIdInvalid
        # await callback_query.edit_message_text(
        #     text, reply_markup=InlineKeyboardMarkup(buttons)
        # )

    def is_filter(name: str) -> bool:
        split_ = name.split(".")
        return bool(split_[0] and len(split_) == 2)

    def parse_buttons(
        page_num: int,
        cur_pos: str,
        func: Callable[[str], str],
        data: Union[List[str], Dict[str, Any]],
        rows: int = 5,
    ):
        buttons = [
            InlineKeyboardButton(
                func(x), callback_data=f"enter({cur_pos}|{x})".encode()
            )
            for x in sorted(data)
        ]
        pairs = list(map(list, zip(buttons[::2], buttons[1::2])))
        if len(buttons) % 2 == 1:
            pairs.append([buttons[-1]])
        max_pages = ceil(len(pairs) / rows)
        current_page = page_num % max_pages
        if len(pairs) > rows:
            pairs = pairs[current_page * rows : (current_page + 1) * rows] + [
                [
                    InlineKeyboardButton(
                        "⏪ Previous",
                        callback_data=f"({cur_pos})prev({current_page})".encode(),
                    ),
                    InlineKeyboardButton(
                        "⏩ Next",
                        callback_data=f"({cur_pos})next({current_page})".encode(),
                    ),
                ],
            ]
        pairs += default_buttons(cur_pos)
        return pairs

    def main_menu_buttons():
        return parse_buttons(
            0,
            "mm",
            lambda x: f"{_CATEGORY.get(x, '📁')} {x}",
            userge.manager.get_all_plugins(),
        )

    def default_buttons(cur_pos: str):
        tmp_btns = []
        if cur_pos != "mm":
            tmp_btns.append(
                InlineKeyboardButton(
                    "⬅ Back", callback_data=f"back({cur_pos})".encode()
                )
            )
            if len(cur_pos.split("|")) > 2:
                tmp_btns.append(
                    InlineKeyboardButton("🖥 Main Menu", callback_data="mm")
                    # .encode()
                )
                tmp_btns.append(
                    InlineKeyboardButton(
                        "🔄 Refresh", callback_data=f"refresh({cur_pos})".encode()
                    )
                )
        else:
            cur_clnt = "👤 USER" if Config.USE_USER_FOR_CLIENT_CHECKS else "⚙️ BOT"
            tmp_btns.append(
                InlineKeyboardButton(
                    f"🔩 Client for Checks and Sudos : {cur_clnt}",
                    callback_data="chgclnt"
                    # .encode()
                )
            )
        return [tmp_btns]

    def category_data(cur_pos: str):
        pos_list = cur_pos.split("|")
        plugins = userge.manager.get_all_plugins()[pos_list[1]]
        text = (
            f"**(`{len(plugins)}`) Plugin(s) Under : "
            f"`{_CATEGORY.get(pos_list[1], '📁')} {pos_list[1]}`  Category**"
        )
        buttons = parse_buttons(0, "|".join(pos_list[:2]), lambda x: f"🔹 {x}", plugins)
        return text, buttons

    def plugin_data(cur_pos: str, p_num: int = 0):
        pos_list = cur_pos.split("|")
        plg = userge.manager.plugins[pos_list[2]]
        text = f"""🔹 <u><b>Plugin Status<b></u> 🔹

🎭 **Category** : `{pos_list[1]}`
🔖 **Name** : `{plg.name}`
📝 **Doc** : `{plg.doc}`
◾️ **Commands** : `{len(plg.commands)}`
⚖ **Filters** : `{len(plg.filters)}`
✅ **Loaded** : `{plg.is_loaded}`
➕ **Enabled** : `{plg.is_enabled}`
"""
        tmp_btns = []
        if plg.is_loaded:
            tmp_btns.append(
                InlineKeyboardButton(
                    "❎ Unload",
                    callback_data=f"unload({'|'.join(pos_list[:3])})".encode(),
                )
            )
        else:
            tmp_btns.append(
                InlineKeyboardButton(
                    "✅ Load", callback_data=f"load({'|'.join(pos_list[:3])})".encode()
                )
            )
        if plg.is_enabled:
            tmp_btns.append(
                InlineKeyboardButton(
                    "➖ Disable",
                    callback_data=f"disable({'|'.join(pos_list[:3])})".encode(),
                )
            )
        else:
            tmp_btns.append(
                InlineKeyboardButton(
                    "➕ Enable",
                    callback_data=f"enable({'|'.join(pos_list[:3])})".encode(),
                )
            )
        buttons = parse_buttons(
            p_num,
            "|".join(pos_list[:3]),
            lambda x: f"⚖ {x}" if is_filter(x) else f" {x}",
            (flt.name for flt in plg.commands + plg.filters),
        )
        buttons = buttons[:-1] + [tmp_btns] + [buttons[-1]]
        return text, buttons

    def filter_data(cur_pos: str):
        pos_list = cur_pos.split("|")
        plg = userge.manager.plugins[pos_list[2]]
        flts = {flt.name: flt for flt in plg.commands + plg.filters}
        flt = flts[pos_list[-1]]
        flt_data = f"""
🔖 **Name** : `{flt.name}`
📝 **Doc** : `{flt.doc}`
🤖 **Via Bot** : `{flt.allow_via_bot}`
✅ **Loaded** : `{flt.is_loaded}`
➕ **Enabled** : `{flt.is_enabled}`"""
        if hasattr(flt, "about"):
            text = f"""<b><u>Command Status</u></b>
{flt_data}
{flt.about}
"""
        else:
            text = f"""⚖ <b><u>Filter Status</u></b> ⚖
{flt_data}
"""
        buttons = default_buttons(cur_pos)
        tmp_btns = []
        if flt.is_loaded:
            tmp_btns.append(
                InlineKeyboardButton(
                    "❎ Unload", callback_data=f"unload({cur_pos})".encode()
                )
            )
        else:
            tmp_btns.append(
                InlineKeyboardButton(
                    "✅ Load", callback_data=f"load({cur_pos})".encode()
                )
            )
        if flt.is_enabled:
            tmp_btns.append(
                InlineKeyboardButton(
                    "➖ Disable", callback_data=f"disable({cur_pos})".encode()
                )
            )
        else:
            tmp_btns.append(
                InlineKeyboardButton(
                    "➕ Enable", callback_data=f"enable({cur_pos})".encode()
                )
            )
        buttons = [tmp_btns] + buttons
        return text, buttons

    async def get_alive_():
        global MEDIA_TYPE, MEDIA_URL
        type_, media_ = await check_media_link(Config.ALIVE_MEDIA)
        if not media_:
            return
        MEDIA_TYPE = type_
        if type(media_) is str:
            limit = 1 if type_ == "url_gif" else 5
            media_info = MediaInfo.parse(media_)
            for track in media_info.tracks:
                if track.track_type == "General":
                    media_size = track.file_size / 1000000
            if media_size < limit:
                MEDIA_URL = media_
        else:
            try:
                msg = await userge.bot.get_messages(media_[0], media_[1])
                f_id, f_ref = get_file_id_and_ref(msg)
                if msg.photo:
                    MEDIA_TYPE = "tg_image"
            except BadRequest:
                return
            MEDIA_URL = [f_id, f_ref]

    @userge.bot.on_inline_query()
    async def inline_answer(_, inline_query: InlineQuery):
        results = []
        i_q = inline_query.query
        string = i_q.lower()  # All lower
        str_x = i_q.split(" ", 2)  # trigger @username Text
        str_y = i_q.split(" ", 1)  # trigger and Text
        string_split = string.split()  # All lower and Split each word

        if (
            inline_query.from_user.id in Config.OWNER_ID
            or inline_query.from_user.id in Config.SUDO_USERS
        ):

            if string == "syntax":
                owner = [
                    [
                        InlineKeyboardButton(
                            text="Contact", url="https://t.me/deleteduser420"
                        )
                    ]
                ]
                results.append(
                    InlineQueryResultPhoto(
                        photo_url="https://coverfiles.alphacoders.com/123/123388.png",
                        caption="Hey I solved **𝚂𝚢𝚗𝚝𝚊𝚡's ░ Σrr♢r**",
                        reply_markup=InlineKeyboardMarkup(owner),
                    )
                )

            if string == "age_verification_alert":
                buttons = [
                    [
                        InlineKeyboardButton(
                            text="Yes I'm 18+", callback_data="age_verification_true"
                        ),
                        InlineKeyboardButton(
                            text="No I'm Not", callback_data="age_verification_false"
                        ),
                    ]
                ]
                results.append(
                    InlineQueryResultPhoto(
                        photo_url="https://i.imgur.com/Zg58iXc.jpg",
                        caption="**ARE YOU OLD ENOUGH FOR THIS ?**",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )

            if str_y[0] == "reddit":
                reddit_api = "https://meme-api.herokuapp.com/gimme/"
                if len(str_y) == 2:
                    subreddit_regex = r"^([a-zA-Z]+)\.$"
                    match = re.search(subreddit_regex, str_y[1])
                    if match:
                        subreddit_name = match.group(1)
                        reddit_api += f"{subreddit_name}/30"
                    else:
                        return

                else:
                    reddit_api += "30"

                cn = requests.get(reddit_api)
                r = cn.json()
                if "code" in r:
                    bool_is_gallery = False
                    code = r["code"]
                    code_message = r["message"]
                    results.append(
                        InlineQueryResultArticle(
                            title=str(code),
                            input_message_content=InputTextMessageContent(
                                f"**Error Code: {code}**\n`{code_message}`"
                            ),
                            description="Enter A Valid Subreddit Name !",
                            thumb_url="https://i.imgur.com/7a7aPVa.png",
                        )
                    )
                else:
                    bool_is_gallery = True
                    for post in r["memes"]:
                        if "url" in post:
                            postlink = post["postLink"]
                            subreddit = post["subreddit"]
                            title = post["title"]
                            media_url = post["url"]
                            author = post["author"]
                            upvote = post["ups"]
                            captionx = f"<b>{title}</b>\n"
                            captionx += f"`Posted by u/{author}`\n"
                            captionx += f"↕️ <code>{upvote}</code>\n"
                            thumbnail = reddit_thumb_link(post["preview"])
                            if post["spoiler"]:
                                captionx += "⚠️ Post marked as SPOILER\n"
                            if post["nsfw"]:
                                captionx += "🔞 Post marked Adult \n"
                            buttons = [
                                [
                                    InlineKeyboardButton(
                                        f"Source: r/{subreddit}", url=postlink
                                    )
                                ]
                            ]
                            if media_url.endswith(".gif"):
                                results.append(
                                    InlineQueryResultAnimation(
                                        animation_url=media_url,
                                        thumb_url=thumbnail,
                                        caption=captionx,
                                        reply_markup=InlineKeyboardMarkup(buttons),
                                    )
                                )
                            else:
                                results.append(
                                    InlineQueryResultPhoto(
                                        photo_url=media_url,
                                        thumb_url=thumbnail,
                                        caption=captionx,
                                        reply_markup=InlineKeyboardMarkup(buttons),
                                    )
                                )
                await inline_query.answer(
                    results=results,
                    cache_time=1,
                    is_gallery=bool_is_gallery,
                    switch_pm_text="Available Commands",
                    switch_pm_parameter="inline",
                )
                return

            if string == "rick":
                rick = [[InlineKeyboardButton(text="🔍", callback_data="mm")]]
                results.append(
                    InlineQueryResultArticle(
                        title="Not a Rick Roll",
                        input_message_content=InputTextMessageContent("Search Results"),
                        description="Definately Not a Rick Roll",
                        thumb_url="https://i.imgur.com/hRCaKAy.png",
                        reply_markup=InlineKeyboardMarkup(rick),
                    )
                )

            if string == "alive":
                buttons = [
                    [
                        InlineKeyboardButton(
                            "🔧 SETTINGS", callback_data="settings_btn"
                        ),
                        InlineKeyboardButton(text="⚡️ REPO", url=Config.UPSTREAM_REPO),
                    ]
                ]

                alive_info = f"""
    **[USERGE-X](https://telegram.dog/x_xtests) is Up and Running**

 • 🐍 Python :  `v{versions.__python_version__}`
 • 🔥 Pyrogram :  `v{versions.__pyro_version__}`
 • 🧬 𝑿 :  `v{get_version()}`

{_get_mode()}  |  🕔: {userge.uptime}
"""

                if not MEDIA_URL and Config.ALIVE_MEDIA:
                    await get_alive_()

                if MEDIA_URL:
                    if MEDIA_TYPE == "url_gif":
                        results.append(
                            InlineQueryResultAnimation(
                                animation_url=MEDIA_URL,
                                caption=alive_info,
                                reply_markup=InlineKeyboardMarkup(buttons),
                            )
                        )
                    elif MEDIA_TYPE == "url_image":
                        results.append(
                            InlineQueryResultPhoto(
                                photo_url=MEDIA_URL,
                                caption=alive_info,
                                reply_markup=InlineKeyboardMarkup(buttons),
                            )
                        )
                    elif MEDIA_TYPE == "tg_image":
                        results.append(
                            InlineQueryResultCachedPhoto(
                                file_id=MEDIA_URL[0],
                                file_ref=MEDIA_URL[1],
                                caption=alive_info,
                                reply_markup=InlineKeyboardMarkup(buttons),
                            )
                        )
                    else:
                        results.append(
                            InlineQueryResultCachedDocument(
                                title="USERGE-X",
                                file_id=MEDIA_URL[0],
                                file_ref=MEDIA_URL[1],
                                caption=alive_info,
                                description="ALIVE",
                                reply_markup=InlineKeyboardMarkup(buttons),
                            )
                        )
                else:  # default
                    random_alive = random.choice(ALIVE_IMGS)
                    results.append(
                        InlineQueryResultPhoto(
                            photo_url=random_alive,
                            caption=alive_info,
                            reply_markup=InlineKeyboardMarkup(buttons),
                        )
                    )

            if string == "geass":
                results.append(
                    InlineQueryResultAnimation(
                        animation_url="https://i.imgur.com/DeZHcRK.gif",
                        caption="To defeat evil, I must become a greater evil",
                    )
                )

            if string == "gapps":
                buttons = [
                    [
                        InlineKeyboardButton("Open GApps", callback_data="open_gapps"),
                        InlineKeyboardButton(
                            "Flame GApps", callback_data="flame_gapps"
                        ),
                    ],
                    [InlineKeyboardButton("Nik GApps", callback_data="nik_gapps")],
                ]
                results.append(
                    InlineQueryResultArticle(
                        title="GApps",
                        input_message_content=InputTextMessageContent(
                            "[\u200c](https://i.imgur.com/BZBMrfn.jpg) **LATEST Android 10 arm64 GApps**"
                        ),
                        description="Get Latest GApps Download Links Directly from SF",
                        thumb_url="https://i.imgur.com/Npzw8Ph.png",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )

            if len(string_split) == 2:  # workaround for list index out of range
                if string_split[0] == "ofox":
                    codename = string_split[1]
                    t = TelegraphPoster(use_api=True)
                    t.create_api_token("Userge-X")
                    photo = "https://i.imgur.com/582uaSk.png"
                    api_host = "https://api.orangefox.download/v2/device/"
                    try:
                        cn = requests.get(f"{api_host}{codename}")
                        r = cn.json()
                    except ValueError:
                        return
                    s = requests.get(
                        f"{api_host}{codename}/releases/stable/last"
                    ).json()
                    info = f"📱 **Device**: {r['fullname']}\n"
                    info += f"👤 **Maintainer**: {r['maintainer']['name']}\n\n"
                    recovery = f"🦊 <code>{s['file_name']}</code>\n"
                    recovery += f"📅 {s['date']}\n"
                    recovery += f"ℹ️ **Version:** {s['version']}\n"
                    recovery += f"📌 **Build Type:** {s['build_type']}\n"
                    recovery += f"🔰 **Size:** {s['size_human']}\n\n"
                    recovery += "📍 **Changelog:**\n"
                    recovery += f"<code>{s['changelog']}</code>\n\n"
                    msg = info
                    msg += recovery
                    notes_ = s.get("notes")
                    if notes_:
                        notes = t.post(title="READ Notes", author="", text=notes_)
                        buttons = [
                            [
                                InlineKeyboardButton("🗒️ NOTES", url=notes["url"]),
                                InlineKeyboardButton("⬇️ DOWNLOAD", url=s["url"]),
                            ]
                        ]
                    else:
                        buttons = [
                            [InlineKeyboardButton(text="⬇️ DOWNLOAD", url=s["url"])]
                        ]

                    results.append(
                        InlineQueryResultPhoto(
                            photo_url=photo,
                            thumb_url="https://i.imgur.com/o0onLYB.jpg",
                            title="Latest OFOX RECOVERY",
                            description=f"For device : {codename}",
                            caption=msg,
                            reply_markup=InlineKeyboardMarkup(buttons),
                        )
                    )

            if string == "repo":
                results.append(REPO_X)

            if str_y[0] == "spoiler":
                if not os.path.exists("./userge/xcache/spoiler_db.json"):
                    results.append(
                        InlineQueryResultArticle(
                            title="No Spoiler Found",
                            input_message_content=InputTextMessageContent(
                                "No Spoiler Found !\nLet's Add Some 😈"
                            ),
                            description="See .help spoiler for more info",
                        )
                    )
                else:
                    bot_name = (await userge.bot.get_me()).username
                    if len(str_y) == 2:
                        link = f"https://t.me/{bot_name}?start=spoiler_{str_y[1]}"
                        buttons = [
                            [InlineKeyboardButton(text="View Spoiler", url=link)]
                        ]
                        results.append(
                            InlineQueryResultArticle(
                                title="Spoiler",
                                input_message_content=InputTextMessageContent(
                                    "<b>Click To View The Spoiler !</b>"
                                ),
                                description="Click To Send",
                                thumb_url="https://telegra.ph/file/ee3a6439494463acd1a3a.jpg",
                                reply_markup=InlineKeyboardMarkup(buttons),
                            )
                        )
                    else:
                        view_db = json.load(open("./userge/xcache/spoiler_db.json"))
                        if len(view_db) != 0:
                            numm = 0
                            for spoilerr in view_db:
                                numm += 1
                                buttons = [
                                    [
                                        InlineKeyboardButton(
                                            text="View Spoiler",
                                            url=f"https://t.me/{bot_name}?start=spoiler_{spoilerr}",
                                        )
                                    ]
                                ]
                                saved_at = view_db.get(spoilerr, None)
                                savetime = (
                                    saved_at.get("savetime", None) if saved_at else None
                                )
                                results.append(
                                    InlineQueryResultArticle(
                                        title=f"#{numm}  Spoiler",
                                        input_message_content=InputTextMessageContent(
                                            "<b>Click To View The Spoiler !</b>"
                                        ),
                                        description=f"Created At: {savetime}",
                                        thumb_url="https://telegra.ph/file/ee3a6439494463acd1a3a.jpg",
                                        reply_markup=InlineKeyboardMarkup(buttons),
                                    )
                                )

            if str_x[0].lower() == "op" and len(str_x) > 1:
                txt = i_q[3:]

                opinion = os.path.join(PATH, "emoji_data.txt")
                try:
                    view_data = json.load(open(opinion))
                except:
                    view_data = False

                if view_data:
                    # Uniquely identifies an inline message
                    new_id = {int(inline_query.id): [{}]}
                    view_data.update(new_id)
                    json.dump(view_data, open(opinion, "w"))
                else:
                    d = {int(inline_query.id): [{}]}
                    json.dump(d, open(opinion, "w"))

                buttons = [
                    [
                        InlineKeyboardButton(
                            "👍", callback_data=f"op_y_{inline_query.id}"
                        ),
                        InlineKeyboardButton(
                            "👎", callback_data=f"op_n_{inline_query.id}"
                        ),
                    ]
                ]
                results.append(
                    InlineQueryResultArticle(
                        title="Ask For Opinion",
                        input_message_content=InputTextMessageContent(txt),
                        description=f"Q. {txt}",
                        thumb_url="https://i.imgur.com/Zlc98qS.jpg",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )

            if "btn_" in str_y[0] or str_y[0] == "btn":

                inline_db_path = "./userge/xcache/inline_db.json"
                if os.path.exists(inline_db_path):
                    with open(inline_db_path, "r") as data_file:
                        view_db = json.load(data_file)

                    data_count_n = 1
                    reverse_list = list(view_db)
                    reverse_list.reverse()
                    for butt_ons in reverse_list:
                        if data_count_n > 15:
                            view_db.pop(butt_ons, None)
                        data_count_n += 1

                    with open(inline_db_path, "w") as data_file:
                        json.dump(view_db, data_file)

                    if str_y[0] == "btn":
                        inline_storage = list(view_db)
                    else:
                        rnd_id = (str_y[0].split("_", 1))[1]
                        inline_storage = [rnd_id]

                    if len(inline_storage) == 0:
                        return

                    for inline_content in inline_storage:
                        inline_db = view_db.get(inline_content, None)
                        if inline_db:
                            if (
                                inline_db["media_valid"]
                                and int(inline_db["media_id"]) != 0
                            ):
                                saved_msg = await userge.bot.get_messages(
                                    Config.LOG_CHANNEL_ID, int(inline_db["media_id"])
                                )
                                media_data = get_file_id_and_ref(saved_msg)

                            textx, buttonsx = pb(inline_db["msg_content"])

                            if inline_db["media_valid"]:
                                if saved_msg.photo:
                                    results.append(
                                        InlineQueryResultCachedPhoto(
                                            file_id=media_data[0],
                                            file_ref=media_data[1],
                                            caption=textx,
                                            reply_markup=buttonsx,
                                        )
                                    )
                                else:
                                    results.append(
                                        InlineQueryResultCachedDocument(
                                            title=textx,
                                            file_id=media_data[0],
                                            file_ref=media_data[1],
                                            caption=textx,
                                            description="Inline Button",
                                            reply_markup=buttonsx,
                                        )
                                    )
                            else:
                                results.append(
                                    InlineQueryResultArticle(
                                        title=textx,
                                        input_message_content=InputTextMessageContent(
                                            textx
                                        ),
                                        reply_markup=buttonsx,
                                    )
                                )

            if str_y[0].lower() == "stylish":
                if len(str_y) == 2:
                    results = []
                    input_text = str_y[1]
                    font_names = [
                        "serif",
                        "sans",
                        "sans_i",
                        "serif_i",
                        "medi_b",
                        "medi",
                        "double",
                        "cursive_b",
                        "cursive",
                        "bigsmall",
                        "reverse",
                        "circle",
                        "circle_b",
                        "mono",
                        "square_b",
                        "square",
                        "smoth",
                        "goth",
                        "wide",
                        "web",
                        "weeb",
                        "weeeb",
                    ]
                    for f_name in font_names:
                        styled_str = await font_gen(f_name, input_text)
                        results.append(
                            InlineQueryResultArticle(
                                title=f_name.upper(),
                                input_message_content=InputTextMessageContent(
                                    styled_str
                                ),
                                description=styled_str,
                            )
                        )
                    await inline_query.answer(
                        results=results,
                        cache_time=1,
                        switch_pm_text="Available Commands",
                        switch_pm_parameter="inline",
                    )
                    return

            if str_x[0].lower() == "secret":
                if len(str_x) == 3:
                    user_name = str_x[1]
                    msg = str_x[2]
                    try:
                        a = await userge.get_users(user_name)
                        user_id = a.id
                    except:
                        return
                    secret = os.path.join(PATH, "secret.txt")
                    try:
                        view_data = json.load(open(secret))
                    except:
                        view_data = False

                    if view_data:
                        # Uniquely identifies an inline message
                        new_id = {
                            str(inline_query.id): {"user_id": user_id, "msg": msg}
                        }
                        view_data.update(new_id)
                        json.dump(view_data, open(secret, "w"))
                    else:
                        d = {str(inline_query.id): {"user_id": user_id, "msg": msg}}
                        json.dump(d, open(secret, "w"))

                    buttons = [
                        [
                            InlineKeyboardButton(
                                "🔐  SHOW", callback_data=f"secret_{inline_query.id}"
                            )
                        ]
                    ]
                    results.append(
                        InlineQueryResultArticle(
                            title="Send A Secret Message",
                            input_message_content=InputTextMessageContent(
                                f"📩 <b>Secret Msg</b> for {user_name}. Only he/she can open it."
                            ),
                            description=f"Send Secret Message to: {user_name}",
                            thumb_url="https://i.imgur.com/c5pZebC.png",
                            reply_markup=InlineKeyboardMarkup(buttons),
                        )
                    )

            if str_y[0].lower() == "ytdl" and len(str_y) == 2:
                link = get_yt_video_id(str_y[1])
                if link is None:
                    search = VideosSearch(str_y[1], limit=15)
                    resp = (search.result()).get("result")
                    if len(resp) == 0:
                        results.append(
                            InlineQueryResultArticle(
                                title="not Found",
                                input_message_content=InputTextMessageContent(
                                    f"No Results found for {str_y[1]}"
                                ),
                                description="INVALID",
                            )
                        )
                    else:
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
                    photo = get_ytthumb(link)

                results.append(
                    InlineQueryResultPhoto(
                        photo_url=photo,
                        title=link,
                        description="⬇️ Click to Download",
                        caption=caption,
                        reply_markup=buttons,
                    )
                )

            MAIN_MENU = InlineQueryResultArticle(
                title="Main Menu",
                input_message_content=InputTextMessageContent(" 𝐔𝐒𝐄𝐑𝐆𝐄-𝐗  𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨 "),
                url="https://github.com/code-rgb/USERGE-X",
                description="Userge-X Main Menu",
                thumb_url="https://i.imgur.com/1xsOo9o.png",
                reply_markup=InlineKeyboardMarkup(main_menu_buttons()),
            )
            results.append(MAIN_MENU)
            if len(results) != 0:
                await inline_query.answer(
                    results=results,
                    cache_time=1,
                    switch_pm_text="Available Commands",
                    switch_pm_parameter="inline",
                )
        else:
            results.append(REPO_X)
            owner_name = (await userge.get_me()).first_name
            await inline_query.answer(
                results=results,
                cache_time=1,
                switch_pm_text=f"This bot is only for {owner_name}",
                switch_pm_parameter="start",
            )
