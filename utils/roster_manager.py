import streamlit as st
from datetime import datetime
import requests
import json
import sys

import pandas as pd

from google.oauth2.service_account import Credentials
import gspread

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Playoff_Fantasy_Overview



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

# def check_roster_is_filled():
#     return all(value is not None for value in form_values.values()

class RosterManager:

    def __init__(self, google_sheet) -> None:
        self.google_sheet = google_sheet
        self.full_rosters_dict = self.create_full_rosters_dict(google_sheet)
        self.cleaned_full_rosters_dict = self.clean_player_names(self.full_rosters_dict)
        pass

    def create_full_rosters_dict(self, google_sheet):

        """Take the Google Sheet of Rosters and return a dict"""
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
        """
        # Mapping of short names to full names
        name_mapping = {
            'Deebo': 'Deebo Samuel',
            'CD': 'CeeDee Lamb',
            'CMC': 'Christian McCaffrey'
            # Add more mappings here
            ## Will be replaced with data from sportsdata.io / internet
        }

        cleaned_rosters_dict = {}   

        with open('name_cleaning.txt', 'w') as f:
            for gm, roster in full_rosters_dict.items():
                cleaned_roster = {}
                for pos, player in roster.items():
                    original_name = player
                    fixed_name = name_mapping.get(original_name, player)  # Get the full name from the mapping, or use the short name if the full name is not in the mapping
                    cleaned_roster[pos] = fixed_name

                    if original_name != fixed_name:
                        f.write(f'{gm}, {original_name}, {fixed_name}\n')  # Write the GM, original name, and fixed name to the file

                cleaned_rosters_dict[gm] = cleaned_roster

        return cleaned_rosters_dict



if __name__ == '__main__':
    gsheet = access_sheet_in_drive()

    rm = RosterManager(gsheet)

    print(f"full_rosters_dict {rm.cleaned_full_rosters_dict}")
