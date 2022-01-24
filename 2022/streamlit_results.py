## streamlit_results.py

from WC_scrape import *

#import WC_scrape

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import requests
from lxml import html
from lxml import etree
#st.set_page_config(page_title="Playoff Fantasy -- Results", layout="wide", page_icon="🏈")


###
###
###

###### *PART 1 - CREATE DFs FROM ROSTER INPUT FORM*
#   Most important tables :
#       - popular_players
#       - allteams2 = Team GM & their chosen players
#       - teams_dict = {gm: df of roster}
#       - all_owners =  (list of gms)
#

# List of teams that are still playin'
alive_list = [ "LAR", "SF",  "KC", "CIN"]

## Get Teams from Rosters_2022.csv

roster_infos = pd.read_csv("2022/Rosters_2022.csv")[['GM', 'QB1', 'QB2', 'K1', 'K2', 'D1', 'D2', 'P1', 'P2', 'P3', 'P4',
                                                'P5', 'P6', 'P7', 'SB_Champ', 'Runner_Up', 'SB_Points']]
allteams2 = roster_infos[['GM', 'QB1', 'QB2', 'K1', 'K2', 'D1', 'D2', 'P1', 'P2', 'P3', 'P4',
                          'P5', 'P6', 'P7']]
## Remove all pre- and post-name spaces
allteams2 = allteams2.applymap(lambda x: x.strip() if isinstance(x, str) else x)


## Create teams_dict {owner: roster} & all_owners (list of owners) & sort each position alphabetically per team
teams_dict = {}

for index, team in allteams2.iterrows():
    # get GM's name
    name = team["GM"]

    # sort QBs in alphabetic for each team
    qbs = [team["QB1"], team["QB2"]]
    qbs.sort()
    team["QB1"], team["QB2"] = qbs
    # sort Ks in alphabetic for each team
    ks = [team["K1"], team["K2"]]
    ks.sort()
    team["K1"], team["K2"] = ks
    # sort Ds in alphabetic for each team
    ds = [team["D1"], team["D2"]]
    ds.sort()
    team["D1"], team["D2"] = ds
    # sort Pos in alphabetic for each team
    ps = [team["P1"], team["P2"], team["P3"], team["P4"], team["P5"], team["P6"], team["P7"]]
    ps.sort()
    team["P1"], team["P2"], team["P3"], team["P4"], team["P5"], team["P6"], team["P7"] = ps

    # create dictionary that makes stores the GM: Team
    team = pd.DataFrame(team[1:])
    team.columns = ["player"]
    teams_dict[name] = team




all_gms = list(teams_dict.keys())


# QB
qb_owners = allteams2[['QB1', 'QB2']].apply(pd.Series.value_counts).fillna(0)
qb_owners["#_squads"] = qb_owners["QB1"] + qb_owners["QB2"]
qb_owners = qb_owners.drop(columns={"QB1", "QB2"}).rename(columns={"index": "NFL Player"}).sort_values("#_squads",
                                                                                       ascending=False)
qb_owners = qb_owners.reset_index()
qb_owners["NFL"] = ["GB", "KC", "BUF", "TB", "CIN", "DAL", "LAR", "PIT", "PHI"]
qb_owners["Position"] = "QB"

# POSITION PLAYERS
p_owners = allteams2[['P1', 'P2', 'P3', 'P4', "P5", 'P6', 'P7']].apply(pd.Series.value_counts).reset_index().fillna(
    0)
p_owners["#_squads"] = p_owners["P1"] + p_owners["P2"] + p_owners['P3'] + p_owners['P4'] + p_owners["P5"] + \
                       p_owners['P6'] + p_owners['P7']
p_owners = p_owners.drop(columns={"P1", "P2", "P3", "P4", "P5", "P6", "P7"}).sort_values("#_squads",
                                                                                         ascending=False)
