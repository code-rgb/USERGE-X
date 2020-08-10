from uuid import uuid4
from pyrogram import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQuery)
from userge import userge, Message, Config
#Filters

if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge
    results = []
    @ubot.on_inline_query()
    async def inline_answer(_, inline_query: InlineQuery):
        button = [[
                InlineKeyboardButton(
                text="🏠 DEMO BUTTON", 
                url="https://www.youtube.com/"
                )
        ]]
                
        if inline_query.from_user and inline_query.from_user.id == Config.OWNER_ID:
            results.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title="Demo Inline Test 1",
                    input_message_content=InputTextMessageContent(
                        "Demo Inline Test 2"
                    ),
                    url="https://google.com",
                    description="Demo Inline Test 3",
                    #thumb_url="https://i.imgur.com/1xsOo9o.png",
                    reply_markup=InlineKeyboardMarkup(button)
                )
            )
        await inline_query.answer(results=results, cache_time=1)
