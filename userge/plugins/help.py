# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.
import random
from math import ceil
import asyncio
from typing import List, Callable, Dict, Union, Any
from userge.utils import parse_buttons as pb
from pyrogram import filters
from pyrogram.types import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, InlineQuery, InlineQueryResultPhoto,
    InlineQueryResultAnimation)
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified, MessageIdInvalid, MessageEmpty
from userge import userge, Message, Config, get_collection, versions, get_version
import json
import os
import requests
from html_telegraph_poster import TelegraphPoster
import re
import urllib
  

MEDIA_TYPE, MEDIA_URL = None, None

PATH = "userge/xcache"

if not os.path.exists(PATH):
    os.mkdir(PATH)

_CATEGORY = {
    'admin': '🙋🏻‍♂️',
    'fun': '🎨',
    'misc': '🧩',
    'tools': '🧰',
    'utils': '🗂',
    'unofficial': '➕',
    'temp': '♻️',
    'plugins': '💎',
    'bot' : '🔰' 
}
# Database
SAVED_SETTINGS = get_collection("CONFIGS")

BUTTON_BASE = get_collection("TEMP_BUTTON") # TODO use json cache


REPO_X = InlineQueryResultArticle(
                    title="Repo",
                    input_message_content=InputTextMessageContent(
                        "**Here's how to setup USERGE-X** "),
                    url="https://github.com/code-rgb/USERGE-X",
                    description="Setup Your Own",
                    thumb_url="https://i.imgur.com/1xsOo9o.png",
                    reply_markup=InlineKeyboardMarkup(
                        [[
                            InlineKeyboardButton(                  
                            "🔥 USERGE-X Repo",
                            url="https://github.com/code-rgb/USERGE-X"),
                            InlineKeyboardButton(
                            "🚀 Deploy USERGE-X",
                            url=("https://heroku.com/deploy?template="
                            "https://github.com/code-rgb/USERGE-X/tree/alpha")
                            )
                        ]]
                    )
            )

 


# Thanks boi @FLAMEPOSEIDON
ALIVE_IMGS = ["https://telegra.ph/file/11123ef7dff2f1e19e79d.jpg", "https://i.imgur.com/uzKdTXG.jpg",
"https://telegra.ph/file/6ecab390e4974c74c3764.png",
"https://telegra.ph/file/995c75983a6c0e4499b55.png",
"https://telegra.ph/file/86cc25c78ad667ca5e691.png"]



async def _init() -> None:
    data = await SAVED_SETTINGS.find_one({'_id': 'CURRENT_CLIENT'})
    if data:
        Config.USE_USER_FOR_CLIENT_CHECKS = bool(data['is_user'])


@userge.on_cmd("help", about={'header': "Guide to use USERGE commands"}, allow_channels=False)
async def helpme(message: Message) -> None:  # pylint: disable=missing-function-docstring
    plugins = userge.manager.enabled_plugins
    if not message.input_str:
        out_str = f"""⚒ <b><u>(<code>{len(plugins)}</code>) Plugin(s) Available</u></b>\n\n"""
        cat_plugins = userge.manager.get_all_plugins()
        for cat in sorted(cat_plugins):
            if cat == "plugins":
                continue
            out_str += (f"    {_CATEGORY.get(cat, '📁')} <b>{cat}</b> "
                        f"(<code>{len(cat_plugins[cat])}</code>) :   <code>"
                        + "</code>    <code>".join(sorted(cat_plugins[cat])) + "</code>\n\n")
        out_str += f"""📕 <b>Usage:</b>  <code>{Config.CMD_TRIGGER}help [plugin_name]</code>"""
    else:
        key = message.input_str
        if (not key.startswith(Config.CMD_TRIGGER)
                and key in plugins
                and (len(plugins[key].enabled_commands) > 1
                     or plugins[key].enabled_commands[0].name.lstrip(Config.CMD_TRIGGER) != key)):
            commands = plugins[key].enabled_commands
            out_str = f"""<b><u>(<code>{len(commands)}</code>) Command(s) Available</u></b>

🔧 <b>Plugin:</b>  <code>{key}</code>
📘 <b>Doc:</b>  <code>{plugins[key].doc}</code>\n\n"""
            for i, cmd in enumerate(commands, start=1):
                out_str += (f"    🤖 <b>cmd(<code>{i}</code>):</b>  <code>{cmd.name}</code>\n"
                            f"    📚 <b>info:</b>  <i>{cmd.doc}</i>\n\n")
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
    await message.edit(out_str, del_in=0, parse_mode='html', disable_web_page_preview=True)