p_owners = p_owners.reset_index(drop=True)
p_owners["NFL"] = ["GB", "KC", "CIN", "KC", "LAR", "TEN", "BUF", "CIN", "TB", "GB",
                   "TB", "SF", "BUF", "TB", "DAL", "BUF", "DAL", "LAR", "SF", "CIN",
                   "SF", "GB", "PHI", "KC", "GB", "BUF", "BUF", "OAK", "ARI", "PIT",
                   "PIT", "PIT", "NE", "BUF", "PHI", "DAL", "TEN"]
p_owners["Position"] = "Pos"

# DEFENSE
d_owners = allteams2[['D1', 'D2']].apply(pd.Series.value_counts).fillna(0)
d_owners["#_squads"] = d_owners["D1"] + d_owners["D2"]
d_owners = d_owners.drop(columns={"D1", "D2"}).rename(columns={"index": "NFL Player"}).sort_values("#_squads",
                                                                                                ascending=False)
d_owners = d_owners.reset_index()
d_owners["NFL"] = d_owners["index"]
d_owners["Position"] = "D"

#KICKERS
k_owners = allteams2[['K1', 'K2']].apply(pd.Series.value_counts).fillna(0)
k_owners["#_squads"] = k_owners["K1"] + k_owners["K2"]
k_owners = k_owners.drop(columns={"K1", "K2"}).rename(columns={"index": "NFL Player"}).sort_values("#_squads",
                                                                                                 ascending=False)
k_owners = k_owners.reset_index()
k_owners["NFL"] = ["KC", "TB", "BUF", "DAL", "GB", "LAR", "CIN", "SF", "PIT", "PHI", "ARI", "NE", "TEN"]
k_owners["Position"] = "K"
k_owners.head(2)

# ADD QBs, Ps, Ks, Ds together w/ NFL team, Position, #_squads
all_owners = pd.concat([qb_owners, p_owners, k_owners, d_owners])[
    ["index", "NFL", "Position", "#_squads"]].sort_values("#_squads", ascending=False)
popular_players = all_owners.rename(columns={"index": "player"})
# ADD ALIVE LIST
popular_players["Alive"] = np.where(popular_players["NFL"].isin(alive_list), True, False)
# Get the columns in the correct oder
popular_players = popular_players[["player", "NFL", "Position", "#_squads", "Alive", ]].reset_index(drop=True)


###
### PART 2: Scrape the web for scoring
###

# A
def get_scoring_data(input_url):
    #"""This function returns all the scoring plays from a given game as a list of strings"""
    #"""this format is for the ESPN Gamecast version of games"""

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
    #"""This function assigns fantasy points from a single playoff game to the respective player"""

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
    #"""This function splits scoring plays into 3 distinct lists of distances, players, and play_type"""

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
    #"""This combines all the functions written above into 1"""
    #"""This function's output is all the scoring (and respective points) for a single playoff game"""
    #"""Make sure the input_url format is for the ESPN Gamecast version of games in string form"""

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
#ne_buf_scorers

phi_tb = get_single_game_scores("https://www.espn.com/nfl/game/_/gameId/401326630")
phi_tb_scorers = phi_tb.groupby("player").sum().sort_values("points", ascending=False).reset_index()[
        ["player", "FG", "PAT", "TD", "PAT2", "Safety", "points"]]
#phi_tb_scorers

sf_dal = get_single_game_scores("https://www.espn.com/nfl/game/_/gameId/401326629")
sf_dal_scorers = sf_dal.groupby("player").sum().sort_values("points", ascending=False).reset_index()[
        ["player", "FG", "PAT", "TD", "PAT2", "Safety", "points"]]
#sf_dal_scorers

pit_kc = get_single_game_scores("https://www.espn.com/nfl/game/_/gameId/401326628").replace({"TJ Watt": "PIT"})
pit_kc_scorers = pit_kc.groupby("player").sum().sort_values("points", ascending=False).reset_index()[
        ["player", "FG", "PAT", "TD", "PAT2", "Safety", "points"]]
#pit_kc_scorers

