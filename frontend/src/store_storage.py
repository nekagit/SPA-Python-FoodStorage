import streamlit as st
import plotly.express as px
from features.FoodStorage.store_helper import get_food_data
from features.FoodStorage.store_shopping_list import (
    display_food_summary_table,
    process_food_data
)
# Custom CSS for better styling
def load_custom_css():
    st.markdown("""
    <style>
        .food-card {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 5px solid;
        }
        .card-pantry {
            border-left-color: #FF9933 !important;
        }
        .card-fridge {
            border-left-color: #3366FF !important;
        }
        .card-freezer {
            border-left-color: #99CCFF !important;
        }
        .expiring-soon {
            color: #FF5733;
            font-weight: bold;
        }
        .fresh {
            color: #4CAF50;
        }
        .category-badge {
            background-color: #EEEEEE;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }
        .metric-box {
            margin: 3rem 0;
            color: #333;
            background-color: #f0f2f6;
            border-radius: 7px;
            padding: 10px 15px;
            text-align: center;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
        }
        .metric-label {
            font-size: 14px;
            color: #666;
        }
        .shortage {
            color: #FF5733;
        }
        .surplus {
            color: #4CAF50;
        }
        .balanced {
            color: #3366FF;
        }
        .shopping-item {
            padding: 5px 10px;
            margin: 3px 0;
            border-radius: 5px;
            background-color: #f0f2f6;
        }
    </style>
    """, unsafe_allow_html=True)

def display_summary_metrics(foods_df):
    """Display summary metrics as colorful cards."""
    if foods_df.empty:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{len(foods_df)}</div>
            <div class="metric-label">Total Food Items</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Count items by location
    with col2:
        location_counts = foods_df['location'].value_counts()
        icon_text = "🗄️❄️🧊"
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{icon_text}</div>
            <div class="metric-label">
                Pantry: {location_counts.get('pantry', 0)} | 
                Fridge: {location_counts.get('fridge', 0)} | 
                Freezer: {location_counts.get('freezer', 0)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Calculate expiring soon items (within 7 days)
    with col3:
        if 'days_until_expiration' in foods_df.columns:
            expiring_soon = len(foods_df[foods_df['days_until_expiration'] <= 7])
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">⚠️ {expiring_soon}</div>
                <div class="metric-label">Expiring Within 7 Days</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Show categories count 
    with col4:
        categories_count = len(foods_df['category'].unique())
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">🏷️ {categories_count}</div>
            <div class="metric-label">Food Categories</div>
        </div>
        """, unsafe_allow_html=True)


def display_food_table(foods_df):
    """Display the food inventory as a detailed table."""
    if foods_df.empty:
        return
        
    # Sort by expiration date if available
    if 'expiration_date' in foods_df.columns:
        foods_df = foods_df.sort_values(by="expiration_date")
    
    # Reorder columns for display
    columns_order = ['id', 'name', 'category', 'quantity', 'unit', 
                     'location', 'expiration_date', 'days_until_expiration']
    display_df = foods_df[[col for col in columns_order if col in foods_df.columns]]
    
    # Rename columns for display
    display_df = display_df.rename(columns={
        'days_until_expiration': 'Days Left'
    })
    
    st.dataframe(display_df, use_container_width=True)

def search_filter_foods(df):
    """Provide search and filter functionality for the food inventory."""
    if df.empty:
        return df

    # Add search and filter capabilities
    st.subheader("🔍 Search & Filter")
    with st.expander("Filter Food Items"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Get unique categories from the data
            categories = ["All"] + sorted(df['category'].unique().tolist())
            selected_category = st.selectbox("Filter by Category", categories)
        
        with col2:
            # Filter by expiration timeframe
            expiry_options = ["All", "Expired", "Expiring in 7 days", "Expiring in 30 days", "Good for > 30 days"]
            selected_expiry = st.selectbox("Filter by Expiration", expiry_options)
        
        with col3:
            # Search by name
            search_term = st.text_input("Search by Name", "")
        
        # Filter the dataframe based on selections
        filtered_df = df.copy()
        
        # Apply category filter
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
        
        # Apply expiration filter
        if selected_expiry != "All" and 'days_until_expiration' in filtered_df.columns:
            if selected_expiry == "Expired":
                filtered_df = filtered_df[filtered_df['days_until_expiration'] < 0]
            elif selected_expiry == "Expiring in 7 days":
                filtered_df = filtered_df[(filtered_df['days_until_expiration'] >= 0) & (filtered_df['days_until_expiration'] <= 7)]
            elif selected_expiry == "Expiring in 30 days":
                filtered_df = filtered_df[(filtered_df['days_until_expiration'] >= 0) & (filtered_df['days_until_expiration'] <= 30)]
            elif selected_expiry == "Good for > 30 days":
                filtered_df = filtered_df[filtered_df['days_until_expiration'] > 30]
        
        # Apply name search
        if search_term:
            filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False)]
        
    return filtered_df

def expiration_soon_chart(df):
    """Create a visualization of food items by expiration date."""
    if df.empty or 'expiration_date' not in df.columns:
        return
    
    with st.expander("View Expiration Timeline"):
        # Create subset for visualization
        vis_df = df[['name', 'expiration_date', 'days_until_expiration']] \
                     .dropna(subset=['expiration_date'])
        
        if not vis_df.empty:
            vis_df = vis_df.sort_values('expiration_date')
            
            # Create horizontal bar chart ordered by expiration date
            fig = px.bar(vis_df, 
                         x='days_until_expiration', 
                         y='name', 
                         orientation='h',
                         color='days_until_expiration',
                         color_continuous_scale=[(0, "red"), (0.1, "orange"), (1, "green")],
                         title='Days Until Expiration',
                         labels={'days_until_expiration': 'Days Left', 'name': 'Food Item'})
            
            fig.update_layout(height=max(250, len(vis_df) * 25))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expiration date data available for visualization")

def current_storage():
    """Display the current food storage inventory."""
    # Load CSS
    load_custom_css()
    
    # Get and process food data
    foods_list = get_food_data()
    df = process_food_data(foods_list)
    
    if df.empty:
        st.info("No food items in storage")
        return
    
    # Main section
    st.subheader("📦 Current Food Storage")
    
    # Display summary metrics
    with st.expander("View Storage Metrics"):
        display_summary_metrics(df)
    
    # NEW FEATURE: Food quantity summary by name
    with st.expander("Food Quantity Summary"):
        display_food_summary_table(df)
    
    # Filter and search functionality
    filtered_df = search_filter_foods(df)
    
    # Display detailed food table
    st.subheader("📋 Detailed Food Inventory")
    display_food_table(filtered_df)
    
    # Display expiration chart
    expiration_soon_chart(filtered_df)