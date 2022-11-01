import requests
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import re
import plotly.express as px


def add_sidebar_select_box(label, options, index):
    select_box = st.sidebar.selectbox(label, options, index)
    return select_box


@st.cache
def get_seasons():
    seasons = []
    url = "https://ergast.com/api/f1/seasons.json?limit=1000"
    response = requests.request("GET", url)
    data = response.json()
    for data_item in data['MRData']['SeasonTable']['Seasons']:
        seasons.append(data_item['season'])
    seasons.reverse()
    return seasons


@st.cache
def get_rounds(select_box):
    year = select_box
    url = f'https://ergast.com/api/f1/{year}/results.json?limit=10000'
    response = requests.request("GET", url)
    data = response.json()
    races = []

    for dataItem in data['MRData']['RaceTable']['Races']:
        races.append(dataItem['raceName'])

    return races


@st.cache
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


def plot_chart(data, selection_status):
    if selection_status:
        fig = px.line(data, x="Laps", y="Times")
        st.plotly_chart(fig, use_container_width=True)


def add_line(fig, year, round_number, driver):
    laps_data = get_laps_times(year, round_number, driver)
    fig.add_scatter(x=laps_data['Laps'], y=laps_data['Times'], name=driver)


@st.cache
def get_laps_times(year, round_number, driver_id):
    data_dict = {'Laps': [], 'Times': []}
    url = f'https://ergast.com/api/f1/{year}/{round_number}/laps.json?limit=10000'
    response = requests.request("GET", url)
    data = response.json()
    if data['MRData']['total'] != '0':
        for dataItem in data['MRData']['RaceTable']['Races'][0]['Laps']:
            data_dict['Laps'].append(dataItem['number'])
            for x in range(len(dataItem['Timings'])):
                if dataItem['Timings'][x]['driverId'] == driver_id:
                    time = dataItem['Timings'][x]["time"]
                    time = str_time_to_sec(time)
                    data_dict['Times'].append(time)
    else:
        print('No data for this year')

    df = pd.DataFrame.from_dict(data_dict, orient='index')
    df = df.transpose()
    df['Laps'] = df['Laps'].astype(int)

    return df


def str_time_to_sec(time):
    m, s, f = re.split('[: .]', time)
    second = int(m) * 60 + int(s) + float(f) * 0.001

    return second


def check_selection_status(table):
    selected = table["selected_rows"]
    if selected:
        return True
    else:
        return False


def get_driver_id(table):
    selected = table["selected_rows"]
    selected = selected[0]['DriverId']
    return selected


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
    options = GridOptionsBuilder.from_dataframe(df)
    options.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)

    options.configure_side_bar()
    options.configure_selection('multiple')

    options.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True)

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
