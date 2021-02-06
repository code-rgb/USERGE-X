from userge import Message, userge
from userge.utils import rand_array


@userge.on_cmd(
    "rand",
    about={
        "header": "Gives a random Output from given Input",
        "usage": "{tr}rand 1 2 3 4",
    },
)
async def random_pick_(message: Message):
    """random picker"""
    input_str = message.input_str
    if not input_str:
        await message.err("Give some items to pick from", del_in=5)
        return
    a = input_str.split()
    if len(a) < 2:
        await message.err("Atleast 2 or more items are required!", del_in=5)
        return
    pick = rand_array(a)
    result = f"""
**Query: **
`{input_str}`
**Output: **
`{pick}`
"""
    await message.edit(result)
