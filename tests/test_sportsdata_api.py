import streamlit as st

from utils.sportsdata_interface import access_sportsdata_api, get_all_teams_names, get_all_players, get_team_roster

sportsdata_api_key = st.secrets["sportsdata"]["api_key"]

# teams = access_sportsdata_api(f'https://api.sportsdata.io/v3/nfl/scores/json/TeamsBasic?key={sportsdata_api_key}')

# print(type(teams))
# print()
# print(len(teams)) 
# print()
# print(teams[:2])


teams_list = ["SF", "KC", "NE"]
team_names = get_all_teams_names(teams_list)

print(type(team_names))
print(len(team_names))
print(team_names)

team_roster = get_team_roster("SF")
print(type(team_roster))
print(len(team_roster))
print(team_roster)


# all_players = get_all_players(teams_list)
# print(type(all_players))
# print(len(all_players))
# print(all_players[:2])