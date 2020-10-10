import requests
import re
import pprint
import numpy as np 
import json 
import random

from bs4 import BeautifulSoup
from reviewhandler import ReviewHandler

NB_REVIEWS_PER_PAGE = 10

def get_soup(url):
    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")

def get_nb_reviews(soup):
    nb_reviews = soup.find('div', class_ = "giantNumber")
    return nb_reviews.get_text()

def reviews(soup):
    all_data_reviews = []
    reviews = soup.find_all('div', class_ = "review_box")
    for review in reviews:
        data_review = ReviewHandler(review)
        all_data_reviews.append(
            {
            "game_id": data_review.get_game_id(),
            "recommendation": data_review.get_review_status(),
            "appreciation": data_review.get_appreciation(),
            "awards_info":data_review.get_awards(info=False),
            "posted_date": data_review.get_date()["posted"],
            "last_edit": data_review.get_date()["last_edit"],
            "total_words": data_review.get_total_words()
            }
        )
    return all_data_reviews

def get_urls(url, nb_reviews):
    urls = []
    nb_pages = int(np.ceil(nb_reviews / NB_REVIEWS_PER_PAGE))
    for i in range(nb_pages):
        new_url = url + "?p=" + f"{i+1}"
        urls.append(new_url)
    return urls


def get_games(account_id, api_key):
    games = []
    call = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={account_id}&include_appinfo=1&include_played_free_games=1&format=json"
    print(call)
    response = requests.get(call)
    games_info = response.json()["response"]["games"]
    for i in games_info:
        games.append({
                    "name":i["name"], 
                    "appid": i["appid"],
                    "playtime":i["playtime_forever"]
                    })
    return games

def get_user_info():
    with open('user_info.json') as f:
        user_info = json.load(f)
    return user_info


def main(url):
    reviews_data = []
    soup = get_soup(url)
    nb_reviews = int(get_nb_reviews(soup))
    urls = get_urls(url, nb_reviews)

    for url in urls:
        print(f"Fetching data from {url}")
        soup = get_soup(url)
        reviews_data += reviews(soup)
        
    user_info = get_user_info()
    account_id = user_info["Steam_info"]["ID"]
    api_key = user_info["API_Steam_key"]
    games = get_games(account_id, api_key)
    reviews_ = reviews_data.copy()
    for game in games:
        for review in reviews_data:
            if review["game_id"] == game["appid"]:
                del review["game_id"]
                game["review_data"] = review 
                reviews_data.remove(review)

    for review in reviews_data:
        appid = review["game_id"]
        del review["game_id"]
        call = f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={api_key}&steamid={account_id}"
        response = requests.get(call)
        if response:
            game_name = response.json()["playerstats"]["gameName"]
        else: 
            game_name = "Unknown"
        games.append({
            "name":game_name,
            "appid":appid,
            "playtime":None,
            "review_data": review
        })

    not_reviewed_games = []
    reviewed_games = []
    for game in games:
        try:
            if game["review_data"]:
                reviewed_games.append(game)
        except KeyError:
            not_reviewed_games.append(game)
    print(len(games), len(reviewed_games), len(not_reviewed_games))

    games_to_review = random.sample(not_reviewed_games, 10)
    for game in games_to_review:
        print(game["name"])



if __name__ == "__main__":
    main("https://steamcommunity.com/id/sacrezar/recommended/")