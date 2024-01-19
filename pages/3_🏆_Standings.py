## streamlit_results.py

def main():

    import altair as alt
    import numpy as np
    import pandas as pd
    import streamlit as st
    import requests
    import sys
    import os
    import json

    # sys.path.insert(0, '../utils/')  # Add the directory to the Python path
    import Playoff_Fantasy_Overview
    from utils import ui_utils, roster_manager


     # Load the yearly_settings.json file
    with open('yearly_settings.json', 'r') as yearly_settings:
        config_data = json.load(yearly_settings)

    # Access the selected year's settings
    if Playoff_Fantasy_Overview.selected_year in config_data.get('settings', {}):
        year_settings = config_data['settings'][Playoff_Fantasy_Overview.selected_year]
        start_date_deadline_str = year_settings.get('start_date_deadline_pst')
        roster_google_sheet_name = year_settings.get("roster_google_sheet_name")

    start_date_deadline_utc = ui_utils.get_utc_datetime(start_date_deadline_str)
    diff, before_deadline_bool = ui_utils.compute_time_till_deadline(start_date_deadline_utc)


    if before_deadline_bool:
        st.write("Coming soon...after the first weekend's games take place")
    else:

        # Path to the JSON file
        roster_json_file = 'full_alphabetized_rosters.json' 
        ## note: even though this Compare_Rosters.py file is in the pages directory, 
        ## this looks in / writes to the NFLPlayoffFantasyFootball (parent) directory 
        ## (b/c this page is run via the Playoff_Fantasy_Overview.py page in that directory)
       
        # Call Google sheets the first time. After that, just access the json file
        if not os.path.exists(roster_json_file):
            gsheet = roster_manager.access_sheet_in_drive(roster_google_sheet_name)
            # create instance of the RosterManager class to do the managin! 
            rm = roster_manager.RosterManager(gsheet)
            full_rosters_dict = rm.alphabetized_full_rosters_dict
            with open(roster_json_file, 'w') as f:
                json.dump(full_rosters_dict, f)

        else:
            # If the JSON file exists, set full_rosters_dict equal to the contents of the file
            with open(roster_json_file, 'r') as f:
                full_rosters_dict = json.load(f)
        
        with open('total_scoring.json', 'r') as f:
            total_scoring_dict = json.load(f)

        scoring_by_roster_dict = {}
        for gm, roster in full_rosters_dict.items():
            scoring_by_roster_dict[gm] = {}
            for position, player in roster.items():
                if position in ['SB Champ', 'SB Runner Up', "pos"]:
                    continue
                scoring_by_roster_dict[gm][player] = total_scoring_dict.get(player, 0)

        standings_dict = {}

        st.markdown("""# Standings 
        
                    """)
        standings_slot = st.empty()

        st.markdown("""
                    ---
                    
                    ### Scoring by Team 
        
                    """)
        for gm, roster in scoring_by_roster_dict.items():

            scoring_df =(pd.DataFrame.from_dict(roster, 
                                                orient = 'index')
                                                .reset_index(drop = False)
                                                .rename(columns = {'index': "Players", 0: "Points"})
                                                .sort_values(by = "Points", ascending = False)
                                                .reset_index(drop = True)
                                                )
            total_points = scoring_df['Points'].sum()
            new_row = pd.DataFrame([{'Players': 'TOTAL', 'Points': total_points}])
            scoring_df = pd.concat([scoring_df, new_row], ignore_index=True)
            
            standings_dict[gm] = total_points
            st.write(f"{gm} - {total_points}")
            st.dataframe(scoring_df, height = len(scoring_df)*38)


        standings_df = (pd.DataFrame.from_dict(standings_dict, 
                                                    orient = 'index') 
                                                    .reset_index(drop = False)
                                                    .rename(columns = {'index': "GM", 0: "Points"})
                                                    .sort_values(by = "Points", ascending = False)
                                                    .reset_index(drop = True)
                                )
        standings_slot.dataframe(standings_df, height = len(standings_df)*38 )
    # st.set_page_config(page_title="Results", layout="wide", page_icon="🏈")




if __name__ == "__main__":
    main()