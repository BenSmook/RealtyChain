import streamlit as st
import requests
import json
import pandas as pd
import folium
from streamlit_folium import st_folium

@st.cache
def get_property_listings(city, state, limit):
    url = "https://realty-mole-property-api.p.rapidapi.com/saleListings"
    querystring = {"city": city, "state": state, "limit": limit}
    headers = {
        "X-RapidAPI-Key": "ed559ee283msh649d2a47430748cp19d57ajsn27b169833529",
        "X-RapidAPI-Host": "realty-mole-property-api.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    real_estate_df = pd.DataFrame(json.loads(response.text))
    return real_estate_df

def create_map(real_estate_df):
    map_ = folium.Map(location=[real_estate_df["latitude"].mean(), real_estate_df["longitude"].mean()], zoom_start=12)
    for i, row in real_estate_df.iterrows():
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=f"{row['formattedAddress']}<br>Price: ${row['price']}",
        ).add_to(map_)
    return map_

st.title("Real Estate")
st.sidebar.header("Search Filters")


city = st.sidebar.text_input("Enter a city:")
state = st.sidebar.text_input("Enter a state (use abbreviation, e.g. CA for California):")
limit = st.sidebar.selectbox("Select a limit", ["150", "200", "250"])

st.sidebar.header("Search")
search_button = st.sidebar.button("Search")

real_estate_df = get_property_listings(city, state, limit)
st.write(real_estate_df)
map_real_estate = create_map(real_estate_df)

st.write("Map of Real Estate Properties")
st_folium(map_real_estate)