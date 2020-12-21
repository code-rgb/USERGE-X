from enum import Enum, auto

from bs4 import BeautifulSoup as soup
from pyrogram import raw, types
from pyrogram.parser.parser import Parser
from pyrogram.raw.functions.users import GetUsers
from pyrogram.types.messages_and_media.message_entity import MessageEntity

from userge.core.ext.raw_client import RawClient as userge


class AutoName(Enum):
    def _generate_next_value_(self, *args):
        return self.lower()


class MessageEntityType(AutoName):
    MENTION = auto()
    HASHTAG = auto()
    CASHTAG = auto()
    BOT_COMMAND = auto()
    URL = auto()
    EMAIL = auto()
    PHONE_NUMBER = auto()
    BOLD = auto()
    ITALIC = auto()
    UNDERLINE = auto()
    STRIKETHROUGH = auto()
    CODE = auto()
    PRE = auto()
    TEXT_LINK = auto()
    TEXT_MENTION = auto()
    BLOCKQUOTE = auto()


RAW_ENTITIES_TO_TYPE = {
    raw.types.MessageEntityMention: MessageEntityType.MENTION,
    raw.types.MessageEntityHashtag: MessageEntityType.HASHTAG,
    raw.types.MessageEntityCashtag: MessageEntityType.CASHTAG,
    raw.types.MessageEntityBotCommand: MessageEntityType.BOT_COMMAND,
    raw.types.MessageEntityUrl: MessageEntityType.URL,
    raw.types.MessageEntityEmail: MessageEntityType.EMAIL,
    raw.types.MessageEntityBold: MessageEntityType.BOLD,
    raw.types.MessageEntityItalic: MessageEntityType.ITALIC,
    raw.types.MessageEntityCode: MessageEntityType.CODE,
    raw.types.MessageEntityPre: MessageEntityType.PRE,
    raw.types.MessageEntityUnderline: MessageEntityType.UNDERLINE,
    raw.types.MessageEntityStrike: MessageEntityType.STRIKETHROUGH,
    raw.types.MessageEntityBlockquote: MessageEntityType.BLOCKQUOTE,
    raw.types.MessageEntityTextUrl: MessageEntityType.TEXT_LINK,
    raw.types.MessageEntityMentionName: MessageEntityType.TEXT_MENTION,
    raw.types.MessageEntityPhone: MessageEntityType.PHONE_NUMBER,
    raw.types.InputMessageEntityMentionName: MessageEntityType.TEXT_MENTION,  # <- HACKS
}


async def e_gen(entity, client):
    entity_type = RAW_ENTITIES_TO_TYPE.get(entity.__class__)
    if entity_type is None:
        return None

    # language=getattr(entity, "language", None),
    return MessageEntity(
        type=entity_type.value,
        offset=entity.offset,
        length=entity.length,
        url=getattr(entity, "url", None),
        user=(await get_user(entity)),
        client=client,
    )


async def get_user(entity):
    user_id = getattr(getattr(entity, "user_id", None), "user_id", None)
    if not user_id:
        return
    k = await userge.send(GetUsers(id=[await userge.resolve_peer(user_id)]))
    return types.User._parse(userge, k[0])


async def mixed_to_html(text: str):
    pyro_entity = types.List()
    x = Parser(userge)
    y = await x.parse(text, mode="combined")
    for i in y["entities"]:
        ent = await e_gen(i, userge)
        if ent:
            pyro_entity.append(ent)
    out = x.unparse(y["message"], pyro_entity, is_html=True)
    return str(soup(out, "html.parser"))
