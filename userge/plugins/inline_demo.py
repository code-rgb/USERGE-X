from uuid import uuid4
from pyrogram import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQuery, Emoji)
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
        string = inline_query.query.lower()
        if string == "":
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

        if string =="lmao":
            button = [[
                    InlineKeyboardButton(
                    text="YOU TYPED LMAO", 
                    url="https://www.youtube.com/"
                    )
            ]]
                    
            if inline_query.from_user and inline_query.from_user.id == Config.OWNER_ID:
                results.append(
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title="IM A COOL FIRE EMOJI",
                        input_message_content=InputTextMessageContent(
                            "VROOOOOO"
                        ),
                        url="https://google.com",
                        description="FUCKING FIRE BRO",
                        thumb_url="https://i.imgur.com/1xsOo9o.png",
                        reply_markup=InlineKeyboardMarkup(button)
                    )
                )
            
        elif string == "error":
            switch_pm_text = f"{Emoji.SHARK} Syntax ERROR BABYYYY"

            if inline_query.from_user and inline_query.from_user.id == Config.OWNER_ID:
                results.append(
                    InlineQueryResultPhoto(
                        photo_url="https://i.imgur.com/53mdl2v.png",
                        # thumb_url="https://i.imgur.com/f32hngs.jpg",
                        title="You Solved Syntax's Error",
                        description="Haha YES",
                        caption=f"Hey, I found @deleteduser420 {Emoji.SHARK}",
                        # input_message_content=InputTextMessageContent(f"Hey, I found @ColinShark {Emoji.SHARK}"),
                    )
                )
                
        await inline_query.answer(results=results, cache_time=1)
        return