# Ported From [PaperPlane Userbot](https://github.com/RaphielGang/Telegram-Paperplane)

""" Userbot module for getting the date
    and time of any country or the userbot server.  """

import os
from datetime import datetime as dt

from pytz import country_names as c_n
from pytz import country_timezones as c_tz
from pytz import timezone as tz
from userge import Message, get_collection, userge

COUNTRY_CITY = os.environ.get("COUNTRY_CITY", None)
LOC_NAME = get_collection("LOC_NAME")


async def get_tz(con):
    """ Get time zone of the given country. """
    if "(Uk)" in con:
        con = con.replace("Uk", "UK")
    if "(Us)" in con:
        con = con.replace("Us", "US")
    if " Of " in con:
        con = con.replace(" Of ", " of ")
    if "(Western)" in con:
        con = con.replace("(Western)", "(western)")
    if "Minor Outlying Islands" in con:
        con = con.replace("Minor Outlying Islands", "minor outlying islands")
    if "Nl" in con:
        con = con.replace("Nl", "NL")

    for c_code in c_n:
        if con == c_n[c_code]:
            return c_tz[c_code]
    try:
        if c_n[con]:
            return c_tz[con]
    except KeyError:
        return


@userge.on_cmd(
    "dt(?: |$)(.*)(?<![0-9])(?: |$)([0-9]+)?",
    about={
        "header": "Get Date and Time of a country",
        "description": "Get the Date and Time of a country. If a country has multiple timezones, "
        "it will list all of them and let you select one.",
        "usage": "{tr}dt <country name/code> <timezone number>",
        "examples": ["{tr}dt Russia 2"],
        "default timezone": 'Choose from the <b><a href="https://pastebin.com/raw/0KSh9CMj">Timezones Avaliable</a></b>'
        "\n and Set any of them in (<code>COUNTRY_CITY</code>) for your default timezone and see help `{tr}setloc` to set Display Location",
    },
)
async def date_time_func(message: Message):
    """get date and time"""
    # For .dt command, return the date and time of
    # 1. The country passed as an argument,
    # 2. The default userbot country,
    # 3. The server where the userbot runs.
    con = message.matches[0].group(1).title()
    tz_num = message.matches[0].group(2)
    d_form = "%d/%m/%y - %A"
    t_form = "%I:%M %p"
    c_name = None

    if len(con) > 4:
        try:
            c_name = c_n[con]
        except KeyError:
            c_name = con
        timezones = await get_tz(con)
    elif COUNTRY_CITY:
        timezones = [COUNTRY_CITY]
    else:
        await message.edit(
            f"`It's`  **{dt.now().strftime(t_form)}** `on` **{dt.now().strftime(d_form)}**  `here.`"
        )
        return

    if not timezones:
        await message.err("Invaild country.", del_in=5)
        return

    if len(timezones) == 1:
        time_zone = timezones[0]
    elif len(timezones) > 1:
        if tz_num:
            tz_num = int(tz_num)
            time_zone = timezones[tz_num - 1]
        else:
            return_str = f"`{c_name} has multiple timezones:`\n"

            for i, item in enumerate(timezones):
                return_str += f"`{i+1}. {item}`\n"

            return_str += "\n`Choose one by typing the number "
            return_str += "in the command.`\n"
            return_str += f"Example: .dt {c_name} 2"

            await message.edit(return_str)
            return

    dtnow = dt.now(tz(time_zone)).strftime(d_form)
    dttime = dt.now(tz(time_zone)).strftime(t_form)

    if not c_name:
        s_o = await LOC_NAME.find_one({"_id": "LOC_NAME"})
        c_name = s_o["name"] if s_o else ""

    await message.edit(
        f"<code>It's</code>  **{dttime}** <code>on</code> **{dtnow}** <code>in</code> {c_name} ({time_zone} timezone)."
    )


@userge.on_cmd(
    "setloc",
    about={
        "header": "Set the location disaplay name with the time zone you set",
    },
)
async def set_loc_(message: Message):
    """set display location"""
    loc_name = message.input_str
    if not loc_name:
        return await message.err("Input Not found", del_in=3)
    result = await LOC_NAME.update_one(
        {"_id": "LOC_NAME"}, {"$set": {"name": loc_name}}, upsert=True
    )
    out = "{} Display Location to <b>{}</b>"
    if result.upserted_id:
        out = out.format("Added", loc_name)
    else:
        out = out.format("Updated", loc_name)
    await message.edit(out, del_in=5)