if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge

    def check_owner(func):
        async def wrapper(_, c_q: CallbackQuery):
            if c_q.from_user and c_q.from_user.id == Config.OWNER_ID:
                try:
                    await func(c_q)
                except MessageNotModified:
                    await c_q.answer("Nothing Found to Refresh 🤷‍♂️", show_alert=True)
                except MessageIdInvalid:
                    await c_q.answer("Sorry, I Don't Have Permissions to edit this 😔",
                                     show_alert=True)
            else:
                user_dict = await ubot.get_user_dict(Config.OWNER_ID)
                await c_q.answer(
                    f"Only {user_dict['flname']} Can Access this...! Build Your USERGE-X",
                    show_alert=True)
        return wrapper

    @ubot.on_callback_query(filters.regex(pattern=r"\((.+)\)(next|prev)\((\d+)\)"))
    @check_owner
    async def callback_next_prev(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        n_or_p = str(callback_query.matches[0].group(2))
        p_num = int(callback_query.matches[0].group(3))
        p_num = p_num + 1 if n_or_p == "next" else p_num - 1
        pos_list = cur_pos.split('|')
        if len(pos_list) == 1:
            buttons = parse_buttons(p_num, cur_pos,
                                    lambda x: f"{_CATEGORY.get(x, '📁')} {x}",
                                    userge.manager.get_all_plugins())
        elif len(pos_list) == 2:
            buttons = parse_buttons(p_num, cur_pos,
                                    lambda x: f"🔹 {x}",
                                    userge.manager.get_all_plugins()[pos_list[-1]])
        elif len(pos_list) == 3:
            _, buttons = plugin_data(cur_pos, p_num)
        await callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons))

    @ubot.on_callback_query(filters.regex(pattern=r"back\((.+)\)"))
    @check_owner
    async def callback_back(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split('|')
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
        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons))

    @ubot.on_callback_query(filters.regex(pattern=r"enter\((.+)\)"))
    @check_owner
    async def callback_enter(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split('|')
        if len(pos_list) == 2:
            text, buttons = category_data(cur_pos)
        elif len(pos_list) == 3:
            text, buttons = plugin_data(cur_pos)
        elif len(pos_list) == 4:
            text, buttons = filter_data(cur_pos)
        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons))

    @ubot.on_callback_query(filters.regex(pattern=r"((?:un)?load|(?:en|dis)able)\((.+)\)"))
    @check_owner
    async def callback_manage(callback_query: CallbackQuery):
        task = str(callback_query.matches[0].group(1))
        cur_pos = str(callback_query.matches[0].group(2))
        pos_list = cur_pos.split('|')
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
        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons))

    @ubot.on_callback_query(filters.regex(pattern=r"^mm$"))
    @check_owner
    async def callback_mm(callback_query: CallbackQuery):
        await callback_query.edit_message_text(
            " 𝐔𝐒𝐄𝐑𝐆𝐄-𝐗  𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨 ", reply_markup=InlineKeyboardMarkup(main_menu_buttons()))

    @ubot.on_callback_query(filters.regex(pattern=r"^chgclnt$"))
    @check_owner
    async def callback_chgclnt(callback_query: CallbackQuery):
        if Config.USE_USER_FOR_CLIENT_CHECKS:
            Config.USE_USER_FOR_CLIENT_CHECKS = False
        else:
            Config.USE_USER_FOR_CLIENT_CHECKS = True
        await SAVED_SETTINGS.update_one({'_id': 'CURRENT_CLIENT'},
                                        {"$set": {'is_user': Config.USE_USER_FOR_CLIENT_CHECKS}},
                                        upsert=True)
        await callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(main_menu_buttons()))

    @ubot.on_callback_query(filters.regex(pattern=r"refresh\((.+)\)"))
    @check_owner
    async def callback_exit(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split('|')
        if len(pos_list) == 4:
            text, buttons = filter_data(cur_pos)
        else:
            text, buttons = plugin_data(cur_pos)
        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons))

    def is_filter(name: str) -> bool:
        split_ = name.split('.')
        return bool(split_[0] and len(split_) == 2)

    def parse_buttons(page_num: int,
                      cur_pos: str,
                      func: Callable[[str], str],
                      data: Union[List[str], Dict[str, Any]],
                      rows: int = 5):
        buttons = [InlineKeyboardButton(
            func(x), callback_data=f"enter({cur_pos}|{x})".encode()) for x in sorted(data)]
        pairs = list(map(list, zip(buttons[::2], buttons[1::2])))
        if len(buttons) % 2 == 1:
            pairs.append([buttons[-1]])
        max_pages = ceil(len(pairs) / rows)
        current_page = page_num % max_pages
        if len(pairs) > rows:
            pairs = pairs[current_page*rows:(current_page + 1)*rows] + [
                [
                    InlineKeyboardButton(
                        "⏪ Previous", callback_data=f"({cur_pos})prev({current_page})".encode()),
                    InlineKeyboardButton(
                        "⏩ Next", callback_data=f"({cur_pos})next({current_page})".encode())],
            ]
        pairs += default_buttons(cur_pos)
        return pairs

    def main_menu_buttons():
        return parse_buttons(0, "mm",
                             lambda x: f"{_CATEGORY.get(x, '📁')} {x}",
                             userge.manager.get_all_plugins())

    def default_buttons(cur_pos: str):
        tmp_btns = []
        if cur_pos != "mm":
            tmp_btns.append(InlineKeyboardButton(
                "⬅ Back", callback_data=f"back({cur_pos})".encode()))
            if len(cur_pos.split('|')) > 2:
                tmp_btns.append(InlineKeyboardButton(
                    "🖥 Main Menu", callback_data="mm".encode()))
                tmp_btns.append(InlineKeyboardButton(
                    "🔄 Refresh", callback_data=f"refresh({cur_pos})".encode()))
        else:
            cur_clnt = "👤 USER" if Config.USE_USER_FOR_CLIENT_CHECKS else "⚙️ BOT"
            tmp_btns.append(InlineKeyboardButton(
                f"🔩 Client for Checks and Sudos : {cur_clnt}", callback_data="chgclnt".encode()))
        return [tmp_btns]

    def category_data(cur_pos: str):
        pos_list = cur_pos.split('|')
        plugins = userge.manager.get_all_plugins()[pos_list[1]]
        text = (f"**(`{len(plugins)}`) Plugin(s) Under : "
                f"`{_CATEGORY.get(pos_list[1], '📁')} {pos_list[1]}`  Category**")
        buttons = parse_buttons(0, '|'.join(pos_list[:2]),
                                lambda x: f"🔹 {x}",
                                plugins)
        return text, buttons

    def plugin_data(cur_pos: str, p_num: int = 0):
        pos_list = cur_pos.split('|')
        plg = userge.manager.plugins[pos_list[2]]
        text = f"""🔹 **--Plugin Status--** 🔹

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
            tmp_btns.append(InlineKeyboardButton(
                "❎ Unload", callback_data=f"unload({'|'.join(pos_list[:3])})".encode()))
        else:
            tmp_btns.append(InlineKeyboardButton(
                "✅ Load", callback_data=f"load({'|'.join(pos_list[:3])})".encode()))
        if plg.is_enabled:
            tmp_btns.append(InlineKeyboardButton(
                "➖ Disable", callback_data=f"disable({'|'.join(pos_list[:3])})".encode()))
        else:
            tmp_btns.append(InlineKeyboardButton(
                "➕ Enable", callback_data=f"enable({'|'.join(pos_list[:3])})".encode()))
        buttons = parse_buttons(p_num, '|'.join(pos_list[:3]),
                                lambda x: f"⚖ {x}" if is_filter(x) else f" {x}",
                                (flt.name for flt in plg.commands + plg.filters))
        buttons = buttons[:-1] + [tmp_btns] + [buttons[-1]]
        return text, buttons

    def filter_data(cur_pos: str):
        pos_list = cur_pos.split('|')
        plg = userge.manager.plugins[pos_list[2]]
        flts = {flt.name: flt for flt in plg.commands + plg.filters}
        flt = flts[pos_list[-1]]
        flt_data = f"""
