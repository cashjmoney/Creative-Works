import pandas as pd
import folium
from folium.plugins import MarkerCluster

class MapVisualizer:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = None
        self.base_map = None

    def load_data(self):
        # Read the CSV file
        self.df = pd.read_csv(self.csv_path)
        
        # Inspect the columns and clean data
        if 'latitude' not in self.df.columns or 'longitude' not in self.df.columns:
            raise ValueError("CSV must contain 'latitude' and 'longitude' columns.")
        
        self.df['latitude'] = pd.to_numeric(self.df['latitude'], errors='coerce')
        self.df['longitude'] = pd.to_numeric(self.df['longitude'], errors='coerce')
        self.df.dropna(subset=['latitude', 'longitude'], inplace=True)
        print("Cleaned data:")
        print(self.df.head())

    def create_base_map(self):
        if self.df is not None and not self.df.empty:
            # Center the map around the mean latitude and longitude
            self.base_map = folium.Map(location=[self.df['latitude'].mean(), self.df['longitude'].mean()], zoom_start=12)
        else:
            raise ValueError("DataFrame is empty or not loaded correctly.")

    def add_markers(self):
        if self.df is not None and not self.df.empty:
            marker_cluster = MarkerCluster().add_to(self.base_map)
            for _, row in self.df.iterrows():
                try:
                    popup_text = (f"Name: {row['name']}             <br>"
                      f"Price: ${row['price']}<br>"
                      f"Reviews: {row['number_of_reviews']}<br>"
                       f"Reviews per Month: {row['reviews_per_month']}")
                     
                    folium.Marker(
                        location=[row['latitude'], row['longitude']],
                        icon=folium.Icon(color='blue', icon='info-sign'),
                        popup=popup_text
                    ).add_to(marker_cluster)
                except Exception as e:
                    print(f"Error adding marker: {e}")
        else:
            raise ValueError("No data available to add markers.")

    def save_map(self, output_html):
        try:
            if self.base_map is not None:
                self.base_map.save(output_html)
                print(f"Map saved to {output_html}")
            else:
                raise ValueError("Base map is not created.")
        except Exception as e:
            print(f"Error saving map: {e}")

    def visualize(self, output_html):
        try:
            self.load_data()
            self.create_base_map()
            self.add_markers()
            self.save_map(output_html)
        except Exception as e:
            print(f"Error during visualization: {e}")
        return self.save_map(output_html)
