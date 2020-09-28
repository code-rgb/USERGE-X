import os
import json
import requests
from userge import logging
from ..core.ext.raw_client import RawClient
from ..config import Config
from ..core.database import get_collection


_LOG = logging.getLogger(__name__)
SPOTIFY_DB = get_collection("SPOTIFY_DB")


async def spotify_db_loader():
    if not os.path.exists("./userge/xcache/spotify_database.json"):
        sdb = await SPOTIFY_DB.find_one({'_id': 'SPOTIFY_DB'})
        if sdb:
            sdb_msgid = sdb['database_id']
            
            sdb_get = await RawClient.get_messages(Config.LOG_CHANNEL_ID, sdb_msgid)
        
            _LOG.error(f"sdb_get = {sdb_get}")
            await RawClient.download_media(
                sdb_get.document,
                file_name="userge/xcache/spotify_database.json")
        else:
            body = {"client_id": Config.SPOTIFY_CLIENT_ID, "client_secret": Config.SPOTIFY_CLIENT_SECRET,
                    "grant_type": "authorization_code", "redirect_uri": "https://example.com/callback",
                    "code": Config.SPOTIFY_INITIAL_TOKEN}
            r = requests.post("https://accounts.spotify.com/api/token", data=body)
            save = r.json()
            try:
                to_create = {'bio': Config.SPOTIFY_INITIAL_BIO, 'access_token': save['access_token'], 'refresh_token': save['refresh_token'],
                                'telegram_spam': False, 'spotify_spam': False}
                with open('./userge/xcache/spotify_database.json', 'w+') as outfile:
                    json.dump(to_create, outfile, indent=4, sort_keys=True)
            except KeyError:
                _LOG.error('SPOTIFY_INITIAL_TOKEN expired recreate one')
            except FileNotFoundError:
                _LOG.error('Database not found')
            else:
                s_database = await RawClient.send_document(
                                Config.LOG_CHANNEL_ID,
                                'userge/xcache/spotify_database.json',
                                disable_notification=True,
                                caption="#SPOTIFY_DB Don't Delete"
                )
                await SPOTIFY_DB.update_one(
                        {'_id': 'SPOTIFY_DB'}, {"$set": {'database_id': s_database.message_id}}, upsert=True)
