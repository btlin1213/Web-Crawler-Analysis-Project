from bs4 import BeautifulSoup
from urllib.parse import urljoin
from numpy import arange
import json
import requests
import pandas as pd
import unicodedata
import re
import numpy as np
import matplotlib.pyplot as plt

# %matplotlib inline


# parsing tennis.json file
with open("tennis.json") as f:
    data = json.load(f)
    win_percent_dct = {}
    name_strings = []

    for i in range(len(data)):
        name = data[i]["name"]
        name_strings.append(name)
        win_percent = data[i]["wonPct"]
        win_percent_dct[name.title()] = win_percent

nested_names = [name.split() for name in name_strings]
name_words = list(set([name for full_name in nested_names for name in full_name]))


def add_header(header_txt, row_list):
    row_list["header"].append(header_txt)


def find_names(string):
    answer = []
    string_words = string.split()
    capital_words = [word for word in string_words if word[0].isupper()]
    for word in capital_words:
        if word.upper() in name_words:
            answer.append(word.upper())
        else:
            answer = []
        answer_string = " ".join(answer)
        if answer_string in name_strings:
            return answer_string
    return "no name here"


def add_player_name(player_name, row_list):
    row_list["player"].append(player_name.title())


def validate_score(lst):
    copy = lst.copy()
    for score in copy:
        if score[0] == "(":
            copy.remove(score)
        elif "-" not in score:
            copy.remove(score)
        elif score[0] == score[2]:
            copy.remove(score)
        elif int(score[0]) == 0 and int(score[2:]) > 6:
            return False
    return 2 <= len(copy) <= 5


def extract_scores(header_txt, body_txt):
    string = header_txt + body_txt
    pattern = r"\d[-\(\)\/\d\s]+"
    all_scores = re.findall(pattern, string)
    for score_str in all_scores:
        score_str_list = score_str.split()
        if validate_score(score_str_list):
            return " ".join(score_str_list)


def add_score(score, row_list):
    row_list["score"].append(score)


def extract_avg_diff(score_string):
    score_string_list = score_string.split()

    player_1 = 0
    player_2 = 0
    for score in score_string_list:
        if score[0] == "(":
            continue
        else:
            dash_index = score.index("-")
            a, b = int(score[0:dash_index]), int(score[dash_index + 1 :])
            player_1 += a
            player_2 += b
    avg_diff = abs(player_1 - player_2)
    #   DEBUG STATEMENT:
    # print("Score String is {0}\nPlayer 1 is {1}\nPlayer 2 is {2}\nDifference is {3}\n".format(score_string, player_1, player_2, avg_diff))
    return avg_diff


def add_avg_diff(avg_diff, row_list):
    row_list["avg_game_difference"].append(int(avg_diff))


def task_1():
    # create empty series for writing to csv file for task 1
    row_list_1 = {}
    row_list_1["url"] = []
    row_list_1["header"] = []

    # requesting access
    base_url = "http://comp20008-jh.eng.unimelb.edu.au:9889/main/"
    seed_item = "index.html"
    seed_url = base_url + seed_item
    response = requests.get(seed_url)

    # parse with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # creating list V of urls that have been visited and when
    visited = {}
    visited[seed_url] = True

    links = soup.findAll("a")
    # creating prioritised list L of urls to-visit (seed urls)
    to_visit = []
    for link in links:
        to_visit.append(urljoin(seed_url, link["href"]))

    # find all outbound links on successor pages and explore each one
    while to_visit:
        re 
        # add current url to series
        link = to_visit.pop(0)
        row_list_1["url"].append(link)
        # request access to current page
        page = requests.get(link)
        # scrape the current page
        soup = BeautifulSoup(page.text, "html.parser")

        # add current header to series
        header_txt = soup.find("h1").text
        add_header(header_txt, row_list_1)

        # mark the current page as visited by adding to list V
        visited[link] = True

        # add the new urls {u'} from current page to to-visit list L
        new_links = soup.findAll("a")
        for new_link in new_links:
            new_item = new_link["href"]
            new_url = urljoin(link, new_item)

            # add {u'} - V to list L (provided that it's not in list L already)
            if new_url not in visited and new_url not in to_visit:
                to_visit.append(new_url)

    # writing series to dataframe
    df = pd.DataFrame(row_list_1)
    df.set_index("url", inplace=True)
    # writing dataframe to csv file
    df.to_csv("task1.csv")

    # pass the urls from task 1 to task 2a
    task_1_urls = row_list_1["url"]
    return task_1_urls


