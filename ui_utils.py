
from datetime import datetime
import pytz
import streamlit as st
import numpy as np
"""
This module provides utility functions for the streamlit user interface.
"""

def display_start_date_countdown(start_date_deadline_str, year):
        # Calculate a "Days, Hours, Mins, Seconds To"/"Days, Hours, Mins, Second Since" start_date_deadline and display it on the page using streamlit

        # Remove the day of the week from the string
        start_date_deadline = start_date_deadline_str.split(' (')[0]

        # Convert the string to a datetime object
        start_date_deadline = datetime.strptime(start_date_deadline, '%Y-%m-%d %I:%M%p %Z')

        # Convert the datetime object to UTC
        start_date_deadline = start_date_deadline.astimezone(pytz.UTC)

        # Get the current time in UTC
        now = datetime.now(pytz.UTC)

        # Calculate the difference
        diff = start_date_deadline - now

        # Convert the difference to days and hours
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds // 60) % 60
        seconds = diff.seconds % 60

        # Display the result
        if np.abs(days) > 7:
            start_date_deadline_str = start_date_deadline_str.split(' (')[0] ## day of week extra clutter more than a week out away
        if diff.total_seconds() > 0:
            st.write(f"""# {days} days {hours} hours, {minutes} mins til the {year} NFL Playoffs Kick Off ({start_date_deadline_str})""")
        else:
            st.write(f"""{-days} days, {hours} hours, {minutes} mins since the {year} NFL Playoffs Kicked Off ({start_date_deadline_str})""")

def check_past_deadline(start_date_deadline_str):
    pass

def function2():
    # Function 2 implementation
    pass

# if __name__ == "__main__":
#     # Code to execute when the module is run as a standalone script
#     pass
