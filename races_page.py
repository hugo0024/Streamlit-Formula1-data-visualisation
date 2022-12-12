import streamlit as st
import pandas as pd
import re
from functions import add_sidebar_select_box
from functions import get_seasons
from functions import get_rounds
from functions import insert_line
from functions import fit_table_check_box
from functions import create_table
from functions import check_selection_status
from functions import clear_plot_button
from functions import create_state_dataframe
from functions import plot_chart
from functions import insert_empty_space
from functions import add_mark_down_text
from functions import clear_session_df
from functions import make_request


def create_races_page():
    """
    Main function to create the races page
    See each functions for detailed explanations
    """

    seasons = add_sidebar_select_box('Seasons:', get_seasons(), 0)  # add a select box to store all the seasons
    rounds = get_rounds(seasons)  # get all the rounds from a season
    insert_line(1, True)
    # load all the rounds into a select box and getting the index value for each item using streamlit format_func
    rounds = st.sidebar.selectbox("Races:", range(len(rounds)), 0, format_func=lambda x: rounds[x])
    fit_check_box = fit_table_check_box()  # create the fit column on gird check box

    # get the selected season from the season select box
    selected_year = seasons
    # get the selected round number, adding 1 to it because the index value starts with 0 but round number start from 1
    selected_round = rounds + 1

    df_race = get_race_details(selected_year, selected_round)  # get the race details dataframe for the selected round
    details_table = create_table(df_race, fit_check_box)  # create the table

    selection_status = check_selection_status(details_table)  # check is the table selected or not

    if selection_status:  # if the table is selected

        clear_plot_button()  # create and show the clear plot line button

        create_state_dataframe()  # create the state dataframe

        selected_driver_id = get_driver_id(details_table)  # get the selected driver id from the table
        selected_driver_name = get_driver_name(details_table)  # get the selected driver name from the table

        # get the lap times for the selected driver
        lap_times = get_laps_times(selected_year, selected_round, selected_driver_id, selected_driver_name)

        if lap_times:  # if there are lap times data to show
            plot_chart(st.session_state.df, 'Laps', st.session_state.df.columns, 'Laps', 'Seconds')

    else:
        insert_empty_space(7, False)
        add_mark_down_text('Select from the table to compare lap times')
        # clear the session dataframe because the table is unselected, meaning the user has selected a different
        # season or round or to a different page
        clear_session_df()


@st.cache(persist=True)
def get_race_details(year, round_number):
    """Function to get the race details for a specific race, enabled streamlit caching to cache this function"""

    url = f'https://ergast.com/api/f1/{year}/{round_number}/results.json?limit=10000'  # url to make request from
    data = make_request(url)  # making request and store the json object

    # Empty dictionary to store all the data
    data_dict = {'Pos': [], 'No': [], 'Driver': [], 'Constructor': [], 'Laps': [], 'Grid': [], 'Status': [], 'Time': [],
                 'Points': [], 'DriverId': []}

    # append corresponding data from the json object to the dictionary
    for dataItem in data['MRData']['RaceTable']['Races'][0]['Results']:
        data_dict['Pos'].append(dataItem['position'])
        data_dict['No'].append(dataItem['number'])
        data_dict['Driver'].append(dataItem['Driver']['givenName'] + ' ' + dataItem['Driver']['familyName'])
        data_dict['Constructor'].append(dataItem['Constructor']['name'])
        data_dict['Laps'].append(dataItem['laps'])
        data_dict['Grid'].append(dataItem['grid'])
        data_dict['Status'].append(dataItem['status'])
        data_dict['Points'].append(dataItem['points'])
        data_dict['DriverId'].append(dataItem['Driver']['driverId'])

        # data for time can be empty in the json object, because some driver may not finish the race
        # using a try and except to catch key error
        try:
            data_dict['Time'].append(dataItem['Time']['time'])
        except KeyError:
            data_dict['Time'].append(dataItem['status'])

    df = pd.DataFrame.from_dict(data_dict)  # create a pandas dataframe from the dictionary and return it
    return df


def get_laps_times(year, round_number, driver_id, driver_name):
    """
    Function to get the lap times for a driver in a race
    Session state is needed in this function because variables will be reset between reruns
    In this case the user will need to compare laps times data for different drivers by selecting them individually
    By using the session state dataframe, the dataframe will not get reset when the user select another driver
    Therefore, displaying lap times data for multiple drivers in a plot will be possible
    """

    url = f'https://ergast.com/api/f1/{year}/{round_number}/laps.json?limit=10000'  # url to make request from
    data = make_request(url)
    if data['MRData']['total'] != '0':  # check if the json object have any lap times data
        laps_lst = []
        times_lst = []
        for dataItem in data['MRData']['RaceTable']['Races'][0]['Laps']:
            laps_lst.append(dataItem['number'])  # append all the laps number to the laps list
            for x in range(len(dataItem['Timings'])):
                if dataItem['Timings'][x]['driverId'] == driver_id:  # filter the data for the correct driver
                    time = dataItem['Timings'][x]["time"]  # get the lap times for the driver
                    time = str_time_to_sec(time)  # convert from str minutes and seconds to float seconds
                    times_lst.append(time)  # append the time to the time list

        df_laps = pd.DataFrame({'Laps': laps_lst})  # create dataframes from the lists
        df_times = pd.DataFrame({driver_name: times_lst})

        # if there is no laps column in the session dataframe
        if 'Laps' not in st.session_state.df.columns:
            # add the laps dataframe to the session dataframe
            st.session_state.df = pd.concat([st.session_state.df, df_laps], axis=1)

        # check if the driver has been already added to the session dataframe
        if driver_name not in st.session_state.df.columns:
            # add the time dataframe to the session dataframe
            st.session_state.df = pd.concat([st.session_state.df, df_times], axis=1)
        else:
            st.session_state.df.drop(driver_name, axis=1)

        return True  # return turn for getting the lap times successfully
    else:
        insert_empty_space(7, False)
        add_mark_down_text('No lap times data for this race')
        return False  # return false because there is no lap times data in the json object


def str_time_to_sec(time):
    """Function to convert str minutes and seconds to float second"""
    m, s, f = re.split('[: .]', time)
    second = int(m) * 60 + int(s) + float(f) * 0.001
    return second


def get_driver_id(table):
    """Function to get the selected driver id in the table"""
    selected = table["selected_rows"]
    selected = selected[0]['DriverId']
    return selected


def get_driver_name(table):
    """Function to get the selected driver name in the table"""
    selected = table["selected_rows"]
    selected = selected[0]['Driver']
    return selected