🔖 **Name** : `{flt.name}`
📝 **Doc** : `{flt.doc}`
🤖 **Via Bot** : `{flt.allow_via_bot}`
✅ **Loaded** : `{flt.is_loaded}`
➕ **Enabled** : `{flt.is_enabled}`"""
        if hasattr(flt, 'about'):
            text = f"""**--Command Status--**
{flt_data}
{flt.about}
"""
        else:
            text = f"""⚖ **--Filter Status--** ⚖
{flt_data}
"""
        buttons = default_buttons(cur_pos)
        tmp_btns = []
        if flt.is_loaded:
            tmp_btns.append(InlineKeyboardButton(
                "❎ Unload", callback_data=f"unload({cur_pos})".encode()))
        else:
            tmp_btns.append(InlineKeyboardButton(
                "✅ Load", callback_data=f"load({cur_pos})".encode()))
        if flt.is_enabled:
            tmp_btns.append(InlineKeyboardButton(
                "➖ Disable", callback_data=f"disable({cur_pos})".encode()))
        else:
            tmp_btns.append(InlineKeyboardButton(
                "➕ Enable", callback_data=f"enable({cur_pos})".encode()))
        buttons = [tmp_btns] + buttons
        return text, buttons


    def check_url():
        global MEDIA_TYPE, MEDIA_URL
        media_link = Config.ALIVE_MEDIA
        if media_link:
            imgur = r"^http[s]?://i\.imgur\.com/(\w+)\.(gif|jpg|png)$"
            match = re.search(imgur, media_link)
            if not match:
                telegraph = r"http[s]?://telegra\.ph/file/(\w+)\.(jpg|png)"
                match = re.search(telegraph, media_link)
            if match:
                media_type = match.group(2)
                link = match.group(0)
                limit = 1 if media_type == 'gif' else 5
                req = urllib.request.Request(link, method='HEAD')
                f = urllib.request.urlopen(req)
                if f.status == 200:
                    size = '{:.2f}'.format(int(f.headers['Content-Length']) / float(1 << 20))
                    if float(size) < limit:
                        MEDIA_TYPE = media_type
                        MEDIA_URL = media_link
        
            
            

    @ubot.on_inline_query()
    async def inline_answer(_, inline_query: InlineQuery):
        results = []
        i_q = inline_query.query
        string = i_q.lower()
        str_x = i_q.split(" ", 2)
        string_split = string.split()

        if inline_query.from_user and inline_query.from_user.id == Config.OWNER_ID or inline_query.from_user.id in Config.SUDO_USERS:
            MAIN_MENU = InlineQueryResultArticle(
                        
                        title="Main Menu",
                        input_message_content=InputTextMessageContent(
                            " 𝐔𝐒𝐄𝐑𝐆𝐄-𝐗  𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨 "
                        ),
                        url="https://github.com/code-rgb/USERGE-X",
                        description="Userge-X Main Menu",
                        thumb_url="https://i.imgur.com/1xsOo9o.png",
                        reply_markup=InlineKeyboardMarkup(main_menu_buttons())
                    )           
            results.append(MAIN_MENU)             
        
            if string == "syntax":
                owner = [[
                        InlineKeyboardButton(
                        text="Contact", 
                        url="https://t.me/deleteduser420"
                        )
                ]]
                results.append(
                        InlineQueryResultPhoto(
                            photo_url="https://coverfiles.alphacoders.com/123/123388.png",
                            caption="Hey I solved **𝚂𝚢𝚗𝚝𝚊𝚡's ░ Σrr♢r**",
                            reply_markup=InlineKeyboardMarkup(owner)
                        )
                )

            if string =="rick":
                rick = [[
                        InlineKeyboardButton(
                        text="🔍", 
                        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                        )
                ]]                           
                results.append(
                        InlineQueryResultArticle(
                            title="Not a Rick Roll",
                            input_message_content=InputTextMessageContent(
                                "Search Results"
                            ),
                            description="Definately Not a Rick Roll",
                            thumb_url="https://i.imgur.com/hRCaKAy.png",
                            reply_markup=InlineKeyboardMarkup(rick)
                        )
                )

            if string == "alive":
                buttons = [[InlineKeyboardButton("🔧 SETTINGS", callback_data="settings_btn"),
                            InlineKeyboardButton(text="⚡️ REPO", url=Config.UPSTREAM_REPO)]]

                alive_info = f"""
    **[USERGE-X](https://github.com/code-rgb/USERGE-X) is Up and Running**

 • 🐍 Python :  `v{versions.__python_version__}`
 • 🔥 Pyrogram :  `v{versions.__pyro_version__}`
 • 🧬 𝑿 :  `v{get_version()}`

    🕔 Uptime : {userge.uptime}
"""  
                if not MEDIA_URL:
                    check_url()
                
                if MEDIA_URL:
                    if MEDIA_TYPE == 'gif':
                        results.append(
                            InlineQueryResultAnimation(
                                animation_url=MEDIA_URL,
                                caption=alive_info,
                                reply_markup=InlineKeyboardMarkup(buttons)
                            )
                        )

                    else:
                        results.append(
                            InlineQueryResultPhoto(
                                photo_url=MEDIA_URL,
                                caption=alive_info,
                                reply_markup=InlineKeyboardMarkup(buttons)
                            )
                        )


                else: #default
                    random_alive = random.choice(ALIVE_IMGS) 
                    results.append(
                            InlineQueryResultPhoto(
                                photo_url=random_alive,
                                caption=alive_info,
                                reply_markup=InlineKeyboardMarkup(buttons)
                            )
                    )

            if string == "geass":
                results.append(
                        InlineQueryResultAnimation(
                            animation_url="https://i.imgur.com/DeZHcRK.gif",
                            caption="To defeat evil, I must become a greater evil",
                            
                        )
                )

            if string =="gapps":
                buttons = [[InlineKeyboardButton("Open GApps", callback_data="open_gapps"),
                           InlineKeyboardButton("Flame GApps", callback_data="flame_gapps")],
                           [InlineKeyboardButton("Nik GApps", callback_data="nik_gapps")]]          
                results.append(
                        InlineQueryResultArticle(
                            title="GApps",
                            input_message_content=InputTextMessageContent(
                                "[\u200c](https://i.imgur.com/BZBMrfn.jpg) **LATEST Android 10 arm64 GApps**" 
                            ),
                            description="Get Latest GApps Download Links Directly from SF",
                            thumb_url="https://i.imgur.com/Npzw8Ph.png",
                            reply_markup=InlineKeyboardMarkup(buttons)
                        )
                )

            if len(string_split) == 2:     #workaround for list index out of range
                if string_split[0] == "ofox":
                    codename = string_split[1]
                    t = TelegraphPoster(use_api=True)
                    t.create_api_token('Userge-X')
                    photo = "https://i.imgur.com/582uaSk.png" 
                    api_host = 'https://api.orangefox.download/v2/device/'
                    try:
                        cn = requests.get(f"{api_host}{codename}")
                        r = cn.json()
                    except ValueError:
                        return
                    s = requests.get(f"{api_host}{codename}/releases/stable/last").json()
                    info = f"📱 **Device**: {r['fullname']}\n"
                    info += f"👤 **Maintainer**: {r['maintainer']['name']}\n\n"
                    recovery = f"🦊 <code>{s['file_name']}</code>\n"
                    recovery+= f"📅 {s['date']}\n"
                    recovery += f"ℹ️ **Version:** {s['version']}\n"
                    recovery+= f"📌 **Build Type:** {s['build_type']}\n"
                    recovery+= f"🔰 **Size:** {s['size_human']}\n\n"
                    recovery+= "📍 **Changelog:**\n"
                    recovery+= f"<code>{s['changelog']}</code>\n\n" 
                    msg = info
                    msg += recovery
                    notes_ = s.get('notes')
                    if notes_: 
                        notes = t.post(
                        title='READ Notes', 
                        author="", 
                        text=notes_
                        )
                        buttons = [[InlineKeyboardButton("🗒️ NOTES", url=notes['url']),
                                    InlineKeyboardButton("⬇️ DOWNLOAD", url=s['url'])]]
                    else:
                        buttons = [[InlineKeyboardButton(text="⬇️ DOWNLOAD", url=s['url'])]]

                    results.append(
                            InlineQueryResultPhoto(
                                photo_url=photo,
                                thumb_url="https://i.imgur.com/o0onLYB.jpg",
                                title="Latest OFOX RECOVERY",
                                description=f"For device : {codename}",
                                caption=msg,
                                reply_markup=InlineKeyboardMarkup(buttons)
                            )
                    )

            if string =="repo":        
                results.append(REPO_X)

            if str_x[0].lower() == "op" and len(str_x) > 1:        
                txt = i_q[3:]          # TODO change it

                opinion = os.path.join(PATH, "emoji_data.txt")
                try:
                    view_data = json.load(open(opinion))
                except:
                    view_data = False

                if view_data:
                    # Uniquely identifies an inline message
                    new_id = {int(inline_query.id) : [{}]}
                    view_data.update(new_id)
                    json.dump(view_data, open(opinion,'w'))
                else:
                    d = {int(inline_query.id) : [{}]}
                    json.dump(d, open(opinion,'w'))

                buttons = [[
                        InlineKeyboardButton("👍", callback_data=f"op_y_{inline_query.id}"),
                        InlineKeyboardButton("👎", callback_data=f"op_n_{inline_query.id}")
                ]]                           
                results.append(
                        InlineQueryResultArticle(
                            
                            title="Ask For Opinion",
                            input_message_content=InputTextMessageContent(txt),
                            description="e.g @yourbot op Are Cats Cute?",
                            thumb_url="https://i.imgur.com/Zlc98qS.jpg",
                            reply_markup=InlineKeyboardMarkup(buttons)
                        )
                )    

            if string =="buttonnn":          
                async for data in BUTTON_BASE.find():
                    button_data = data['msg_data']
                text, buttons = pb(button_data)
                try:
                    photo_url = data['photo_url']
                except KeyError:
                    photo_url = None
                if photo_url:
                    results.append(
                            InlineQueryResultPhoto(
                                photo_url=photo_url,
                                caption=text,
                                reply_markup=buttons
                            )
                    )
                else:    
                    results.append(
                                InlineQueryResultArticle(
                                    title=text,
                                    input_message_content=InputTextMessageContent(text),
                                    reply_markup=buttons
                                )
                    )
           
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
                        new_id = {str(inline_query.id) : {'user_id': user_id, 'msg': msg}}
                        view_data.update(new_id)
                        json.dump(view_data, open(secret,'w'))
                    else:
                        d = {str(inline_query.id) : {'user_id': user_id, 'msg': msg}}
                        json.dump(d, open(secret,'w'))
                    
                    buttons = [[InlineKeyboardButton("🔐 REVEAL", callback_data=f"secret_{inline_query.id}")]]
                    results.append(
                                InlineQueryResultArticle(
                                    title="Send A Secret Message",
                                    input_message_content=InputTextMessageContent(f"📩 <b>TOPSECRET!</b> for {user_name}. Only he/she can open it."),
                                    description=f"Send Secret Message to: {user_name}",
                                    thumb_url="https://i.imgur.com/c5pZebC.png",
                                    reply_markup=InlineKeyboardMarkup(buttons)
                                )
                    )
                else:
                    results = [(
                                InlineQueryResultArticle(
                                    title="Send A Secret Message",
                                    input_message_content=InputTextMessageContent("Do `.secret` for more info"),
                                    description="secret @username message ..."
                                )
                    )]
                    await inline_query.answer(
                        results=results,
                        cache_time=1,
                        switch_pm_text="🔒 SECRETS",
                        switch_pm_parameter="start"
                    )
                    return
        else:
            results.append(REPO_X)
        try:
            if len(results) != 0:
                await inline_query.answer(results=results, cache_time=1)
        except MessageEmpty:
            return
        