def task_2a():
    # create empty series for writing to csv file for task 2a
    row_list_2a = {}
    row_list_2a["url"] = []
    row_list_2a["header"] = []
    row_list_2a["player"] = []

    url_from_task1 = task_1()

    for url in url_from_task1:
        # add url to csv
        row_list_2a["url"].append(url)

        # get its header
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        header_txt = soup.find("h1").text
        body_txt = soup.find(id="articleDetail").text
        # add header to csv
        add_header(header_txt, row_list_2a)

        # add player names
        # if there is no valid player name in header or body text
        if find_names(header_txt) == "no name here":
            if find_names(body_txt) == "no name here":
                # discard article
                row_list_2a["url"].remove(url)
                row_list_2a["header"].remove(header_txt)
            # if there is valid player name in body text, add it to csv
            else:
                player_name = find_names(body_txt)
                add_player_name(player_name, row_list_2a)
        # if there is valid player name in header text, add it to csv
        else:
            player_name = find_names(header_txt)
            add_player_name(player_name, row_list_2a)

    # writing series to dataframe
    #     df = pd.DataFrame(row_list_2a)
    #     df.set_index('url', inplace=True)
    #     # writing dataframe to csv file
    #     df.to_csv('task2a_draft_1.csv')

    # pass the urls from task 2a to task 2b
    task_2a_urls = row_list_2a["url"]
    return task_2a_urls


def task_2b():
    # create empty series for writing to csv file for task 2b
    row_list_2b = {}
    row_list_2b["url"] = []
    row_list_2b["header"] = []
    row_list_2b["player"] = []
    row_list_2b["score"] = []

    url_from_task2a = task_2a()

    for url in url_from_task2a:
        # add url to csv
        row_list_2b["url"].append(url)

        # get its header
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        header_txt = soup.find("h1").text
        body_txt = soup.find(id="articleDetail").text
        # add header to csv
        add_header(header_txt, row_list_2b)

        # add player names (all urls should have a player name)
        if find_names(header_txt) != "no name here":
            player_name = find_names(header_txt)
        else:
            player_name = find_names(body_txt)
        add_player_name(player_name, row_list_2b)
        player_name = player_name.title()

        # add scores
        valid_score = extract_scores(header_txt, body_txt)
        if not valid_score:
            row_list_2b["url"].remove(url)
            row_list_2b["header"].remove(header_txt)
            row_list_2b["player"].remove(player_name)
        else:
            add_score(valid_score, row_list_2b)

    #     writing series to dataframe
    df = pd.DataFrame(row_list_2b)
    df.set_index("url", inplace=True)
    # writing dataframe to csv file
    df.to_csv("task2.csv")

    # pass the urls from task 2a to task 2b
    task_2b_urls = row_list_2b["url"]
    return task_2b_urls


def task_3():
    # create empty series for writing to csv file for task 3
    row_list_3 = {}
    row_list_3["player"] = []
    row_list_3["avg_game_difference"] = []

    url_from_task2b = task_2b()

    for url in url_from_task2b:

        # get its header and body texts
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        header_txt = soup.find("h1").text
        body_txt = soup.find(id="articleDetail").text

        # add player names (all urls should have a player name)
        if find_names(header_txt) != "no name here":
            player_name = find_names(header_txt)
        else:
            player_name = find_names(body_txt)

        if player_name.title() in row_list_3["player"]:
            continue

        else:
            add_player_name(player_name, row_list_3)
            player_name = player_name.title()

            # add average difference (all urls should have a valid score)
            valid_score = extract_scores(header_txt, body_txt)
            avg_diff = extract_avg_diff(valid_score)
            add_avg_diff(avg_diff, row_list_3)

    # writing series to dataframe
    df = pd.DataFrame(row_list_3)
    df.set_index("player", inplace=True)
    # writing dataframe to csv file
    df.to_csv("task3.csv")

    # pass urls to task 4 and 5
    return url_from_task2b


