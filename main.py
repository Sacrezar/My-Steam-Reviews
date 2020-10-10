import requests
import re
import pprint

from bs4 import BeautifulSoup
from reviewhandler import ReviewHandler

def get_soup(URL):
    page = requests.get(URL)
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
    for element in all_data_reviews:
        pprint.pprint(element) 


def main(URL):
    soup = get_soup(URL)
    nb_reviews = int(get_nb_reviews(soup))
    print(f"{nb_reviews=}")
    reviews(soup)


if __name__ == "__main__":
    main("https://steamcommunity.com/id/sacrezar/recommended/")