import streamlit as st
import numpy as np
import requests
import json
import pandas as pd
import folium
from streamlit_folium import st_folium
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split

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
    real_estate_df = real_estate_df[~real_estate_df['propertyType'].isin(['Land', 'Manufactured', 'Duplex-Triplex'])]
    return real_estate_df

def create_map(real_estate_df):
    map_ = folium.Map(location=[real_estate_df["latitude"].mean(), real_estate_df["longitude"].mean()], zoom_start=12)
    for i, row in real_estate_df.iterrows():
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=f"{row['formattedAddress']}<br>Price: ${row['price']}",
        ).add_to(map_)
    return map_

def fit_knn(real_estate_df):
    X = real_estate_df[["latitude", "longitude"]]
    y = real_estate_df["price"]
    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    knn = KNeighborsRegressor(n_neighbors=5)
    knn.fit(X, y)
    X_test = pd.DataFrame({0:[40.75898], 1:[-73.982]})
    st.table(X_test)
    y_pred = knn.predict(X_test)
    
    df = pd.DataFrame({'Predicted Price': y_pred})

    #df = df.style.format({'Actual Price': '${:,.0f}', 'Predicted Price': '${:,.0f}'})
    st.table(df)



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

st.header("KNN Regression Model")
address = st.text_input("Enter an address:")
if address:
    address_df = real_estate_df[real_estate_df['formattedAddress'].str.contains(address, case=False)]
    
fit_knn(real_estate_df)