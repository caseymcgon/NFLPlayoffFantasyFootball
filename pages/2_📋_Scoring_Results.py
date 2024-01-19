## Scoring_Results.py, a page in the Playoff_Fantasy.py app

def main():

    import altair as alt
    import numpy as np
    import pandas as pd
    import streamlit as st
    import requests
    import sys
    import regex as re
    import json
    from lxml import html, etree

    from datetime import date

    # sys.path.insert(0, '../utils/')  # Add the directory to the Python path
    from utils import ui_utils, sportsdata_interface
    from utils import WC_scrape

    today = date.today()

    #########################################################################
    ##### DEFINE FUNCS TO EXTRACT FANTASY SCORING INFO FROM API RESULTS #####
    #########################################################################

    def calculate_points(row):
        """
        Calculate the points based on the given row of data.
        ----------
        Params:
        - row: A dictionary representing a row of data with the following keys:
            - 'Distance': The distance of the play.
            - 'FG': Boolean indicating if it is a field goal.
            - 'TD': Boolean indicating if it is a touchdown.
            - 'Safety': Boolean indicating if it is a safety.

        Returns:
        - Integer: The calculated points based on the given row of data.
        """
        if row['FG']:
            return (row['Distance'] // 10) + max(0, row['Distance'] - 55)
        elif row['TD']:
            return 5 + (row['Distance'] // 10)
        elif row['Safety']:
            return 2
        else:
            return 0

    # Function to extract Player1
    def extract_player1(row):
        if row['Def TD'] or row['Safety']:
            return row['Team'].strip()
        else:
            match = re.match(r'([A-Z][a-z\'.]*\s*(?:[A-Z][a-z\'.]*\s*)*)', row['PlayDescription'])
            return match.group(1).strip() if match else ''
        
    # Function to extract Player2
    def extract_player2(row):
        match = re.search(r'passed to ([A-Z][a-z\'.]*\s*(?:[A-Z][a-z\'.]*\s*)*)', row['PlayDescription'])
        return match.group(1).strip() if match else ''

    def filter_out_missed_kicks(df):
        condition = ~(
            (~df['PlayDescription'].str.contains('touchdown', case=False)) &
            (~df['PlayDescription'].str.contains('Safety', case=False)) &
            (df['PlayDescription'].str.contains('missed|blocked', case=False))
        )
        return df[condition].reset_index(drop=True)
    
    def add_pat_to_scoring_df(df, matchup_pats_dict):
        new_rows = []  # List to store the new rows
        for player, pat in matchup_pats_dict.items():
            # Extract the number of PATs from the string
            num_pats = int(pat.split()[0])
            # Calculate the points based on the type of PAT
            if '1pt' in pat:
                points = num_pats * 1
            elif '2pt' in pat:
                points = num_pats * 2
            else:
                print(f"PAT Type not recognized for {player}")
                continue  # Skip if the PAT type is not recognized

            
            # Create a new row and add it to the list
            new_row = {'Player1': player, 'PlayDescription': pat, 'Points': points, 
                       'Team': '', 'Player2': '', 'Distance': 0, 
                       'TD': False, 'FG': False, 'Def TD': False, 'Safety': False}
            new_rows.append(new_row)
        
        # Convert the list of new rows to a DataFrame and concatenate it with the existing DataFrame
        new_rows_df = pd.DataFrame(new_rows)
        df = pd.concat([df, new_rows_df], ignore_index=True)
        
        return df

    ## re-load data once daily if on weekday. If on weekends, reload every 15 mins
    @st.cache_data(ttl=3600*24 if today.weekday() < 5 else 3600/4)
    def create_game_scoring_dfs_by_week(season_str, week_int):
        all_scoring_plays_list = sportsdata_interface.get_all_scoring_plays_by_week(season_str, week_int)

        # Regular expression pattern for a 1 or 2 digit integer
        distance_pattern = r'(\b\d{1,2}\b)'
        scoring_dfs = {}
        
        ## Create Tables of Scoring in Each Game & put them on streamlit
        for game in all_scoring_plays_list:
            awayteam, hometeam = game[0].get("AwayTeam"), game[0].get("HomeTeam")
            matchup = f"{awayteam}@{hometeam}"
            # st.markdown(f"""### {matchup}""")
            raw_scoring_df = pd.DataFrame(game)
            raw_scoring_df = raw_scoring_df[["Team", "PlayDescription"]]

            # Extract the key values from the PlayDescription
            raw_scoring_df['Distance'] = raw_scoring_df['PlayDescription'].str.extract(distance_pattern, expand=False).astype(int)
            raw_scoring_df['TD'] = raw_scoring_df['PlayDescription'].str.contains('touchdown')
            raw_scoring_df['FG'] = raw_scoring_df['PlayDescription'].str.contains('kicked')
            raw_scoring_df['Def TD'] = raw_scoring_df['PlayDescription'].str.contains('intercepted|fumbled|Kick off|Punt')
            raw_scoring_df['Safety'] = raw_scoring_df['PlayDescription'].str.contains('Safety')

            raw_scoring_df['Points'] = raw_scoring_df.apply(calculate_points, axis=1)

            raw_scoring_df['Player1'] = raw_scoring_df.apply(extract_player1, axis=1)
            raw_scoring_df['Player2'] = raw_scoring_df.apply(extract_player2, axis=1)

            raw_scoring_df = filter_out_missed_kicks(raw_scoring_df)

            # Temporary workaround for getting PAT data (manual) -- since the API doesnt provide it
            with open('pats_temp.json', 'r') as f:
                pat_data = json.load(f)
            matchup_pats_dict = pat_data.get(matchup, {})
            raw_scoring_df = add_pat_to_scoring_df(raw_scoring_df, matchup_pats_dict)

            raw_scoring_df = raw_scoring_df[["Team", "Player1", "Player2", "PlayDescription",  "Points", "Distance", "TD", "FG", "Def TD", "Safety"]]

            scoring_dfs[matchup] = raw_scoring_df
        return scoring_dfs
    
    @st.cache_data(ttl=3600*24 if today.weekday() < 5 else 3600/4)
    def create_player_total_scoring_df(scoring_dfs, total_scoring_dict = {}):
        for matchup, scoring_df in scoring_dfs.items():
            for index, row in scoring_df.iterrows():
                player1 = row['Player1']
                player2 = row['Player2']
                points = row['Points']
                total_scoring_dict[player1] = total_scoring_dict.get(player1, 0) + points
                if player2 != '':
                    total_scoring_dict[player2] = total_scoring_dict.get(player2, 0) + points

        players_total_scoring_df = (pd.DataFrame.from_dict(total_scoring_dict, 
                                                          orient = 'index')
                                                          .reset_index(drop = False)
                                                          .rename(columns = {'index': "Players", 0: "Points"})
                                                          .sort_values(by = "Points", ascending = False)
                                                          .reset_index(drop = True)
                                                        )
        return players_total_scoring_df, total_scoring_dict
    
    ##############################################
    ####### GET SCORING FOR SPECIFIC WEEK ########
    ##############################################

    wc_scoring_dfs = create_game_scoring_dfs_by_week('2023POST', '1')
    players_total_scoring_df, players_total_scoring_dict = create_player_total_scoring_df(wc_scoring_dfs, {})

    with open('total_scoring.json', 'w') as f:
        json.dump(players_total_scoring_dict, f)

    st.markdown(f"""

                # Players Total Scoring

                """)
    st.table(players_total_scoring_df)


    st.markdown("""
                ---

                ## WC Weekend
                
                """)
    for matchup, scoring_df in wc_scoring_dfs.items():
            st.markdown(f"""### {matchup}""")
            st.table(scoring_df)

    st.markdown("""
                ---
                ## Divisional Round
                
                coming soon
                """)



if __name__ == "__main__":
    main()