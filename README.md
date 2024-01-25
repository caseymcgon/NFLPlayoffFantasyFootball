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

I use conda to manage my environment (NFL_conda_environment.yml) when running locally. However, 'deploying' a streamlit app requires requirements.txt. To generate that: run the conda_to_requirements.py script.

Likewise, to deploy in streamlit (not just on your local server), the secrets must be shared with the streamlit cloud version of the app as well (via their web UI -- 3 dots > Settings > Secrets)

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

- Q: How to split teams that won from those that lost, automatically, each week (maybe also using sportsdata.io?) -- count # of alive & dead players on each roster & color players red if dead

- Add position & # of owners to "Players Total Scoring" 

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



##### Yearly ToDos:

- Read through the full README to understand the structure / refresh on changes I made last year
- Update the selected_year in Playoff_Fantasy.py
- Update the settings for the new selected_year in yearly_settings.py
- Copy last year's roster over to a new google sheet (using my 11 email). Clear the team info & share it with the Google Service account associated w/ my 11 email

##### Weekly ToDos (since the Free version of the sportsdata.io API hides/scrambles this info)
- update yearly_settings.json's 'alive_AFC' and 'alive_NFC' fields
- update temp_pats.json with total PAT scoring info per player

###### TODO (Next Year)

- Tidyings of current code (but resist fully rewriting it. Small improvements this year)

- Do cleaning & check for correct position on user form 'submit' (this is currently done on the backend / after input to Google Sheets then loading in via the Google sheets API. This proposal would be done before sending it to google sheets). Then print out cleaned players for user to see / check

- Could turn Tiebreaker & D sections into dropdowns, potentially even match start of strings for player inputs

- Create a script out of get_all_team_names() and get_all_players() so I just run that once next year w/ the year and it creates the right json files 

    --> sportsdata_interface.get_all_team_names() should yield city, mascot, FullName, abbreviation etc. (not just FullName)

- Consider a different API that will have PAT info & winner info for cheap

- More Testing

- Add logging


###### Tidyings 

- move jsons (except yearly_settings.json) into a json_storage directory

- revisit all names (good opportunity to do this: when I'm making the 'data flow' section in the README)
