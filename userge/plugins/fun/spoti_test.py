import asyncio
import time
#import readable_time
from datetime import datetime

import json

import requests
from pyrogram.errors import FloodWait, AboutTooLong
#from importlib import import_module
import os
from userge import userge, Message, Config, get_collection
from pyrogram import filters

device_model = "spotify_bot"
version = "1.5"
system_version, app_version = version, version

StartTime = time.time()


SAVED_SETTINGS = get_collection("CONFIGS")
LOG = userge.getLogger(__name__)
ubot = userge.bot
#CHANNEL = userge.getCLogger(__name__)

KEY = '🎶'
BIOS = [KEY + ' Vibing ; {interpret} - {title} {progress}/{duration}',
        KEY + ' Vibing : {interpret} - {title}',
        KEY + ' : {interpret} - {title}',
        KEY + ' Vibing : {title}',
        KEY + ' : {title}']
OFFSET = 1
# reduce the OFFSET from our actual 70 character limit
LIMIT = 70 - OFFSET


async def _init() -> None:
    data = await SAVED_SETTINGS.find_one({'_id': 'SPOTIFY_MODE'})
    if data:
        Config.SPOTIFY_MODE = bool(data['is_active'])




@userge.on_cmd("spotify_bio", about={'header': "enable / disable Spotify Bio"}, allow_channels=False)
async def spotify_bio_(message: Message):
	if Config.SPOTIFY_MODE:
		Config.SPOTIFY_MODE = False
		await userge.update_profile(bio=Config.SPOTIFY_INITIAL_BIO)
		await message.edit("`Spotify Bio disabled !`", del_in=3)
	else:
		await message.edit("`Spotify Bio enabled` \nCurrent Spotify playback will update in bio", del_in=5)
		Config.SPOTIFY_MODE = True
		await spotify_biox()
	await SAVED_SETTINGS.update_one({'_id': 'SPOTIFY_MODE'}, {"$set": {'is_active': Config.SPOTIFY_MODE}}, upsert=True)



def ms_converter(millis):
	millis = int(millis)
	seconds = (millis/1000) % 60
	seconds = int(seconds)
	if str(seconds) == '0':
		seconds = '00'
	if len(str(seconds)) == 1:
		seconds = '0' + str(seconds)
	minutes = (millis/(1000*60)) % 60
	minutes = int(minutes)
	return str(minutes) + ":" + str(seconds)





class Database:
	def __init__(self):
		try:
			self.db = json.load(open("./userge/xcache/spotify_database.json"))
		except FileNotFoundError:
			print("You need to run generate.py first, please read the Readme.")
			

	def save_token(self, token):
		self.db["access_token"] = token
		self.save()

	def save_refresh(self, token):
		self.db["refresh_token"] = token
		self.save()

	def save_bio(self, bio):
		self.db["bio"] = bio
		self.save()

	def save_spam(self, which, what):
		self.db[which + "_spam"] = what

	def return_token(self):
		return self.db["access_token"]

	def return_refresh(self):
		return self.db["refresh_token"]

	def return_bio(self):
		return self.db["bio"]

	def return_spam(self, which):
		return self.db[which + "_spam"]

	def save(self):
		with open('./userge/xcache/spotify_database.json', 'w') as outfile:
			json.dump(self.db, outfile, indent=4, sort_keys=True)


database = Database()

# to stop unwanted spam, we sent these type of message only once. So we have a variable in our database which we check
# for in return_info. When we send a message, we set this variable to true. After a successful update
# (or a closing of spotify), we reset that variable to false.


def save_spam(which, what):
	# see below why

	# this is if False is inserted, so if spam = False, so if everything is good.
	if not what:
		# if it wasn't normal before, we proceed
		if database.return_spam(which):
			# we save that it is normal now
			database.save_spam(which, False)
			# we return True so we can test against it and if it this function returns, we can send a fitting message
			return True
	# this is if True is inserted, so if spam = True, so if something went wrong
	else:
		# if it was normal before, we proceed
		if not database.return_spam(which):
			# we save that it is not normal now
			database.save_spam(which, True)
			# we return True so we can send a message
			return True
	# if True wasn't returned before, we can return False now so our test fails and we dont send a message
	return False


