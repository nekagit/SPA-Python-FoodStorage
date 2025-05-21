
import streamlit as st

st.set_page_config(
    page_title="Food Inventory",
    layout="wide", 
    initial_sidebar_state="expanded"
)

from main import main

if __name__ == "__main__":
    main()