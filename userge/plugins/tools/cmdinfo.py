# Copyright (C) 2021 by USERGE-X
#
# Author: GitHub.com/code-rgb [TG - @deleteduser420]
#
# All rights reserved.


import os
from re import compile as comp_regex

from git import Repo
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from userge import Config, Message, userge
from userge.utils import check_owner, humanbytes

plugin_regex = comp_regex(r"Path[\s:]{1,5}(userge/plugins/\w+/\w+\.py)")


@userge.on_cmd(
    "cmdinfo",
    about={
        "header": "find plugin and other info for a given command",
        "description": "you can also provide optional text to search within the plugin",
        "usage": "{tr}cmdinfo [cmd] | [optional text]",
        "examples": "{tr}cmdinfo .ars\n" "  {tr}cmdinfo .ars | tracemoepy",
    },
)
async def see_info(message: Message):
    cmd_str = message.input_str
    if not cmd_str:
        return await message.err("Provide a Valid Command to Search", del_in=5)
    word = None
    if "|" in cmd_str:
        cmd_str, word = cmd_str.split("|", 1)
    cmd_str = cmd_str.strip()
    other_trigger = [".", Config.SUDO_TRIGGER]
    cmd_list = list(userge.manager.commands)
    found = True
    if not (cmd_str.startswith(Config.CMD_TRIGGER) and (cmd_str in cmd_list)):
        found = False
        for character in other_trigger:
            if cmd_str.startswith(character) and (
                cmd_str.replace(character, Config.CMD_TRIGGER) in cmd_list
            ):
                cmd_str = cmd_str.replace(character, Config.CMD_TRIGGER)
                found = True
                break
        if cmd_str.isalpha() and (Config.CMD_TRIGGER + cmd_str) in cmd_list:
            found = True
            cmd_str = Config.CMD_TRIGGER + cmd_str
    if not found:
        return await message.err("provide a valid command name", del_in=5)
    repo = Repo()
    try:
        branch = repo.active_branch.name
    except Exception:
        with open(".git/HEAD", "r") as gitfile:
            branch = gitfile.read().split("/")[-1].strip()
    if branch == "master":
        branch = "alpha"
    plugin_name = userge.manager.commands[cmd_str].plugin_name
    plugin_loc = ("/" + userge.manager.plugins[plugin_name].parent).replace(
        "/plugins", ""
    )
    if plugin_loc == "/xtra":
        extra_plugins = (
            "https://github.com/code-rgb/Userge-Plugins/blob/master/plugins/"
        )
        plugin_link = f"{extra_plugins}/{plugin_name}.py"
    elif plugin_loc == "/custom":
        custom_plugins = os.environ.get("CUSTOM_PLUGINS_REPO", "")
        plugin_link = f"{custom_plugins}/blob/master/plugins/{plugin_name}.py"
    elif plugin_loc == "/temp":
        plugin_link = False
    else:
        plugin_link = "{}/blob/{}/userge/plugins{}/{}.py".format(
            Config.UPSTREAM_REPO, branch, plugin_loc, plugin_name
        )
    local_path = f"userge/plugins{plugin_loc}/{plugin_name}.py"
    f_size = humanbytes(os.stat(local_path).st_size)
    search_path = count_lines(local_path, word)
    result = f"""
<b>•>  CMD:</b>  <code>{cmd_str}</code>

📂  <b>Path :</b>  <code>{local_path}</code><pre>
  - Size on Disk: {f_size}
  - No. of lines: {search_path[0]}</pre>
"""
    if plugin_link:
        result += f"\n💻  <b>[View Code on Github]({plugin_link})</b>"
    if word:
        result += f"\n\n🔎  <b>Matches for:</b> {word}\n"
        s_result = ""
        if len(search_path[1]) == 0:
            s_result += "  ❌  Not Found !"
        else:
            for line_c, line in enumerate(search_path[1], start=1):
                s_result += f"[#L{line}]({plugin_link}#L{line})  "
                if line_c >= 8:
                    break
        result += "  <b>{}</b>".format(s_result)
    buttons = (
        InlineKeyboardMarkup(
            [[InlineKeyboardButton("📤  Upload", callback_data="plugin_upload")]]
        )
        if message.client.is_bot
        else None
    )
    await message.edit(result, disable_web_page_preview=True, reply_markup=buttons)


def count_lines(cmd_path: str, word: str = None):
    arr = []
    num_lines = 0
    if word:
        word = word.strip().lower()
    with open(cmd_path, "r") as f:
        for num_lines, line in enumerate(f, start=1):
            if word and word in line.lower():
                arr.append(num_lines)
    return num_lines, arr


if userge.has_bot:

    @userge.bot.on_callback_query(filters.regex(pattern=r"^plugin_upload$"))
    @check_owner
    async def plugin_upload_(c_q: CallbackQuery):
        if match := plugin_regex.search(c_q.message.text):
            if os.path.exists(plugin_loc := match.group(1)):
                p_name = plugin_loc.split("/")[-1]
                await c_q.answer(f"📤  Uploading - {p_name}")
                await userge.bot.send_chat_action(
                    c_q.message.chat.id, "upload_document"
                )
                await userge.bot.send_document(
                    chat_id=c_q.message.chat.id,
                    document=plugin_loc,
                    caption=p_name,
                    parse_mode="html",
                    disable_notification=True,
                    reply_to_message_id=c_q.message.message_id,
                )
            else:
                await c_q.answer("❌ ERROR: Plugin Not Found !")
        else:
            await c_q.answer()
