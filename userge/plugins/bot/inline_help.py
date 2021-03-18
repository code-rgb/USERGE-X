# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.

"""Module that handles Inline Help"""

from asyncio import gather

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from userge import Config, Message, userge
from userge.utils import sublists

HELP_BUTTONS = None
OwnerFilter = filters.user(list(Config.OWNER_ID))

_COMMANDS = {
    "secret": {
        "help_txt": "**Send a secret message to a user**\n (only the entered user and you can view the message)\n\n>>>  `secret @username [text]`",
        "i_q": "secret @DeletedUser420 This is a secret message",
    },
    "troll": {
        "help_txt": "**Troll to a user**\n (everyone can view the message except the entered user)\n\n>>>  `troll @username [text]`",
        "i_q": "troll @Lostb053 Lostboy can view this message",
    },
    "alive": {
        "help_txt": "**Alive Command for USERGE-X**\nHere You can view Uptime, Setting and Versions of your bot and when you change settings they are updated in Real-time UwU\n\n>>>  `alive`",
        "i_q": "alive",
    },
    "opinion": {
        "help_txt": "**Ask for opinion via inline**\nYou can now send multiple opinion messages at once\n**Note: **All button data is cleared as soon as you restart or update the bot\n\n>>>  `op [Question or Statement]`",
        "i_q": "op Are Cats Cute ?",
    },
    "repo": {
        "help_txt": "**Your USERGE-X Github repo**\nwith direct deploy button\n\n>>>  `repo`",
        "i_q": "repo",
    },
    "gapps": {
        "help_txt": "**Lastest arm64 Gapps for <u>Android 10 Only !</u>**\nChoose from Niksgapps, Opengapps and Flamegapps\n\n>>>  `gapps`",
        "i_q": "gapps",
    },
    "ofox": {
        "help_txt": "**Lastest Ofox Recovery for supported device, Powered By offcial Ofox API v2**\n\n>>>  `ofox [device codename]`",
        "i_q": "ofox whyred",
    },
    "reddit": {
        "help_txt": '**Get Reddit Image post**\nGet Random Reddit meme or a post from specific subreddit, if you want post from specific subreddit do "reddit [subreddit]."\n\n>>> `reddit  or  reddit dankmemes.`',
        "i_q": "reddit nextfuckinglevel.",
    },
    "help": {
        "help_txt": "**Help For All Userbot plugins**\n**Note:** `You can also load and unload a plugin, and which chat types the commands is permitted`",
        "i_q": "",
    },
    "stylish": {
        "help_txt": "**Write it in Style**\nplugin to decorate text with unicode fonts.\n\n>>>  `stylish [text]`",
        "i_q": "stylish USERGE-X",
    },
    "ytdl": {
        "help_txt": f"**Download YouTube Videos or Audio with Buttons**\nTo Download Video / Audio from youtube with desired quality.\n\n>>>  `ytdl [URL or Text]\n   Non-Inline: {Config.CMD_TRIGGER}iytdl [URL / Text] or [Reply to URL / Text]`",
        "i_q": "ytdl https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    },
    "spoiler": {
        "help_txt": "**Send Saved Spoiler Via Inline**\n For more info see `.help spoiler`\n\n>>>  `spoiler [ID]`",
        "i_q": "spoiler",
    },
    "btn": {
        "help_txt": "**Get upto 15 of your most recently created inline messages in the inline query, so you can post it in any channel or group effortlessly**\n For Creating inline messages see `.help .ibutton`\n\n>>>  `btn`",
        "i_q": "btn",
    },
    "anime": {
        "help_txt": "**Anime Downloader**\nSearch Anime via inline bot and then choose episodes number and desired quality\n\n>>> `anime [Query]`",
        "i_q": "anime Naruto",
    },
}


if userge.has_bot:

    async def help_btn_generator():
        help_list = [
            InlineKeyboardButton(cmd.capitalize(), callback_data="ihelp_" + cmd)
            for cmd in list(_COMMANDS)
        ]
        return InlineKeyboardMarkup(sublists(help_list))

    async def help_btn():
        global HELP_BUTTONS
        if HELP_BUTTONS is None:
            HELP_BUTTONS = await help_btn_generator()
        return HELP_BUTTONS

    inline_help_txt = (
        " <u><b>INLINE COMMANDS</b></u>\n\nHere is a list of all available inline commands."
        "\nChoose a command and for usage see:\n**📕  EXAMPLE**"
    )

    @userge.bot.on_message(
        OwnerFilter
        & filters.private
        & (filters.command("inline") | filters.regex(pattern=r"^/start inline$"))
    )
    async def inline_help(_, message: Message):
        await userge.bot.send_message(
            chat_id=message.chat.id,
            text=inline_help_txt,
            reply_markup=(await help_btn()),
        )

    @userge.bot.on_callback_query(
        OwnerFilter & filters.regex(pattern=r"^backbtn_ihelp$")
    )
    async def back_btn(_, c_q: CallbackQuery):
        await gather(
            c_q.answer(),
            c_q.edit_message_text(
                text=inline_help_txt, reply_markup=(await help_btn())
            ),
        )

    @userge.bot.on_callback_query(
        OwnerFilter & filters.regex(pattern=r"^ihelp_([a-zA-Z]+)$")
    )
    async def help_query(_, c_q: CallbackQuery):
        command_name = c_q.matches[0].group(1)
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("◀️  Back", callback_data="backbtn_ihelp"),
                    InlineKeyboardButton(
                        "📕  EXAMPLE",
                        switch_inline_query_current_chat=_COMMANDS[command_name]["i_q"],
                    ),
                ]
            ]
        )
        await gather(
            c_q.answer(),
            c_q.edit_message_text(
                _COMMANDS[command_name]["help_txt"], reply_markup=buttons
            ),
        )
