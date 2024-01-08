
from datetime import datetime
import time
import pytz
import streamlit as st
import numpy as np
from datetime import datetime
import pytz
"""
This module provides utility functions for the streamlit user interface.
"""

def display_deadline_message(start_date_deadline_str, year):
     
    # Convert the string to UTC datetime object 
    start_date_deadline_utc = get_utc_datetime(start_date_deadline_str)
    diff, before_deadline_bool = compute_time_till_deadline(start_date_deadline_utc)

    # Convert the difference to days and hours
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds // 60) % 60
    # seconds = diff.seconds % 60

    # Display the result
    if before_deadline_bool:
        pst_timezone = pytz.timezone('US/Pacific')
        day_of_week = check_day_of_week(start_date_deadline_utc.astimezone(pst_timezone))
        st.markdown(f"""
                ---
                ##### 🕜 **{day_of_week} {start_date_deadline_str} PST** 
                is the deadline to submit your team (in the **Roster Input** tab on the Left Side)

                You may submit as many times as you'd like before the deadline.
                Only your final submission before the deadline will be counted.
            """)
    else:
        st.markdown(f"""
                ---
                🕜 Uh oh! The first NFL playoff games of {year} kicked off at {start_date_deadline_str}

                You may no longer submit a team this year :( -- Hope you'll join us next year
         """)
        
def compute_time_till_deadline(start_date_deadline_utc):
    """ Returns (diff, bool) 
        - diff = datetime time difference between now and deadline
    ##  - bool =  True if now is before the deadline
    """
    # Get the current time in UTC
    now = datetime.now(pytz.UTC)

    # Calculate the difference
    diff = start_date_deadline_utc - now

    # Check if the deadline has passed
    if diff.total_seconds() <= 0:
        return diff, False
    else:
        return diff, True
    
def get_utc_datetime(start_date_deadline_str):
    # Convert the string to a datetime object
    start_date_deadline = datetime.strptime(start_date_deadline_str, '%b %d, %Y %I:%M %p')
    
    ## localize the timezone-naive object to PST then cast to UTC
    pst_timezone = pytz.timezone('US/Pacific')
    start_date_deadline_utc = pst_timezone.localize(start_date_deadline).astimezone(pytz.utc)

    return start_date_deadline_utc
    
def check_day_of_week(start_date_deadline):
    # Convert the string to a datetime object
    

    # Get the day of the week
    day_of_week = start_date_deadline.strftime('%A')

    return day_of_week


# def display_start_date_countdown(start_date_deadline_str, year):
#        ## Useful if counting down seconds til kickoff of first game

#         # Convert the string to UTC datetime object 
#         start_date_deadline = get_utc_datetime(start_date_deadline_str)

#         diff, before_deadline_bool = time_till_deadline(start_date_deadline)

#         # Convert the difference to days and hours
#         days = diff.days
#         hours = diff.seconds // 3600
#         minutes = (diff.seconds // 60) % 60
#         seconds = diff.seconds % 60

#         # Display the result
#         if before_deadline_bool:
#             day_of_week = check_day_of_week(start_date_deadline_str)
#             st.write(f"""# {days} days {hours} hours, {minutes} mins til the {year} NFL Playoffs Kick Off: {start_date_deadline_str}, {day_of_week} """)
#         else:
#             st.write(f"""{-days} days, {hours} hours, {minutes} mins since the {year} NFL Playoffs Kicked Off ({start_date_deadline_str})""")


        ## If you wanted to make live updating time (seconds, it'd look something like this)
        # # Streamlit app loop
        # while True:
        #     now =  datetime.now(pytz.UTC)
            
        #     countdown_time = start_date_deadline - now

        #     # # Check if the deadline has passed
        #     # if countdown_time.total_seconds() <= 0:
        #     #     st.write("The deadline has passed!")
        #     #     break

        #     # Display the countdown
        #     st.write(f"Time remaining: {countdown_time}")

        #     # Refresh every second
        #     time.sleep(1)
        #     st.rerun()


# start_date_deadline_str = "Jan 15, 2024 1:30 PM PST"
# day_of_week = check_day_of_week(start_date_deadline_str)
# print(day_of_week)

def function2():
    # Function 2 implementation
    pass

# if __name__ == "__main__":
#     # Code to execute when the module is run as a standalone script
#     pass
