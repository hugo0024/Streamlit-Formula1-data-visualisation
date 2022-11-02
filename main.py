from functions import *

if __name__ == '__main__':
    streamlit_setup('F1 data Visualiser', 'wide')

    lottie = load_lottie()

    seasons = add_sidebar_select_box('Please choose a season', get_seasons(), 0)
    rounds = get_rounds(seasons)
    rounds = st.sidebar.selectbox("Please choose a race", range(len(rounds)), 0, format_func=lambda x: rounds[x])

    selected_year = seasons
    selected_round = rounds + 1

    df_race = get_race_details(selected_year, selected_round)

    details_table = create_drivers_table(df=df_race)

    selection_status = check_selection_status(details_table)

    if selection_status:
        selected_driver_id = get_driver_id(details_table)

        create_state_dataframe()

        get_laps_times(selected_year, selected_round, selected_driver_id)

        plot_chart()