ari_la = get_single_game_scores("https://www.espn.com/nfl/game/_/gameId/401326625").replace({"jr 4 yd pass": "4 yd pass", "jr 3 yd interception return": "3 yd interception return", "David Long Jr": "LAR"})
ari_la_scorers = ari_la.groupby("player").sum().sort_values("points", ascending=False).reset_index()[
        ["player", "FG", "PAT", "TD", "PAT2", "Safety", "points"]]
#ari_la_scorers

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

## Add Divisional Weekend Games
cin_ten = get_single_game_scores("https://www.espn.com/nfl/game/_/gameId/401326632")#.replace({"TJ Watt": "PIT"})
cin_ten_scorers = cin_ten.groupby("player").sum().sort_values("points", ascending=False).reset_index()[
        ["player", "FG", "PAT", "TD", "PAT2", "Safety", "points"]]

sf_gb = get_single_game_scores("https://www.espn.com/nfl/game/_/gameId/401326631").replace({"Talanoa Hufanga": "SF"})
sf_gb_scorers = sf_gb.groupby("player").sum().sort_values("points", ascending=False).reset_index()[
        ["player", "FG", "PAT", "TD", "PAT2", "Safety", "points"]]

lar_tb = get_single_game_scores("https://www.espn.com/nfl/game/_/gameId/401326634")#.replace({"Talanoa Hufanga": "SF"})
lar_tb_scorers = lar_tb.groupby("player").sum().sort_values("points", ascending=False).reset_index()[
        ["player", "FG", "PAT", "TD", "PAT2", "Safety", "points"]]

buf_kc = get_single_game_scores("https://www.espn.com/nfl/game/_/gameId/401326633")#.replace({"Talanoa Hufanga": "SF"})
buf_kc_scorers = buf_kc.groupby("player").sum().sort_values("points", ascending=False).reset_index()[
        ["player", "FG", "PAT", "TD", "PAT2", "Safety", "points"]]


def div_scores():
    col1, col2 = st.columns(2)

    # Bengals / Titans
    col1.title("Bengals @ Titans")
    col1.write("**Points for Each Player**")
    col1.dataframe(cin_ten_scorers)
    col1.write("")
    col1.write("")
    col1.write("")
    col1.write("")
    col1.write("**Each Scoring Play ... scroll!**")
    col1.dataframe(cin_ten)
    col1.write("")

    # 49ers / Packers
    col1.title("49ers @ Packers")
    col1.write("**Points for Each Player**")
    col1.dataframe(sf_gb_scorers)
    col1.write("")
    col1.write("")
    col1.write("")
    col1.write("")
    col1.write("")
    col1.write("")
    col1.write("")
    col1.write("**Each Scoring Play ... scroll!**")
    col1.dataframe(sf_gb)


    # Rams / Bucs
    col2.title("Rams @ Bucs")
    col2.write("**Points for Each Player**")
    col2.dataframe(lar_tb_scorers)
    col2.write("")
    col2.write("**Each Scoring Play ... scroll!**")
    col2.dataframe(lar_tb)
    col2.write("")

    # Bills / Chiefs
    col2.title("Bills @ Chiefs")
    col2.write("**Points for Each Player**")
    col2.dataframe(buf_kc_scorers)
    col2.write("")
    col2.write("**Each Scoring Play ... scroll!**")
    col2.dataframe(buf_kc)
    col2.write("")

def concat_wc(word = "Go"): # Concat WC weekend games together
    wc_games = [lv_cin, ne_buf, phi_tb, sf_dal, pit_kc, ari_la]

    wc = pd.concat(wc_games)[["player", "points"]]
    wc = wc.groupby("player").sum().reset_index()
    wc_sort = wc.sort_values("points", ascending=0).reset_index(drop=True).rename(columns={"points": "WC Points"})

    return wc, wc_sort
# Merge wc_sort (from WC_scrape.py) with popular_players
wc, wc_sort = concat_wc()

def concat_div():
    div_games = [cin_ten, sf_gb, lar_tb, buf_kc]
    div = pd.concat(div_games)[["player", "points"]]
    div = div.groupby("player").sum().reset_index()
    div_sort = div.sort_values("points", ascending = 0).reset_index(drop=True).rename(columns={"points": "Div Points"})

    return div, div_sort

