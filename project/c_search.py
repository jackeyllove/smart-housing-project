import requests
import pandas as pd
import json

from buildfirebase import *


# search crime by key word: like 'vehicle', 'weapon', 'house', 'robber'
# return crime's Latitude, Longitude, Description, Date as list
def find_crime_by_keyword(keyword):
    crime_partition_urls = getPartitionLocations('/user/vincent/Crime.csv')  # find the urls for all partitions

    # final_results = [] # contains all valid crime cases
    final_df = pd.DataFrame()

    # distributed: find from each partition
    for url in crime_partition_urls:
        curr_partition = requests.get(url).json()

        # analyze each crime
        for case in curr_partition:

            # if keyword appears in crime description, this is one of the results
            if case and type(case) is dict:
                description = case['Crm Cd Desc']

                if description != None and keyword.lower() in description.lower():
                    final_df = pd.concat([final_df, pd.DataFrame([case])], axis=0)

    return final_df


# search crime by street name: like 'wilshire', 'vermont'
# return crime's Latitude, Longitude, Description, Date as list
def find_crime_by_street_name(street):
    crime_partition_urls = getPartitionLocations('/user/vincent/Crime.csv')  # find the urls for all partitions

    final_results = []  # contains all valid crime cases

    # distributed: find from each partition
    for url in crime_partition_urls:
        curr_partition = requests.get(url).json()

        # analyze each crime
        for case in curr_partition:

            curr_result = []  # contains [Latitude, Longitude, Description, Date]

            # if keyword appears in crime description, this is one of the results
            if case and type(case) is dict:
                description = case['LOCATION']

                if description != None and street.lower() in description.lower():
                    curr_result.append(case['LAT'])
                    curr_result.append(case['LON'])
                    curr_result.append(case['Crm Cd Desc'])
                    curr_result.append(case['DATE OCC'])

                    # add current case to the final results
                    final_results.append(curr_result)

    if (len(final_results) == 0):
        print("No Crime Case Found for the Street You Searched!")
        return

    return final_results


# Analysis the occurances / frequency of different types of crime
def find_crime_frequency(keyword):
    crime_partition_urls = getPartitionLocations('/user/vincent/Crime.csv')  # find the urls for all partitions

    final_results = []  # contains all valid crime cases

    # distributed: find from each partition
    for url in crime_partition_urls:
        curr_partition = requests.get(url).json()

        # analyze each crime
        for case in curr_partition:

            curr_result = []  # contains [Latitude, Longitude, Description, Date]

            # if keyword appears in crime description, this is one of the results
            if case and type(case) is dict:
                description = case['Crm Cd Desc']

                if description != None and keyword.lower() in description.lower():
                    curr_result.append(case['LAT'])
                    curr_result.append(case['LON'])
                    curr_result.append(case['Crm Cd Desc'])
                    curr_result.append(case['DATE OCC'])

                    # add current case to the final results
                    final_results.append(curr_result)

    return len(final_results)
