## Compare_Rosters.py, a page in the Playoff_Fantasy.py app

def show_rosters():
    import streamlit as st
    from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
    import os
    import json
    import pandas as pd
    from collections import Counter

    import Playoff_Fantasy_Overview
    from utils import roster_manager, datetime_utils, scoring_utils

    st.set_page_config(
            page_title=" Roster Comparison", 
            layout="wide", 
            page_icon = "🏈")

    # Load the yearly_settings.json file
    with open('yearly_settings.json', 'r') as yearly_settings:
        settings = json.load(yearly_settings)

    # Access the selected year's settings
    if Playoff_Fantasy_Overview.SELECTED_YEAR in settings.get('settings', {}):
        year_settings = settings['settings'][Playoff_Fantasy_Overview.SELECTED_YEAR]
        start_date_deadline_str = year_settings.get('start_date_deadline_pst')
        roster_google_sheet_name = year_settings.get("roster_google_sheet_name")

    start_date_deadline_utc = datetime_utils.get_utc_datetime(start_date_deadline_str)
    diff, before_deadline_bool = datetime_utils.compute_time_till_deadline(start_date_deadline_utc)


    if before_deadline_bool:
        st.write(f"Coming soon...after Kickoff on Saturday -- {diff}")
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


        full_rosters_df = pd.DataFrame.from_dict(full_rosters_dict, orient = 'index')\
                                        .rename(columns = {"pos": "SB Total Points"})

        ## get count of each player
        all_players_list = []
        for team_dict in full_rosters_dict.values():
            for pos, player in team_dict.items():
                if "QB" in pos or "K" in pos or "D" in pos or "P" in pos:
                    all_players_list.append(player)
        # print(Counter(all_players_list))
        player_counts = Counter(all_players_list)
        player_counts_df = pd.DataFrame(player_counts.items(), columns=['Player', '# Owners'])\
                                .sort_values(by = '# Owners', ascending = False)\
                                .reset_index(drop = True)
        player_counts_df["Team"] = player_counts_df["Player"].apply(scoring_utils.get_player_team)
        player_counts_df["Alive?"] = player_counts_df["Player"].apply(lambda x: "✅" if scoring_utils.is_player_alive(x) else "❌")
        st.markdown("## Player Counts")
        
        # Create GridOptionsBuilder to customize grid options
        gob = GridOptionsBuilder.from_dataframe(player_counts_df)
        for column in player_counts_df.columns:
            gob.configure_column(column, filter=True)
        gridOptions = gob.build()
        AgGrid(player_counts_df, gridOptions=gridOptions, update_mode=GridUpdateMode.MODEL_CHANGED)

        "---"

        st.markdown("## All Submitted Rosters")
        full_rosters_df = full_rosters_df.reset_index(drop = False).rename(columns = {"index": "GM"})
        # Create GridOptionsBuilder to customize grid options
        gob = GridOptionsBuilder.from_dataframe(full_rosters_df)
        for column in full_rosters_df.columns:
            gob.configure_column(column, filter=True)
        gridOptions = gob.build()
        AgGrid(full_rosters_df, gridOptions=gridOptions, update_mode=GridUpdateMode.MODEL_CHANGED)

        # st.dataframe(full_rosters_df, use_container_width = False, height = len(full_rosters_dict)*37)
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