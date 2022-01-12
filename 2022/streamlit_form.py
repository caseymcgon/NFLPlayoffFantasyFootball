def make_form():
    import streamlit as st
    from datetime import datetime
    import pytz

    from google.oauth2.service_account import Credentials
    import gspread

    st.set_page_config(page_title="Playoff Fantasy -- Roster Input", layout="wide", page_icon = "🏈")
    deadline = "**Deadline: 1:30pm PST Sat. Jan 15, 2022.**"


    # CONNECT TO GOOGLE SHEETS
    # credit: https://www.codeforests.com/2020/11/22/gspread-read-write-google-sheet/
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes)
    client = gspread.authorize(creds)
    google_sh = client.open("Rosters_2022")
    sheet1 = google_sh.get_worksheet(0)


    # creds = Credentials.from_service_account_file(".streamlit/keys.json", scopes=scopes)
    # client = gspread.authorize(creds)
    # google_sh = client.open("Rosters_2022")
    # sheet1 = google_sh.get_worksheet(0)

    # Intro & Instructions
    st.write(f"""
    # **2022 McGon NFL Playoff Fantasy Pool**
    ---
    ##### $10 Buy-In. Winner-Take-All
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
    
    {deadline}
    
    You may submit as many times as you'd like before the deadline.
    Only your final submission before the deadline will be counted.
    """)

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
        form.write("please venmo $10 @kelly-McGonigle")



    # Logic for what to do when user hits Submit Button
    if submit:

        PST = pytz.timezone('America/Los_Angeles')
        dt = datetime.now(PST)
        entryTime = dt.strftime('%Y-%m-%d %H:%M')
        sheet1.append_rows(values=[[f"{name}", f"{entryTime}" , f"{qb1}", f"{qb2}",
                                    f"{k1}", f"{k2}", f"{d1}", f"{d2}",
                                    f"{p1}", f"{p2}", f"{p3}", f"{p4}",
                                    f"{p5}", f"{p6}", f"{p7}",
                                    f"{champ}", f"{runner}", f"{score}"]])


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

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
