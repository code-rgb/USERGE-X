from .botapi import XBot
from .botapi import XMediaTypes as xmedia
from .functions import (
    cleanhtml,
    deEmojify,
    escape_markdown,
    media_to_image,
    mention_html,
    mention_markdown,
    rand_array,
    thumb_from_audio,
)
from .progress import progress  # noqa
from .sys_tools import SafeDict, get_import_path, secure_text, terminate  # noqa
from .tools import (
    get_file_id_and_ref,
    humanbytes,
    parse_buttons,
    post_to_telegraph,
    runcmd,
    take_screen_shot,
    time_formatter,
)

# bot api class
xbot = XBot()
