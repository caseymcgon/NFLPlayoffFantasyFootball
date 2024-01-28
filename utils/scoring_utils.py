


import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import regex as re
import json

from datetime import datetime
import pytz

# sys.path.insert(0, '../utils/')  # Add the directory to the Python path
import Playoff_Fantasy_Overview
from utils import sportsdata_interface, datetime_utils


now_pst = datetime.now(pytz.timezone('US/Pacific'))
this_postseason_for_API = f'{int(Playoff_Fantasy_Overview.selected_year) - 1}POST' 
cache_ttl_logic = 3600*6 if now_pst.weekday() < 5 else 3600/4

player_name_regex = '([A-Z][a-z\'.-]*\s*(?:[A-Z][a-z\'.-]*\s*)*)'

#########################################################################
############## LOAD DATA FROM JSON FILES & APIs #########################
#########################################################################

## Load all playoff players metadata so we can track who's still alive
with open('all_players.json', 'r') as f:
    all_players_meta_dict = json.load(f)

## Load in active teams from yearly_settings.json
with open('yearly_settings.json', 'r') as yearly_settings:
    config_data = json.load(yearly_settings)

    if Playoff_Fantasy_Overview.selected_year in config_data.get('settings', {}):
        year_settings = config_data['settings'][Playoff_Fantasy_Overview.selected_year]
        alive_teams_list = year_settings.get("alive_AFC") + year_settings.get("alive_NFC")
        week_info_dict = year_settings.get("week_info", "No week info found")
    else:
        alive_teams_list = []
        week_info_dict = {}

## Load in all selected players so we can count how many owners each player has
with open('full_alphabetized_rosters.json') as f:
    alphabetized_rosters_dict = json.load(f)

    ## remove tiebreaker keys that aren't actually player selections
    for gm, roster_dict in alphabetized_rosters_dict.items():
        roster_dict.pop("SB Champ", None)
        roster_dict.pop("SB Runner Up", None)
        roster_dict.pop("pos", None)
        alphabetized_rosters_dict[gm] = roster_dict


#########################################################################
##### HELPER FUNCS TO EXTRACT FANTASY SCORING INFO FROM API RESULTS #####
#########################################################################

