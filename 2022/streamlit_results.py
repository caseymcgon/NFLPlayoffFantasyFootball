from WC_scrape import *

import streamlit as st
import pandas as pd
import numpy as np
import re
import math


import altair as alt
from collections import Counter


st.set_page_config(page_title="Playoff Fantasy -- Results", layout="wide", page_icon="🏈")
pd.set_option('display.max_rows', None)

###### *PART 1 - CREATE DFs FROM ROSTER INPUT FORM*
#   Most important tables :
#       - popular_players
#       - allteams2 = Team GM & their chosen players
#       - teams_dict = {gm: df of roster}
#       - all_owners =  (list of gms)
#

# List of teams that are still playin'
alive_list = ["GB", "TB", "LAR", "SF", "TEN", "KC", "BUF", "CIN"]

## Get Teams from Rosters_2022.csv

roster_infos = pd.read_csv("2022/Rosters_2022.csv")[['GM', 'QB1', 'QB2', 'K1', 'K2', 'D1', 'D2', 'P1', 'P2', 'P3', 'P4',
                                                'P5', 'P6', 'P7', 'SB_Champ', 'Runner_Up', 'SB_Points']]
allteams2 = roster_infos[['GM', 'QB1', 'QB2', 'K1', 'K2', 'D1', 'D2', 'P1', 'P2', 'P3', 'P4',
                          'P5', 'P6', 'P7']]
## Remove all pre- and post-name spaces
allteams2 = allteams2.applymap(lambda x: x.strip() if isinstance(x, str) else x)

## Create teams_dict {owner: roster} & all_owners (list of owners)
teams_dict = {}

for index, team in allteams2.iterrows():
    name = team["GM"]
    #print(name)
    team = pd.DataFrame(team[1:])
    team.columns=["player"]
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

## Merge wc_sort (from WC_scrape.py) with popular_players
wc_full = wc_sort.merge(popular_players, how="right", on="player")[
    ["player", "NFL", "Position", "WC Points", "Alive", "#_squads"]].fillna(0)
wc_full = wc_full.sort_values(["WC Points"], ascending=0).reset_index(drop=True)

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

    # """Creating a Total Column that sums all the other columns"""
    team["Total"] = team["WC"] #+ team["Div"] + team["Ship"] + team["SB"]
    team = team.append(team.sum(numeric_only=True), ignore_index=True)

    total = int(team.at[13, "Total"])
    alive = int(team.at[13, "Alive"])
    team.at[13, "player"], team.at[13, "NFL"], team.at[13, "Position"] = name, name, "GM"

    qbs = list(list(team.loc[(team['Alive'] == True) & (team["Position"] == "QB")]["player"]))
    # print(qbs)
    ks = list(list(team.loc[(team['Alive'] == True) & (team["Position"] == "K")]["player"]))
    # print(ks)
    ds = list(list(team.loc[(team['Alive'] == True) & (team["Position"] == "D")]["player"]))
    ps = list(list(team.loc[(team['Alive'] == True) & (team["Position"] == "Pos")]["player"]))
    dead = list(team.loc[(team['Alive'] == False)]["player"])


    # # ## Consider including the list of their players that are still alive?
    stand.loc[len(stand.index)] = [name, total, alive , qbs, ks, ds, ps, dead]
    return team


stand = pd.DataFrame(columns=["Team", "Total Points", "Num Alive", "QBs Remaining", "Ks Remaining", "Ds Remaining",
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
    color = alt.Color("Num Alive", scale = alt.Scale(scheme = "darkblue", reverse=False))
    #color=alt.condition(single, 'count()', alt.value('lightgray'), legend = None)
).properties(width=1400, height=600, title = "Points by Team").configure_axis(
    labelFontSize=30,
    titleFontSize=35
).configure_title(fontSize= 45).add_selection(single)

# bar
#
# #### WRITE TO STREAMLIT
#
#
# st.write("---")
# st.title("Standings")
# full_stand
#
# st.title("Popular Players")
# st.write("click on columns to sort by different values")
# wc_full
#
#
# st.title("Full Wild Card Scoring Info")
# st.dataframe(wc_sort)
#


## change next line each week
all_scorers = wc_full
wc_scoring_chart = alt.Chart(all_scorers).mark_bar().encode(
    x=alt.X("player", sort=alt.SortField(field="WC Points", order='descending')),
    y="WC Points",
    tooltip=alt.Tooltip(["player", "NFL:O", "Position", "#_squads", "WC Points"]),
    color=alt.Color("Alive", scale=alt.Scale(domain=[True, False], range=['green', 'red']))

).properties(width=1400, height=500, title="Points for All Owned Players, Wild Card Weekend").configure_axis(
    labelFontSize=20,
    titleFontSize=30
).configure_title(fontSize= 40)




def main():
    pages = {
        "Standings": page_home,
        #"Teams": page_teams,
        "WC Weekend Scoring": page_wc_scoring,
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
    st.title("Standings Table")
    full_stand

def page_teams():
   # gms_tuple = tuple(full_stand["GM"])

    form = st.form("name form")
    with form:
        # Section for Participant's Name
        form.write("inside the form")
        name = form.selectbox("Which roster do you want to check out?", all_gms)
        name_str = str(name)
        print(name_str)
        #teams_dict[name_str]

        submitted = form.form_submit_button("Submit")
        if submitted:
            st.write("submit :)")
            teams_dict[name]


def page_wc_scoring():
    st.title("Full Wild Card Scoring Info")
    st.altair_chart(wc_scoring_chart)
    wc_sort



def page_wc():
    st.title("Wild Card Weekend Game-by-Game")

    ## Put in DFs of each WC game
    wc_scores()



if __name__ == "__main__":
    main()