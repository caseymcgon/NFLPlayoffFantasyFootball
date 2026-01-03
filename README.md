# NFL-Playoff-Fantasy-Football
Webscraping, Regex, and Pandas skills mobilized to efficiently compile and manipulate NFL Playoff scoring data for family and friends' Playoff Fantasy Football Pool

# A Little Backstory

This project's *original* purpose was just to automate scoring calculations and assignments for my family's Fantasy Football Pool for the 2020 NFL Playoffs.

To do that, I webscraped ESPN's scoring summaries of each playoff game to calculate fantasy scores for each player in those games. 

That script also combined all players and points on a (fantasy) roster into 1 dataFrame so we could see which of the participants in our league was leading at any given point in the playoffs.

Ultimately, the original notebook exported the tables it created to Excel (in order to share the information in a familiar and legible format).

In the ensuing years, the scope of the project has grown in accordance with my own technical development. The project has been a source of introspection & learning as I  return to this project every 11 months, critique what I built in the past, and improve upon it. These days, the project is less concerned with 'webscraping & pandas'; I'm more focused on system design, data pipelining, and UI design.

I now have a web app (via streamlit) that handles storing user Rosters via the Google Sheets API, updates Weekly Scoring & Standings via the sportsdata.io API, and provides an interface for sharing results with our friends involved in each years' competition. 




# Reproduction

In 2025, I switched to poetry to manage my environment. See pyproject.toml & poetry.lock files & "How To Run using Poetry" section below.

I also use yearly_settings.json to store key dates & info for each year. Those will need updates each january to make the app function again.

## Progress by Year

### 2020: First Year w/ Automated Scoring for our League
- Created a Jupyter Notebook w/ webscraping functions & pandas manipulation to tally the scoring each week
- Automated the following work that was previously manual & error-prone: looking at box scores, tallying points, and assigning to each player

### 2021: Minor addition 
- Added functionality to easily discern how many rosters each player is on
- Added functionality to determine the top scorers (even those not on rosters)

### 2022: First Year of Deploying a web app (actually 2)
- Web App #1: Utilized Streamlit to give users an UI to input their teams (as opposed to emailing) 
- Employed Google's sheets API to store roster inputs from web app (taking advantage of the now standardized inputs)
- Web App #2: Utilized Streamlit to give users an UI for viewing the results each week

