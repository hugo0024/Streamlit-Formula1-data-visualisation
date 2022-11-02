import streamlit as st
import pandas as pd
import numpy as np
from functions import *
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode, DataReturnMode
import datetime
import plotly.express as px
import plotly.graph_objects as go

if __name__ == '__main__':
    streamlit_setup('F1 data Visualiser', 'wide')
    seasons = add_sidebar_select_box('Please choose a season', get_seasons(), 0)
    rounds = get_rounds(seasons)
    rounds = st.sidebar.selectbox("Please choose a race", range(len(rounds)), 0, format_func=lambda x: rounds[x])
    st.sidebar.write("Round:", rounds + 1)

    selected_year = seasons
    selected_round = rounds + 1

    df_race = get_race_details(selected_year, selected_round)

    details_table = create_drivers_table(df=df_race)

    selection_status = check_selection_status(details_table)

    selected_driver_id = get_driver_id(details_table)
    print(selected_driver_id)
    laps_data = get_laps_times(selected_year, selected_round, selected_driver_id)

    url = f'https://ergast.com/api/f1/{selected_year}/{selected_round}/laps.json?limit=10000'
    response = requests.request("GET", url)
    data = response.json()

    if "mdf" not in st.session_state:
        st.session_state.mdf = pd.DataFrame({})

    if data['MRData']['total'] != '0':
        laps_lst = []
        times_lst = []

        for dataItem in data['MRData']['RaceTable']['Races'][0]['Laps']:
            laps_lst.append(dataItem['number'])
            for x in range(len(dataItem['Timings'])):
                if dataItem['Timings'][x]['driverId'] == selected_driver_id:
                    time = dataItem['Timings'][x]["time"]
                    time = str_time_to_sec(time)
                    times_lst.append(time)

        print(laps_lst)
        print(times_lst)

        df_laps = pd.DataFrame({'Laps': laps_lst})
        df_times = pd.DataFrame({selected_driver_id: times_lst})

        if 'Laps' not in st.session_state.mdf.columns:
            st.session_state.mdf = pd.concat([st.session_state.mdf, df_laps], axis=1)

        if selected_driver_id not in st.session_state.mdf.columns:
            st.session_state.mdf = pd.concat([st.session_state.mdf, df_times], axis=1)

    fig = px.line( st.session_state.mdf, x='Laps', y= st.session_state.mdf.columns)

    st.plotly_chart(fig, use_container_width=True)
