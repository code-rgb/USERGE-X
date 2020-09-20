# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.
"""Module that handles Inline Help"""

from userge import userge, Message, Config
from pyrogram.types import (  
     InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery)
from pyrogram import filters


HELP_BUTTONS = None

PRIV_USERS = list(Config.SUDO_USERS)
PRIV_USERS.append(Config.OWNER_ID)


rick_roll = """
We're no strangers to love
You know the rules and so do I
A full commitment's what I'm thinking of
You wouldn't get this from any other guy

I just wanna tell you how I'm feeling
Gotta make you understand

Never gonna give you up
Never gonna let you down
Never gonna run around and desert you
Never gonna make you cry
Never gonna say goodbye
Never gonna tell a lie and hurt you

We've known each other for so long
Your heart's been aching, but
You're too shy to say it
Inside, we both know what's been going on
We know the game and we're gonna play it

And if you ask me how I'm feeling
Don't tell me you're too blind to see

Never gonna give you up
Never gonna let you down
...
"""


COMMANDS = {
            "secret" : { 'help_txt' : '**Send a secret message to a user**\n (only the entered user and you can view  the message)\n\n`secret @username [text]`', 'i_q' : 'secret @DeletedUser420 This is a secret message'},
            "alive" : { 'help_txt' : '**Alive Command for USERGE-X**', 'i_q' : 'alive'},
            "opinion" : { 'help_txt' : '**Ask for opinion via inline**\n\n`op [Question or Statement]`', 'i_q' : 'op Are Cats Cute ?'},
            "repo" : { 'help_txt' : '**Your USERGE-X Github repo**', 'i_q' : 'repo'},
            "gapps" : { 'help_txt' : '**Lastest arm64 Gapps**\n\n`Choose from Niksgapps, Opengapps and Flamegapps`', 'i_q' : 'gapps'},
            "ofox" : { 'help_txt' : '**Lastest Ofox Recovery for supported device, Powered By offcial Ofox API**\n\n`ofox <device codename>`', 'i_q' : 'ofox whyred'},
            "rick" : { 'help_txt' : f'**Useless Rick Roll**\n\n{rick_roll}\n`rick`', 'i_q' : 'rick'},
            "help" : { 'help_txt' : '**Help For All Userbot plugins**\n\n**Note:** `You can load and unload a plugin`', 'i_q' : ''},
            "stylish" : { 'help_txt' : '**Write it in Style**\n\nplugin to decorate text with unicode fonts.\n`stylish [text]`', 'i_q' : 'stylish USERGE-X'}
            }


if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge


    def help_btn_generator():
        btn = []
        b = []
        for cmd in list(COMMANDS.keys()):
            name = cmd.capitalize()
            call_back = f"ihelp_{cmd}"
            b.append(
               InlineKeyboardButton(name, callback_data=call_back)
            )
            if len(b) == 3:   # no. of columns
                btn.append(b)
                b = []
        if len(b) != 0: 
            btn.append(b)     # buttons in the last row
        return btn
   

    if not HELP_BUTTONS:
        HELP_BUTTONS = help_btn_generator()

    BACK_BTN = InlineKeyboardButton(" ◀️  Back ", callback_data="backbtn_ihelp")

    inline_help_txt ="<u><b>INLINE COMMANDS</b></u>\n\nHere is a list of all available inline commands.\nChoose a command and click **📕  EXAMPLE** to know the use."
            

    @ubot.on_message(filters.user(PRIV_USERS) & filters.private & (filters.command("inline") | filters.regex(pattern=r"^/start inline$")))
    async def inline_help(_, message: Message):
        await ubot.send_message(
            chat_id=message.chat.id,
            text=inline_help_txt,
            reply_markup=InlineKeyboardMarkup(HELP_BUTTONS)
        )


    @ubot.on_callback_query(filters.user(PRIV_USERS) & filters.regex(pattern=r"^backbtn_ihelp$"))
    async def back_btn(_, c_q: CallbackQuery): 
        await c_q.edit_message_text(
            text=inline_help_txt,
            reply_markup=InlineKeyboardMarkup(HELP_BUTTONS)
        )


    @ubot.on_callback_query(filters.user(PRIV_USERS) & filters.regex(pattern=r"^ihelp_([a-zA-Z]+)$"))
    async def help_query(_, c_q: CallbackQuery): 
        command_name = c_q.matches[0].group(1)
        msg = COMMANDS[command_name]['help_txt']
        switch_i_q = COMMANDS[command_name]['i_q']
        buttons = [[InlineKeyboardButton(BACK_BTN, " 📕  EXAMPLE ", switch_inline_query_current_chat=switch_i_q)]]
        await c_q.edit_message_text(
                msg,
                reply_markup=InlineKeyboardMarkup(buttons)
        )