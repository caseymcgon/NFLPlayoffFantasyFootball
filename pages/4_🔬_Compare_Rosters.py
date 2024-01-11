## Compare_Rosters.py, a page in the Playoff_Fantasy.py app

def show_rosters():
    import streamlit as st
    import json
    import pandas as pd

    import Playoff_Fantasy_Overview
    from utils import ui_utils, roster_manager

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

    start_date_deadline_utc = ui_utils.get_utc_datetime(start_date_deadline_str)
    print(start_date_deadline_utc)
    diff, before_deadline_bool = ui_utils.compute_time_till_deadline(start_date_deadline_utc)


    if False: #before_deadline_bool:
        st.write("Coming soon...after Kickoff on Saturday")
    else: ## Show Roster DFs
       
        ## Access Data in Rosters Google Sheet
        gsheet = roster_manager.access_sheet_in_drive(roster_google_sheet_name)

        # create instance of the RosterManager class to do the managin! 
        rm = roster_manager.RosterManager(gsheet)

        full_rosters_dict = rm.alphabetized_full_rosters_dict

        full_rosters_df = pd.DataFrame.from_dict(full_rosters_dict, orient = 'index')

        st.markdown("## All Submitted Rosters")
        st.dataframe(full_rosters_df, use_container_width = False)
        tip_expander = st.expander("free tip")
        tip_expander.markdown(f"use the search button (🔍) in the top right (or click on the table & hit `⌘+F` or `Ctrl+F`) to quickly see which people drafted any player")   
        
        
        st.markdown("""
                    ---
                    ### Compare Rosters
                """)
            ## TODO: Add 4 search fields
            

        st.markdown("""
                    ---
                    ### Quick Stats    
                """)








    # else:



if __name__ == '__main__':
    show_rosters()