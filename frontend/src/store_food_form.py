import streamlit as st
import pandas as pd
from datetime import date
from api.food_service import create_food, update_food, delete_food
from features.FoodStorage.store_helper import (
    FoodCategory,
    Unit, 
    Location, 
)
from api.food_category_service import fetch_food_categories

def load_category_data():
    """Load all food categories from API and enum."""
    food_categories = fetch_food_categories()
    food_categories = [cat['name'] for cat in food_categories]
    food_categories.extend([str(cat) for cat in FoodCategory])
    return food_categories

def get_food_object(food_name, food_category, food_quantity,food_minimal_stock, food_unit, food_location, food_expiration):
    """Create a food data dictionary from form inputs."""
    if not food_name:
        st.error("❌ Food name cannot be empty")
        return None
        
    expiration = food_expiration.isoformat() if isinstance(food_expiration, date) else None

    food_data = {
        "name": food_name,
        "category": food_category,
        "quantity": food_quantity,
        "minimal_stock": food_minimal_stock,
        "unit": food_unit.value,
        "location": food_location.value,
        "expiration_date": expiration
    }
    return food_data

def food_form(existing_food=None):
    """Unified form for adding or updating food items.
    
    Args:
        existing_food: If provided, form will be pre-filled with this food's data
    
    Returns:
        Tuple of (food_data, food_id)
    """
    food_id = existing_food.get('id') if existing_food else None
    is_update = existing_food is not None
    form_key_prefix = "update" if is_update else "add"
    
    # Load categories
    food_categories = load_category_data()
    
    # Setup default values
    default_name = existing_food.get('name', '') if is_update else ''
    
    # Find default category index
    default_category_index = 0
    if is_update and existing_food.get('category'):
        try:
            default_category_index = food_categories.index(existing_food.get('category'))
        except ValueError:
            pass
    
    # Get default quantity with safe conversion
    default_quantity = 0.0
    if is_update and existing_food.get('quantity'):
        try:
            default_quantity = float(existing_food.get('quantity', 0))
        except (ValueError, TypeError):
            pass
    
    # Get default quantity with safe conversion
    default_minimal_stock = 0.0
    if is_update and existing_food.get('quantity'):
        try:
            default_minimal_stock = float(existing_food.get('minimal_stock', 0))
        except (ValueError, TypeError):
            pass
    

    # Find default unit
    default_unit_index = 0
    if is_update and existing_food.get('unit'):
        for i, unit in enumerate(Unit):
            if unit.value == existing_food.get('unit'):
                default_unit_index = i
                break
    
    # Find default location
    default_location_index = 0
    if is_update and existing_food.get('location'):
        for i, loc in enumerate(Location):
            if loc.value == existing_food.get('location'):
                default_location_index = i
                break
    
    # Parse default date
    default_date = date.today()
    if is_update and existing_food.get('expiration_date'):
        default_date = pd.to_datetime(existing_food.get('expiration_date')).date()
    
    # Render form
    col1, col2 = st.columns(2)
    with col1:
        food_name = st.text_input("Food Name", value=default_name, key=f"{form_key_prefix}_food_name")
        food_category = st.selectbox("Food Category", food_categories, index=default_category_index, 
                                    key=f"{form_key_prefix}_food_category", 
                                    format_func=lambda x: f"{str(x)}")
        food_quantity = st.number_input("Quantity", min_value=0.0, step=0.1, value=default_quantity, 
                                       key=f"{form_key_prefix}_food_quantity")
        food_minimal_stock = st.number_input("Minimal Stock", min_value=0.0, step=0.1, value=default_minimal_stock, 
                                       key=f"{form_key_prefix}_food_minimal_stock")
    
    with col2:
        food_unit = st.selectbox("Unit", list(Unit), index=default_unit_index, 
                                key=f"{form_key_prefix}_food_unit")
        food_location = st.selectbox("Location", list(Location), index=default_location_index, 
                                    key=f"{form_key_prefix}_food_location", 
                                    format_func=lambda x: f"{str(x).capitalize()}")
        food_expiration = st.date_input("Expiration Date", value=default_date, 
                                       key=f"{form_key_prefix}_food_expiration")
    
    food = get_food_object(food_name, food_category, food_quantity,food_minimal_stock, food_unit, food_location, food_expiration)
    return food, food_id
