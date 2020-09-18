from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import concurrent.futures
import threading
import random
import	json
import requests
import queue
import csv

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

def convert_date(date):
    months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November', 
    'December'
    ]
    date = date.split(" ")
    date_to_return = date[0] + "/" + str(months.index(date[1])+1) + "/" 
    if len(date)<3:
        date_to_return += str(datetime.today().year)
    else: 
        date_to_return += date[2]
    return date_to_return




def get_reviews(url,pages):

    # driver = webdriver.Firefox(executable_path=r'.\geckodriver.exe')
    profile = webdriver.FirefoxProfile()
    profile.set_preference('intl.accept_languages', 'en-US, en')
    driver = webdriver.Firefox(firefox_profile=profile)
    driver.get(url)
    end_loop = False
    nbr_loop = 0
    while not end_loop and nbr_loop<=pages-1:
        nbr_loop+=1
        e_game_id = driver.find_elements_by_class_name("leftcol")
        e_likes_and_funny = driver.find_elements_by_class_name("header")
        e_content = driver.find_elements_by_class_name("content")
        e_dates = driver.find_elements_by_class_name("posted")
        for i in range(len(e_game_id)):
            nbr_awards = 0  
            likes_and_funny = e_likes_and_funny[i].text
            if len(likes_and_funny.split("\n"))>=2:
                likes, funny = likes_and_funny.split("\n",1)
                nbr_likes = likes.split(" ")[0]
                nbr_funny = funny.split(" ")[0]
            else:
                nbr_likes = likes_and_funny.split(" ")[0]
                nbr_funny = 0
            try:
                nbr_likes = int(nbr_likes)
            except ValueError:
                nbr_likes = 0
            # print(e_likes_and_funny[i].get_attribute("innerHTML"))
            if e_likes_and_funny[i].get_attribute("innerHTML").find("review_award_count"):
                awards = e_likes_and_funny[i].get_attribute("innerHTML").split("review_award_count")
                del awards[0]
                for award in awards:
                    nb = award.split("</span>")
                    nb = nb[0].split(">")
                    nbr_awards += int(nb[1])
            posted, edited = e_dates[i].text.replace(",","").split(".", 1)
            posted = posted.replace("Posted ","")
            posted = convert_date(posted)
            if len(edited)>0:
                edited = edited.replace(" Last edited ", "").replace(".","")
                last_edited = convert_date(edited)
            else:
                last_edited = None


            total_words = len(e_content[i+1].text.split())

            html_text = e_game_id[i].get_attribute("innerHTML")
            reviews.append({
                            "game_name": None,
                            "game_id": int(html_text.split("https://steamcommunity.com/app/")[1].split('"')[0]),
                            "nbr_likes": nbr_likes,
                            "nbr_funny": nbr_funny,
                            "nbr_awards": nbr_awards,
                            "total_words":total_words,
                            "posted":posted,
                            "last_edited":last_edited
            })

        change_page = driver.find_elements_by_class_name("pagebtn")
        
        if change_page[1].get_attribute("href"):
            change_page[1].click()
        else:
            end_loop = True

    driver.close()
    return reviews


games = []
reviews = []
rated_games = []
not_rated_games = []
nbr_thread = 10

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

# Calculate how many page for a gven thread
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

curr_page = 1
threads = []
que = queue.Queue()
for thread in range(nbr_thread-1):
    t = threading.Thread(target=lambda q, arg1, arg2 : q.put(get_reviews(arg1, arg2)), args=(que, url_reviews + "?p=" + str(curr_page), nbr_pages_for_each_thread))
    curr_page+=nbr_pages_for_each_thread
    threads.append(t)
    t.start()

t = threading.Thread(target=lambda q, arg1, arg2 : q.put(get_reviews(arg1, arg2)), args=(que, url_reviews + "?p=" + str(curr_page), nbr_pages_for_last_thread))
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

for i in range(10):
    print(random.choice(not_rated_games))

csv_columns = ['game_name', 'game_id', 'nbr_likes', 'nbr_funny', 'nbr_awards', 'total_words', 'posted','last_edited', "id"]
csv_file = "reviewed_games.csv"

try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in reviews:
            writer.writerow(data)
except IOError:
    print("I/O error")