def calculate_points(row):
    """
    Calculate the points based on the given row of data.
    ----------
    Params:
    - row: A dictionary representing a row of data with the following keys:
        - 'Distance': The distance of the play.
        - 'FG': Boolean indicating if it is a field goal.
        - 'TD': Boolean indicating if it is a touchdown.
        - 'Safety': Boolean indicating if it is a safety.

    Returns:
    - Integer: The calculated points based on the given row of data.
    """
    if row['FG']:
        return (row['Distance'] // 10) + max(0, row['Distance'] - 55)
    elif row['TD']:
        return 5 + (row['Distance'] // 10)
    elif row['Safety']:
        return 2
    else:
        return 0

# Function to extract Player1
def extract_player1(row):
    if row['Def TD'] or row['Safety']:
        return row['Team'].strip()
    else:
        match = re.match(fr'{player_name_regex}', row['PlayDescription'])
        return match.group(1).strip() if match else ''
    
# Function to extract Player2
def extract_player2(row):
    match = re.search(fr'passed to {player_name_regex}', row['PlayDescription'])
    return match.group(1).strip() if match else ''

def filter_out_missed_kicks(df):
    condition = ~(
        (~df['PlayDescription'].str.contains('touchdown', case=False)) &
        (~df['PlayDescription'].str.contains('Safety', case=False)) &
        (df['PlayDescription'].str.contains('missed|blocked', case=False))
    )
    return df[condition].reset_index(drop=True)

def add_pat_to_scoring_df(df, matchup_pats_dict):
    new_rows = []  # List to store the new rows
    for player, pat in matchup_pats_dict.items():
        # Extract the number of PATs from the string
        num_pats = int(pat.split()[0])
        # Calculate the points based on the type of PAT
        if '1pt' in pat:
            points = num_pats * 1
        elif '2pt' in pat:
            points = num_pats * 2
        else:
            print(f"PAT Type not recognized for {player}")
            continue  # Skip if the PAT type is not recognized

        
        # Create a new row and add it to the list
        new_row = {'Player1': player, 'PlayDescription': pat, 'Points': points, 
                    'Team': '', 'Player2': '', 'Distance': 0, 
                    'TD': False, 'FG': False, 'Def TD': False, 'Safety': False}
        new_rows.append(new_row)
    
    # Convert the list of new rows to a DataFrame and concatenate it with the existing DataFrame
    new_rows_df = pd.DataFrame(new_rows)
    df = pd.concat([df, new_rows_df], ignore_index=True)
    
    return df

def is_player_alive(player_name, all_players_dict = all_players_meta_dict, alive_team_list = alive_teams_list):
    ## look for defenses first
    if player_name not in all_players_dict.keys():
        if player_name in alive_team_list:
            return True
        else:
            return False
    elif all_players_dict.get(player_name).get("Team") in alive_team_list:
        return True
    else:
        return False
    
def count_num_owners(player_name, full_rosters_dict = alphabetized_rosters_dict):
    ## full_rosters_dict should be formatted like {GM1: {posA: playerA, posB: playerB...}, GM2: {posA: playerA...}}
    return sum(player_name in player for roster in full_rosters_dict.values() for player in roster.values())


#########################################################################
######### CREATE SCORING DATAFRAMES FOR EACH WEEK FROM API ##############
#########################################################################

## re-load data once daily if on weekday. If on weekends, reload every 15 mins
@st.cache_data(ttl=cache_ttl_logic)
def create_game_scoring_dfs_by_week(playoff_round_name_str, season_str = this_postseason_for_API):
    
    # Regular expression pattern for a 1 or 2 digit integer with ' yard' or '-yard' after it
    distance_pattern = r'(\d+)(?=\s*-?\s*yard(?!\s*s))' 
    scoring_dfs = {}
    
    week_int = week_info_dict.get(playoff_round_name_str, '').get("week_num")
    ## all_scoring_plays list is of lists of dicts (each dict is 1 scoring play -- thus, the inner list is 1 game's-worth of scoring plays)
    all_scoring_plays_list = sportsdata_interface.get_all_scoring_plays_by_week(season_str, week_int)
    print('L164', all_scoring_plays_list, '\n')
    if len(all_scoring_plays_list) == 0:
        st.markdown(f"""### No scoring yet in the {playoff_round_name_str} Round""")
        return {}

    ## Create Tables of Scoring in Each Game & put them on streamlit
    for game in all_scoring_plays_list:
        if len(game) == 0:
            continue
        awayteam, hometeam = game[0].get("AwayTeam"), game[0].get("HomeTeam")
        matchup = f"{awayteam}@{hometeam}"

        raw_scoring_df = pd.DataFrame(game)
        raw_scoring_df = raw_scoring_df[["Team", "PlayDescription"]]

        # Extract the key values from the PlayDescription
        raw_scoring_df['Distance'] = raw_scoring_df['PlayDescription'].str.extract(distance_pattern, expand=False).astype(int)
        raw_scoring_df['TD'] = raw_scoring_df['PlayDescription'].str.contains('touchdown')
        raw_scoring_df['FG'] = raw_scoring_df['PlayDescription'].str.contains('kicked')
        raw_scoring_df['Def TD'] = raw_scoring_df['PlayDescription'].str.contains('intercepted|fumbled|kicked off|punted')
        raw_scoring_df['Safety'] = raw_scoring_df['PlayDescription'].str.contains('Safety')

        raw_scoring_df['Points'] = raw_scoring_df.apply(calculate_points, axis=1)

        raw_scoring_df['Player1'] = raw_scoring_df.apply(extract_player1, axis=1)
        raw_scoring_df['Player2'] = raw_scoring_df.apply(extract_player2, axis=1)

        raw_scoring_df = filter_out_missed_kicks(raw_scoring_df)

        # Temporary workaround for getting PAT data (manual) -- since the API doesnt provide it
        with open('pats_temp.json', 'r') as f:
            pat_data = json.load(f)
        matchup_pats_dict = pat_data.get(matchup, {})
        raw_scoring_df = add_pat_to_scoring_df(raw_scoring_df, matchup_pats_dict)

        raw_scoring_df = raw_scoring_df[["Points", "Player1", "Player2", "Team", "PlayDescription",  "Distance", "TD", "FG", "Def TD", "Safety"]]

        scoring_dfs[matchup] = raw_scoring_df
    return scoring_dfs

############################################################################
###### CREATE PLAYERS TOTAL SCORING DATAFRAME VIA WEEKLY SCORING DFS #######
############################################################################

@st.cache_data(ttl=cache_ttl_logic)
def create_player_total_scoring_df(scoring_dfs, total_scoring_dict = {}, is_player_alive_helper = is_player_alive):
    for matchup, scoring_df in scoring_dfs.items():
        for index, row in scoring_df.iterrows():
            player1 = row['Player1']
            player2 = row['Player2']
            points = row['Points']
            total_scoring_dict[player1] = total_scoring_dict.get(player1, 0) + points
            if player2 != '':
                total_scoring_dict[player2] = total_scoring_dict.get(player2, 0) + points

    players_total_scoring_df = (pd.DataFrame.from_dict(total_scoring_dict, 
                                                        orient = 'index')
                                                        .reset_index(drop = False)
                                                        .rename(columns = {'index': "Players", 0: "Points"})
                                                        .sort_values(by = "Points", ascending = False)
                                                        .reset_index(drop = True)
                                                    )
    
    players_total_scoring_df["Alive?"] = players_total_scoring_df["Players"].apply(lambda x: "✅" if is_player_alive_helper(x) else "❌")
    players_total_scoring_df['# Owners'] = players_total_scoring_df['Players'].apply(count_num_owners)
    return players_total_scoring_df, total_scoring_dict