def task_4():

    # create empty series for writing to csv file for task 3
    row_list_4 = {}
    row_list_4["url"] = []
    row_list_4["player"] = []

    url_from_task3 = task_3()

    for url in url_from_task3:
        # add url to csv
        row_list_4["url"].append(url)

        # get its header and body texts
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        header_txt = soup.find("h1").text
        body_txt = soup.find(id="articleDetail").text

        # add player names (all urls should have a player name)
        if find_names(header_txt) != "no name here":
            player_name = find_names(header_txt)
        else:
            player_name = find_names(body_txt)

        add_player_name(player_name, row_list_4)
        player_name = player_name.title()

    # convert to df and extract list of player names
    df = pd.DataFrame(row_list_4)
    player_names = row_list_4["player"]

    # group by number of unique urls in descending order (want top 5)
    grouped = df.groupby(player_names)
    top_5 = grouped.count().sort_values("url", ascending=False)[0:5]

    # extract the input data for bar graph (player names and # of articles)
    names = list(top_5.index)
    articles = list(top_5["player"])

    # set figure size for bar graph
    plt.figure(figsize=(8, 5))

    # colour the bars
    cmap = plt.cm.tab10
    colors = plt.cm.tab10(np.arange(len(df)) % cmap.N)

    # plot the bar graph
    plt.bar(arange(len(articles)), articles, color=colors)

    # set font size, roation and style for ticks and labels
    plt.yticks(size=16)
    plt.xticks(arange(len(names)), names, rotation=30, size=12, ha="center")
    plt.ylabel("number of articles", size=16)
    plt.xlabel("player", size=16)

    # set title of bar graph
    plt.title("Task 4: Top 5 Players with Most Articles Written", size=16)

    # save bar graph to task4.png
    plt.savefig("task4.png", bbox_inches="tight")
    plt.show()
    plt.close()


def task_5():

    # create empty series for writing to csv file for task 3
    row_list_5 = {}
    row_list_5["player"] = []
    row_list_5["avg_game_difference"] = []
    row_list_5["win_percentage"] = []

    url_from_task3 = task_3()

    for url in url_from_task3:

        # get its header and body texts
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        header_txt = soup.find("h1").text
        body_txt = soup.find(id="articleDetail").text

        # add player names (all urls should have a player name)
        if find_names(header_txt) != "no name here":
            player_name = find_names(header_txt)
        else:
            player_name = find_names(body_txt)

        if player_name.title() in row_list_5["player"]:
            continue

        else:
            add_player_name(player_name, row_list_5)
            player_name = player_name.title()

            # add average difference (all urls should have a valid score)
            valid_score = extract_scores(header_txt, body_txt)
            avg_diff = extract_avg_diff(valid_score)
            add_avg_diff(avg_diff, row_list_5)

    unique_names = list(set(row_list_5["player"]))

    # add win percentage
    for name in row_list_5["player"]:
        row_list_5["win_percentage"].append(float(win_percent_dct[name].strip("%")))

    # draw scatter plot
    plt.figure(figsize=(24, 15))
    plt.scatter(
        row_list_5["avg_game_difference"],
        row_list_5["win_percentage"],
        s=160,
        c=np.random.rand(len(row_list_5["win_percentage"]), 3),
    )
    plt.xlim(-1, 11)
    plt.ylim(40, 85)
    plt.xlabel("average game difference", size=20)
    plt.ylabel("win percentage (%)", size=20)
    plt.grid(True)
    plt.title(
        "Task 5: Win Percentage vs. Average Game Difference of Players with >0 Valid Articles",
        size=20,
    )

    plt.figtext(
        0,
        0,
        "NOTE: overlapped player names are Robin Soderling and Carlos Moya, with win average of 64.2% and 64.3% respectively, and an average game difference of 3 for both.",
        size=20,
    )

    # label each point
    for name, percent, avg in zip(
        row_list_5["player"],
        row_list_5["win_percentage"],
        row_list_5["avg_game_difference"],
    ):
        plt.annotate(
            name,
            (avg, percent),
            size=14,
            textcoords="offset points",
            xytext=(0, 10),
            ha="left",
            va="baseline",
        )

    plt.savefig("task5.png", bbox_inches="tight")
    plt.show()
    plt.close()


#     DEBUG: writing series to dataframe
#     df = pd.DataFrame(row_list_5)
#     df.set_index('player', inplace=True)
#     # writing dataframe to csv file
#     df.to_csv('task5.csv')


# calling functions
task_4()
task_5()
