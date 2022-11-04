import json
import requests
import streamlit as st
import pandas as pd
import re
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu


def create_nav_menu():
    selected = option_menu(
        menu_title=None,
        options=['Races', 'Championships', 'Maps'],
        icons=['card-heading', 'calendar3', 'map'],
        orientation='horizontal')
    return selected


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
    url = "http://ergast.com/api/f1/seasons.json?limit=1000"
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


def plot_chart(df, x, y, x_label, y_label):
    fig = px.line(df, x=x, y=y).update_layout(xaxis_title=x_label, yaxis_title=y_label)
    st.plotly_chart(fig, use_container_width=True)
    return fig

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


def check_selection_status(table):
    selected = table["selected_rows"]
    if selected:
        return True
    else:
        return False


def streamlit_setup(title, layout):
    st.set_page_config(page_title=title, layout=layout)
    load_lottie()
    insert_line(1, True)


def create_table(df, fit_columns):
    options = GridOptionsBuilder.from_dataframe(df)
    options.configure_default_column(groupable=False, value=True, enableRowGroup=False, aggFunc='sum', editable=False,
                                     sorteable=False)
    options.configure_selection('single', groupSelectsChildren=True, groupSelectsFiltered=True)

    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        height=300,
        fit_columns_on_grid_load=fit_columns,
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


def fit_table_check_box():
    with st.sidebar:
        insert_line(1, False)
        fit_columns_on_grid_load = st.sidebar.checkbox("Fit table columns on page", value=True)
        return fit_columns_on_grid_load
