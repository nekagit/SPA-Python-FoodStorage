import streamlit as st
import requests
import pandas as pd
API_URL = "http://127.0.0.1:8000/food_category"
# Fetch all food_categorys from the backend
def fetch_food_categories():
    response = requests.get(API_URL)
    if response.status_code == 200:
        lst = list(response.json())
        return lst
    st.error(f"Error fetching food_categorys: {response.status_code}")
    return []

# Fetch food_category by ID
def fetch_food_category_by_id(food_category_id):
    response = requests.get(f"{API_URL}/{food_category_id}")
    if response.status_code == 200:
        return response.json()
    st.error(f"Error fetching food_category {food_category_id}: {response.status_code}")
    return None

# Create new food_category
def create_food_category(food_category_data):
    try:
        print(food_category_data)
        response = requests.post(API_URL, json=food_category_data)
        print(response)
        response.raise_for_status()  # This will throw an exception for 4xx/5xx errors
        st.success("food_category created successfully!")
    except requests.exceptions.HTTPError as e:
        st.error(f"Error creating food_category: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


# Update food_category by ID
def update_food_category(food_category_id, food_category_data):
    response = requests.put(f"{API_URL}/{food_category_id}", json=food_category_data)
    if response.status_code == 200:
        st.success(f"food_category {food_category_id} updated successfully!")
    else:
        st.error(f"Error updating food_category: {response.status_code} - {response.text}")
    st.rerun()

# Delete food_category by ID
def delete_food_category(food_category_id):
    response = requests.delete(f"{API_URL}/{food_category_id}")
    if response.status_code == 200:
        st.success(f"food_category {food_category_id} deleted successfully!")
    else:
        st.error(f"Error deleting food_category: {response.status_code}")
