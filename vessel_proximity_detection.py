import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import plotly.express as px
from itertools import combinations

# Function to find vessel proximity events using Geopandas
def find_vessel_proximity_geopandas(data, threshold_distance=1.0):
    results = []
    
    # Convert the timestamp column to datetime
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    
    # Create a GeoDataFrame with Points
    gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.lon, data.lat))
    
    # Set the CRS (Coordinate Reference System) to WGS84 (EPSG:4326)
    gdf.set_crs(epsg=4326, inplace=True)
    
    # Iterate through the dataset grouped by timestamp
    for timestamp, group in gdf.groupby('timestamp'):
        if len(group) < 2:
            continue
            
        # Get all combinations of vessel pairs
        vessel_pairs = list(combinations(group.index, 2))
        
        for i, j in vessel_pairs:
            point1, mmsi1 = group.loc[i, ['geometry', 'mmsi']]
            point2, mmsi2 = group.loc[j, ['geometry', 'mmsi']]
            
            # Calculate the distance between the vessels in kilometers
            distance = point1.distance(point2) * 100  # Geopandas returns distance in degrees, convert to kilometers
            
            # If the distance is within the threshold, record the event
            if distance <= threshold_distance:
                results.append({
                    'mmsi': mmsi1,
                    'vessel_proximity': mmsi2,
                    'timestamp': timestamp
                })
                results.append({
                    'mmsi': mmsi2,
                    'vessel_proximity': mmsi1,
                    'timestamp': timestamp
                })
    
    # Convert the results to a DataFrame
    proximity_df = pd.DataFrame(results)
    
    # Group by mmsi and timestamp to aggregate vessel proximity lists
    proximity_df = proximity_df.groupby(['mmsi', 'timestamp'])['vessel_proximity'].apply(list).reset_index()
    
    return proximity_df

# Function to visualize vessel proximity events using Matplotlib
def plot_proximity_events(gdf):
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(ax=ax, color='blue', markersize=5)
    plt.title("Vessel Positions and Proximity Events")
    plt.show()

# Function to visualize vessel proximity events using Plotly
def plot_proximity_events_plotly(gdf):
    fig = px.scatter_geo(gdf, lat=gdf.geometry.y, lon=gdf.geometry.x, color='mmsi', hover_name='mmsi',
                         title='Vessel Positions and Proximity Events')
    fig.show()

# Main execution function
def main(file_path):
    # Load the provided CSV file
    data = pd.read_csv(file_path)
    
    # Find proximity events using Geopandas
    proximity_events_df = find_vessel_proximity_geopandas(data)
    
    # Save the results to a new CSV file
    output_file = file_path.replace('.csv', '_proximity_events.csv')
    proximity_events_df.to_csv(output_file, index=False)
    print(f"Proximity events saved to {output_file}")
    
    # Create a GeoDataFrame for plotting
    gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.lon, data.lat))
    gdf.set_crs(epsg=4326, inplace=True)
    
    # Plot using Matplotlib
    plot_proximity_events(gdf)
    
    # Plot using Plotly
    plot_proximity_events_plotly(gdf)
# Run the main function when the script is executed
if __name__ == "__main__":
    # Specify the path to your input CSV file here
    file_path = 'C:\\Users\\iamak\\Desktop\\MyProject\\sample_data.csv'
    main(file_path)
