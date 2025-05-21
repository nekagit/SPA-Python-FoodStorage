import streamlit as st
import pandas as pd
from api.food_category_service import (
    create_food_category,
    update_food_category,
    delete_food_category,
    fetch_food_categories,
)

def main():
    st.title("🏷️ Food Categories Management")
    
    # Load categories once to avoid redundant API calls
    categories = load_categories()
    
    # App sections
    add_food_category()
    display_categories(categories)
    
    # Optional dataframe view
    with st.expander("📊 View as Table"):
        display_categories_table(categories)

def load_categories():
    """Load categories with error handling"""
    try:
        return fetch_food_categories()
    except Exception as e:
        st.error(f"❌ Failed to load categories: {e}")
        return []

def add_food_category():
    """Add new category section"""
    with st.expander("➕ Add New Category"):
        new_name = st.text_input("New Category Name", key="new_category")
        if st.button("Add Category"):
            if not new_name.strip():
                st.error("❌ Category name cannot be empty")
            else:
                try:
                    create_food_category({"name": new_name})
                    st.success("✅ Category added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to add category: {e}")

def display_categories(categories):
    """Display and manage existing categories"""
    st.markdown("---")
    
    if not categories:
        st.info("No categories found.")
        return
    
    for cat in categories:
        col1, col2, col3 = st.columns([4, 2, 2], vertical_alignment="bottom")
        
        with col1:
            new_val = st.text_input("Category Name", value=cat["name"], key=f"edit_{cat['id']}")
        
        with col2:
            if st.button("Update", key=f"update_{cat['id']}"):
                handle_update(cat["id"], new_val)
        
        with col3:
            if st.button("Delete", key=f"delete_{cat['id']}"):
                handle_delete(cat["id"])

def handle_update(category_id, new_name):
    """Handle category update with validation"""
    if not new_name.strip():
        st.error("❌ Name cannot be empty")
        return
        
    try:
        update_food_category(category_id, {"name": new_name})
        st.success("✅ Category updated!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Failed to update category: {e}")

def handle_delete(category_id):
    """Handle category deletion"""
    try:
        delete_food_category(category_id)
        st.success("✅ Category deleted!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Failed to delete category: {e}")

def display_categories_table(categories):
    """Display categories as a dataframe"""
    if not categories:
        st.info("No categories available")
        return
    
    df = pd.DataFrame(categories)
    st.dataframe(df, use_container_width=True)