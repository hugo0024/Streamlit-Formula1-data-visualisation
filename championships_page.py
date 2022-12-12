import streamlit as st
import pandas as pd
import plotly.express as px
from functions import add_sidebar_select_box
from functions import get_seasons
from functions import fit_table_check_box
from functions import create_table
from functions import make_request
from functions import option_menu


def create_championships_page():
    """Main function for the championships page"""

    selected = create_championships_options()  # create the nav menu for the drivers and constructors page
    seasons = add_sidebar_select_box('Seasons:', get_seasons(), 0)  # create a select box to store all the seasons
    fit_check_box = fit_table_check_box()  # create the fit tabel columns on grid check box

    if selected == 'Drivers':  # if selected drivers from the nav menu
        drivers_championships_df = get_driver_championships(seasons)  # get data and create a df
        create_table(drivers_championships_df, fit_check_box)  # create the table
        create_bar_chart(seasons, 'Drivers')  # plot the bar chart using the df

    if selected == 'Constructors':  # if selected constructors from the nav menu
        constructor_championships_df = get_constructor_championships(seasons)
        create_table(constructor_championships_df, fit_check_box)
        create_bar_chart(seasons, 'Constructors')


def create_championships_options():
    """Function to creat the nav menu for the drivers and constructors' championship"""

    with st.sidebar:  # add the nav menu to sidebar
        selected = option_menu(
            menu_title=None,
            options=['Drivers', 'Constructors'],
            icons=['people', 'building'])
    return selected  # return the selected item


@st.cache(persist=True)
def get_driver_championships(year):
    """
    Function to get the data from the driver championships in a specific year
    Cache this function to save time between reruns
    """

    url = f'https://ergast.com/api/f1/{year}/driverStandings.json'  # url to make request from
    data = make_request(url)  # get the json object from request

    # dictionary to append to
    data_dict = {'Standing': [], 'Driver': [], 'Constructor': [], 'Points': [], 'Wins': []}

    # append corresponding data to the dictionary
    for dataItem in data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']:
        data_dict['Standing'].append(dataItem['position'])
        data_dict['Driver'].append(dataItem['Driver']['givenName'] + ' ' + dataItem['Driver']['familyName'])
        data_dict['Constructor'].append(dataItem['Constructors'][0]['name'])
        data_dict['Points'].append(dataItem['points'])
        data_dict['Wins'].append(dataItem['wins'])

    df = pd.DataFrame.from_dict(data_dict)  # create a pandas dataframe from the dictionary

    return df  # return the dataframe


@st.cache(persist=True)
def get_constructor_championships(year):
    """
    Function to get the data from the constructor championships in a specific year
    Cache this function to save time between reruns
    """

    url = f'https://ergast.com/api/f1/{year}/constructorStandings.json'
    data = make_request(url)

    data_dict = {'Standing': [], 'Constructor': [], 'Nationality': [], 'Points': [], 'Wins': []}

    for dataItem in data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']:
        data_dict['Standing'].append(dataItem['position'])
        data_dict['Constructor'].append(dataItem['Constructor']['name'])
        data_dict['Nationality'].append(dataItem['Constructor']['nationality'])
        data_dict['Points'].append(dataItem['points'])
        data_dict['Wins'].append(dataItem['wins'])

    df = pd.DataFrame.from_dict(data_dict)

    return df


def create_bar_chart(year, championships):
    """Function to create bar chart for the Drivers and Constructors' championship"""

    if championships == 'Drivers':
        df = get_driver_championships(year)
        df = df.astype({'Points': 'float'})
        fig = px.bar(df, x='Driver', y='Points', color="Driver", text_auto=True)
        fig.update_traces(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    if championships == 'Constructors':
        df = get_constructor_championships(year)
        df = df.astype({'Points': 'float'})
        fig = px.bar(df, x='Constructor', y='Points', color="Constructor", text_auto=True)
        fig.update_traces(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
