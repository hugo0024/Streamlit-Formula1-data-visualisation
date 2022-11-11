from functions import *


def create_championships_page():
    selected = create_championships_options()
    seasons = add_sidebar_select_box('Seasons:', get_seasons(), 0)
    fit_check_box = fit_table_check_box()

    if selected == 'Drivers':
        drivers_championships_df = get_driver_championships(seasons)
        create_table(drivers_championships_df, fit_check_box)

    if selected == 'Constructors':
        constructor_championships_df = get_constructor_championships(seasons)
        create_table(constructor_championships_df, fit_check_box)


def create_championships_options():
    with st.sidebar:
        selected = option_menu(
            menu_title=None,
            options=['Drivers', 'Constructors'],
            icons=['people', 'building'])
    return selected


def create_championships_radio_btn():
    with st.sidebar:
        championships = st.radio(
            'Select:', ('Driver Championships', 'Constructor Championships')
        )
    insert_line(1, True)
    return championships


@st.cache(persist=True)
def get_driver_championships(year):
    url = f'https://ergast.com/api/f1/{year}/driverStandings.json'
    response = requests.request("GET", url)
    data = response.json()

    data_dict = {'Standing': [], 'Driver': [], 'Constructor': [], 'Points': [], 'Wins': []}

    for dataItem in data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']:
        data_dict['Standing'].append(dataItem['position'])
        data_dict['Driver'].append(dataItem['Driver']['givenName'] + ' ' + dataItem['Driver']['familyName'])
        data_dict['Constructor'].append(dataItem['Constructors'][0]['name'])
        data_dict['Points'].append(dataItem['points'])
        data_dict['Wins'].append(dataItem['wins'])

    df = pd.DataFrame.from_dict(data_dict)

    return df


@st.cache(persist=True)
def get_constructor_championships(year):
    url = f'https://ergast.com/api/f1/{year}/constructorStandings.json'
    response = requests.request("GET", url)
    data = response.json()

    data_dict = {'Standing': [], 'Constructor': [], 'Nationality': [], 'Points': [], 'Wins': []}

    for dataItem in data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']:
        data_dict['Standing'].append(dataItem['position'])
        data_dict['Constructor'].append(dataItem['Constructor']['name'])
        data_dict['Nationality'].append(dataItem['Constructor']['nationality'])
        data_dict['Points'].append(dataItem['points'])
        data_dict['Wins'].append(dataItem['wins'])

    df = pd.DataFrame.from_dict(data_dict)

    return df
