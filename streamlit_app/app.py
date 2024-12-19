import streamlit as st
import pandas as pd
import random
from fuzzywuzzy import fuzz, process  # Fuzzy matching library

# Load product data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df.head(100)  # Load only the first 100 rows

# Fuzzy Search Function
def fuzzy_search(query, choices, limit=10):
    """Perform fuzzy search on a list of choices."""
    if not query:
        return choices
    results = process.extract(query, choices, scorer=fuzz.partial_ratio, limit=limit)
    return [match[0] for match in results]

# Load CSV file
csv_file = "clean.csv"  # Replace with your CSV file path
data = load_data(csv_file)

# Initialize session state for selected items
if "selected_items" not in st.session_state:
    st.session_state["selected_items"] = []

# Streamlit App Title
st.title("Product Recommendation System")

# Create Tabs
tab1, tab2, tab3 = st.tabs(["🛒 Select Products", "📋 Selected Items", "✨ View Recommendations"])

# Tab 1: Select Products
with tab1:
    st.write("### Browse and Select Products")
    st.write("Search for products using fuzzy search for approximate matches!")

    # Search Bar
    search_query = st.text_input("🔍 Search Products:", placeholder="Type product name...")

    # Fuzzy Search Filtering
    if search_query:
        product_titles = data['title'].tolist()
        matching_titles = fuzzy_search(search_query, product_titles, limit=20)
        filtered_data = data[data['title'].isin(matching_titles)]
    else:
        filtered_data = data

    # Display Products in 2 Columns
    for i in range(0, len(filtered_data), 2):
        cols = st.columns(2)  # Two products per row
        for col, (_, product) in zip(cols, filtered_data.iloc[i:i+2].iterrows()):
            with col:
                # Highlight product if selected
                if product['product_id'] in st.session_state["selected_items"]:
                    st.markdown(f"### ✅ {product['title']}")
                else:
                    st.markdown(f"### {product['title']}")

                # Display Image
                st.image(product['url'], use_container_width=True, caption=product['title'])

                # Add Select/Deselect Button
                if st.button(
                    f"{'Deselect' if product['product_id'] in st.session_state['selected_items'] else 'Select'}",
                    key=product['product_id']
                ):
                    if product['product_id'] in st.session_state["selected_items"]:
                        st.session_state["selected_items"].remove(product['product_id'])
                        st.success(f"Deselected '{product['title']}'!")
                    else:
                        st.session_state["selected_items"].append(product['product_id'])
                        st.success(f"Selected '{product['title']}'!")

# Tab 2: Selected Items
with tab2:
    st.write("### Your Selected Items")
    if st.session_state["selected_items"]:
        selected_products = data[data['product_id'].isin(st.session_state["selected_items"])]
        st.write(f"**You have selected {len(selected_products)} items:**")
        cols = st.columns(min(4, len(selected_products)))
        for col, (_, product) in zip(cols, selected_products.iterrows()):
            with col:
                st.image(product['url'], use_container_width=True, caption=product['title'])
                st.markdown(f"**{product['title']}**")
    else:
        st.info("You have not selected any products yet. Go to 'Select Products' tab to choose.")

# Tab 3: View Recommendations
with tab3:
    st.write("### Recommended Products")
    
    # Ensure enough products are selected
    if len(st.session_state["selected_items"]) >= 3:
        st.write("Here are 10 products recommended for you:")

        # Filter unselected products
        remaining_products = data[~data['product_id'].isin(st.session_state["selected_items"])]
        
        # Randomly select 10 products for recommendation
        recommended_products = remaining_products.sample(n=min(10, len(remaining_products)), random_state=42)

        # Display Recommended Products in 2 Columns
        for i in range(0, len(recommended_products), 2):
            cols = st.columns(2)
            for col, (_, product) in zip(cols, recommended_products.iloc[i:i+2].iterrows()):
                with col:
                    st.image(product['url'], use_container_width=True, caption=product['title'])
                    st.write(f"**{product['title']}**")
    else:
        st.info("Please select at least 3 products in the 'Select Products' tab to view recommendations.")
