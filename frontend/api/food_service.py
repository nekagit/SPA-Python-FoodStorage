import streamlit as st
import requests
import pandas as pd
API_URL = "http://127.0.0.1:8000/food"
# Fetch all foods from the backend
def fetch_foods():
    response = requests.get(API_URL)
    if response.status_code == 200:
        lst = list(response.json())
        return lst
    st.error(f"Error fetching foods: {response.status_code}")
    return []

# Fetch food by ID
def fetch_food_by_id(food_id):
    response = requests.get(f"{API_URL}/{food_id}")
    if response.status_code == 200:
        return response.json()
    st.error(f"Error fetching food {food_id}: {response.status_code}")
    return None

# Create new food
def create_food(food_data):
    try:
        print(food_data)
        response = requests.post(API_URL, json=food_data)
        print(response)
        response.raise_for_status()  # This will throw an exception for 4xx/5xx errors
        st.success("food created successfully!")
    except requests.exceptions.HTTPError as e:
        st.error(f"Error creating food: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


# Update food by ID
def update_food(food_id, food_data):
    response = requests.put(f"{API_URL}/{food_id}", json=food_data)
    if response.status_code == 200:
        st.success(f"food {food_id} updated successfully!")
    else:
        st.error(f"Error updating food: {response.status_code} - {response.text}")
    st.rerun()

# Delete food by ID
def delete_food(food_id):
    response = requests.delete(f"{API_URL}/{food_id}")
    if response.status_code == 200:
        st.success(f"food {food_id} deleted successfully!")
    else:
        st.error(f"Error deleting food: {response.status_code}")