div, div_sort = concat_div()
# wc_full = wc_sort.merge(popular_players, how="right", on="player")[
#     ["player", "NFL", "Position", "WC Points", "Alive", "#_squads"]].fillna(0)
# wc_full = wc_full.sort_values(["WC Points"], ascending=0).reset_index(drop=True)

scoring_full = wc_sort.merge(popular_players, how = "outer", on = "player")#[["player","NFL", "Position", "WC Points", "Alive", "#_squads"]].fillna(0)
scoring_full = scoring_full.merge(div_sort, how = "outer", on = "player")[["player","NFL", "Position", "WC Points", "Div Points", "Alive", "#_squads"]].fillna(0)
scoring_full["Total Points"] = scoring_full["WC Points"] + scoring_full["Div Points"]
scoring_full = scoring_full.sort_values("Total Points", ascending = False).reset_index(drop = True)

scoring_full = scoring_full[["player","NFL", "Position", "Total Points", "WC Points", "Div Points",  "#_squads"]].fillna(0)
scoring_full["NFL"] = scoring_full["NFL"].replace({0: "na"})
scoring_full["Position"] = scoring_full["Position"].replace({0: "na"})
#scoring_full["Alive"] = scoring_full["Alive"].replace({0: "na"})
scoring_full.tail(40)


def make_team(squad, standings_df):
    #"""CREATE DF WITH EACH PLAYER ON A (FANTASY) ROSTER AND THEIR POINT TOTALS, BY ROUND"""
    name = squad[0]
    team = pd.DataFrame(squad[1:])
    team.columns=["player"]

    #"""Adding team & alive info"""
    #b = team
    ## take out the [[]] if you'd like to keep the #teams column
    team = team.merge(popular_players, how = "left", on = "player")[["player", "NFL", "Alive", "Position"]]

    # """Adding Wild Card results"""
    team = team.merge(wc, how = "left", on = "player").fillna(0).rename(columns = {"points" : "WC" })

    # """Adding Divisional results"""
    team = team.merge(div, how="left", on="player").fillna(0).rename(columns={"points": "Div"})

    # """Creating a Total Column that sums all the other columns"""
    team["Total"] = team["WC"] + team["Div"]# + team["Ship"] + team["SB"]
    team = team.append(team.sum(numeric_only=True), ignore_index=True)

    total = int(team.at[13, "Total"])
    alive = int(team.at[13, "Alive"])
    wc_points = int(team.at[13, "WC"])
    div_points = int(team.at[13, "Div"])
    team.at[13, "player"], team.at[13, "NFL"], team.at[13, "Position"] = name, name, "GM"

    qbs = list(list(team.loc[(team['Alive'] == True) & (team["Position"] == "QB")]["player"]))
    # print(qbs)
    ks = list(list(team.loc[(team['Alive'] == True) & (team["Position"] == "K")]["player"]))
    # print(ks)
    ds = list(list(team.loc[(team['Alive'] == True) & (team["Position"] == "D")]["player"]))
    ps = list(list(team.loc[(team['Alive'] == True) & (team["Position"] == "Pos")]["player"]))
    dead = list(team.loc[(team['Alive'] == False)]["player"])


    # # ## Consider including the list of their players that are still alive?
    stand.loc[len(stand.index)] = [name, total, wc_points, div_points, alive , qbs, ks, ds, ps, dead]
    return team


stand = pd.DataFrame(columns=["Team", "Total Points", "WC", "Div", "Num Alive", "QBs Remaining", "Ks Remaining", "Ds Remaining",
                              "Positions Remaining", "Dead"])

for index, row in allteams2.iterrows():
    squad = allteams2.loc[index]

    a = make_team(squad, stand)
    df_ind = a.at[13, "player"]
    teams_dict[df_ind] = a
stand = stand.sort_values("Total Points", ascending=0).reset_index(drop=True)

