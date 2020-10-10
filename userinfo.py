import json 
import os.path
import requests


class UserInfo:
    def __init__(self):
        self.filename = "user_info.json"
        if self.is_user_info():
            self.get_user_info()
        else:
            self.create_user_info()

    def is_user_info(self):
        return True if os.path.isfile(self.filename) else False


    def is_api_key(self, api_key):
        call =  f"http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={api_key}&appid=218620"
        return True if requests.get(call) else False


    def is_account_id(self, api_key, account_id):
        call = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={account_id}"
        return True if len(requests.get(call).json()["response"]["players"])>=1 else False
    
    def request_account_id(self, api_key, vanity_url):
        call = f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={api_key}&vanityurl={vanity_url}"
        account_id = requests.get(call).json()["response"]["steamid"]
        return account_id

    def create_user_info(self):
        api_key = ""
        vanity_url = ""
        account_id = ""

        while not self.is_api_key(api_key):

            api_key = input("\t Prompt your Steam API KEY: ")
            
            if not self.is_api_key(api_key):
                print("Your API Key is invalid")
        
        vanity_url = input("\t Prompt your vanity URL (leave blank if none): ")
        if vanity_url != "":
            account_id = self.request_account_id(api_key, vanity_url)

        while not self.is_account_id(api_key, account_id):
            account_id = input("\t Prompt your account id: ")

            if not self.is_account_id(api_key, account_id):
                print("Can't find this id")

        if vanity_url == "":
            vanity_url = account_id

        self.set_api_key(api_key)
        self.set_vanity_url(vanity_url)
        self.set_account_id(account_id)

        user_info_json = {
            "api_steam_key": self.api_key,
            "steam_info": {
                "vanity_url": self.vanity_url,
                "account_id": self.account_id
            }
        }

        with open(self.filename, 'w') as json_file:
            json.dump(user_info_json, json_file)


    def get_user_info(self):
        with open(self.filename) as json_file:
            user_info = json.load(json_file)
        
        try:
            self.set_api_key(user_info["api_steam_key"])
            self.set_vanity_url(user_info["steam_info"]["vanity_url"])
            self.set_account_id(user_info["steam_info"]["account_id"])
        except KeyError:
            self.create_user_info()
            


    def get_vanity_url(self):
        return self.vanity_url


    def set_vanity_url(self, vanity_url):
        self.vanity_url = vanity_url


    def get_account_id(self):
        return self.account_id


    def set_account_id(self, account_id):
        self.account_id = account_id


    def get_api_key(self):
        return self.api_key
    

    def set_api_key(self, api_key):
        self.api_key = api_key


