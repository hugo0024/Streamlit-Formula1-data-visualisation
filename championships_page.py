from functions import *


def create_championships_page():
    selected = create_championships_options()
    seasons = add_sidebar_select_box('Seasons:', get_seasons(), 0)
    fit_check_box = fit_table_check_box()

    if selected == 'Drivers':
        drivers_championships_df = get_driver_championships(seasons)
        create_table(drivers_championships_df, fit_check_box)
        create_bar_chart(seasons, 'Drivers')

    if selected == 'Constructors':
        constructor_championships_df = get_constructor_championships(seasons)
        create_table(constructor_championships_df, fit_check_box)
        create_bar_chart(seasons, 'Constructors')


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
    data = make_request(url)

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
