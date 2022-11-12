from races_page import create_races_page
from championships_page import create_championships_page
from maps_page import create_map_page
from functions import *

#
if __name__ == '__main__':

    # Initialize streamlit by calling various functions
    # See each functions for detailed explanation
    streamlit_setup('F1 data Visualiser', 'wide')
    selected = create_nav_menu()

    # Change pages when selecting different item in the nav menu
    if selected == 'Races':
        create_races_page()
    if selected == 'Championships':
        create_championships_page()
    if selected == 'Circuits':
        create_map_page()