async def spotify_biox():
	while Config.SPOTIFY_MODE:
		# SPOTIFY
		skip = False
		to_insert = {}
		oauth = {
			"Authorization": "Bearer " + database.return_token()}
		r = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=oauth)
		# 200 means user plays smth
		if r.status_code == 200:
			received = r.json()
			if received["currently_playing_type"] == "track":
				to_insert["title"] = received["item"]["name"]
				to_insert["progress"] = ms_converter(received["progress_ms"])
				to_insert["interpret"] = received['item']["artists"][0]["name"]
				to_insert["duration"] = ms_converter(received["item"]["duration_ms"])
				to_insert["link"] = received['item']['external_urls']['spotify']
				to_insert["image"] = received['item']['album']['images'][1]['url']
				if save_spam("spotify", False):
					stringy = "**[INFO]**\n\nEverything returned back to normal, the previous spotify issue has been " \
							"resolved."
					await ubot.send_message(Config.OWNER_ID, stringy)
				
			else:
				if save_spam("spotify", True):
					# currently item is not passed when the user plays a podcast
					string = f"**[INFO]**\n\nThe playback {received['currently_playing_type']} didn't gave me any " \
						f"additional information, so I skipped updating the bio."
					await ubot.send_message(Config.OWNER_ID, string)
	
		# 429 means flood limit, we need to wait
		elif r.status_code == 429:
			to_wait = r.headers['Retry-After']
			LOG.error(f"Spotify, have to wait for {str(to_wait)}")
			await ubot.send_message(Config.OWNER_ID, f'**[WARNING]**\n\nI caught a spotify api limit. I shall sleep for '
										f'{str(to_wait)} seconds until I refresh again')
			skip = True
			await asyncio.sleep(int(to_wait))
		# 204 means user plays nothing, since to_insert is false, we dont need to change anything
		elif r.status_code == 204:
			if save_spam("spotify", False):
				stringy = "**[INFO]**\n\nEverything returned back to normal, the previous spotify issue has been " \
						"resolved."
				await ubot.send_message(Config.OWNER_ID, stringy)
			pass
		# 401 means our access token is expired, so we need to refresh it
		elif r.status_code == 401:
			data = {"client_id": Config.SPOTIFY_CLIENT_ID, "client_secret": Config.SPOTIFY_CLIENT_SECRET,
					"grant_type": "refresh_token",
					"refresh_token": database.return_refresh()}
			r = requests.post("https://accounts.spotify.com/api/token", data=data)
			received = r.json()
			# if a new refresh is token as well, we save it here
			try:
				database.save_refresh(received["refresh_token"])
			except KeyError:
				pass
			database.save_token(received["access_token"])
			# since we didnt actually update our status yet, lets do this without the 30 seconds wait
			skip = True
		# 502 means bad gateway, its an issue on spotify site which we can do nothing about. 30 seconds wait shouldn't
		# put too much pressure on the spotify server, so we are just going to notify the user once
		
		elif r.status_code == 502:
			if save_spam("spotify", True):
				string = f"**[WARNING]**\n\nSpotify returned a Bad gateway, which means they have a problem on their " \
					f"servers. The bot will continue to run but may not update the bio for a short time."
				await ubot.send_message(Config.OWNER_ID, string)
		# 503 means service unavailable, its an issue on spotify site which we can do nothing about. 30 seconds wait
		# shouldn't put too much pressure on the spotify server, so we are just going to notify the user once
		elif r.status_code == 503:
			if save_spam("spotify", True):
				string = f"**[WARNING]**\n\nSpotify said that the service is unavailable, which means they have a " \
						f"problem on their servers. The bot will continue to run but may not update the bio for a " \
						f"short time."
				await ubot.send_message(Config.OWNER_ID, string)
		# 404 is a spotify error which isn't supposed to happen (since our URL is correct). Track the issue here:
		# https://github.com/spotify/web-api/issues/1280
		elif r.status_code == 404:
			if save_spam("spotify", True):
				string = f"**[INFO]**\n\nSpotify returned a 404 error, which is a bug on their side."
				await ubot.send_message(Config.OWNER_ID, string)
		# catch anything else
		else:
			await ubot.send_message(Config.OWNER_ID, '**[ERROR]**\n\nOK, so something went reeeally wrong with spotify. The bot '
										'was stopped.\nStatus code: ' + str(r.status_code) + '\n\nText: ' + r.text)
			LOG.error(f"Spotify, error {str(r.status_code)}, text: {r.text}")
			# stop the whole program since I dont know what happens here and this is the safest thing we can do
			SPOTIFY_MODE = False # TODO check this
		# TELEGRAM
		try:
			# full needed, since we dont get a bio with the normal request
			full = await userge.get_chat(Config.OWNER_ID)
			bio = full.description
			# to_insert means we have a successful playback
			if to_insert:
				# putting our collected information's into nice variables
				
				title = to_insert["title"]
				interpret = to_insert["interpret"]
				progress = to_insert["progress"]
				duration = to_insert["duration"]
				spotify_biox.interpret = to_insert["interpret"]
				spotify_biox.progress = to_insert["progress"]
				spotify_biox.duration = to_insert["duration"]
				spotify_biox.title = to_insert["title"]
				spotify_biox.link = to_insert["link"]
				spotify_biox.image = to_insert["image"]
				# we need this variable to see if actually one of the BIOS is below the character limit
				new_bio = ""
				for bio in BIOS:
					temp = bio.format(title=title, interpret=interpret, progress=progress, duration=duration)
					# we try to not ignore for telegrams character limit here
					
					if len(temp) < LIMIT:
						# this is short enough, so we put it in the variable and break our for loop
						new_bio = temp
						break
				# if we have a bio, one bio was short enough
				if new_bio:
					# test if the user changed his bio to blank, we save it before we override
					if not bio:
						database.save_bio(bio)
					# test if the user changed his bio in the meantime, if yes, we save it before we override
					elif "🎶" not in bio:
						database.save_bio(bio)
					# test if the bio isn't the same, otherwise updating it would be stupid
					if not new_bio == bio:
						try:
							await userge.update_profile(bio=new_bio)
							spotify_biox.lrt = time.time()
						
							if save_spam("telegram", False):
								stringy = "**[INFO]**\n\nEverything returned back to normal, the previous telegram " \
										"issue has been resolved."
								await ubot.send_message(Config.OWNER_ID, stringy)
						# this can happen if our LIMIT check failed because telegram counts emojis twice and python
						# doesnt. Refer to the constants file to learn more about this
						except AboutTooLong:
							if save_spam("telegram", True):
								stringy = f'**[WARNING]**\n\nThe biography I tried to insert was too long. In order ' \
									f'to not let that happen again in the future, please read the part about OFFSET ' \
									f'in the constants. Anyway, here is the bio I tried to insert:\n\n{new_bio}'
								await ubot.send_message(Config.OWNER_ID, stringy)
				# if we dont have a bio, everything was too long, so we tell the user that
				if not new_bio:
					if save_spam("telegram", True):
						to_send = f"**[INFO]**\n\nThe current track exceeded the character limit, so the bio wasn't " \
							f"updated.\n\n Track: {title}\nInterpret: {interpret}"
						await ubot.send_message(Config.OWNER_ID, to_send)
			# not to_insert means no playback
			else:
				if save_spam("telegram", False):
					stringy = "**[INFO]**\n\nEverything returned back to normal, the previous telegram issue has " \
							"been resolved."
					await ubot.send_message(Config.OWNER_ID, stringy)
				old_bio = database.return_bio()
				# this means the bio is blank, so we save that as the new one
				if not bio:
					database.save_bio(bio)
				# this means an old playback is in the bio, so we change it back to the original one
				elif "🎶" in bio:
					await userge.update_profile(bio=database.return_bio())
					
				# this means a new original is there, lets save it
				elif not bio == old_bio:
					database.save_bio(bio)
				# this means the original one we saved is still valid
				else:
					pass
		except FloodWait as e:
			to_wait = e.seconds
			LOG.error(f"to wait for {str(to_wait)}")
			await ubot.send_message(Config.OWNER_ID, f'**[WARNING]**\n\nI caught a telegram api limit. I shall sleep '
										f'{str(to_wait)} seconds until I refresh again')
			skip = True
			await asyncio.sleep(int(to_wait))
		# skip means a flood error stopped the whole program, no need to wait another 30 seconds after that
		if not skip:
			await asyncio.sleep(30)