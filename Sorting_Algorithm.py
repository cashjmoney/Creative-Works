import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import math

class airbnb_sorting:
    def __init__(self, DataFrame_Info_as_Dict):
        self.df = DataFrame_Info_as_Dict

    def quicksort_price(self, arr=None):
        if arr is None:
            arr = self.df

        key = "price"

        if len(arr) <= 1:
            return arr

        pivot = arr[len(arr) // 2][key]
        left = [x for x in arr if x[key] < pivot]
        middle = [x for x in arr if x[key] == pivot]
        right = [x for x in arr if x[key] > pivot]

        return self.quicksort_price(left) + middle + self.quicksort_price(right)

    def mergesort_number_of_reviews(self, arr=None):
        if arr is None:
            arr = self.df

        key = "number_of_reviews"

        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]

        left_sorted = self.mergesort_number_of_reviews(left_half)
        right_sorted = self.mergesort_number_of_reviews(right_half)

        return self._merge(left_sorted, right_sorted, key)

    def mergesort_reviews_per_month(self, arr=None):
        if arr is None:
            arr = self.df

        key = "reviews_per_month"

        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]

        left_sorted = self.mergesort_reviews_per_month(left_half)
        right_sorted = self.mergesort_reviews_per_month(right_half)

        return self._merge(left_sorted, right_sorted, key)

    def _merge(self, left, right, key):
        sorted_array = []
        i = j = 0

        while i < len(left) and j < len(right):
            left_value = left[i][key] if pd.notna(left[i][key]) else 0 # this checks if cell in excell is empty (NaN) and replaces it with 0
            right_value = right[j][key] if pd.notna(right[j][key]) else 0

            if left_value < right_value:
                sorted_array.append(left[i])
                i += 1
            else:
                sorted_array.append(right[j])
                j += 1

        sorted_array.extend(left[i:])
        sorted_array.extend(right[j:])

        return sorted_array

    def price_range(self, start_price, end_price):
        quick_sorted_data = self.quicksort_price()

        filtered_data = [item for item in quick_sorted_data if start_price <= item['price'] <= end_price]

        filtered_df = pd.DataFrame(filtered_data)
        filtered_df.to_csv("filtered_price_data.csv", index=False)

    def number_of_reviews_range(self,start_num,end_num):
        merge_sorted_data = self.mergesort_number_of_reviews()

        filtered_data = [item for item in merge_sorted_data if start_num <= item['number_of_reviews'] <= end_num]

        filtered_df = pd.DataFrame(filtered_data)
        filtered_df.to_csv("filtered_number_of_reviews_data.csv", index=False)

    def reviews_per_month_range(self,start_num,end_num):
        merge_sorted_data = self.mergesort_number_of_reviews()

        filtered_data = [item for item in merge_sorted_data if start_num <= item['reviews_per_month'] <= end_num]

        filtered_df = pd.DataFrame(filtered_data)
        filtered_df.to_csv("filtered_reviews_per_month_data.csv", index=False)

def find_distance(lat1, long1, lat2, long2):
    # credit to https://en.wikipedia.org/wiki/Haversine_formula for the formula used to find the distance between points on a spehere
    r = 3959  # earth radius
    lat1 = lat1 * (math.pi / 180)
    lat2 = lat2 * (math.pi / 180)
    long1 = long1 * (math.pi / 180)
    long2 = long2 * (math.pi / 180)
    hav = (1 - math.cos(lat2 - lat1) + math.cos(lat1) * math.cos(lat2) * (1 - math.cos(long2 - long1))) / 2
    d = 2 * r * math.asin(math.sqrt(hav))
    return d


def sort_all(start_price, end_price, start_reviews, end_reviews, start_rpm, end_rpm,clicked_lat,clicked_long,distance):
    fields = [
        "id",
        "name",
        "host_id",
        "host_name",
        "neighbourhood_group",
        "neighbourhood",
        "latitude",
        "longitude",
        "room_type",
        "price",
        "minimum_nights",
        "number_of_reviews",
        "last_review",
        "reviews_per_month",
        "calculated_host_listings_count",
        "availability_365",
        "number_of_reviews_ltm",
        "city"
    ]

    dtype_dict = {
        "id": float,
        "name": str,
        "host_id": int,
        "host_name": str,
        "neighbourhood_group": str,
        "neighbourhood": str,
        "latitude": float,
        "longitude": float,
        "room_type": str,
        "price": float,
        "minimum_nights": int,
        "number_of_reviews": int,
        "last_review": str,
        "reviews_per_month": float,
        "calculated_host_listings_count": int,
        "availability_365": int,
        "number_of_reviews_ltm": int,
        "city": str
    }

    df = pd.read_csv('AB_US_2023.csv', names=fields, header=0, dtype=dtype_dict,
                     low_memory=False)  # reads data from csv
    # Convert DataFrame to list of dictionaries
    data_list = df.to_dict(orient='records')  # converts csv data to a dict
    sorted_data = airbnb_sorting(data_list)
    sorted_data.price_range(start_price, end_price)
    df = pd.read_csv('filtered_price_data.csv', names=fields, header=0, dtype=dtype_dict,
                     low_memory=False)  # reads data from csv
    # Convert DataFrame to list of dictionaries
    data_list = df.to_dict(orient='records')  # converts csv data to a dict
    sorted_data = airbnb_sorting(data_list)
    sorted_data.number_of_reviews_range(start_reviews, end_reviews)
    df = pd.read_csv('filtered_number_of_reviews_data.csv', names=fields, header=0, dtype=dtype_dict,
                     low_memory=False)  # reads data from csv
    data_list = df.to_dict(orient='records')  # converts csv data to a dict
    sorted_data = airbnb_sorting(data_list)
    sorted_data.reviews_per_month_range(start_rpm, end_rpm)
    df = pd.read_csv('filtered_reviews_per_month_data.csv', names=fields, header=0, dtype=dtype_dict,
                     low_memory=False)  # reads data from csv
    # Convert DataFrame to list of dictionaries
    data_list = df.to_dict(orient='records')  # converts csv data to a dict
    sorted_data = airbnb_sorting(data_list)
    quick_sorted_data=sorted_data.quicksort_price()
    filtered_data = []
    for item in quick_sorted_data:
        if find_distance(clicked_lat,clicked_long,item["latitude"],item["longitude"]) <distance:
            filtered_data.append(item)
    filtered_df = pd.DataFrame(filtered_data)
    filtered_df.to_csv("New.csv", index=False)

