def make_results():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import re
    import math
    plt.style.use('fivethirtyeight')
    import requests
    from lxml import html
    from lxml import etree

    from bs4 import BeautifulSoup

    import pandas as pd
    import altair as alt
    import seaborn as sns


    from collections import Counter

    roster_infos = pd.read_csv("Rosters_2022.csv")[['GM', 'QB1', 'QB2', 'K1', 'K2', 'D1', 'D2', 'P1', 'P2', 'P3', 'P4',
                                                    'P5', 'P6', 'P7', 'SB_Champ', 'Runner_Up', 'SB_Points']]
    roster_infos.head(2)


























# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    make_results()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/