# Map Visualizer

This project provides a Python class for visualizing Airbnb data from a CSV file on a Folium map. The `MapVisualizer` class allows users to filter listings based on price, reviews, and location, and displays the filtered results on an interactive map.

## Features

- **Dynamic Map Visualization**: Interactive map display using Folium, with support for dynamic marker placement and clustering.
- **Search Functionality**: Search for locations using Geopy's Nominatim API.
- **Filter Airbnb Listings**: Filter data by price range, number of reviews, and reviews per month.
- **Custom Radius Filtering**: Filter listings based on distance from a selected point.
- **Map Click Handling**: Capture latitude and longitude from map clicks.

## Getting Started

## Usage Instructions

### Prerequisites

- Python 3.x
- GeoPandas
- Folium
- Geopy
- Pandas
- Shapely
- NiceGUI

### Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/cashjmoney/Creative-Works/niceGui.git
    cd niceGui
    ```

2. **Install dependencies**:

    ```bash
    pip install geopandas folium geopy pandas shapely nicegui
    ```

3. **Download the Airbnb dataset**:

    Ensure you have the `AB_US_2023.csv` file in your project directory. If you don't have it, you can download it from [here](https://www.kaggle.com/datasets/kritikseth/us-airbnb-open-data?select=AB_US_2023.csv) (Note: Ensure to match the dataset structure as expected by the code).

### Usage

1. **Create a Python script** (e.g., `niceGui.py`) with the following content:

    ```python
    from new_code import sort_all
    from nicegui import ui
    from geopy.geocoders import Nominatim
    import pandas as pd
    import geopandas as gpd
    import folium
    from shapely.geometry import Point
    from marker import MapVisualizer
    import webbrowser  # Importing webbrowser to open links

    # Initialize Nominatim API
    geolocator = Nominatim(user_agent="my_updated_geocoding_app")

    # Define the CSS for the layout
    css = """
    #map_container {
        position: absolute;
        top: 20px;
        left: 20px;
        width: 80%;
        height: 70vh;
        z-index: 1;
    }
    .centered_title {
        position: absolute;
        bottom: 40px;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 4em;
        font-weight: bold;
        opacity: 1;
        text-align: center;
        color: #000;
        z-index: 1;
    }
    .search_bar, .price_bar, .button, .finalbutton {
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        width: 60%;
        padding: 10px;
        box-sizing: border-box;
        border: 2px solid #ccc;
        border-radius: 7px;
        font-size: 2em;
        z-index: 2;
    }
    .result {
        position: absolute;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        width: 60%;
        font-size: 1.5em;
        text-align: center;
        color: #000;
        z-index: 2;
    }
    """

    # Add the CSS to the head of the document
    ui.add_head_html(f'<style>{css}</style>')

    # Create the UI elements
    min_value = 0
    max_value = 0
    min_price = 0
    max_price = 0
    x_cord = 0
    y_cord = 0
    min_review_per_month = 0
    max_review_per_month = 0
    min_review_overall = 0
    max_review_overall = 0
    radius = 0
    label_state = None
    label_price = None
    button = None
    min_max_review = None
    min_max_range = None
    min_max_review_overall = None
    current_map_view = None
    search_b = None
    location = None
    label = ui.label('Where to?')
    label.classes('centered_title')
    search_b = ui.input(label='Search', placeholder='Search...')
    search_b.classes('search_bar')
    result_label = ui.label('')
    result_label.classes('result')
    location = geolocator.geocode("Nebraska")
    current_map_view = ui.leaflet(center=(location.latitude, location.longitude), zoom=4)
    current_map_view.style('height: 75vh; width: 100%;')  # Adjust the map's size

    df = None

    async def handle_search_state(e):
        global current_map_view, min_value, max_value, location, df
        query = str(search_b.value)  # Explicitly convert to string
        location = geolocator.geocode(query)
        if current_map_view:
            current_map_view.delete()
        if location:
            current_map_view = ui.leaflet(center=(location.latitude, location.longitude), zoom=8)
            current_map_view.style('height: 75vh; width: 100%;')  # Adjust the map's size

        if query:
            search_b.delete()
            label.delete()
            label_price = ui.label('Price?')
            label_price.classes('centered_title')
            with ui.row():
                button = ui.button('Enter', on_click=(lambda: ui.notify('Filter Submitted')))
                button.classes('button')
                min_max_range = ui.range(min=0, max=10000, value={'min': 20, 'max': 80}).props('label-always snap label-color="secondary" right-label-text-color="black"')
                min_max_range.classes('price_bar')  
                min_max_range.on('change', handle_search)  
                await button.clicked()
                min_price = min_value
                max_price = max_value
                label_price.delete()
                min_max_range.delete()
                
                label_price = ui.label('Reviews Per Month?')
                label_price.classes('centered_title')
                min_max_review = ui.range(min=0.01, max=101, value={'min': 0.01, 'max': 20}).props('label-always snap label-color="secondary" right-label-text-color="black"')
                min_max_review.classes('price_bar')
                min_max_review.on('change', handle_search)
                await button.clicked()
                min_review_per_month = min_value
                max_review_per_month = max_value
                
                label_price.delete()
                min_max_review.delete()
                label_price = ui.label('Overall Review?')
                label_price.classes('centered_title')
                min_max_review_overall = ui.range(min=0, max=1314, value={'min': 0, 'max': 100}).props('label-always snap label-color="secondary" right-label-text-color="black"')
                min_max_review_overall.classes('price_bar')
                min_max_review_overall.on('change', handle_search)
                await button.clicked()
                min_review_overall = min_value
                max_review_overall = max_value
                
                label_price.delete()
                min_max_review_overall.delete()
                label_price = ui.label('Radius?')
                label_price.classes('centered_title')
                slider = ui.slider(min=0, max=100, value=50).props('label-always snap label-color="secondary" right-label-text-color="black"')
                ui.label().bind_text_from(slider, 'value')
                slider.classes('price_bar')
                slider.on('change', handle_search_r)
                await button.clicked()
                radius = max_value
                
                label_price.delete()
                slider.delete()
                label_price = ui.label('Click Area To Search')
                label_price.classes('centered_title')
                current_map_view.on('map-click', handle_click)
                await button.clicked()
                button.clear()
                sort_all(min_price, max_price, min_review_overall, max_review_overall, min_review_per_month, max_review_per_month, x_cord, y_cord, radius)

                df = pd.read_csv('New.csv')
                for _, row in df.iterrows():
                    current_map_view.marker(latlng=(row['latitude'], row['longitude']))
                visualizer = MapVisualizer('New.csv')
                visualizer.visualize('mapp.html')
                webbrowser.open('mapp.html')  # Using webbrowser to open the map visualization

            return location

    def handle_search(e): 
        global min_value, max_value
        min_value = e.args.get('min', None)
        max_value = e.args.get('max', None)

    def handle_search_r(e): 
        global max_value
        max_value = e.args

    def handle_click(e):
        global x_cord, y_cord
        x_cord = e.args['latlng']['lat']
        y_cord = e.args['latlng']['lng']  
        current_map_view.marker(latlng=(x_cord, y_cord))

    # Bind the search input to the handle_search function
    search_b.on('change', handle_search_state)

   print("Running UI...")  # Debug print
   ui.run()
    ```

2.****Download the other files within the repository **


3. **Run the script**:

    ```bash
    python niceGui.py
    ```

4. **Interact with the UI**:

    - **Search for a Location**: Enter the location you want to search in the search bar and press Enter.
    - **Filter Listings by Price**: Adjust the price range slider and press the Enter button.
    - **Filter Listings by Reviews per Month**: Adjust the reviews per month range slider and press the Enter button.
    - **Filter Listings by Overall Reviews**: Adjust the overall reviews range slider and press the Enter button.
    - **Select Radius for Filtering**: Adjust the radius slider and press the Enter button.
    - **Click on the Map**: Click on the map to set a specific point for the search.Press Enter afterwards
    - **View(document should pop up)
