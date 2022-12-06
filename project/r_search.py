import requests
import pandas as pd
import json

from buildfirebase import *


# find restaurants by keyword (food type)
# return restaurant's Latitude, Longitude, Name, Score, and Grade as list
# return result: [ .. ,  [Latitude, Longitude, Restaurant_Name, Score, Grade], .....  ]
def find_restaurant_by_type(keyword):
    restaurant_partition_urls = getPartitionLocations('/user/vincent/Restaurant.csv')

    final_df = pd.DataFrame()

    for url in restaurant_partition_urls:
        curr_partition = requests.get(url).json()

        for shop in curr_partition:

            curr_result = []

            if shop and type(shop) is dict:
                name = shop['facility_name']

                if name != None and keyword.lower() in name.lower():

                    final_df = pd.concat([final_df, pd.DataFrame([shop])], axis=0)

    return final_df


# find restaurants by score range (with min and max score limits)
# return restaurant's Latitude, Longtitude, Name, Score, and Grade as list
def find_restaurant_by_score(low, high):
    restaurant_partition_urls = getPartitionLocations('/user/vincent/Restaurant.csv')

    final_results = []

    for url in restaurant_partition_urls:
        curr_partition = requests.get(url).json()

        for shop in curr_partition:

            curr_result = []

            if shop and type(shop) is dict:
                score = shop['score']

                if score != None and score >= low and score <= high:
                    curr_result.append(shop['latitude'])
                    curr_result.append(shop['longitude'])
                    curr_result.append(shop['facility_name'])
                    curr_result.append(shop['score'])
                    curr_result.append(shop['grade'])

                    final_results.append(curr_result)

    if len(final_results) == 0:
        print("No Restaurant Found for the Score Range You Searched !")
        return

    return final_results


# Analysis: find number of restaurants within the score range
def find_restaurant_number(low, high):
    restaurant_partition_urls = getPartitionLocations('/user/vincent/Restaurant.csv')

    final_results = []

    for url in restaurant_partition_urls:
        curr_partition = requests.get(url).json()

        for shop in curr_partition:

            curr_result = []

            if shop and type(shop) is dict:
                score = shop['score']

                if score != None and score >= low and score <= high:
                    curr_result.append(shop['latitude'])
                    curr_result.append(shop['longitude'])
                    curr_result.append(shop['facility_name'])
                    curr_result.append(shop['score'])
                    curr_result.append(shop['grade'])

                    final_results.append(curr_result)

    return len(final_results)
