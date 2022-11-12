from functions import *


# Main function for the circuits page
def create_circuits_page():
    seasons = add_sidebar_select_box('Seasons:', get_seasons(), 0)  # create a select box to store all the seasons
    fit_check_box = fit_table_check_box()  # create the fit tabel columns on grid check box
    circuits_details_df = get_circuits_details(seasons)  # get and create the dataframe for the circuits data
    create_table(circuits_details_df, fit_check_box)  # create the table using the dataframe
    location_df = get_circuits_location(seasons)  # get all the location data for the circuits

    st.map(data=location_df, zoom=1, use_container_width=True)  # display the map containing all the circuits location


# Function to get the data for the circuits in a specific year
# Cache this function to save time between reruns
@st.cache(persist=True)
def get_circuits_details(year):
    url = f'https://ergast.com/api/f1/{year}/circuits.json?limit=10000'  # url to make request from
    data = make_request(url)  # get the json object from request

    data_dict = {'Circuit': [], 'Location': [], 'Country': []}  # dictionary to append to

    # append corresponding data to the dictionary
    for dataItem in data['MRData']['CircuitTable']['Circuits']:
        data_dict['Circuit'].append(dataItem['circuitName'])
        data_dict['Location'].append(dataItem['Location']['locality'])
        data_dict['Country'].append(dataItem['Location']['country'])

    df = pd.DataFrame.from_dict(data_dict)  # create a pandas dataframe from the dictionary

    return df  # return the dataframe


# Function to get the data for the circuits location in a specific year
# Cache this function to save time between reruns
@st.cache(persist=True)
def get_circuits_location(year):
    url = f'https://ergast.com/api/f1/{year}/circuits.json?limit=10000'
    data = make_request(url)

    data_dict = {'lat': [], 'lon': []}

    for dataItem in data['MRData']['CircuitTable']['Circuits']:
        data_dict['lat'].append(dataItem['Location']['lat'])
        data_dict['lon'].append(dataItem['Location']['long'])

    df = pd.DataFrame.from_dict(data_dict)
    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)

    return df
