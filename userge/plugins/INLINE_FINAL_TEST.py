from uuid import uuid4
from pyrogram import InlineQueryResultArticle, __version__, InlineQueryResultPhoto
from pyrogram import errors, InlineKeyboardMarkup, InputTextMessageContent, InlineKeyboardButton, Emoji, InlineQuery
from userge import userge, Message, Config, get_collection

FIRE_THUMB = "https://i.imgur.com/qhYYqZa.png"

if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge
  
@ubot.on_inline_query()
async def inline_query_handler(_, query: InlineQuery):
    string = query.query.lower()
    results = []
    if string == "":
      results.append(InlineQueryResultArticle(
                    title="Types",
                    description="Pyrogram Bound Methods online documentation page",
                    input_message_content=InputTextMessageContent(
                        f"{Emoji.FIRE} **Pyrogram Bound Methods**\n\n"
                        f"`This page contains all available bound methods existing in Pyrogram v{VERSION}.`"
                    ),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(
                            f"{Emoji.OPEN_BOOK} Online docs",
                            url="https://docs.pyrogram.org/api/bound-methods"
                        )]]
                    ),
                    
                ))
      await query.answer(
            results=results,
            cache_time=2,
            switch_pm_text=f"{Emoji.MAGNIFYING_GLASS_TILTED_RIGHT} I WILL FIND YOU AND I WILL KILL YOU",
            switch_pm_parameter="start",
        )

      return

