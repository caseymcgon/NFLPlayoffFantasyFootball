import streamlit as st
import json

import ui_utils

st.set_page_config(
    page_title="Hello",
    layout="wide", 
    page_icon="🏈",
)

# Load the yearly_settings.json file
with open('yearly_settings.json', 'r') as yearly_settings:
    config_data = json.load(yearly_settings)

# Choose the year for which you want to use settings
selected_year = '2022'  # You can change this to '2024' as needed

st.write(f"# {selected_year} McGonigle Playoff Fantasy Pool")

# Access the selected year's settings
if selected_year in config_data.get('settings', {}):
    year_settings = config_data['settings'][selected_year]
    start_date_deadline = year_settings.get('start_date_deadline')
    roster_google_file_path = year_settings.get('roster_google_file_path')
    buy_in = year_settings.get('buy_in')
    
    ui_utils.display_start_date_countdown(start_date_deadline, selected_year)



st.markdown(
    f"""
    ## ⬅️ Click Roster Input on the Left to Choose Your Team

    ### So far, xxx people have made a team!


    ### Basic rules of the league: 

    ##### {buy_in} Buy-In. Winner-Take-All
    venmo @kelly-McGonigle or arrange with John McGonigle
    
    ---
    ##### Scoring
     - **TD** = 5 + 1 for every 10 yards
        - Ex: 47yd TD = 9 pts
     - **FG** = 1 for every 10 yards, + 1 for every yard over 55
        - Ex: 47yd FG = 4 pts; 57yd FG = 7 pts
     - **PAT** = 1
     - **2-point PAT** = 2
     - **Safety** = 2 (for defense)
       - All returns for a TD, including INTs, fumbles, KO’s, and punts, count as Defense TD’s.  
       - These TD’s and safeties are the only way for defenses to score.

    ---
    ##### Input Your Playoff Roster Below
     - 2 Quarterbacks
     - 2 Kickers
     - 2 Defenses
     - 7 Position Players (RBs, WRs, TEs)
       - 1st Tiebreaker: Super Bowl Champion 
       - 2nd Tiebreaker: Super Bowl Runner-Up
       - 3rd Tiebreaker: Super Bowl Total Points
    
    {start_date_deadline}
    
    You may submit as many times as you'd like before the deadline.
    Only your final submission before the deadline will be counted.
"""
)

