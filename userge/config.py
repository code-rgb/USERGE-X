# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ["Config", "get_version"]

import os
from json.decoder import JSONDecodeError
from re import compile as comp_regex
from typing import Set

import heroku3
from git import Repo
from pyrogram import filters
from requests import Session

from userge import logbot, logging

from . import versions

GRepo_regex = comp_regex(
    "http[s]?://github\.com/(?P<owner>[-\w.]+)/(?P<repo>[-\w.]+)(?:\.git)?"
)

_REPO = Repo()
_LOG = logging.getLogger(__name__)
logbot.reply_last_msg("Setting Configs ...")


class Config:
    """ Configs to setup USERGE-X """

    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    WORKERS = int(os.environ.get("WORKERS")) or os.cpu_count() + 4
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    HU_STRING_SESSION = os.environ.get("HU_STRING_SESSION")
    OWNER_ID = tuple(
        filter(lambda x: x, map(int, os.environ.get("OWNER_ID", "0").split()))
    )
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID"))
    AUTH_CHATS = (OWNER_ID[0], LOG_CHANNEL_ID) if OWNER_ID else (LOG_CHANNEL_ID,)
    DB_URI = os.environ.get("DATABASE_URL")
    LANG = os.environ.get("PREFERRED_LANGUAGE")
    DOWN_PATH = os.environ.get("DOWN_PATH")
    CACHE_PATH = "userge/xcache"
    CMD_TRIGGER = os.environ.get("CMD_TRIGGER")
    SUDO_TRIGGER = os.environ.get("SUDO_TRIGGER")
    FINISHED_PROGRESS_STR = os.environ.get("FINISHED_PROGRESS_STR")
    UNFINISHED_PROGRESS_STR = os.environ.get("UNFINISHED_PROGRESS_STR")
    ALIVE_MEDIA = os.environ.get("ALIVE_MEDIA")
    CUSTOM_PACK_NAME = os.environ.get("CUSTOM_PACK_NAME")
    INSTA_ID = os.environ.get("INSTA_ID")
    INSTA_PASS = os.environ.get("INSTA_PASS")
    UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO")
    UPSTREAM_REMOTE = os.environ.get("UPSTREAM_REMOTE")
    SPAM_WATCH_API = os.environ.get("SPAM_WATCH_API")
    CURRENCY_API = os.environ.get("CURRENCY_API")
    OCR_SPACE_API_KEY = os.environ.get("OCR_SPACE_API_KEY")
    OPEN_WEATHER_MAP = os.environ.get("OPEN_WEATHER_MAP")
    REMOVE_BG_API_KEY = os.environ.get("REMOVE_BG_API_KEY")
    WEATHER_DEFCITY = os.environ.get("WEATHER_DEFCITY")
    TZ_NUMBER = os.environ.get("TZ_NUMBER", 1)
    G_DRIVE_CLIENT_ID = os.environ.get("G_DRIVE_CLIENT_ID")
    G_DRIVE_CLIENT_SECRET = os.environ.get("G_DRIVE_CLIENT_SECRET")
    G_DRIVE_PARENT_ID = os.environ.get("G_DRIVE_PARENT_ID")
    G_DRIVE_INDEX_LINK = os.environ.get("G_DRIVE_INDEX_LINK")
    GOOGLE_CHROME_DRIVER = os.environ.get("GOOGLE_CHROME_DRIVER")
    GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_BIN")
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY")
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
    G_DRIVE_IS_TD = os.environ.get("G_DRIVE_IS_TD") == "true"
    LOAD_UNOFFICIAL_PLUGINS = os.environ.get("LOAD_UNOFFICIAL_PLUGINS") == "true"
    THUMB_PATH = DOWN_PATH + "thumb_image.jpg"
    TMP_PATH = "userge/plugins/temp/"
    MAX_MESSAGE_LENGTH = 4096
    MSG_DELETE_TIMEOUT = 120
    WELCOME_DELETE_TIMEOUT = 120
    EDIT_SLEEP_TIMEOUT = 10
    AUTOPIC_TIMEOUT = 300
    ALLOWED_CHATS = filters.chat([])
    ALLOW_ALL_PMS = True
    USE_USER_FOR_CLIENT_CHECKS = False
    SUDO_ENABLED = False
    SUDO_USERS: Set[int] = set()
    DISABLED_ALL = False
    DISABLED_CHATS: Set[int] = set()
    ALLOWED_COMMANDS: Set[str] = set()
    ANTISPAM_SENTRY = False
    SPAM_PROTECTION = False
    RUN_DYNO_SAVER = False
    HEROKU_ENV = bool(int(os.environ.get("HEROKU_ENV", "0")))
    HEROKU_APP = (
        heroku3.from_key(HEROKU_API_KEY).apps()[HEROKU_APP_NAME]
        if HEROKU_ENV and HEROKU_API_KEY and HEROKU_APP_NAME
        else None
    )
    STATUS = None
    BOT_FORWARDS = False
    BOT_MEDIA = os.environ.get("BOT_MEDIA")
    SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_MODE = False
    IMGFLIP_ID = os.environ.get("IMGFLIP_ID")
    IMGFLIP_PASS = os.environ.get("IMGFLIP_PASS")
    ALLOW_NSFW = os.environ.get("ALLOW_NSFW", "False")
    PM_LOG_GROUP_ID = int(os.environ.get("PM_LOG_GROUP_ID", 0))
    PM_LOGGING = False
    DEEP_AI = os.environ.get("DEEP_AI")
    LASTFM_USERNAME = os.environ.get("LASTFM_USERNAME")
    LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY")
    TG_IDS = [777000, 1087968824, 454000]
    INLINE_NOTES = False
    BOT_ANTIFLOOD = False


def get_version() -> str:
    """ get USERGE-X version """
    ver = f"{versions.__major__}.{versions.__minor__}.{versions.__micro__}"
    if Config.HEROKU_ENV:
        if not hasattr(Config, "HBOT_VERSION"):
            setattr(Config, "HBOT_VERSION", hbot_version(ver))
        return Config.HBOT_VERSION
    try:
        if "/code-rgb/userge-x" in Config.UPSTREAM_REPO.lower():
            diff = list(_REPO.iter_commits(f"v{ver}..HEAD"))
            if diff:
                ver = f"{ver}|VULCAN.{len(diff)}"
        else:
            diff = list(_REPO.iter_commits(f"{Config.UPSTREAM_REMOTE}/alpha..HEAD"))
            if diff:
                ver = f"{ver}|fork-[X].{len(diff)}"
        branch = f"@{_REPO.active_branch.name}"
    except Exception as err:
        _LOG.error(err)
    else:
        ver += branch
    return ver


def hbot_version(tag: str) -> str:
    tag_name, commits, branch = None, None, None
    pref_branch = os.environ.get("PREF_BRANCH")
    if match := GRepo_regex.match(Config.UPSTREAM_REPO):
        g_api = (
            f"https://api.github.com/repos/{match.group('owner')}/{match.group('repo')}"
        )
        with Session() as req:
            try:
                if (
                    r_com := req.get(g_api + f"/compare/v{tag}...HEAD")
                ).status_code == 200:
                    rcom = r_com.json()
                    if commits := rcom.get("total_commits"):
                        commits = f".{commits}"
                    branch = rcom.get("target_commitish")
                if (
                    r_name := req.get(g_api + f"/releases/tags/v{tag}")
                ).status_code == 200:
                    tag_name = (r_name.json().get("name") or "").replace(" ", "-")
            except JSONDecodeError:
                pass
    return f"{tag}|{tag_name or ''}{commits or ''}@{pref_branch or branch or 'alpha'}"
