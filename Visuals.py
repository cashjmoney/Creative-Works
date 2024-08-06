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
    top: 20px;       /* Adjust as needed */
    left: 20px;      /* Adjust as needed */
    width: 80%;      /* Adjust the width */
    height: 70vh;    /* Adjust the height */
    z-index: 1;      /* Ensure it's below other elements if needed */
}
.centered_title {
    position: absolute;
    bottom: 40px;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 4em;       /* Increase font size */
    font-weight: bold;    /* Make the font bolder */
    opacity: 1;           /* Reduce transparency (0 is fully transparent, 1 is fully opaque) */
    text-align: center;
    color: #000;          /* Adjust text color as needed */
    z-index: 1;           /* Ensure it is above other content */
}

.search_bar {
    position: absolute;
    bottom: 10px;  /* Position the search bar at the bottom of the map */
    left: 50%;
    transform: translateX(-50%);  /* Center it horizontally */
    width: 60%;           /* Adjust the width of the search bar */
    padding: 10px;        /* Add padding for better appearance */
    box-sizing: border-box; /* Include padding in the width calculation */
    border: 2px solid #ccc; /* Add border */
    border-radius: 7px;   /* Rounded corners */
    font-size: 2em;       /* Adjust font size */
    z-index: 2;           /* Ensure it is above the map */
}
.price_bar {
    position: absolute;
    bottom: 10px;  /* Position the search bar at the bottom of the map */
    left: 50%;
    transform: translateX(-50%);  /* Center it horizontally */
    width: 50%;           /* Adjust the width of the search bar */
    padding: 10px;        /* Add padding for better appearance */
    box-sizing: border-box; /* Include padding in the width calculation */
    border: 2px solid #ccc; /* Add border */
    border-radius: 7px;   /* Rounded corners */
    font-size: 2em;       /* Adjust font size */
    z-index: 2;           /* Ensure it is above the map */
}
.button {
    position: absolute;
    bottom: 10px;  /* Position the search bar at the bottom of the map */
    left: 80%;
    transform: translateX(-50%);  /* Center it horizontally */
    width: 10%;           /* Adjust the width of the search bar */
    padding: 10px;        /* Add padding for better appearance */
    box-sizing: border-box; /* Include padding in the width calculation */
    border: 2px solid #ccc; /* Add border */
    border-radius: 7px;   /* Rounded corners */
    font-size: 2em;       /* Adjust font size */
    z-index: 2;           /* Ensure it is above the map */
}
.finalbutton {
    position: absolute;
    bottom: 10px;  /* Position the search bar at the bottom of the map */
    left: 80%;
    transform: translateX(-50%);  /* Center it horizontally */
    width: 10%;           /* Adjust the width of the search bar */
    padding: 10px;        /* Add padding for better appearance */
    box-sizing: border-box; /* Include padding in the width calculation */
    border: 2px solid #ccc; /* Add border */
    border-radius: 7px;   /* Rounded corners */
    font-size: 2em;       /* Adjust font size */
    z-index: 3;           /* Ensure it is above the map */
}
    
.result {
    position: absolute;
    top: 10px;  /* Position result at the top of the map */
    left: 50%;
    transform: translateX(-50%);
    width: 60%;  /* Adjust width to fit the search bar */
    font-size: 1.5em;     /* Adjust font size */
    text-align: center;
    color: #000;          /* Adjust text color as needed */
    z-index: 2;           /* Ensure it is above the map */
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
raduis = 0
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
    print("Search triggered")  # Debug print
    query = str(search_b.value)  # Explicitly convert to string
    print(f"Query: {query}")  # Debug print
    
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
            print(min_value)
            print(max_value)
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
            print(min_value)
            print(max_value)
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
            print(min_value)
            print(max_value)
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
            raduis = max_value
            print(raduis)
            
            label_price.delete()
            slider.delete()
            label_price = ui.label('Click Area To Search')
            label_price.classes('centered_title')
            current_map_view.on('map-click', handle_click)
            await button.clicked()
            button.clear()
            sort_all(90,100,10,20,1,20,40.54518,-74.15356, 100)

           #sort_all(min_price, max_price, min_review_overall, max_review_overall, min_review_per_month, max_review_per_month, x_cord, y_cord, raduis)

            df = pd.read_csv('New.csv')
            for _, row in df.iterrows():
                current_map_view.marker(latlng=(row['latitude'], row['longitude']))
            visualizer = MapVisualizer('New.csv')
            print("doing it")
            visualizer.visualize('mapp.html')
            webbrowser.open('mapp.html')  # Using webbrowser to open the map visualization

        return location

def handle_search(e): 
    global min_value, max_value
    print(f'Event args: {e.args}')  # Print the entire event arguments to inspect the structure
    
    min_value = e.args.get('min', None)
    max_value = e.args.get('max', None)

def handle_search_r(e): 
    global max_value
    print(f'Event args: {e.args}')  # Print the entire event arguments to inspect the structure
    
    max_value = e.args

def handle_click(e):
    global x_cord, y_cord
    x_cord = e.args['latlng']['lat']
    y_cord = e.args['latlng']['lng']  
    print(x_cord)
    print(y_cord)
    current_map_view.marker(latlng=(x_cord, y_cord))

# Bind the search input to the handle_search function
search_b.on('change', handle_search_state)
print("d")

print("Running UI...")  # Debug print
ui.run()
