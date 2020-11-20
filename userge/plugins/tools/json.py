"""Json / Yaml"""

# by - @DeletedUser420

import json
import re

import yaml

from userge import Message, userge


@userge.on_cmd(
    "json",
    about={
        "header": "message object to json",
        "usage": "reply {tr}json to any message",
    },
)
async def jsonify(message: Message):
    """Json-ify"""
    if message.reply_to_message:
        msg = str(message.reply_to_message)
    else:
        msg = str(message)
    await message.edit_or_send_as_file(
        text=msg, filename="json.txt", caption="Too Large"
    )


@userge.on_cmd(
    "yaml",
    about={
        "header": "message object to yaml",
        "usage": "reply {tr}yaml to any message",
    },
)
async def yamlify(message: Message):
    """yaml-ify"""
    if message.reply_to_message:
        msg = str(message.reply_to_message)
    else:
        msg = str(message)
    json_file = json.loads(msg)
    yaml_ify = yaml.dump(convert(json_file), allow_unicode=True)
    regex = r"(\s+|)(?:- _:|_:)[\s]"
    result = re.sub(regex, " ", yaml_ify, re.MULTILINE)
    if result:
        await message.edit_or_send_as_file(
            text=f"```{result[1:]}```", filename="yaml.txt", caption="Too Large"
        )


def convert(obj):
    if isinstance(obj, bool):
        return bool_emoji(obj)
    if isinstance(obj, (list, tuple)):
        return [convert(item) for item in obj]
    if isinstance(obj, dict):
        return {convert(key): convert(value) for key, value in obj.items()}
    return obj


def bool_emoji(choice: bool) -> str:
    return "✔" if choice else "✖"
