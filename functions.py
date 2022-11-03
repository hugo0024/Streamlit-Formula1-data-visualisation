import json
import requests
import streamlit as st
import pandas as pd
import re
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from streamlit_lottie import st_lottie


def add_sidebar_select_box(label, options, index):
    select_box = st.sidebar.selectbox(label, options, index)
    return select_box


def load_lottie():
    with open('car_lottie.json') as f:
        lottie = json.load(f)
    with st.sidebar:
        st_lottie(lottie, height=100, key='car')


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


def get_race_details(year, round_number):
    url = f'https://ergast.com/api/f1/{year}/{round_number}/results.json?limit=10000'
    response = requests.request("GET", url)
    data = response.json()

    data_dict = {'Pos': [], 'No': [], 'Driver': [], 'Constructor': [], 'Laps': [], 'Grid': [], 'Status': [], 'Time': [],
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
        try:
            data_dict['Time'].append(dataItem['Time']['time'])
        except KeyError:
            data_dict['Time'].append(dataItem['status'])

    df = pd.DataFrame.from_dict(data_dict)

    return df


def plot_chart():
    fig = px.line(st.session_state.df, x='Laps', y=st.session_state.df.columns).update_layout(yaxis_title="Seconds")
    st.plotly_chart(fig, use_container_width=True)


def create_state_dataframe():
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame({})


def insert_line(number, is_sidebar):
    for x in range(number):
        if is_sidebar:
            with st.sidebar:
                st.markdown("***")
        else:
            st.markdown("***")


def insert_empty_space(number, is_sidebar):
    for x in range(number):
        if is_sidebar:
            with st.sidebar:
                st.write('')
        else:
            st.write('')


def mark_down_test(test):
    test = st.markdown(f"<h1 style='text-align: center; color: grey;'>{test}</h1>", unsafe_allow_html=True)
    return test


def get_laps_times(year, round_number, driver_id, driver_name):
    url = f'https://ergast.com/api/f1/{year}/{round_number}/laps.json?limit=10000'
    response = requests.request("GET", url)
    data = response.json()
    if data['MRData']['total'] != '0':
        laps_lst = []
        times_lst = []
        for dataItem in data['MRData']['RaceTable']['Races'][0]['Laps']:
            laps_lst.append(dataItem['number'])
            for x in range(len(dataItem['Timings'])):
                if dataItem['Timings'][x]['driverId'] == driver_id:
                    time = dataItem['Timings'][x]["time"]
                    time = str_time_to_sec(time)
                    times_lst.append(time)

        df_laps = pd.DataFrame({'Laps': laps_lst})
        df_times = pd.DataFrame({driver_name: times_lst})

        if 'Laps' not in st.session_state.df.columns:
            st.session_state.df = pd.concat([st.session_state.df, df_laps], axis=1)

        if driver_name not in st.session_state.df.columns:
            st.session_state.df = pd.concat([st.session_state.df, df_times], axis=1)
        else:
            st.session_state.df.drop(driver_name, axis=1)

        return True
    else:
        insert_empty_space(7, False)
        mark_down_test('No lap times data for this race')
        return False


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


def get_driver_name(table):
    selected = table["selected_rows"]
    selected = selected[0]['Driver']
    return selected


def streamlit_setup(title, layout):
    st.set_page_config(page_title=title, layout=layout)


def create_drivers_table(df: pd.DataFrame):
    options = GridOptionsBuilder.from_dataframe(df)
    options.configure_default_column(groupable=False, value=True, enableRowGroup=False, aggFunc='sum', editable=False,
                                     sorteable=False)
    options.configure_selection('single', groupSelectsChildren=True, groupSelectsFiltered=True)

    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        fit_columns_on_grid_load=True,
        gridOptions=options.build(),
        height=300,
        theme="streamlit",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )
    return selection


def clear_plot_button():
    with st.sidebar:
        insert_line(1, True)
        if st.button('Clear Plot Lines'):
            clear_session_df()


def clear_session_df():
    for key in st.session_state.keys():
        del st.session_state[key]
