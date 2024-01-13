import streamlit as st
from datetime import datetime
# import requests
import json
import sys

import pandas as pd

from thefuzz import fuzz, process
from google.oauth2.service_account import Credentials
import gspread

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Playoff_Fantasy_Overview
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import sportsdata_interface



def access_sheet_in_drive(roster_google_sheet_name, worksheet_number = 0):
    """Connect to Google sheets & get access to the sheet with name matching 
            yearly_setting[Playoff_Fantasy_Overview.selected_year][roster_google_sheet_name]"""

    # CONNECT TO GOOGLE SHEETS (where I store the roster info)
    # credit: https://www.codeforests.com/2020/11/22/gspread-read-write-google-sheet/
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes)
    client = gspread.authorize(creds)
    google_sh = client.open(roster_google_sheet_name)
    google_sheet = google_sh.get_worksheet(worksheet_number)

    return google_sheet

def write_all_players_to_json_file():
    ## Get settings from config file
    with open('yearly_settings.json', 'r') as yearly_settings:
        config_data = json.load(yearly_settings)

    if Playoff_Fantasy_Overview.selected_year in config_data.get('settings', {}):
        year_settings = config_data['settings'][Playoff_Fantasy_Overview.selected_year]
        afc_alive_teams = year_settings.get("alive_AFC")
        nfc_alive_teams = year_settings.get("alive_NFC")

        teams = afc_alive_teams + nfc_alive_teams
                                                                    
    ## write all playoff_players to a 
    all_players_dict = sportsdata_interface.get_all_players(teams)

    with open('all_players.json', 'w') as f:
        json.dump(all_players_dict, f)


def write_team_names_to_json_file():
    ## Get settings from config file
    with open('yearly_settings.json', 'r') as yearly_settings:
        config_data = json.load(yearly_settings)

    if Playoff_Fantasy_Overview.selected_year in config_data.get('settings', {}):
        year_settings = config_data['settings'][Playoff_Fantasy_Overview.selected_year]
        afc_alive_teams = year_settings.get("alive_AFC")
        nfc_alive_teams = year_settings.get("alive_NFC")

        teams = afc_alive_teams + nfc_alive_teams
                                                                    
    ## write all playoff_players to a  json file
    all_teams_dict = sportsdata_interface.get_all_teams_names(teams)

    with open('all_playoff_teams.json', 'w') as f:
        json.dump(all_teams_dict, f)


