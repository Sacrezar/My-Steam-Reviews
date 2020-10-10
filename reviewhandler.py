import re
from datetime import datetime


def convert_date(date):
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    if date == "":
        return None
    date = date.replace(",","")
    date = date.split(" ")
    month = months.index(date[1]) + 1
    date_to_return = date[0] + "/" + str(month) + "/"

    if len(date) < 3:
        date_to_return += str(datetime.today().year)
    else:
        date_to_return += date[2]
    return date_to_return


class ReviewHandler:


    def __init__(self, review):
        self.review = review


    def get_appreciation(self):
        nb_helpful = 0
        nb_funny = 0
        appreciation = self.review.find('div', class_ = "header").get_text()

        try:
            nb_helpful = re.findall("\t([0-9]*?) (people|person) found this review helpful",appreciation)[0][0]
        except IndexError:
            pass
        try:
            nb_funny = re.findall("\t([0-9]*?) (people|person) found this review funny",appreciation)[0][0]
        except IndexError:
            pass
        
        return {
            "nb_helpful": int(nb_helpful),
            "nb_funny": int(nb_funny)
        }


    def get_game_id(self):
        title = self.review.find('div', class_ = "title")
        game_url = title.find(href=True)
        game_id = re.search("[0-9]+", game_url['href']).group()
        return game_id


    def get_awards(self, info=True):
        awards_info = []
        total_awards = 0
        total_points = 0

        awards = self.review.find_all('div', class_ = "review_award")

        for award in awards:
            data = award.get("data-tooltip-html")
            
            award_name = re.findall('<div class="reaction_award_name">(.*?)</div>', data)[0]
            award_count = re.findall('<div class="reaction_award_count">(.*?)</div>', data)[0]
            award_points = re.findall('<div class="reaction_award_points">(.*?)</div>', data)[0]
            award_count = int(re.search("[0-9]+", award_count).group())
            award_points = int(re.search("[0-9]+", award_points).group())

            awards_info.append({
                "award_name": award_name,
                "award_count": award_count,
                "award_value": award_points,
                "total_value": award_count*award_points
            })

        for element in awards_info:
            total_awards += element["award_count"]
            total_points += element["total_value"]

        all_awards_infos = {
            "total_awards": total_awards,
            "total_points": total_points,
        }

        if info:
            all_awards_infos["all_info"] = awards_info

        return all_awards_infos


    def get_date(self):
        dates = self.review.find('div', class_ = "posted").get_text()
        posted = re.findall('Posted (.*?)[.]', dates)[0]
        try:
            edited = re.findall('Last edited (.*?)[.]', dates)[0]
        except IndexError:
            edited = ""

        return {
            "posted":convert_date(posted),
            "last_edit": convert_date(edited)
        }


    def get_total_words(self):

        to_split = r"[:|;|,|.\s|?|!|\s]"
        content = self.review.find('div', class_ = "content")
        text = content.get_text()

        total_words = re.split(to_split, text)
        total_words[:] = [item for item in total_words if item != '']

        return len(total_words)


    def get_review_status(self):
        title = self.review.find('div', class_ = "title")
        status = title.get_text()
        return status


