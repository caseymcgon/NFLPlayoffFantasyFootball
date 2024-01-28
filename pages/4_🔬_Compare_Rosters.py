## Compare_Rosters.py, a page in the Playoff_Fantasy.py app

def show_rosters():
    import streamlit as st
    import os
    import json
    import pandas as pd

    import Playoff_Fantasy_Overview
    from utils import roster_manager, datetime_utils

    st.set_page_config(
            page_title=" Roster Comparison", 
            layout="wide", 
            page_icon = "🏈")

    # Load the yearly_settings.json file
    with open('yearly_settings.json', 'r') as yearly_settings:
        config_data = json.load(yearly_settings)

    # Access the selected year's settings
    if Playoff_Fantasy_Overview.selected_year in config_data.get('settings', {}):
        year_settings = config_data['settings'][Playoff_Fantasy_Overview.selected_year]
        start_date_deadline_str = year_settings.get('start_date_deadline_pst')
        roster_google_sheet_name = year_settings.get("roster_google_sheet_name")

    start_date_deadline_utc = datetime_utils.get_utc_datetime(start_date_deadline_str)
    diff, before_deadline_bool = datetime_utils.compute_time_till_deadline(start_date_deadline_utc)


    if before_deadline_bool:
        st.write("Coming soon...after Kickoff on Saturday")
    else: ## Show Roster DFs

        # Path to the JSON file
        json_file = 'full_alphabetized_rosters.json' 
        ## note: even though this Compare_Rosters.py file is in the pages directory, 
        ## this looks in / writes to the NFLPlayoffFantasyFootball (parent) directory 
        ## (b/c this page is run via the Playoff_Fantasy_Overview.py page in that directory)
       
        # Call Google sheets the first time. After that, just access the json file
        if not os.path.exists(json_file):
            gsheet = roster_manager.access_sheet_in_drive(roster_google_sheet_name)
            # create instance of the RosterManager class to do the managin! 
            rm = roster_manager.RosterManager(gsheet)
            full_rosters_dict = rm.alphabetized_full_rosters_dict
            with open(json_file, 'w') as f:
                json.dump(full_rosters_dict, f)

        else:
            # If the JSON file exists, set full_rosters_dict equal to the contents of the file
            with open(json_file, 'r') as f:
                full_rosters_dict = json.load(f)

        full_rosters_df = pd.DataFrame.from_dict(full_rosters_dict, orient = 'index')

        st.markdown("## All Submitted Rosters")
        st.dataframe(full_rosters_df, use_container_width = False, height = len(full_rosters_dict)*37)
        tip_expander = st.expander("free tip")
        tip_expander.markdown(f"use the search button (🔍) in the top right (or click on the table & hit `⌘+F` or `Ctrl+F`) to quickly see which people drafted any player")   
        
        
        # st.markdown("""
        #             ---
        #             ### Compare Rosters
        #         """)
        #     ## TODO: Add 4 search fields
            

        # st.markdown("""
        #             ---
        #             ### Quick Stats    
        #         """)


if __name__ == '__main__':
    show_rosters()