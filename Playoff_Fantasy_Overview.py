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
           2024 Wild Card Weekend ✅. And just like that...down go the Dallas Cowboys. For the 30th time in the last 30 years, America's Team will not be competing in the NFC's Conference Championship Game and that just breaks this Niners fan's heart...but actually it kinda does -- at the last moment I added 3 'Boys to my roster, as did MANY others (26/34 of us picked CeeDee, 19 Aubrey, 13 DAL D, 11 Dak...).

            Anyway, it's still early, and almost anything can happen from here on out. We'll learn a lot more about who's got a shot at this thing after this weekend's matchups (Texans @ Ravens & Packers @ Niners on Sat; Bucs @ Lions & Chiefs @ Bills on Sunday). 

            For the time being, Bills Mafia Cardholder Will Grant (Kelly's SCU buddy) has 90 points and a 10 point lead over the pack (thanks in part to the Josh Allen <> Khalil Shakir connection), but he's got a load of dead dudes (Dak, Ferguson, Puka, Aubrey, DAL, CeeDee, Raheem) and has earned himself the ignominious distinction of being the first ever participant in our little playoff pool to select a player (Leonard Fournette) who was subsequently released from his NFL team! So that's 8/13 players out after 1 week...yikes. Wilch, next year please remember: in this league, the best ability is *availability*.

            Elsewhere, 4 of the top 5 (Stroud, Mayfield, HOU D, and Love -- all moving on to the Divisional Round) are unowned, but 17 of us are on Josh Allen's league leading 28 points. Other missed opportunities include the 3 unowned Defenses (HOU : 21 pts, GB : 11 pts, TB: 2 pts) that scored this weekend. On the other hand 5 CLE owners and 13 DAL owners went out out scoreless.

            On a non-football note: please leave some feedback & features requests for things you'd like to be able to do in the app! I am still adding new features for this year and would love to incorporate your ideas. And as always, please audit the scorekeeping and let me know if your team looks wrong to you somehow. I changed up a lot of the backend infrastructure this year in an effort to automate a lot of the work (we should get score updates every 30 minutes during this weekend's games), but that work is certainly bug-prone. Shoot me an email or text if anything looks fishy to you.

            Thanks again for playing & see you next week. In the meantime, Go Niners!

            Go Niners!
            - Casey

            ---
            """
        )

        st.markdown(rules, unsafe_allow_html=True)

        ui_utils.display_deadline_message(start_date_deadline, selected_year)

        st.markdown(
            f"""
                ---
                ##### 💰 {buy_in} Buy-In. **Winner-Take-All**
                Please venmo Casey **@cmcgo** or arrange with John McGonigle before the deadline

                ---
                As a reminder, the [NFL Playoff Picture can be found here](https://www.nfl.com/standings/playoff-picture)
                """
        )


    else:
        st.write(f"Still working on updating the website for this year. Please come back later")


if __name__ == "__main__":
    show_league_info(selected_year)