### 2023: Revert to Jupyter Notebook (due to late start & lack of time before beginning of playoffs to spin up web app)
- Switched from webscraping to using the nflscrapy API (since ESPN changed their format of their pages)
- Added some additional data analysis (actually compute 'standings' table & find the optimal team's scoring)

### 2024: Back to Streamlit 
- Created a multpage app to host all things for the project, as opposed to disconnected smaller web apps (new streamlit feature)
- Switched from webscraping scoring plays to using a free-version of NFL API ([sportsdata.io](https://sportsdata.io/developers/data-dictionary/nfl)). This allows for ~ live-updating scoring & removes the hassle of dealing with ESPN changing their 'Gamecast' setup, but has some drawbacks (free version of the API is missing PATs)
- Automated creation of rosters & cleaning of player names to match the API (via the roster_manager.py file)
- Changed from a .venv to conda (NFL_conda_environment.yml) 
- Added yearly_settings.json (config files), ui_utils.py (custom streamlit funcs), and scraping_utils.py (custom webscraping funcs) to make future Casey happy (aka: enhance maintainability)
- Added time-based gates to the app (ie. show X information before kickoff and Y information after kickoff)





###### TODO (This Year)

- figure out PATs longer term fix (for now: manual-input dictionary )

- Q: How to split teams that won from those that lost, automatically, each week (maybe also using sportsdata.io?) & remove the losers from the "still alive" teams"

    - add-on: make the alive / not alive update automatically without needing to reboot the app

- color players red if dead throughout

- Add position & hover to see the owners (idk if that's possible)

- Modularize / configurable code for Scoring_Results.py & Standings.py to enable week-to-week updates to be easier / quicker (move toward: entirely automated)

    - and add 'time last updated' (and the scoring play description) on the Scoring_Results.py & Standings pages

- look through old code in WC_scrape.py & at the bottom of Scoring_Results.py -- check for features / tables / plots that I should carry over

- reformat some streamlit views (ie. collapse around WC Scoring, Div Scoring, etc.)

- create tables of players on each NFL roster who were picked & # of selections 

- create team_name_dict from API -- ie. {team_key : [fullName, city, mascot, nickname(?)]} --> get rid of issues with Niners, Ravens, etc.

- add repo structure & 'data pipeline' diagram near the top of the README

- Add very basic testing


###### Larger Projects / Improvements (Offseason / Future Years)

--> Tab 3: improve Roster Comparison visualization / Filters, etc. & Allow people to toy with 'paths to victory'
--> Tab 4 (todo in offseason): Historical Champions, Winning Rosters, & 'Optimal Team' (available at all times)

- Create an ML Model that picks a team. trained on past years results. 
    --> inputs: Players' TDs during year, team's seeding, team's record, team's record (last 3 games), has bye, offense's total TDs during year

- Analyze 'uniqueness' of teams

- Add testing of API functions & handling of odd names

### How To Run using Poetry

1. Set up a pyenv using python 3.12 (as of Jan 13, 2025, streamlit doesn't accept python > 3.12)'
2. run `pyenv local 3.12.0` so that pyenv is using 3.12 in this directory
3. `poetry env use /Users/caseymcgon/.pyenv/versions/3.12.0/bin/python` where that path is the output of `pyenv which python`

    `source /Users/caseymcgon/Library/Caches/pypoetry/virtualenvs/nflplayofffantasyfootball-9F4Bylxz-py3.12/bin/activate`

    `streamlit run Playoff_Fantasy_Overview.py`

### How to Deploy using Poetry
streamlit prefers a requirements.txt so run `poetry export -f requirements.txt --output requirements.txt`


#### Yearly ToDos:

1. Read through the full README to understand the structure / refresh on changes I made last year
2. Update the SELECTED_YEAR in Playoff_Fantasy_Overview.py
3. Update the settings for the new SELECTED_YEAR in yearly_settings.py
4. Copy last year's Google sheet roster over to a new google sheet (using my 11 email). Clear the team info & share it with the Google Service account associated w/ my 11 email
5. Flip Roster Input page & Compare roster page (just swap the 1 and the 4 preceding their names in the pages directory)
6. Set up the sportsdata.io API key again... (https://sportsdata.io/free-trial). You want to have access to each of the Competition, Events & Player Feeds
    - Put this API key in .streamlit/secrets.toml
##### Once The Playoffs are Set
6. update `all_playoff_teams.json` to this year's Playoff Field
7. the following files should be cleaned up to just be {}
    - `all_players.json`
    - `full_alphabetized_rosters.json`
    - `pats_temp.json`
    - `total_scoring.json`
8. the following file should be cleaned up to be fully empty
    - name_cleaning.txt
9. Run `python3 -m utils.sportsdata_interface` to set up the NFL roster info. This will populate
    - `all_players.json`
    



- (once the playoff matchups are set) Run `python3 -m utils.sportsdata_interface` to set up the NFL roster info
- (once games start) Run `python3 utils/roster_manager.py` to set up the cleaned rosters (once games start)
    --> Make sure to check for any incorrect cleanings in the `name_cleaning.txt` file


##### Weekly ToDos (since the Free version of the sportsdata.io API hides/scrambles this info)
- update yearly_settings.json's 'alive_AFC' and 'alive_NFC' fields
- update temp_pats.json with total PAT scoring info per player

###### TODO (Next Year)

- Tidyings of current code (but resist fully rewriting it. Small improvements this year)

- Do cleaning & check for correct position on user form 'submit' (this is currently done on the backend / after input to Google Sheets then loading in via the Google sheets API. This proposal would be done before sending it to google sheets). Then print out cleaned players for user to see / check

- Could turn Tiebreaker & D sections into dropdowns, potentially even match start of strings for player inputs

- Create a script out of get_all_team_names() and get_all_players() so I just run that once next year w/ the year and it creates the right json files 

    --> sportsdata_interface.get_all_team_names() should yield city, mascot, FullName, abbreviation etc. (not just FullName)

- Workarounds that limit API calls (storing all scoring data after the weekend, etc.)

- Consider a different API that will have PAT info & winner info for cheap (in order to fully automate the app)

- More Testing

- Add logging


###### Tidyings 

- move jsons (except yearly_settings.json) into a json_storage directory

- revisit all variable names (good opportunity to do this: when I'm making the 'data flow' section in the README)


##### 2026 Notes

- started update at 11:45am 1/3/26

- Can clean up 'how to use poetry' section + 

- should document how to handle streamlit secrets

- should document how to set up free trail with sportsdata.io (https://sportsdata.io/free-trial)

- In the future, I may want to consider using (https://github.com/nflverse/nflreadpy), which has updates 3x per day on gamedays

- I `st.write("PATs from Super Bowl are updated")` in 2 places. I should clean this up / not hard-code this word

#### Challenges
Running into the following error:
File "/Users/caseymcgon/code/NFLPlayoffFantasyFootball/utils/sportsdata_interface.py", line 84, in get_all_started_ScoreIDs_from_week
    if score_dict.get("HasStarted"):
       ^^^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

