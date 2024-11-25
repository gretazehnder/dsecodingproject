
import geopandas as gpd 
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from app_data_loading import st_load_data


#Loading data
data = st_load_data(r"C:\Users\greta\OneDrive\Desktop\GlobalLandTemperaturesByMajorCity.csv")

temp_ranges = data.groupby('City')['AverageTemperature'].apply(lambda x: np.ptp(x))
high_variance_cities = temp_ranges[temp_ranges > 15].index  # Adjust threshold as needed

#Setting app title and instructions
st.title("Global Temperature Change Visualization Over Time")
st.write("Explore the change in temperatures over time and identify cities with large temperature ranges.")

#Adding an year slider
year = st.slider("Select Year", int(data['Year'].min()), int(data['Year'].max()), step=1)

#Filtering data for the selected year
year_data = data[data['Year'] == year]

#Loading baseline city data (unique cities with coordinates) for consistent plotting
baseline_cities = data[['City', 'Latitude', 'Longitude']].drop_duplicates()

#Converting data to a GeoDataFrame
gdf_all_cities = gpd.GeoDataFrame(baseline_cities, geometry=gpd.points_from_xy(baseline_cities.Longitude, baseline_cities.Latitude))
gdf_year_data = gpd.GeoDataFrame(year_data, geometry=gpd.points_from_xy(year_data.Longitude, year_data.Latitude))
# creating points on a map for each city using longitude and latitude data.

#Loading a World map shapefile
world = gpd.read_file(r"C:\Users\greta\OneDrive\Desktop\nat.earth\ne_110m_admin_0_countries.shp")
# a shapefile is a file format for geographic data

fig, ax = plt.subplots(figsize=(12, 8)) #creating a blank figure (fig) with a specified size and an axis (ax) to draw on.
world.plot(ax=ax, color='lightgrey', edgecolor='darkgrey')  # World map with borders

#Plotting all of the cities in a light color
gdf_all_cities.plot(ax=ax, color='lightblue', markersize=20, alpha=0.3, edgecolor='black', label="All Cities")

#Plotting cities with temperature data for the selected year in a distinct color (blue)
gdf_year_data.plot(ax=ax, color='blue', markersize=20, alpha=0.5, edgecolor='black', label="Cities with Temp Data")

#Highlighting high variance cities in red with larger markers
high_variance_data = gdf_year_data[gdf_year_data['City'].isin(high_variance_cities)]#only selecting cities from the selected year's data (gdf_year_data) that are also in high_variance_cities.
high_variance_data.plot(ax=ax, color='red', markersize=50, alpha=0.7, edgecolor='black', label="High Temp Range Cities")

#Adding titles
plt.title(f"Temperature Distribution in Major Cities - {year}", fontsize=18, fontweight='bold', color='darkblue')
plt.xlabel("Longitude", fontsize=14)
plt.ylabel("Latitude", fontsize=14)

#Adding a legend and displaying the map
plt.legend()

st.pyplot(fig)



#Selecting a city to display time-series
selected_city = st.selectbox("Select a city to view historical temperature data:", data['City'].unique())

if selected_city:
    city_data = data[data['City'] == selected_city] #If the city is selected, the code filters data to include only rows for the chosen city.

    if not city_data.empty:
        # Grouping by year and calculating the average temperature 
        yearly_data = city_data.groupby('Year', as_index=False)['AverageTemperature'].mean()#as_index=False:We will need to plot Year as the x-axis (or access it as a column directly), so it is simpler if it remains a column rather than being an index.

        fig, ax = plt.subplots(figsize=(10, 6))

        # Plotting
        ax.plot(yearly_data['Year'], yearly_data['AverageTemperature'], 
                color='darkred', marker='o', linewidth=1, markersize=3)
        ax.set_title(f"Average Temperature Change Over Time in {selected_city}", 
                     fontsize=16, fontweight='bold', color='darkblue')
        ax.set_xlabel("Year", fontsize=14, color='gray')
        ax.set_ylabel("Average Temperature (°C)", fontsize=14, color='gray')

        # Adding a grid 
        ax.grid(True, linestyle='--', color='gray', alpha=0.7)
    
        # Showing the plot in Streamlit
    
        st.pyplot(fig)
    else:
        st.write(f"No data available for {selected_city}")

#SECOND PART OF THE PROJECT
#Setting starting and destination coordinates



start_city = "Peking"
end_city = "Los Angeles"


# Directly retrieving coordinates from baseline_cities
start_coords = tuple(baseline_cities[baseline_cities['City'] == start_city][['Latitude', 'Longitude']].values[0])
end_coords = tuple(baseline_cities[baseline_cities['City'] == end_city][['Latitude', 'Longitude']].values[0])

#Creating a filtered copy of the data for the selected period
route_data = year_data.copy()#route_data will be modified throughout the code, so we are creating a copy to avoid changing year_data directly.

#Defining the function to get the three closest cities to a given location
def get_nearest_cities(data, current_coords, num_cities=3):
    # Calculating euclidean distance 
    lat_diffs = data['Latitude'] - current_coords[0] #Subtracting the latitude of the current location (current_coords[0]) from the latitude of each city in the dataset. 
    lon_diffs = data['Longitude'] - current_coords[1]#same but with longitude
    data['Distance'] = np.sqrt(lat_diffs**2 + lon_diffs**2) #data['Distance']: stores the calculated distances as a new column
    nearby_cities = data.nsmallest(num_cities, 'Distance')
    return nearby_cities.sort_values(by='AverageTemperature', ascending=False)  # Sort by temperature

#Iteratively building the route
route = []
current_coords = start_coords

#Creating a loop to build the route
while np.sqrt((current_coords[0] - end_coords[0])**2 + (current_coords[1] - end_coords[1])**2) > 1: #checking if the > 1 unit away: if it is, the loop continues; otherwise, the traveler is considered "close enough" to Los Angeles, and the loop stops.
    nearby_cities = get_nearest_cities(route_data, current_coords) #Finding the three closest cities to current_coords and selecting the warmest one
    if nearby_cities.empty:
        st.write("No more cities within reach.")
        break
    next_city = nearby_cities.iloc[0]  # Warmest among the closest (choosing the first city in nearby_cities)
    route.append({'City': next_city['City'], 'Latitude': next_city['Latitude'], 'Longitude': next_city['Longitude']}) #Adding next_city to route with its name, latitude, and longitude
    current_coords = (next_city['Latitude'], next_city['Longitude']) # Updating current_coords to the location of next_city, moving us forward in the route.
    route_data = route_data[route_data['City'] != next_city['City']]  # Removing next_city from route_data to avoid revisiting it.

st.write("Route:", " → ".join([city['City'] for city in route]))

#Visualizing the route
if route:
    # Reusing the world shapefile from earlier
    fig, ax = plt.subplots(figsize=(12, 8))
    world.plot(ax=ax, color='lightgrey', edgecolor='darkgrey')
    
    # Extracting route coordinates: lats and longs lists store the route’s latitudes and longitudes
    lats = [start_coords[0]] + [city['Latitude'] for city in route] + [end_coords[0]]
    longs = [start_coords[1]] + [city['Longitude'] for city in route] + [end_coords[1]]
    
    # Plotting the route as lines connecting each city
    ax.plot(longs, lats, color='red', linewidth=2, label="Route Line")
    
    # Plotting each city as a point on the route
    ax.plot(longs, lats, 'bo', markersize=5)  # 'bo' makes blue points

    # Adding title and legend
    plt.title("Travel Route Visualization", fontsize=18, fontweight='bold', color= 'darkblue')
    plt.legend()
    
    # Displaying in Streamlit
    st.pyplot(fig)