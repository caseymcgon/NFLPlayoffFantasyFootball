## WC_scrape.py
from streamlit_results import *

import pandas as pd
import streamlit as st
import re
import math

import requests
from lxml import html
from lxml import etree

from bs4 import BeautifulSoup


# Part 2 - Create Webscraping Functions

# A
def get_scoring_data(input_url):
    """This function returns all the scoring plays from a given game as a list of strings"""
    """this format is for the ESPN Gamecast version of games"""

    assert type(input_url) == str, "input_url must be a string -- try putting it in quotes!"

    url = input_url
    res = requests.get(url)
    tree = html.fromstring(res.content)
    # get the info on scoring players, yardage, playtype, etc.
    scoring = tree.xpath('//div[@class="headline"]/text()')
    # get updated home and away scores
    homescore = list(map(int, tree.xpath('//td[@class="home-score"]/text()')))
    awayscore = list(map(int, tree.xpath('//td[@class="away-score"]/text()')))

    c = tuple(zip(awayscore, homescore))

    print(c)
    as_string = [str(i) for i in scoring]
    with_score = tuple(zip(as_string, c))
    return with_score



# B
def scoring_by_player(team1_at_team2_string):
    """This function assigns fantasy points from a single playoff game to the respective player"""

    new = []
    pos = 0
    scoring_string, points_string = zip(*team1_at_team2_string)

    for i in scoring_string:
        if "(Two-Point Pass Conversion Failed)" in i:
            new.append((str(i.rpartition("(Two-Point Pass Conversion Failed)")[0])))
        elif "(Two-Point Run Conversion Failed)" in i:
            new.append((str(i.rpartition("(Two-Point Run Conversion Failed)")[0])))
        elif '(' in i:
            new.extend((i.split("(")))
        else:
            new.append(i)
    new = [i.strip() for i in new]
    new = [i.strip(')') for i in new]
    # new = [i.replace('to ', '') for i in new]
    # get rid of all periods in names *(ie. Jr. or A.J.)
    new = [i.replace('.', '') for i in new]

    newer = []
    pos = 0
    for i in new:
        if 'pass' in i:
            add = i.split('pass from')
            newer.extend(add)
            newer[pos + 1] = newer[pos + 1] + ' ' + newer[pos][-6:] + 'pass'
            newer[pos] = newer[pos] + 'pass'
            pos += 2
        elif "Pass" in i:
            add = i.split("Pass to")
            newer.extend(add)
            newer[pos] = newer[pos] + "Two-Point Conversion"
            pos += 2
        else:
            newer.append(i)
            pos += 1

    newer = [i.strip() for i in newer]

    return newer



# C
def d_p_pt(scoring_by_player_func):
    """This function splits scoring plays into 3 distinct lists of distances, players, and play_type"""

    import re
    import math
    # regex1 = re.compile(r"(\w*? \w*? *?) [0-9|Kick|Pass|Run|for|Two|Safety|Fumble]")
    # regex1 = re.compile(r"(\D*? \D*? *?) [0-9|Kick|Pass|Run|for|Two|Safety|Fumble]")
    # KPRTSFIf is for Kick, Pass, Run, Two, Safety, Fumble, Interception, for
    regex1 = re.compile(r"([A-Z]\D*? [A-Z]\D*? *?) [0-9KPRTSFIf]")
    regex2 = re.compile(r'\d{1,3}')
    # regex3 = re.compile(r'\w+ \w+(.*)')
    # regex3 = re.compile(r'[^to ]\w+ [\w-]+(.*)')
    regex3 = re.compile(r'[A-Z]\w+ [\w-]+[^\s](.*)')

    scoring = scoring_by_player_func

    player = [re.findall(regex1, str(i))[0].strip() for i in scoring]
    dist = [re.findall(regex2, str(i)) for i in scoring]

    play_type = [re.findall(regex3, str(i))[0].strip().lower() for i in scoring]

    for i in dist:
        if i == []:
            i.append(0)
    distances = []
    distances = [i[0] for i in dist]

    return distances, player, play_type

