import streamlit as st
import numpy as np
import requests
import json
import pandas as pd
import folium
from streamlit_folium import st_folium
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split

state_city_dict = {
'AL': ['Birmingham', 'Montgomery', 'Mobile'],
'AK': ['Anchorage', 'Fairbanks', 'Juneau'],
'AZ': ['Phoenix', 'Tucson', 'Mesa'],
'AR': ['Little Rock', 'Fort Smith', 'Fayetteville'],
'CA': ['Los Angeles', 'San Francisco', 'San Diego', 'Sacramento', 'San Jose'],
'CO': ['Denver', 'Colorado Springs', 'Boulder', 'Aurora'],
'CT': ['Hartford', 'New Haven', 'Stamford', 'Bridgeport'],
'DE': ['Wilmington', 'Dover', 'Newark'],
'FL': ['Miami', 'Orlando', 'Tampa', 'Jacksonville', 'Tallahassee'],
'GA': ['Atlanta', 'Savannah', 'Augusta', 'Athens'],
'HI': ['Honolulu', 'Hilo', 'Kailua'],
'ID': ['Boise', 'Idaho Falls', 'Pocatello', 'Nampa'],
'IL': ['Chicago', 'Springfield', 'Peoria', 'Rockford'],
'IN': ['Indianapolis', 'Fort Wayne', 'Evansville', 'Bloomington'],
'IA': ['Des Moines', 'Cedar Rapids', 'Davenport', 'Sioux City'],
'KS': ['Wichita', 'Kansas City', 'Topeka', 'Manhattan'],
'KY': ['Louisville', 'Lexington', 'Frankfort', 'Bowling Green'],
'LA': ['New Orleans', 'Baton Rouge', 'Lafayette', 'Shreveport'],
'ME': ['Portland', 'Bangor', 'Augusta'],
'MD': ['Baltimore', 'Annapolis', 'Rockville', 'Frederick'],
'MA': ['Boston', 'Worcester', 'Springfield', 'Cambridge'],
'MI': ['Detroit', 'Grand Rapids', 'Ann Arbor', 'Lansing'],
'MN': ['Minneapolis', 'St. Paul', 'Duluth', 'Rochester'],
'MS': ['Jackson', 'Biloxi', 'Hattiesburg', 'Meridian'],
'MO': ['Kansas City', 'St. Louis', 'Springfield', 'Columbia'],
'MT': ['Billings', 'Missoula', 'Great Falls', 'Bozeman'],
'NE': ['Omaha', 'Lincoln', 'Bellevue', 'Grand Island'],
'NV': ['Las Vegas', 'Reno', 'Henderson', 'North Las Vegas'],
'NH': ['Manchester', 'Nashua', 'Concord', 'Dover'],
'NJ': ['Newark', 'Jersey City', 'Trenton', 'Atlantic City'],
'NM': ['Albuquerque', 'Santa Fe', 'Las Cruces', 'Roswell'],
'NY': ['New York City', 'Buffalo', 'Rochester', 'Syracuse'],
'NC': ['Charlotte', 'Raleigh', 'Greensboro', 'Wilmington'],
'ND': ['Fargo', 'Bismarck', 'Grand Forks', 'Minot'],
'OH': ['Columbus', 'Cleveland', 'Cincinnati', 'Toledo'],
'OK': ['Oklahoma City', 'Tulsa', 'Norman', 'Broken Arrow'],
'OR': ['Portland', 'Salem', 'Eugene', 'Gresham'],
'PA': ['Philadelphia', 'Pittsburgh', 'Allentown', 'Erie'],
'RI': ['Providence', 'Warwick', 'Cranston', 'Pawtucket'],
'SC': ['Charleston', 'Columbia', 'Myrtle Beach', 'Greenville'],
'SD': ['Sioux Falls', 'Rapid City', 'Aberdeen', 'Brookings'],
'TN': ['Nashville', 'Memphis', 'Knoxville', 'Chattanooga'],
'TX': ['Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth'],
'UT': ['Salt Lake City', 'Provo', 'Orem', 'West Jordan'],
'VT': ['Burlington', 'Essex', 'Montpelier', 'Rutland'],
'VA': ['Richmond', 'Virginia Beach', 'Norfolk', 'Arlington'],
'WA': ['Seattle', 'Spokane', 'Tacoma', 'Vancouver'],
'WV': ['Charleston', 'Huntington', 'Parkersburg', 'Wheeling'],
'WI': ['Milwaukee', 'Madison', 'Green Bay', 'Kenosha'],
'WY': ['Cheyenne', 'Casper', 'Laramie', 'Gillette']
}


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

def fit_knn(real_estate_df, address):
    address_df = real_estate_df[real_estate_df['formattedAddress'].str.contains(address, case=False)]
    if len(address_df) == 0:
        return 'No matching address found'
    elif len(address_df) > 1:
        st.warning('Multiple matching addresses found. Using the first one.')
    X = real_estate_df[["latitude", "longitude"]]
    y = real_estate_df["price"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    knn = KNeighborsRegressor(n_neighbors=5)
    knn.fit(X_train, y_train)
    latitude = address_df.iloc[0]['latitude']
    longitude = address_df.iloc[0]['longitude']
    X_test = pd.DataFrame({'latitude': [latitude], 'longitude': [longitude]})
    y_pred = knn.predict(X_test)
    predicted_price = '${:,.0f}'.format(y_pred[0])
    return f"Predicted price for {address}, : {predicted_price}"
    




st.title("Real Estate Listings")
st.sidebar.header("Search Listings")

state_options = list(state_city_dict.keys())
default_state = state_options[0]
city_options = state_city_dict[default_state]
default_city = city_options[0]

selected_state = st.sidebar.selectbox('Select a state', options=state_options, index=0)
selected_city = st.sidebar.selectbox('Select a city', options=state_city_dict[selected_state], index=0)
selected_limit = st.sidebar.selectbox('Select how many listings', options=[100, 150, 200], index=0)

st.sidebar.header("Search")
search_button = st.sidebar.button("Search")

if search_button:
    property_listings = get_property_listings(selected_city, selected_state, selected_limit)
    st.write(property_listings)


real_estate_df = get_property_listings(selected_city, selected_state, selected_limit)
st.write(real_estate_df)
map_real_estate = create_map(real_estate_df)

st.write("Map of Real Estate Properties")
st_folium(map_real_estate)

st.header("KNN Regression Model")

address = st.text_input("Enter an address:")
if address:
    predicted_price = fit_knn(real_estate_df, address)
    st.write(predicted_price)
