import streamlit as st
import pandas as pd
import numpy as np
from functions import *


streamlit_setup('F1 data Visualiser', 'wide')
seasons = add_sidebar_select_box('Please choose a season', get_seasons(), 0)
rounds = get_rounds(seasons)
rounds = st.sidebar.selectbox("Please choose a race", range(len(rounds)), 0, format_func=lambda x: rounds[x])
st.sidebar.write("Round:", rounds + 1)

selected_year = seasons
selected_round = rounds + 1

df = get_race_details(selected_year, selected_round)

selection = create_drivers_table(df=df)

if selection:
    st.write("You selected:")
    st.json(selection["selected_rows"])
