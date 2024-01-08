# NFL-Playoff-Fantasy-Football
Webscraping, Regex, and Pandas skills mobilized to efficiently compile and manipulate NFL Playoff scoring data for family and friends' Playoff Fantasy Football Pool

# A Little Backstory

This project's *original* purpose was just to automate scoring calculations and assignments for my family's Fantasy Football Pool for the 2020 NFL Playoffs.

To do that, I webscraped ESPN's scoring summaries of each playoff game to calculate fantasy scores for each player in those games. 

That script also combined all players and points on a (fantasy) roster into 1 dataFrame so we could see which of our participants was leading at any given point in the playoffs.

Ultimately, the original notebook exported the tables it created to Excel (in order to share the information in a familiar and legible format).

In the ensuing years, the scope of the project has grown. I now have a web app (streamlit) that handles Storing user Rosters via the Google Sheets API, Updating Weekly Scoring via the sportsdata.io API, and sharing results with our friends involved in this years' competition.


# Reproduction

I use conda to manage my environment (NFL_conda_environment.yml) when running locally. However, 'deploying' a streamlit app requires requirements.txt. To generate that: run the conda_to_requirements.py script.

Likewise, to deploy in streamlit (not just on your local server), the secrets must be shared with the streamlit cloud version of the app as well (via their web UI -- 3 dots > Settings > Secrets)

I also use yearly_settings.json to store key dates & info for each year. Those will need updates each january to make the app function again.

## Progress by Year

### 2020: First Year w/ Automated Scoring for our Leage
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
- Added some additional data analysis (actually compute "standings" table & find the optimal team's scoring)

### 2024: Back to Streamlit 
- Created a multpage app to host all things for the project, as opposed to disconnected smaller web apps (new streamlit feature)
- Changed from a .venv to conda (NFL_conda_environment.yml)
- Added yearly_settings.json (config files), ui_utils.py (custom streamlit funcs), and scraping_utils.py (custom webscraping funcs) to make future Casey happy (aka: enhance maintainability)
- 





###### TODO (This Year)

- determine if I should use nflscrapy or go back to scraping myself

- Q: How to split teams that won from those that lost, automatically, each week

--> Check that basic setup works for 2024 (write to & read from Google API)

- differentiate WC_scrape.py from streamlit_results.py -- why both? Maybe have 1 be a file of functions, the other calls those functions

- L113 of streamlit_form.py: remove hard-coding (base it on dt v. deadline) -- see L42 of ui_utils

- Add very basic testing


###### Larger Projects / Improvements

- Automate cleaning of player names (both on rosters/user input & on scoring play scraping from ESPN)
--> fuzzy_wuzzy.process

- Live Updates to Results App: get a quickly updating API or scrape from somewhere that has an existing url before the game

- Everything as 1 app:

--> Tab 0: Landing Page (w/ # of players, countdown to deadline (Days, Hours til NFL Playoffs Start / since ended), rules, etc. ) 
--> Tab 1: Roster input (available until Kickoff of Week 1)
--> Tab 2: Scoring / Results (available after Kickoff of Week 1)
--> Tab 3: Roster inspection / comparison (available after Kickoff of Week 1)
--> Tab 4 (todo in offseason): Historical Champions, Winning Rosters, & 'Optimal Team' (available at all times)

- Add & Improve visualizations of standings & roster comparisons

- Allow people to toy with "paths to victory"

- Create an ML Model that picks a team. trained on past years results. 
    --> inputs: Players' TDs during year, team's seeding, team's record, team's record (last 3 games), has bye, offense's total TDs during year

- Analyze "uniqueness" of teams

- Add testing of webscraping functions & handling of odd names



##### Yearly ToDos:

- Update the selected_year in Playoff_Fantasy.py
- Update the settings for the new selected_year in yearly_settings.py
- Copy last year's roster over to a new google sheet (using my 11 email). Clear the team info & share it with the Google Service account associated w/ my 11 email
