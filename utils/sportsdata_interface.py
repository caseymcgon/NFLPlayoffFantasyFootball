## sportdata_interface.py contains functions to access data from the sportsdata.io APIs
import streamlit as st
import requests
from typing import List
import json

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import Playoff_Fantasy_Overview

def get_all_players(teams: List[str]):
    sportsdata_api_key = st.secrets["sportsdata"]["api_key"]

    all_fantasy_players = {}
    for team in teams:
        team_roster = access_sportsdata_api(f'https://api.sportsdata.io/v3/nfl/scores/json/Players/{team}?key={sportsdata_api_key}')

        for player in team_roster:
            if player.get("Position") in ["QB", "WR", "RB", "RB", "FB", "TE", "K"]:
                player_name = player.get('Name')
                all_fantasy_players[player_name] = {
                        "Position": player.get("Position"),
                        "Team": player.get("Team"),
                        "PlayerID": player.get("PlayerID")
                }
    return all_fantasy_players

def get_all_teams_names(teams: List[str]):

    sportsdata_api_key = st.secrets["sportsdata"]["api_key"]

    team_info_dicts = access_sportsdata_api(f'https://api.sportsdata.io/v3/nfl/scores/json/TeamsBasic?key={sportsdata_api_key}')

    team_name_dict = {} ## will eventually be formatted like {"SF": "San Francisco 49ers"}
    for info_dict in team_info_dicts:
        if info_dict.get("Key") in teams:
            team_name_dict[info_dict.get("Key")] = info_dict.get("FullName")

    return team_name_dict


def access_sportsdata_api(endpoint):

    
    # headers = {
    #     'Ocp-Apim-Subscription-Key:': api_key
    # }


    response = requests.get(endpoint)#, headers)

    data = response.json()

    return data

if __name__ == '__main__':

    ## Get settings from config file
    with open('yearly_settings.json', 'r') as yearly_settings:
        config_data = json.load(yearly_settings)

    if Playoff_Fantasy_Overview.selected_year in config_data.get('settings', {}):
        year_settings = config_data['settings'][Playoff_Fantasy_Overview.selected_year]
        afc_alive_teams = year_settings.get("alive_AFC")
        nfc_alive_teams = year_settings.get("alive_NFC")

        teams = afc_alive_teams + nfc_alive_teams
                                                                    
    ## write all playoff_players to a 
    all_players_dict = get_all_players(teams)

    with open('all_players.json', 'w') as f:
        json.dump(all_players_dict, f)

    # [print(p_dict, '\n') for p_dict in all_players_dict.items()]
