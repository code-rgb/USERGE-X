from userge import Message, userge
from userge.utils.google_images import googleimagesdownload


@userge.on_cmd(
    "gimgs",
    about={
        "header": "get a random reddit post ",
        "usage": "{tr}reddit [subreddit]",
        "examples": "{tr}reddit dankmemes",
    },
)
async def aaa(message: Message):
    """Random reddit post"""

    response = googleimagesdownload()
    # creating list of arguments
    limit = min(int(message.flags.get("l"), 3), 100)
    limit = limit if limit > 0 else 3
    arguments = {
        "keywords": message.filtered_inp_str,
        "limit": limit,
        "format": "jpg",
        "no_directory": "no_directory",
    }
    # passing the arguments to the function

    paths = response.download(arguments)
    print(paths)
