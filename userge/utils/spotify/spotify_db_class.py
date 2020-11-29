import json


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

	