## Roster_Input.py, a page in the Playoff_Fantasy.py app

def make_form():
    import streamlit as st
    from datetime import datetime
    import pytz
    import requests
    import json
    import sys

    from google.oauth2.service_account import Credentials
    import gspread

    # from utils import ui_utils
    import Playoff_Fantasy_Overview
    from utils import ui_utils

    # Load the yearly_settings.json file
    with open('yearly_settings.json', 'r') as yearly_settings:
        config_data = json.load(yearly_settings)

    with open('rules.md', 'r') as file:
        rules = file.read()
        
    # Access the selected year's settings
    if Playoff_Fantasy_Overview.selected_year in config_data.get('settings', {}):
        year_settings = config_data['settings'][Playoff_Fantasy_Overview.selected_year]
        start_date_deadline_str = year_settings.get('start_date_deadline_pst')
        roster_google_sheet_name = year_settings.get('roster_google_sheet_name')
        buy_in = year_settings.get('buy_in')

    deadline = f"**Deadline: {start_date_deadline_str} PST.**"

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
    sheet1 = google_sh.get_worksheet(0)

    ## Add Collapsible Rules section
    expander = st.expander("What are the Rules again?")
    expander.markdown(rules, unsafe_allow_html=True)    

    # Create Form for inputting Roster
    form = st.form(key='Player Input')
    with form:
        # Section for Participant's Name
        name = form.text_input(label='Your Full Name')

        form.write("""---""")
        # Section for Player Inputs
        qbcols = st.columns(2)
        qb1 = qbcols[0].text_input("QB 1")
        qb2 = qbcols[1].text_input("QB 2")

        kcols = st.columns(2)
        k1 = kcols[0].text_input("K 1")
        k2 = kcols[1].text_input("K 2")

        dcols = st.columns(2)
        d1 = dcols[0].text_input("D 1")
        d2 = dcols[1].text_input("D 2")

        p1cols = st.columns(4)
        p2cols = st.columns(4)
        p1 = p1cols[0].text_input("Pos 1")
        p2 = p1cols[1].text_input("Pos 2")
        p3 = p1cols[2].text_input("Pos 3")
        p4 = p1cols[3].text_input("Pos 4")
        p5 = p2cols[0].text_input("Pos 5")
        p6 = p2cols[1].text_input("Pos 6")
        p7 = p2cols[2].text_input("Pos 7")

        form.write("""---""")
        # Section for Tiebreaker Inputs
        tiecols = st.columns(3)
        champ = tiecols[0].text_input("First Tiebreaker: Super Bowl Champ")
        runner = tiecols[1].text_input("Second Tiebreaker: Super Bowl Runner-Up")
        score = tiecols[2].slider("Third Tiebreaker: Super Bowl Total Points", min_value=2, max_value=120, value=60)

        form.write("""---""")
        # Section for the Submit Button
        form.write(f"{deadline}")
        submit = st.form_submit_button('Submit')



    # Logic for what to do when user hits Submit Button
    if submit:

        # Convert the string to UTC datetime object 
        start_date_deadline_utc = ui_utils.get_utc_datetime(start_date_deadline_str)
        diff, before_deadline_bool = ui_utils.compute_time_till_deadline(start_date_deadline_utc)

        pst_timezone = pytz.timezone('US/Pacific')
        now =  datetime.now().astimezone(pst_timezone)
        entry_time = datetime.strftime(now, "%Y-%m-%d %H:%M:%S")


        if before_deadline_bool:
            sheet1.append_rows(values=[[f"{name}", f"{entry_time}" , f"{qb1}", f"{qb2}",
                                        f"{k1}", f"{k2}", f"{d1}", f"{d2}",
                                        f"{p1}", f"{p2}", f"{p3}", f"{p4}",
                                        f"{p5}", f"{p6}", f"{p7}",
                                        f"{champ}", f"{runner}", f"{score}"]
                                    ], insert_data_option="INSERT_ROWS")
            st.write(f"#### please venmo {buy_in} @cmcgo")
            st.title("Team submitted Successfully. Good Luck!!")
            # st.write(f"{sheet1.get_all_values()}")
        # MESSAGE FOR PAST DEADLINE
        else:
            st.title("Sorry! It's past the Deadline!")

        return 
        # Allow user to see their team
        st.title(f"{name}'s Team")

        st.write("**Quarterbacks**")
        st.write(f'   1. {qb1} 2. {qb2}')

        st.write("**Kickers**")
        st.write(f'   1. {k1} 2. {k2}')

        st.write("**Defenses**")
        st.write(f'1. {d1} 2.  {d2}')

        st.write("**Position Players**")
        st.write(f'1. {p1} 2.  {p2} 3. {p3} 4. {p4} 5. {p5} 6. {p6} 7. {p7}')

        st.write("**Tie-Breakers**")
        st.write(f'1. SB Champ: {champ}')
        st.write(f'2. SB Runner-Up: {runner}')
        st.write(f'3. SB Total Points: {score}')

        st.write("**Submitted @**: ", entryTime, "pst")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    make_form()

