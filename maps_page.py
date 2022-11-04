from functions import *


def create_map_page():
    seasons = add_sidebar_select_box('Seasons:', get_seasons(), 0)
    fit_check_box = fit_table_check_box()
    circuits_details_df = get_circuits_details(seasons)
    create_table(circuits_details_df, fit_check_box)
    location_df = get_circuits_location(seasons)

    st.map(data=location_df, zoom=1, use_container_width=True)


@st.cache(persist=True)
def get_circuits_details(year):
    url = f'https://ergast.com/api/f1/{year}/circuits.json?limit=10000'
    response = requests.request("GET", url)
    data = response.json()

    data_dict = {'Circuit': [], 'Location': [], 'Country': []}

    for dataItem in data['MRData']['CircuitTable']['Circuits']:
        data_dict['Circuit'].append(dataItem['circuitName'])
        data_dict['Location'].append(dataItem['Location']['locality'])
        data_dict['Country'].append(dataItem['Location']['country'])

    df = pd.DataFrame.from_dict(data_dict)

    return df


@st.cache(persist=True)
def get_circuits_location(year):
    url = f'https://ergast.com/api/f1/{year}/circuits.json?limit=10000'
    response = requests.request("GET", url)
    data = response.json()

    data_dict = {'lat': [], 'lon': []}

    for dataItem in data['MRData']['CircuitTable']['Circuits']:
        data_dict['lat'].append(dataItem['Location']['lat'])
        data_dict['lon'].append(dataItem['Location']['long'])

    df = pd.DataFrame.from_dict(data_dict)
    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)

    return df
