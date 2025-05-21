import streamlit as st
from api.food_service import create_food, update_food, delete_food
from features.FoodStorage.store_helper import (
    get_food_data
)
from features.FoodStorage.store_food_form import (
    food_form
)
def add_food():
    """Add a new food item to storage."""
    st.subheader("➕ Add New Food Item")
    food_data, _ = food_form()
    
    if st.button("Add Food", type="primary"):
        if not food_data:
            return
            
        try:
            create_food(food_data)
            st.success("✅ Food item added successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to add food: {e}")

def update_food_item():
    """Update an existing food item's information."""
    st.subheader("✏️ Update Food Item")
    foods_list = get_food_data()
    
    if not foods_list:
        st.info("No food items available to update")
        return
        
    # Create food selection dropdown
    food_options = {}
    for food in foods_list:
        if 'id' in food and 'name' in food:
            food_options[f"{food['id']}: {food['name']}"] = food
            
    selected_food_label = st.selectbox(
        "Select Food to Update", 
        options=list(food_options.keys()), 
        key="update_food_select"
    )
    
    selected_food = food_options[selected_food_label]
    
    # Use the unified form with the selected food data
    food_data, food_id = food_form(existing_food=selected_food)
    
    if st.button("Update Food", key="update_food_button", type="primary"):
        if not food_data:
            return
            
        try:
            update_food(food_id, food_data)
            st.success(f"✅ Food item '{food_data['name']}' updated successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to update food: {e}")

def delete_food_item():
    """Delete a food item from storage by ID."""
    st.subheader("🗑️ Delete Food Item")
    foods_list = get_food_data()
    
    if not foods_list:
        st.info("No food items available to delete")
        return
        
    food_options = {}
    for food in foods_list:
        if 'id' in food and 'name' in food:
            food_options[f"{food['id']}: {food['name']}"] = food['id']
            
    selected_food = st.selectbox(
        "Select Food to Delete", 
        options=list(food_options.keys()), 
        key="delete_food_select"
    )
    
    food_id = food_options[selected_food]
    
    if st.button("Delete Food", key="delete_food_button", type="primary"):
        try:
            delete_food(food_id)
            st.success("✅ Food item deleted successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to delete food: {e}")