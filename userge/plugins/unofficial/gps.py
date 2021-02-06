"""GPS"""

from geopy.geocoders import Nominatim
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from userge import Message, userge


@userge.on_cmd(
    "gps",
    about={
        "header": "locate the coordinates by address, cities, countries "
        "or landmarks",
        "usage": "{tr}gps [location]\ne.g {tr}gps 175 5th Avenue NYC",
    },
)
async def gps_locate_(message: Message):
    """send a venue"""
    loc_ = message.input_str
    if not loc_:
        return await message.err("Provide a valid location name", del_in=5)
    await message.edit("Finding This Location In Maps Server.....")
    titlex = None
    if "|" in loc_:
        loc_x = loc_.split("|", 1)
        if len(loc_x) == 2:
            titlex = loc_x[0]
            loc_ = loc_x[1]
    geolocator = Nominatim(user_agent="USERGE-X")
    geoloc = geolocator.geocode(loc_)
    if not geoloc:
        return await message.err("**404 Location Not Found**", del_in=5)
    address = geoloc.address
    place = address.split(",")
    name = titlex or place[0]
    lon = geoloc.longitude
    lat = geoloc.latitude
    await message.delete()
    reply = message.reply_to_message
    reply_id = reply.message_id if reply else None
    buttons = None
    if message.client.is_bot:
        g_maps = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🗺️ Google Maps", url=g_maps)]]
        )
    await message.client.send_venue(
        message.chat.id,
        lat,
        lon,
        name,
        address,
        reply_to_message_id=reply_id,
        reply_markup=buttons,
    )
