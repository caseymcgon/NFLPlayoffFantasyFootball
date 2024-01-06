import streamlit as st
import json

import ui_utils

st.set_page_config(
    page_title="Hello",
    page_icon="🏈",
)

# Load the yearly_settings.json file
with open('yearly_settings.json', 'r') as yearly_settings:
    config_data = json.load(yearly_settings)

# Choose the year for which you want to use settings
selected_year = '2022'  # You can change this to '2024' as needed

st.write("# Welcome to The McGonigle Playoff Fantasy League! 👋")

# Access the selected year's settings
if selected_year in config_data.get('settings', {}):
    year_settings = config_data['settings'][selected_year]
    start_date_deadline = year_settings.get('start_date_deadline')
    roster_google_file_path = year_settings.get('roster_google_file_path')
    buy_in = year_settings.get('buy_in')
    
    ui_utils.display_start_date_countdown(start_date_deadline, selected_year)



st.markdown(
    """
    ## Click Roster Input on the right to Choose Your Team
"""
)

