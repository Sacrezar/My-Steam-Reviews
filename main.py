from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import concurrent.futures
import threading
import random
import	json
import requests
import queue

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
    # reviews = []
    driver = webdriver.Firefox(executable_path=r'.\geckodriver.exe')
    driver.get(url)
    end_loop = False
    nbr_loop = 0

    while not end_loop and nbr_loop<=pages-1:
        nbr_loop+=1
        elem = driver.find_elements_by_class_name("leftcol")
        elem2 = driver.find_elements_by_class_name("header")
        for i in range(len(elem)):
            likes_and_funny = elem2[i].text
            if len(likes_and_funny.split("\n"))==2:
                likes, funny = likes_and_funny.split("\n")
                nbr_likes = likes.split(" ")[0]
                nbr_funny = funny.split(" ")[0]
            else:
                nbr_likes = likes_and_funny.split(" ")[0]
                nbr_funny = 0
            try:
                nbr_likes = int(nbr_likes)
            except ValueError:
                nbr_likes = 0

            html_text = elem[i].get_attribute("innerHTML")
            reviews.append({
                            "game_name": None,
                            "game_id": int(html_text.split("https://steamcommunity.com/app/")[1].split('"')[0]),
                            "likes": nbr_likes,
                            "funny": nbr_funny,
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
nbr_pages = int(elem[2].text)
driver.close() 

nbr_thread = 10
if nbr_pages>nbr_thread:
    nbr_pages_for_each_thread = int(nbr_pages / (nbr_thread-1))
    if int(nbr_pages % nbr_thread) == 0:
        nbr_pages_for_last_thread = nbr_pages_for_each_thread
    else: 
        nbr_pages_for_last_thread = nbr_pages - nbr_pages_for_each_thread*(nbr_thread-1)
else: 
    nbr_thread = nbr_pages
    nbr_pages_for_each_thread= 1
    nbr_pages_for_last_thread= 1

print(nbr_thread, nbr_pages_for_each_thread, nbr_pages_for_last_thread)


page = 1
threads = []
que = queue.Queue()
for thread in range(nbr_thread-1):
    t = threading.Thread(target=lambda q, arg1, arg2 : q.put(get_reviews(arg1, arg2)), args=(que, url_reviews + "?p=" + str(page), nbr_pages_for_each_thread))
    page+=nbr_pages_for_each_thread
    threads.append(t)
    t.start()
    t = threading.Thread(target=lambda q, arg1, arg2 : q.put(get_reviews(arg1, arg2)), args=(que, url_reviews + "?p=" + str(page), nbr_pages_for_last_thread))
threads.append(t)
t.start()

for t in threads:
    t.join()
while not que.empty():
    reviews = que.get()


games = get_games(steam_id,api_steam_key)


x= 0
for review in reviews:
    review["id"] = x
    x+=1


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

# for review in reviews:
#     print(review, "\n")
print(len(games),len(reviews))

for i in range(10):
    print(random.choice(not_rated_games))