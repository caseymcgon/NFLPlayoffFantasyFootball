## Playoff_Fantasy.py -- the main / landing page for the app

selected_year = '2024' ## key to access values from yearly_settings.json

def show_league_info(selected_year):
    import streamlit as st
    import json
    import datetime as dt
    import time

    from utils import ui_utils

    st.set_page_config(
        page_title="Playoff Fantasy",
        layout="wide", 
        page_icon="🏈",
    )

    # load configs & rules stored in external files
    with open('yearly_settings.json', 'r') as yearly_settings:
        config_data = json.load(yearly_settings)

    with open('rules.md', 'r') as file:
        rules = file.read()

    st.write(f"# **{selected_year} McGonigle Playoff Fantasy Football**")

    # Access the selected year's settings
    if selected_year in config_data.get('settings', {}):
        year_settings = config_data['settings'][selected_year]
        start_date_deadline = year_settings.get('start_date_deadline_pst')
        roster_google_file_path = year_settings.get('roster_google_file_path')
        buy_in = year_settings.get('buy_in')
        
        # ui_utils.display_start_date_countdown(start_date_deadline, selected_year)
        
        st.markdown(
            f"""
            ---
            #### ⬅️ Choose Your Team in the Roster Input Tab
            ---
            """
        )

        st.markdown(rules, unsafe_allow_html=True)

        ui_utils.display_deadline_message(start_date_deadline, selected_year)

        st.markdown(
            f"""
                ---
                ##### {buy_in} Buy-In. **Winner-Take-All**
                Please venmo Casey **@cmcgo** or arrange with John McGonigle before the deadline

                ---
                As a reminder, the [NFL Playoff Picture can be found here](https://www.nfl.com/standings/playoff-picture)
                """
        )


    #     # Set your deadline
    # deadline = dt.datetime(2024, 1, 13, 13, 30, 0)

    # # Streamlit app loop
    # while True:
    #     # Calculate time remaining
    #     now = dt.datetime.now()
        
    #     countdown_time = deadline - now

    #     # Check if the deadline has passed
    #     if countdown_time.total_seconds() <= 0:
    #         st.write("The deadline has passed!")
    #         break

    #     # Display the countdown
    #     st.write(f"Time remaining: {countdown_time}")

    #     # Refresh every second
    #     time.sleep(1)
    #     st.experimental_rerun()

    else:
        st.write(f"Still working on updating the website for this year. Please come back later")


if __name__ == "__main__":
    show_league_info(selected_year)
