"""Json / Yaml"""

# by - @DeletedUser420


from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

from userge import Message, userge
from userge.utils import clean_obj


@userge.on_cmd(
    "json",
    about={
        "header": "message object to json",
        "usage": "reply {tr}json to any message",
        "flags": {"-c": "clean json"},
    },
)
async def to_json_(message: Message):
    """Json-ify"""
    msg = message.reply_to_message or message
    if "-c" in message.flags:
        msg = clean_obj(msg, True)
    await message.edit_or_send_as_file(
        text=str(msg), filename="Json.txt", caption="Too Large"
    )


@userge.on_cmd(
    "yaml",
    about={
        "header": "message object to yaml",
        "usage": "reply {tr}yaml to any message",
    },
)
async def to_yaml_(message: Message):
    """yaml-ify"""
    await message.edit_or_send_as_file(
        yamlify(convert(clean_obj(message.reply_to_message or message, True))),
        filename="YAML.txt",
        caption="Too Large",
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


class MyYAML(YAML):
    def dump(self, data, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()


def yamlify(input_):
    yaml = MyYAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    return f"<pre>{yaml.dump(input_)}</pre>"
