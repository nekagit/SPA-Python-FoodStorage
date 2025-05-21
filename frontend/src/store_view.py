import streamlit as st

from features.FoodStorage.store_categories import (
    main as manage_categories
)
from features.FoodStorage.store_shopping_list import ( 
    main as generate_shopping_list
)
from features.FoodStorage.store_crud import (
add_food,
delete_food_item,
update_food_item,
)

from features.FoodStorage.store_storage import (
    current_storage)


def main():
    """Main application function."""
    st.title("🍎 Food Storage Management")
    
    # Application navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Current Storage",
        "➕ Add Food", 
        "✏️ Update Food", 
        "🗑️ Delete Food",
        "🏷️ Categories",
        "🛒 Shopping List"
    ])
    
    with tab1:
        current_storage()
    with tab2:
        add_food()
    with tab3:
        update_food_item()
    with tab4:
        delete_food_item()
    with tab5:
        manage_categories()
    with tab6:
        generate_shopping_list()