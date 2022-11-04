from functions import *
import os


def create_races_page():
    seasons = add_sidebar_select_box('Please choose a season', get_seasons(), 0)
    rounds = get_rounds(seasons)
    insert_line(1, True)
    rounds = st.sidebar.selectbox("Please choose a race", range(len(rounds)), 0, format_func=lambda x: rounds[x])
    fit_check_box = fit_table_check_box()

    selected_year = seasons
    selected_round = rounds + 1

    df_race = get_race_details(selected_year, selected_round)

    details_table = create_table(df_race, fit_check_box)

    selection_status = check_selection_status(details_table)

    if selection_status:

        clear_plot_button()

        create_state_dataframe()

        selected_driver_id = get_driver_id(details_table)
        selected_driver_name = get_driver_name(details_table)

        lap_times = get_laps_times(selected_year, selected_round, selected_driver_id, selected_driver_name)

        if lap_times:
            plot = plot_chart(st.session_state.df, 'Laps', st.session_state.df.columns, 'Laps', 'Seconds')

    else:
        insert_empty_space(7, False)
        mark_down_test('Select from the table to compare lap times')
        clear_session_df()


@st.cache
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


def get_driver_id(table):
    selected = table["selected_rows"]
    selected = selected[0]['DriverId']
    return selected


def get_driver_name(table):
    selected = table["selected_rows"]
    selected = selected[0]['Driver']
    return selected