# create full standing
full_stand = roster_infos.merge(stand[["Team", "Total Points", "Num Alive"]], left_on = "GM", right_on = "Team")
full_stand = full_stand.sort_values(["Total Points", "Num Alive"], ascending = [False, False]).reset_index(drop=True)
full_stand_cols = ["GM", "Total Points", "Num Alive", "QB1", "QB2", "K1", "K2", "D1", "D2", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "SB_Champ", "Runner_Up", "SB_Points"]
full_stand = full_stand[full_stand_cols]


#### VIZZES
single = alt.selection_single()
bar = alt.Chart(stand).mark_bar().encode(
    x = alt.X("Team", sort = alt.SortField(field="Total Points", order='descending'), title = "Team"),
    y = alt.Y("Total Points"),
    tooltip = alt.Tooltip(["Team", "Total Points", "Num Alive", "QBs Remaining",
                           "Ks Remaining", "Ds Remaining", "Positions Remaining", "Dead"]),
    color = alt.Color("Num Alive", scale = alt.Scale(scheme = "lighttealblue", reverse=True))
    #color=alt.condition(single, 'count()', alt.value('lightgray'), legend = None)
).properties(width=1200, height=600, title = "Points by Team").configure_axis(
    labelFontSize=30,
    titleFontSize=35
).configure_title(fontSize= 45).add_selection(single)

circ = alt.Chart(stand).mark_circle(size=100).encode(
    x=alt.Y("Total Points", scale=alt.Scale(domain=(min(stand["Total Points"]), max(stand["Total Points"])))),
    y=alt.Y("Num Alive", title="Players Remaining"),
    tooltip=alt.Tooltip(
        ["Team", "Total Points", "Num Alive", "QBs Remaining", "Ks Remaining", "Ds Remaining", "Positions Remaining"]),
    color=alt.Color("Team", sort=list(stand["Team"]), scale=alt.Scale(scheme="lighttealblue", reverse=True))
).properties(width=1200, height=500, title="Points & Players Remaining by Team").configure_axis(
    labelFontSize=30,
    titleFontSize=35
).configure_title(fontSize= 45)#.add_selection(single)



## change next line each week
all_scoring_chart = alt.Chart(scoring_full).mark_bar().encode(
    x=alt.X("player", sort=alt.SortField(field="Total Points", order='descending')),
    y="Total Points",
    tooltip=alt.Tooltip(["player", "NFL:O", "Position", "#_squads","WC Points", "Div Points", "Total Points"]),
    color=alt.Color("#_squads", scale=alt.Scale(scheme="lighttealblue", reverse=False))
).properties(width=1600, height=500, title="All Weekends: Points for All Players").configure_axis(
    labelFontSize=20,
    titleFontSize=30
).configure_title(fontSize=40)

div_scoring_chart = alt.Chart(scoring_full).mark_bar().encode(
    x=alt.X("player", sort=alt.SortField(field="Div Points", order='descending')),
    y="Div Points",
    tooltip=alt.Tooltip(["player", "NFL:O", "Position", "#_squads", "Div Points", "Total Points"]),
    color=alt.Color("#_squads", scale=alt.Scale(scheme="lighttealblue", reverse=False))
).properties(width=1600, height=500, title="Divisional Weekend: Points for All Players").configure_axis(
    labelFontSize=20,
    titleFontSize=30
).configure_title(fontSize=40)

wc_scoring_chart = alt.Chart(scoring_full).mark_bar().encode(
    x=alt.X("player", sort=alt.SortField(field="WC Points", order='descending')),
    y="WC Points",
    tooltip=alt.Tooltip(["player", "NFL:O", "Position", "#_squads", "WC Points", "Total Points"]),
    color=alt.Color("#_squads", scale=alt.Scale(scheme="lighttealblue", reverse=False))
).properties(width=1600, height=500, title="Wild Card Weekend: Points for All Players").configure_axis(
    labelFontSize=20,
    titleFontSize=30
).configure_title(fontSize=40)

