from functions import *

if __name__ == '__main__':
    streamlit_setup('F1 data Visualiser', 'wide')

    lottie = load_lottie()
    insert_line(1, True)
    seasons = add_sidebar_select_box('Please choose a season', get_seasons(), 0)
    rounds = get_rounds(seasons)
    insert_line(1, True)
    rounds = st.sidebar.selectbox("Please choose a race", range(len(rounds)), 0, format_func=lambda x: rounds[x])

    selected_year = seasons
    selected_round = rounds + 1

    df_race = get_race_details(selected_year, selected_round)

    details_table = create_drivers_table(df=df_race)

    insert_empty_space(15, True)

    selection_status = check_selection_status(details_table)

    if selection_status:

        clear_plot_button()

        create_state_dataframe()

        selected_driver_id = get_driver_id(details_table)
        selected_driver_name = get_driver_name(details_table)

        try:
            get_laps_times(selected_year, selected_round, selected_driver_id, selected_driver_name)
            plot_chart()
        except ValueError:
            insert_empty_space(7, False)
            st.markdown("<h1 style='text-align: center; color: grey;'>No lap times data for this race</h1>",
                        unsafe_allow_html=True)

    else:
        insert_empty_space(7, False)
        st.markdown("<h1 style='text-align: center; color: grey;'>Select from the table to compare lap times</h1>",
                    unsafe_allow_html=True)
        for key in st.session_state.keys():
            del st.session_state[key]

