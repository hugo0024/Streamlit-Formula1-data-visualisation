import requests
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode


def add_sidebar_select_box(label, options, index):
    select_box = st.sidebar.selectbox(label, options, index)
    return select_box


def get_seasons():
    seasons = []
    url = "https://ergast.com/api/f1/seasons.json?limit=1000"
    response = requests.request("GET", url)
    data = response.json()
    for data_item in data['MRData']['SeasonTable']['Seasons']:
        seasons.append(data_item['season'])
    seasons.reverse()
    return seasons


def get_rounds(select_box):
    year = select_box
    url = f'https://ergast.com/api/f1/{year}/results.json?limit=10000'
    response = requests.request("GET", url)
    data = response.json()

    races = []
    rounds = []

    for dataItem in data['MRData']['RaceTable']['Races']:
        races.append(dataItem['raceName'])
        rounds.append(dataItem['round'])

    return races


def get_race_details(year, round_number):
    url = f'https://ergast.com/api/f1/{year}/{round_number}/results.json?limit=10000'
    response = requests.request("GET", url)
    data = response.json()

    data_dict = {'Pos': [], 'No': [], 'Driver': [], 'Constructor': [], 'Laps': [], 'Grid': [], 'Status': [],
                 'Points': [], 'DriverId': []}

    for dataItem in data['MRData']['RaceTable']['Races'][0]['Results']:
        data_dict['Pos'].append(dataItem['position'])
        data_dict['No'].append(dataItem['number'])
        data_dict['Driver'].append(dataItem['Driver']['familyName'])
        data_dict['Constructor'].append(dataItem['Constructor']['name'])
        data_dict['Laps'].append(dataItem['laps'])
        data_dict['Grid'].append(dataItem['grid'])
        data_dict['Status'].append(dataItem['status'])
        data_dict['Points'].append(dataItem['points'])
        data_dict['DriverId'].append(dataItem['Driver']['driverId'])

    df = pd.DataFrame.from_dict(data_dict)
    return df


def ag_grid_interactive_table(df: pd.DataFrame):
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()

    options.configure_selection("single")
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )

    return selection


def streamlit_setup(title, layout):
    st.set_page_config(page_title=title, layout=layout)


def create_drivers_table(df: pd.DataFrame):
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()

    options.configure_selection("single")
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        fit_columns_on_grid_load=True,
        gridOptions=options.build(),
        theme="streamlit",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )

    return selection
