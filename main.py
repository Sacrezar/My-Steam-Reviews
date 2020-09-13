from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from threading import Thread
import concurrent.futures
import random

games = []
reviews = []
rated_games = []
not_rated_games = []

def get_games(url):
    driver = webdriver.Firefox(executable_path=r'.\geckodriver.exe')
    driver.get(url)
    elem = driver.find_elements_by_class_name("gameListRow")
    for i in elem:
        games.append({
                    "name":i.text.split("\n")[0], 
                    "id": i.get_attribute('id').split("_")[1],
                    "playtime":None,
                    "review_id":None
                    })
    driver.close()
    return games

def get_reviews(url):    
    driver = webdriver.Firefox(executable_path=r'.\geckodriver.exe')
    driver.get(url)
    end_loop = False

    while not end_loop:
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

# Change URL there
url = input("COPY PAST YOUR STEAM PROFILE URL (eg: https://steamcommunity.com/id/sacrezar/)\n")
url_games = url + "games?tab=all"
url_reviews = url + "/recommended/"

with concurrent.futures.ThreadPoolExecutor() as executor:
    th1 = executor.submit(get_games, url_games)
    th2 = executor.submit(get_reviews, url_reviews)
    games = th1.result()
    reviews = th2.result()

for review in reviews:
    for game in games:
        if review["game_id"] == game["id"]:
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