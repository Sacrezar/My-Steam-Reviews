from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import random
import	json
import requests

games = []
reviews = []
rated_games = []
not_rated_games = []

def get_games(account_id, api_key):
    call = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={account_id}&include_appinfo=1&include_played_free_games=1&format=json"
    response = requests.get(call)
    games_info = response.json()["response"]["games"]
    for i in games_info:
        games.append({
                    "name":i["name"], 
                    "appid": i["appid"],
                    "playtime":i["playtime_forever"],
                    "review_id":None
                    })
    return games

def get_reviews(url,pages):    
    driver = webdriver.Firefox(executable_path=r'.\geckodriver.exe')
    driver.get(url)
    end_loop = False
    nbr_loop = 0

    while not end_loop or nbr_loop<=pages:
        nbr_loop+=1
        elem = driver.find_elements_by_class_name("leftcol")
        x = 0
        for i in elem:
            x+= 1
            html_text = i.get_attribute("innerHTML")
            reviews.append({
                            "id":x,
                            "game_name": None,
                            "game_id": html_text.split("https://steamcommunity.com/app/")[1].split('"')[0],
                            "likes": None,
                            "total_words":None,
                            "posted":None,
                            "last_edited":None
            })

        change_page = driver.find_elements_by_class_name("pagebtn")
        
        if change_page[1].get_attribute("href"):
            change_page[1].click()
        else:
            end_loop = True

    driver.close()
    return reviews

with open('user_info.json') as f:
    info = json.load(f)

api_steam_key = info["API_Steam_key"]
steam_id = info["Steam_info"]["ID"]
vanity_url = info["Steam_info"]["vanityURL"]
url = "https://steamcommunity.com/id/" + vanity_url
url_games = url + "games?tab=all"
url_reviews = url + "/recommended/"

# Retrieve number of pages
driver = webdriver.Firefox(executable_path=r'.\geckodriver.exe')
driver.get(url_reviews)
elem = driver.find_elements_by_class_name("pagelink")
nbr_pages = int(elem[2].text)-1
driver.close() 

# nbr_thread = 5
# if nbr_pages>nbr_thread:
#     nbr_pages_for_each_thread = int(nbr_pages / nbr_thread)
#     nbr_pages_for_last_thread = int(nbr_pages % nbr_thread)
# else: 
#     nbr_thread = nbr_pages
#     nbr_pages_for_each_thread= 1
#     nbr_pages_for_last_thread= 1

# print(nbr_pages_for_each_thread, nbr_pages_for_last_thread)

games = get_games(steam_id,api_steam_key)
reviews = get_reviews(url_reviews, 0)


for review in reviews:
    for game in games:
        if review["game_id"] == game["appid"]:
            review["game_name"] = game["name"]
            game["review_id"] = review["id"]
            break
        else:
            review["game_name"] = "Unknown (DLC?)"

for game in games: 
    if game["review_id"]:
        rated_games.append(game["name"])
    else:
        not_rated_games.append(game["name"])

for i in range(10):
    print(random.choice(not_rated_games))