free_agents = scoring_full[scoring_full["#_squads"] == 0].sort_values("Total Points", ascending = 0).reset_index(drop=True)[["player", "Total Points", "WC Points", "Div Points"]]
free_agents.head()

undrafted_scoring = alt.Chart(free_agents).mark_bar().encode(
    x=alt.X("player", sort=alt.SortField(field="Total Points", order='descending')),
    y="Total Points",
    tooltip=alt.Tooltip(["player",  "WC Points", "Div Points", "Total Points"]),
    color=alt.Color("#_squads", scale=alt.Scale(scheme="lighttealblue", reverse=False))
).properties(width=1600, height=500, title="Points for All Undrafted Players").configure_axis(
    labelFontSize=20,
    titleFontSize=30
).configure_title(fontSize=40)








def main():
    st.set_page_config(page_title="Playoff Fantasy -- Results", layout="wide", page_icon="🏈")
    pages = {

        "Standings": page_home,
        "Teams": page_teams,
        "Scoring By Player": page_player_scoring,
        "Divisional Weekend Game-by-Game": page_div,
        "WC Weekend Game-by-Game": page_wc,
    }

    if "page" not in st.session_state:
        st.session_state.update({
            # Default page
            "page": "Standings",

            # Radio, selectbox and multiselect options
            "options": ["Hello", "Everyone", "Happy", "Streamlit-ing"],

            # Default widget values
            "text": "",
            "slider": 0,
            "checkbox": False,
            "radio": "Hello",
            "selectbox": "Hello",
            "multiselect": ["Hello", "Everyone"],
        })

    with st.sidebar:
        page = st.radio("Select your page", tuple(pages.keys()))

    pages[page]()


def page_home():
    bar
    st.write("---")
    circ
    st.write("---")
    st.title("Standings Table")
    full_stand

def page_teams():

    gms_tuple = tuple(full_stand["GM"])
    #st.write("I'm here to hold places")
    form = st.form("name form")
    with form:
    #     Section for Participant's Name
        cols1, cols2  = st.columns(2)

        name1 = cols1.selectbox("Which roster do you want to check out?", all_gms)
        name_str1 = str(name1)
        print(name1, name_str1)
        teams_dict.get(name_str1)

        name2 = cols2.selectbox("What other roster do you want to check out?", all_gms)
        name_str2 = str(name2)
        print(name2, name_str2)
        teams_dict.get(name_str2)

    #
        submitted = form.form_submit_button()
        # name2 = cols2.selectbox("What other roster do you want to check out?", all_gms)
        # name_str2 = str(name2)
        # print(name2, name_str2)
        # teams_dict.get(name_str2)

    if submitted:
        out1, out2 = st.columns(2)
        out1.title(name_str1)
        teams_df1 = teams_dict.get(name_str1)
        out1.write("**Points:** ")
        out1.write(teams_df1.loc[13, "Total"])
        out1.write("**Players Left:** ")
        out1.write(teams_df1.loc[13, "Alive"])
        out1.dataframe(teams_dict.get(name_str1).loc[0:12])

        out2.title(name_str2)
        teams_df2 = teams_dict.get(name_str2)
        out2.write("**Points:** ")
        out2.write(teams_df2.loc[13, "Total"])
        out2.write("**Players Left:**")
        out2.write(teams_df2.loc[13, "Alive"])
        out2.dataframe(teams_dict.get(name_str2).loc[0:12])



def page_div():
    st.title("Divisional Weekend Game-by-Game")
    div_scores()

def page_player_scoring():
    st.title("All Scorers -- All Rounds")
    st.altair_chart(all_scoring_chart)

    st.title("All Divisional Weekend Scorers")
    st.altair_chart(div_scoring_chart)

    st.title("All Wild Card Scorers")
    st.altair_chart(wc_scoring_chart)

    st.title("Best Undrafted Players")
    st.altair_chart(undrafted_scoring)


def page_wc():
    st.title("Wild Card Weekend Game-by-Game")

    ## Put in DFs of each WC game
    wc_scores()



if __name__ == "__main__":
    main()