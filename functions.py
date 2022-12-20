import json
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_nav_menu():
    """Function to crate the nav menu, return the current selected item name"""
    selected = option_menu(
        menu_title=None,
        options=['Races', 'Championships', 'Circuits'],
        icons=['card-heading', 'calendar3', 'map'],
        orientation='horizontal')
    return selected


def make_request(url):
    """
    Function to request data from url, sourced from
    https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
    """
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=2)  # Setting max retry number and apply delays between attempts
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    response = session.get(url)  # get the response from the url
    data = response.json()  # get json object from the response
    return data


def add_sidebar_select_box(label, options, index):
    """Function to add selection box to sidebar, return the current selected item"""
    select_box = st.sidebar.selectbox(label, options, 1)
    return select_box


def load_lottie():
    """Function to load and show the lottie image on the sidebar"""
    with open('car_lottie.json') as f:
        lottie = json.load(f)
    with st.sidebar:
        st_lottie(lottie, height=100, key='car')


@st.cache(persist=True)
def get_seasons():
    """
    Function to get all the seasons from the api
    Using st.cache to cache the result and setting persist to true to persist the cache on disk
    """
    seasons = []
    url = "http://ergast.com/api/f1/seasons.json?limit=1000"
    data = make_request(url)  # making request from the url
    for data_item in data['MRData']['SeasonTable']['Seasons']:  # Append each season to the list
        seasons.append(data_item['season'])
    seasons.reverse()  # Reverse the list so that the latest season show up first
    return seasons


@st.cache(persist=True)
def get_rounds(select_box):
    """Function to get all the rounds from a specific season."""
    year = select_box
    url = f'https://ergast.com/api/f1/{year}/results.json?limit=10000'
    data = make_request(url)
    races = []
    for dataItem in data['MRData']['RaceTable']['Races']:
        races.append(dataItem['raceName'])
    return races


def plot_chart(df, x, y, x_label, y_label):
    """Function to plot a line chart using the st.plotly_chart functions"""
    fig = px.line(df, x=x, y=y).update_layout(xaxis_title=x_label, yaxis_title=y_label)
    st.plotly_chart(fig, use_container_width=True)
    return fig


def create_state_dataframe():
    """
    Function to create a dataframe and store it in streamlit session state
    By adding it to streamlit session state, it can prevent clearing the dataframe between reruns
    """
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame({})


def insert_line(number, is_sidebar):
    """
    Function to add lines to the streamlit page
    Takes two arguments, the first is how many line to add, the second one is a boolean to decide where to add the line
    """
    for x in range(number):
        if is_sidebar:
            with st.sidebar:
                st.markdown("***")
        else:
            st.markdown("***")


def insert_empty_space(number, is_sidebar):
    """
    Function to add empty space to the streamlit page. Takes two arguments, the first is how many line of empty space to
    add, the second one is a boolean to decide where to add the empty space
    """
    for x in range(number):
        if is_sidebar:
            with st.sidebar:
                st.write('')
        else:
            st.write('')


def add_mark_down_text(text_str):
    """Function to add Markdown text with specific styles"""
    markdown = st.markdown(f"<h1 style='text-align: center; color: grey;'>{text_str}</h1>", unsafe_allow_html=True)
    return markdown


def check_selection_status(table):
    """Function to check is the table is selected or not, return a boolean"""
    selected = table["selected_rows"]
    if selected:
        return True
    else:
        return False


def streamlit_setup(title, layout):
    """Function to include basic setup of the streamlit page"""
    st.set_page_config(page_title=title, layout=layout)
    load_lottie()
    insert_line(1, True)


def create_table(df, fit_columns):
    """
    Function to create an ag-grid table. Takes two arguments, first is a dataframe to be show on the table, the second
    one is a boolean to decide should the table automatically fit columns to the grid width
    """
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
    """Function to create the clear line button to clear the lines on the plot"""
    with st.sidebar:
        insert_line(1, True)
        if st.button('Clear Plot Lines'):
            clear_session_df()


def clear_session_df():
    """Function to clear the session dataframe"""
    for key in st.session_state.keys():
        del st.session_state[key]


def fit_table_check_box():
    """Function to create the checkbox for toggling between fit table column on grid or not, return a boolean"""
    with st.sidebar:
        insert_line(1, False)
        fit_columns_on_grid_load = st.sidebar.checkbox("Fit table columns on page", value=True)
        return fit_columns_on_grid_load
