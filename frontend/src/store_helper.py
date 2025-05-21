import streamlit as st
import pandas as pd
from datetime import date, datetime
from enum import Enum
from api.food_service import fetch_foods, create_food, update_food, delete_food
import plotly.express as px

class FoodCategory(Enum):
    GRAINS_OR_DOE = "Grains/Doe"
    CANNED_OR_JARRED = "Canned/Jarred"
    BAKING_OR_BREAKFAST_SUPPLIES = "Baking/Breakfast Supplies"
    SPICES_OILS_OR_BASIC_INGREDIENTS = "Spices/Oils/Basic Ingredients"
    LONG_SHELF_LIFE_ITEMS = "Long Shelf Life Items"
    BEVERAGES = "Beverages"
    
    def __str__(self):
        return self.value


class Unit(Enum):
    UNITS = "units"
    KILOGRAMS = "kg"
    GRAMS = "g"
    LITERS = "liters"
    MILLILITERS = "ml"
    
    def __str__(self):
        return self.value


class Location(Enum):
    PANTRY = "pantry"
    FRIDGE = "fridge"
    FREEZER = "freezer"
    
    def __str__(self):
        return self.value


# Icons mapping for categories
CATEGORY_ICONS = {
    "GRAINS_OR_DOE": "🌾",
    "CANNED_OR_JARRED": "🥫",
    "BAKING_OR_BREAKFAST_SUPPLIES": "🥣",
    "SPICES_OILS_OR_BASIC_INGREDIENTS": "🧂",
    "LONG_SHELF_LIFE_ITEMS": "📦",
    "BEVERAGES": "🥤"
}

# Icons mapping for locations
LOCATION_ICONS = {
    "pantry": "🗄️",
    "fridge": "❄️",
    "freezer": "🧊"
}

# Get days until expiration
def days_until_expiration(expiration_date):
    if not expiration_date:
        return None
    
    try:
        exp_date = datetime.strptime(expiration_date, "%Y-%m-%d").date()
        days = (exp_date - date.today()).days
        return days
    except:
        return None


def get_food_data():
    """Safely fetch food data from the API."""
    try:
        foods_list = fetch_foods()
        # Ensure we have a list of dictionaries
        if not isinstance(foods_list, list):
            st.error("Unexpected data format from API")
            return []
        return foods_list
    except Exception as e:
        st.error(f"Error fetching food data: {e}")
        return []

def convert_units(quantity, from_unit, to_unit=None):
    """
    Convert quantity between compatible units.
    If to_unit is not provided, converts to the larger unit automatically.
    
    Parameters:
    - quantity: float, the quantity to convert
    - from_unit: str, the source unit ('g', 'kg', 'ml', 'liters', 'units')
    - to_unit: str or None, the target unit (if None, converts to larger unit)
    
    Returns:
    - tuple: (converted_quantity, unit)
    """
    if not quantity or not from_unit:
        return quantity, from_unit
    
    # Mass conversions (g, kg)
    if from_unit in ['g', 'kg']:
        if to_unit is None:
            # Convert to kg if the quantity is large enough
            if from_unit == 'g' and quantity >= 1000:
                return quantity / 1000, 'kg'
            elif from_unit == 'kg':
                return quantity, 'kg'
            else:
                return quantity, 'g'
        elif to_unit == 'kg' and from_unit == 'g':
            return quantity / 1000, 'kg'
        elif to_unit == 'g' and from_unit == 'kg':
            return quantity * 1000, 'g'
    
    # Volume conversions (ml, liters)
    if from_unit in ['ml', 'liters']:
        if to_unit is None:
            # Convert to liters if the quantity is large enough
            if from_unit == 'ml' and quantity >= 1000:
                return quantity / 1000, 'liters'
            elif from_unit == 'liters':
                return quantity, 'liters'
            else:
                return quantity, 'ml'
        elif to_unit == 'liters' and from_unit == 'ml':
            return quantity / 1000, 'liters'
        elif to_unit == 'ml' and from_unit == 'liters':
            return quantity * 1000, 'ml'
    
    # If units are not compatible or the same, return original
    return quantity, from_unit

def harmonize_units(df):
    """
    Process a dataframe to harmonize units for items with the same name.
    For each unique food name, converts all entries to use the same unit.
    
    Parameters:
    - df: pandas DataFrame with food data (must have 'name', 'quantity', 'unit' columns)
    
    Returns:
    - DataFrame with harmonized units
    """
    if df.empty:
        return df
    
    # Create a copy to avoid modifying the original df
    result_df = df.copy()
    
    # Define unit preference order (larger units first)
    unit_hierarchy = {
        'mass': ['kg', 'g'],
        'volume': ['liters', 'ml']
    }
    
    # Group by name to find items that need harmonization
    for name, group in result_df.groupby('name'):
        # Skip if there's only one unit type
        if group['unit'].nunique() == 1:
            continue
        
        # Check if we need to harmonize mass units (g/kg)
        mass_units = [u for u in group['unit'].unique() if u in unit_hierarchy['mass']]
        if len(mass_units) > 1:
            # Choose the larger unit (kg)
            target_unit = unit_hierarchy['mass'][0]  # 'kg'
            
            # Update all rows for this food name with mass units
            mass_indices = result_df[(result_df['name'] == name) & (result_df['unit'].isin(mass_units))].index
            for idx in mass_indices:
                qty, unit = convert_units(result_df.loc[idx, 'quantity'], result_df.loc[idx, 'unit'], target_unit)
                result_df.loc[idx, 'quantity'] = qty
                result_df.loc[idx, 'unit'] = unit
        
        # Check if we need to harmonize volume units (ml/liters)
        volume_units = [u for u in group['unit'].unique() if u in unit_hierarchy['volume']]
        if len(volume_units) > 1:
            # Choose the larger unit (liters)
            target_unit = unit_hierarchy['volume'][0]  # 'liters'
            
            # Update all rows for this food name with volume units
            volume_indices = result_df[(result_df['name'] == name) & (result_df['unit'].isin(volume_units))].index
            for idx in volume_indices:
                qty, unit = convert_units(result_df.loc[idx, 'quantity'], result_df.loc[idx, 'unit'], target_unit)
                result_df.loc[idx, 'quantity'] = qty
                result_df.loc[idx, 'unit'] = unit
    
    return result_df