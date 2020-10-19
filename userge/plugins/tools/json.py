
import re
import json
import yaml
from userge import userge, Message


@userge.on_cmd("json", about={
    'header': "message object to json",
    'usage': "reply {tr}json to any message"})
async def jsonify(message: Message):
    msg = str(message.reply_to_message) if message.reply_to_message else str(message)
    await message.edit_or_send_as_file(text=msg, filename="json.txt", caption="Too Large")


@userge.on_cmd("yaml", about={
    'header': "message object to yaml",
    'usage': "reply {tr}yaml to any message"})
async def yamlify(message: Message):
    """get yaml"""
    msg = str(message.reply_to_message) if message.reply_to_message else str(message)
    yaml_ify = yaml.dump(json.loads(msg), allow_unicode=True)
    regex = r"(\s+|)(?:- _:|_:)[\s]"
    result = re.sub(regex, " ", yaml_ify, re.MULTILINE)
    if result:
        await message.edit_or_send_as_file(
            text=f"```{result[1:]}```",
            filename="yaml.txt",
            caption="Too Large"
        )
