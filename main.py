from races_page import create_races_page
from functions import *

if __name__ == '__main__':
    streamlit_setup('F1 data Visualiser', 'wide')

    selected = create_nav_menu()

    lottie = load_lottie()
    insert_line(1, True)

    if selected == 'Races':
        create_races_page()
    if selected == 'Championships':
        st.write('Championships')
    if selected == 'Maps':
        st.write('Maps')
