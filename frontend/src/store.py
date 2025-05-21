import streamlit as st
from features.FoodStorage.store_view import (
    main
)



def store_page():
    st.title("🏠 Home Food Storage")
    main()
    