class RosterManager:

    def __init__(self, google_sheet) -> None:
        self.google_sheet = google_sheet
        self.full_rosters_dict = self.create_full_rosters_dict(google_sheet)
        self.cleaned_full_rosters_dict = self.clean_player_names(self.full_rosters_dict)
        self.alphabetized_full_rosters_dict = self.alphabetize_players_by_position(self.cleaned_full_rosters_dict)
        pass

    def create_full_rosters_dict(self, google_sheet):

        """Take the Google Sheet of Rosters and return a dict
        
        The dict is formatted like: {"Casey M": {"QB1": "Brock Purdy", "QB2": "Lamar", "K1": "J Tucker"}}, etc.
        """
        full_rosters_dict = {}
        rows = google_sheet.get_all_values()  # Get all rows in the sheet

        start_of_players_idx = 2 ## skipping 'GM' and 'Time Submitted', the first 2 columns
        for idx, row in enumerate(rows):
            if idx == 0: ## 1st row gives us the column names
                pos_strings = row[start_of_players_idx:]
            else:
                gm = row[0]  # The GM is in the first cell of the row
                player_names = row[start_of_players_idx:]  # The players are in the remaining cells of the row

                # Create a dictionary with keys 'Pos1', 'Pos2', etc. and values being the players
                player_dict = {pos_string: player_name for player_name, pos_string in zip(player_names, pos_strings)}

                # Add the GM and their players to the full rosters dictionary
                full_rosters_dict[gm] = player_dict

        return full_rosters_dict

    def clean_player_names(self, full_rosters_dict):

        """Take in a dict of rosters (1 'roster' on each row) and cleans them to match NFL player names
        outputs the GM, orignal_name, fixed_name for each changed name to a name_cleaning.txt file

        Expect: full_rosters_dict is formatted like: {"Casey M": {"QB1": "Brock Purdy", "QB2": "Lamar", "K1": "J Tucker"}}, etc.
        --> return dict will be formatted in the same way (just having player names that match the API player names)
        """
        # All players in the playoffs, taken from the API (output of write_all_players_to_json_file())
        with open('all_players.json', 'r') as f:
            all_players_dict = json.load(f)
            api_player_names_list = all_players_dict.keys()

        with open('all_playoff_teams.json', 'r') as f:
            all_teams_dict = json.load(f)
            api_teams_list = list(all_teams_dict.keys()) + list(all_teams_dict.values())
        
        cleaned_rosters_dict = {}   

        ## Iterate through each player on each team and 
        with open('name_cleaning.txt', 'w') as f:
            for gm, roster in full_rosters_dict.items():
                cleaned_roster = {}
                for pos, original_player in roster.items():
                    original_player = original_player.strip()
                    if pos == 'SB Total Points': ## won't have matches in the api_player_names_list
                        cleaned_roster["pos"] = original_player

                    elif pos in ["D1", "D2", "SB Champ", "SB Runner Up"]:
                        if original_player == "Niners" or  original_player == "49ers" or original_player == "San Francisco": ## Deal w/ strange edge case where 'Niners' > 'BAL'
                            original_player = "SF"
            
                        ## Need 2 steps here b/c first step cleans into either Key (SF) or team (San Francisco 49ers)
                        ## and 2nd step converts team into Key
                        api_team_name, ratio = process.extractOne(original_player, api_teams_list)
                        if api_team_name == "San Francisco 49ers": ## b/c chose BAL over SF (why!?)
                            api_team_key2, ratio = 'SF', 99
                        if api_team_name == "Kansas City Chiefs": ## b/c chose PHI over KC (why!?)
                             api_team_key2, ratio = 'KC', 99
                        else:    
                            ## Future consideration: maybe this second check should just be a mapping based on the API 'team' an 'Key' values
                            api_team_key2, ratio = process.extractOne(api_team_name, list(all_teams_dict.keys()))
                        cleaned_roster[pos] = api_team_key2

                        if ratio < 100: ## Write to name_cleaning.txt so we can inspect the changes
                            f.write(f'{ratio}, {gm}, {original_player}, {api_team_key2}\n')

                    else:
                        api_player, ratio = process.extractOne(original_player, api_player_names_list)
                        cleaned_roster[pos] = api_player

                        if ratio < 100: ## Write to name_cleaning.txt so we can inspect the changes
                            f.write(f'{ratio}, {gm}, {original_player}, {api_player}\n') 


                cleaned_rosters_dict[gm] = cleaned_roster

        return cleaned_rosters_dict


    def alphabetize_players_by_position(self, cleaned_rosters_dict):
        """
        Takes in a cleaned dict formatted like {"Casey M": {"QB1": "Lamar Jackson", "QB2": "Brock Purdy", "K1": "Justin Tucker",....}}
        and returns an 'alphabetized by position' dict -- ie:  {"Casey M": {"QB1": "Brock Purdy", "QB2": "Lamar Jackson", "K1": "Justin Tucker",....}}
        """
        alphabetized_rosters_dict = {}
        positions_list = ["QB", "K", "D", "P"]
        for gm, roster in cleaned_rosters_dict.items():
            gm_roster_alphabetized_dict = {}
            for simple_pos in positions_list:
                numbered_positions_list = []
                player_name_list = []
                for numbered_pos, player_name in roster.items():
                    if numbered_pos[:-1] == simple_pos:
                        numbered_positions_list.append(numbered_pos)
                        player_name_list.append(player_name)
                player_name_list.sort() 
                for numbered_pos2, player_name2 in zip(numbered_positions_list, player_name_list):
                    gm_roster_alphabetized_dict[numbered_pos2] = player_name2
                
                for numbered_pos3 in roster.keys():
                    if numbered_pos3 not in gm_roster_alphabetized_dict.keys():
                        gm_roster_alphabetized_dict[numbered_pos3] = roster.get(numbered_pos3)
            alphabetized_rosters_dict[gm] = gm_roster_alphabetized_dict
        print(alphabetized_rosters_dict)
        return alphabetized_rosters_dict
                    

    


if __name__ == '__main__':
    ## Get settings from config file
    with open('yearly_settings.json', 'r') as yearly_settings:
        config_data = json.load(yearly_settings)

    if Playoff_Fantasy_Overview.selected_year in config_data.get('settings', {}):
        year_settings = config_data['settings'][Playoff_Fantasy_Overview.selected_year]
        roster_google_sheet_name = year_settings.get("roster_google_sheet_name")

    ## Access Data in Rosters Google Sheet
    gsheet = access_sheet_in_drive(roster_google_sheet_name)

    # create instance of the RosterManager class to do the managin! 
    rm = RosterManager(gsheet)
