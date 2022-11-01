import streamlit as st
import pandas as pd
import numpy as np
from functions import *
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode, DataReturnMode
import datetime
import plotly.express as px

streamlit_setup('F1 data Visualiser', 'wide')
seasons = add_sidebar_select_box('Please choose a season', get_seasons(), 0)
rounds = get_rounds(seasons)
rounds = st.sidebar.selectbox("Please choose a race", range(len(rounds)), 0, format_func=lambda x: rounds[x])
st.sidebar.write("Round:", rounds + 1)

selected_year = seasons
selected_round = rounds + 1

df = get_race_details(selected_year, selected_round)

details_table = create_drivers_table(df=df)

selection_status = check_selection_status(details_table)

fig = px.line()

if selection_status:
    selected_driver_id = get_driver_id(details_table)
    add_line(fig, selected_year, selected_round, selected_driver_id)


st.plotly_chart(fig, use_container_width=True)



