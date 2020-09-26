import requests
import json


from userge import userge, Message, Config


@userge.on_cmd("spotify_db", about={'header': "ADD initial Token"})
async def webss(message: Message):
    if not message.input_str:
        return await message.err('Input Token Not Found', del_in=5)
    spotify_intial_token = message.input_str.split()[0]
    body = {"client_id": Config.SPOTIFY_CLIENT_ID, "client_secret": Config.SPOTIFY_CLIENT_SECRET,
            "grant_type": "authorization_code", "redirect_uri": "https://example.com/callback",
            "code": spotify_intial_token}
    r = requests.post("https://accounts.spotify.com/api/token", data=body)
    save = r.json()
    to_create = {'bio': Config.SPOTIFY_INITIAL_BIO, 'access_token': save['access_token'], 'refresh_token': save['refresh_token'],
                'telegram_spam': False, 'spotify_spam': False}
    with open('./userge/xcache/database.json', 'w') as outfile:
        json.dump(to_create, outfile, indent=4, sort_keys=True)
    await message.edit('Token Set SUCCESSFULLY !', del_in=5)