# D
def make_game_df(d_p_pt_func):
    distances = d_p_pt_func[0]
    player = d_p_pt_func[1]
    play_type = d_p_pt_func[2]

    scores = pd.DataFrame(data={'player': player, 'distance': pd.to_numeric(distances), 'play type': play_type})

    scores["FG"] = 0
    scores["TD"] = 0
    scores["Safety"] = 0
    scores["PAT"] = 0
    scores["PAT2"] = 0
    scores.loc[scores["play type"].str.contains('field goal'), "FG"] = 1
    scores.loc[scores["play type"].str.contains("kick"), "PAT"] = 1
    scores.loc[scores["play type"].str.contains("two-point"), "PAT2"] = 1
    scores.loc[scores["play type"].str.contains("safety"), "Safety"] = 1
    scores.loc[scores["play type"].str.contains("pass"), "TD"] = 1
    scores.loc[scores["play type"].str.contains("run"), "TD"] = 1
    scores.loc[scores["play type"].str.contains("return"), "TD"] = 1
    scores.loc[scores["play type"].str.contains("recovery"), "TD"] = 1
    scores.loc[scores["TD"] == scores["PAT2"], "TD"] = 0

    scores["points"] = (((scores["FG"] * scores['distance']) // 10) +
                        ((5 * scores["TD"] + (scores["distance"]) // 10) * scores["TD"]) +
                        (2 * scores["Safety"]) +
                        (1 * scores["PAT"]) +
                        (2 * scores["PAT2"]))

    scores.loc[(scores["distance"] > 55) & (scores["FG"] == 1), "points"] = scores["points"] + (scores["distance"] - 55)

    return scores


# E - Combine A,B,C,D into 1 function - get_single_game_scores

def get_single_game_scores(input_url):
    """This combines all the functions written above into 1"""
    """This function's output is all the scoring (and respective points) for a single playoff game"""
    """Make sure the input_url format is for the ESPN Gamecast version of games in string form"""

    team1_at_team2_string = get_scoring_data(input_url)

    scoring_by_player_func = scoring_by_player(team1_at_team2_string)

    d_p_pt_func = d_p_pt(scoring_by_player_func)

    game_df = make_game_df(d_p_pt_func)

    full_game = game_df.replace({"kick": "PAT"})

    return full_game


## GET WC Weekend Scoring

lv_cin = get_single_game_scores("https://www.espn.com/nfl/game?gameId=401326627")
lv_cin_scorers = lv_cin.groupby("player").sum().sort_values("points", ascending=False).reset_index()[
        ["player", "FG", "PAT", "TD", "PAT2", "Safety", "points"]]

ne_buf = get_single_game_scores("https://www.espn.com/nfl/game?gameId=401326626")
ne_buf_scorers = ne_buf.groupby("player").sum().sort_values("points", ascending= False).reset_index()[["player","FG", "PAT","TD", "PAT2","Safety", "points"]]
ne_buf_scorers

phi_tb = get_single_game_scores("https://www.espn.com/nfl/game/_/gameId/401326630")
phi_tb_scorers = phi_tb.groupby("player").sum().sort_values("points", ascending=False).reset_index()[
        ["player", "FG", "PAT", "TD", "PAT2", "Safety", "points"]]
phi_tb_scorers

sf_dal = get_single_game_scores("https://www.espn.com/nfl/game/_/gameId/401326629")
sf_dal_scorers = sf_dal.groupby("player").sum().sort_values("points", ascending=False).reset_index()[
        ["player", "FG", "PAT", "TD", "PAT2", "Safety", "points"]]
sf_dal_scorers

pit_kc = get_single_game_scores("https://www.espn.com/nfl/game/_/gameId/401326628").replace({"TJ Watt": "PIT"})
pit_kc_scorers = pit_kc.groupby("player").sum().sort_values("points", ascending=False).reset_index()[
        ["player", "FG", "PAT", "TD", "PAT2", "Safety", "points"]]
pit_kc_scorers

ari_la = get_single_game_scores("https://www.espn.com/nfl/game/_/gameId/401326625").replace({"jr 4 yd pass": "4 yd pass", "jr 3 yd interception return": "3 yd interception return"})
ari_la_scorers = ari_la.groupby("player").sum().sort_values("points", ascending=False).reset_index()[
        ["player", "FG", "PAT", "TD", "PAT2", "Safety", "points"]]
ari_la_scorers

def wc_scores():
    col1, col2 = st.columns(2)

    # Raiders / Bengals
    col1.title("Raiders @ Bengals")
    col1.write("**Points for Each Player**")
    col1.dataframe(lv_cin_scorers)
    col1.write("")
    col1.write("")
    col1.write("")
    col1.write("")
    col1.write("")
    col1.write("")
    col1.write("**Each Scoring Play ... scroll!**")
    col1.dataframe(lv_cin)
    col1.write("")

    # Pats / Bills
    col1.title("Pats @ Bills")
    col1.write("**Points for Each Player**")
    col1.dataframe(ne_buf_scorers)
    col1.write("")
    col1.write("**Each Scoring Play ... scroll!**")
    col1.dataframe(ne_buf)
    col1.write("")

    # Steelers / Chiefs
    col1.title("Steelers @ Chiefs")
    col1.write("**Points for Each Player**")
    col1.dataframe(pit_kc_scorers)
    col1.write("")
    col1.write("**Each Scoring Play ... scroll!**")
    col1.dataframe(pit_kc)
    col1.write("")

    # Eagles / Bucs
    col2.title("Eagles @ Bucs")
    col2.write("**Points for Each Player**")
    col2.dataframe(phi_tb_scorers)
    col2.write("")
    col2.write("**Each Scoring Play ... scroll!**")
    col2.dataframe(phi_tb)
    col2.write("")

    # 49ers / Cowboys
    col2.title("49ers @ Cowboys")
    col2.write("**Points for Each Player**")
    col2.dataframe(sf_dal_scorers)
    col2.write("")
    col2.write("")
    col2.write("")
    col2.write("")
    col2.write("")
    col2.write("")
    col2.write("")
    col2.write("")
    col2.write("**Each Scoring Play ... scroll!**")
    col2.dataframe(sf_dal)
    col2.write("")

    # Cards / Rams
    col2.title("Cardinals @ Rams")
    col2.write("**Points for Each Player**")
    col2.dataframe(ari_la_scorers)
    col2.write("")
    col2.write("")
    col2.write("**Each Scoring Play ... scroll!**")
    col2.dataframe(ari_la)

## Part B: Concat WC weekend together

wc_games = [lv_cin, ne_buf, phi_tb, sf_dal, pit_kc, ari_la]

wc = pd.concat(wc_games)[["player", "points"]]
wc = wc.groupby("player").sum().reset_index()
wc_sort = wc.sort_values("points", ascending = 0).reset_index(drop = True).rename(columns = {"points": "WC Points"})


