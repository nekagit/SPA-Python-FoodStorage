import streamlit as st
import numpy as np
import pandas as pd
from datetime import date
from features.FoodStorage.store_helper import (
    CATEGORY_ICONS,
    get_food_data,
    harmonize_units,
)

def process_food_data(foods_list):
    """Process food data into a DataFrame with calculated fields."""
    if not foods_list:
        return pd.DataFrame()
        
    try:
        df = pd.DataFrame(foods_list)
        if df.empty:
            return df
            
        # Process expiration dates
        if 'expiration_date' in df.columns:
            df["expiration_date"] = pd.to_datetime(df["expiration_date"]).dt.date
            # Calculate days until expiration
            df['days_until_expiration'] = df["expiration_date"].apply(
                lambda x: (x - date.today()).days if pd.notna(x) else None
            )
        
        return df
        
    except Exception as e:
        st.error(f"Error processing food data: {e}")
        return pd.DataFrame()


def display_food_summary_table(foods_df):
    """Display a summary table that groups foods by name and sums quantities."""
    if foods_df.empty:
        st.info("No food items in storage")
        return
    
    # Harmonize units before grouping
    harmonized_df = harmonize_units(foods_df)
    
    # Group by food name and unit, then sum quantities
    summary_df = harmonized_df.groupby(['name', 'unit']).agg({
        'quantity': 'sum',
        'category': lambda x: x.mode()[0] if not x.mode().empty else np.nan
    }).reset_index()
    
    # Display the summary table
    st.subheader("Food Summary")
    
    # Format the table for display
    summary_display = summary_df[['name', 'quantity', 'unit', 'category']]
    summary_display = summary_display.rename(columns={
        'name': 'Name',
        'quantity': 'Total Quantity',
        'unit': 'Unit',
        'category': 'Category'
    })
    
    st.dataframe(summary_display, use_container_width=True)

def generate_shopping_list(foods_df):
    """Generate a shopping list for items below minimum stock level."""
    if foods_df.empty:
        st.info("No food items in storage to check for shopping list")
        return
    
    # Harmonize units before processing
    harmonized_df = harmonize_units(foods_df)
    
    # Check if 'minimal_stock' column exists, if not return a message
    if 'minimal_stock' not in harmonized_df.columns:
        st.error("Minimal stock information not available in the data")
        return
    
    # Group by name and unit to get total quantities and maximum minimal_stock
    grouped_foods = harmonized_df.groupby(['name', 'unit']).agg({
        'quantity': 'sum',
        'minimal_stock': 'max',  # Take the highest minimal_stock for items with same name
        'category': lambda x: x.mode()[0] if not x.mode().empty else np.nan
    }).reset_index()
    
    # Calculate which items need to be purchased
    grouped_foods['needed_quantity'] = grouped_foods.apply(
        lambda row: max(0, row['minimal_stock'] - row['quantity']), 
        axis=1
    )
    
    # Filter only items that need to be purchased
    shopping_list_df = grouped_foods[grouped_foods['needed_quantity'] > 0].copy()
    
    if shopping_list_df.empty:
        st.success("All items are above their minimum stock level. No shopping needed!")
        return
    
    # Sort by category to organize shopping list by store sections
    shopping_list_df = shopping_list_df.sort_values('category')
    
    # Display the shopping list
    st.subheader("Shopping List")
    
    # Format for display
    display_df = shopping_list_df[['name', 'needed_quantity', 'unit', 'category']]
    display_df = display_df.rename(columns={
        'name': 'Item',
        'needed_quantity': 'Quantity to Buy',
        'unit': 'Unit',
        'category': 'Category'
    })
    
    # Add category icons if available
    if 'category' in display_df.columns:
        from features.FoodStorage.store_helper import CATEGORY_ICONS
        display_df['Category'] = display_df['Category'].apply(
            lambda cat: f"{CATEGORY_ICONS.get(cat, '🍽️')} {cat}" if pd.notna(cat) else '🍽️ Other'
        )
    
    st.dataframe(display_df, use_container_width=True)
    
    # Provide option to download the shopping list
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="Download Shopping List",
        data=csv,
        file_name="shopping_list.csv",
        mime="text/csv",
    )

def main():
    st.title("Food Storage & Shopping List")
    
    # Get and process food data
    foods_list = get_food_data()
    df = process_food_data(foods_list)
    
    # Display tabs for different views
    tab1, tab2 = st.tabs(["Food Summary", "Shopping List"])
    
    with tab1:
        display_food_summary_table(df)
    
    with tab2:
        generate_shopping_list(df)
