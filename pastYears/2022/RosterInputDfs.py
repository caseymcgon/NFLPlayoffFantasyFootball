import streamlit as st
import pandas as pd
import numpy as np
import re
import math

import requests
from lxml import html
from lxml import etree

from bs4 import BeautifulSoup

import pandas as pd
import altair as alt
from collections import Counter


###### *PART 1 - CREATE DFs FROM ROSTER INPUT FORM*
#   Most important tables :
#       - popular_players
#       - allteams2 = Team GM & their chosen players
#       - teams_dict = {gm: df of roster}
#       - all_owners =  (list of gms)
#


## Get Teams from Rosters_2022.csv
roster_infos = pd.read_csv("Rosters_2022.csv")[['GM', 'QB1', 'QB2', 'K1', 'K2', 'D1', 'D2', 'P1', 'P2', 'P3', 'P4',
                                                'P5', 'P6', 'P7', 'SB_Champ', 'Runner_Up', 'SB_Points']]
allteams2 = roster_infos[['GM', 'QB1', 'QB2', 'K1', 'K2', 'D1', 'D2', 'P1', 'P2', 'P3', 'P4',
                          'P5', 'P6', 'P7']]
## Remove all pre- and post-name spaces
allteams2 = allteams2.applymap(lambda x: x.strip() if isinstance(x, str) else x)

## QBS
#
qb_owners = allteams2[['QB1', 'QB2']].apply(pd.Series.value_counts).fillna(0)
qb_owners["#_squads"] = qb_owners["QB1"] + qb_owners["QB2"]
qb_owners = qb_owners.drop(columns={"QB1", "QB2"}).rename(columns={"index": "NFL Player"}).sort_values("#_squads",
                                                                                                   ascending=False)
qb_owners = qb_owners.reset_index()
qb_owners["NFL"] = ["GB", "KC", "BUF", "TB", "CIN", "DAL", "LAR", "PIT", "PHI"]
qb_owners["Position"] = "QB"

# Number of Owners for each position player
p_owners = allteams2[['P1', 'P2', 'P3', 'P4', "P5", 'P6', 'P7']].apply(pd.Series.value_counts).reset_index().fillna(
    0)
p_owners["#_squads"] = p_owners["P1"] + p_owners["P2"] + p_owners['P3'] + p_owners['P4'] + p_owners["P5"] + \
                       p_owners['P6'] + p_owners['P7']
p_owners = p_owners.drop(columns={"P1", "P2", "P3", "P4", "P5", "P6", "P7"}).sort_values("#_squads",
                                                                                         ascending=False)
p_owners = p_owners.reset_index(drop=True)
p_owners["NFL"] = ["GB", "KC", "CIN", "KC", "LAR", "TEN", "BUF", "CIN", "TB", "GB",
                   "TB", "SF", "BUF", "TB", "DAL", "BUF", "DAL", "LAR", "SF", "CIN",
                   "SF", "GB", "PHI", "KC", "GB", "BUF", "BUF", "OAK", "ARI", "PIT",
                   "PIT", "PIT", "NE", "BUF", "PHI", "DAL", "TEN"]
p_owners["Position"] = "Pos"

# Number of D Owners
d_owners = allteams2[['D1', 'D2']].apply(pd.Series.value_counts).fillna(0)
d_owners["#_squads"] = d_owners["D1"] + d_owners["D2"]
d_owners = d_owners.drop(columns={"D1", "D2"}).rename(columns={"index": "NFL Player"}).sort_values("#_squads",
                                                                                                   ascending=False)
d_owners = d_owners.reset_index()
d_owners["NFL"] = d_owners["index"]
d_owners["Position"] = "D"