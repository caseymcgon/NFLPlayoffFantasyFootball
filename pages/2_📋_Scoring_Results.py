## Scoring_Results.py, a page in the Playoff_Fantasy.py app

def main():

    import streamlit as st
    import json

    from utils import  scoring_utils, datetime_utils

    import Playoff_Fantasy_Overview

    ##########################################################################
    ####### GET SCORING FOR EACH WEEK & POST RESULTS TO STREAMLIT ########
    ##########################################################################

    ## Save space at the top of the UI for Total Scoring Table
    total_scoring_placeholder = st.empty() 

    all_weeks_scoring_dfs_dict = {}
    for week_str in ['Wild Card', 'Divisional', 'Conference', 'Super Bowl']:

        ## Skip weeks that haven't started yet
        start_date_str = scoring_utils.week_info_dict.get(week_str).get("start_date")
        utc_date = datetime_utils.get_utc_datetime(start_date_str, strp_format = "%b %d, %Y")
        time_till_week_starts, before_week_started_bool = datetime_utils.compute_time_till_deadline(utc_date)
        if week_str == 'Wild Card' and before_week_started_bool:
            print(f"start date: {start_date_str}")
            print(f"utc_date: {utc_date}")
            # Extract days, hours, and minutes from time_till_week_starts
            # total_seconds = int(time_till_week_starts.total_seconds())
            # days, remainder = divmod(total_seconds, 86400)  # Seconds in a day
            # hours, remainder = divmod(remainder, 3600)      # Seconds in an hour
            # minutes = remainder // 60     
            st.write(f""" Coming soon...after Kickoff on Saturday {start_date_str}
                    """)
            return
        elif before_week_started_bool:
            continue

        st.markdown(f"""
                    ---

                    ## {week_str} Round
                    """)
        week_scoring_dfs = scoring_utils.create_game_scoring_dfs_by_week(week_str)
        week_expander = st.expander(f"{week_str} Scoring by Game", expanded = False)
        for matchup, scoring_df in week_scoring_dfs.items():
                week_expander.markdown(f"""### {matchup}""")
                week_expander.dataframe(scoring_df, use_container_width=True)   

        all_weeks_scoring_dfs_dict[week_str] = week_scoring_dfs
        print("week_str")
        if week_str == 'Wild Card':
            players_total_scoring_df, players_total_scoring_dict = scoring_utils.create_player_total_scoring_df(all_weeks_scoring_dfs_dict.get(week_str, {}), {})
        else:
            players_total_scoring_df, players_total_scoring_dict = scoring_utils.create_player_total_scoring_df(all_weeks_scoring_dfs_dict.get(week_str, {}), players_total_scoring_dict)
    
    
    # players_total_scoring_df, players_total_scoring_dict = scoring_utils.create_player_total_scoring_df(all_weeks_scoring_dfs_dict, players_total_scoring_dict)
    with open('total_scoring.json', 'w') as f:
        json.dump(players_total_scoring_dict, f)

    ## Display Total Scoring Table at top of page
    with total_scoring_placeholder.container():
        st.write(Playoff_Fantasy_Overview.PAT_UPDATE_NOTE)
        st.markdown(f"""

            # Players Total Scoring

            """)
        player_total_scoring_expander = st.expander("All Player Points to Date", expanded = True)
        player_total_scoring_expander.dataframe(players_total_scoring_df, 
                     height = (1 + len(players_total_scoring_df)) * 13, 
                     use_container_width=True
                    )


if __name__ == "__main__":
    main()