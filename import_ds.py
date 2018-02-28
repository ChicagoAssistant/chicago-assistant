import csv
import requests
import io
import pandas as pd
import os


def import_training_datasets(dataset_urls, req_cities, cols_to_keep):
    '''
    Retrieve a static dataset (ex: CSV) from a website.

    Inputs:
        dataset_url: (str) URL from which the dataset can be downloaded
        req_cities: (str) city for which to pull CSV from URL
        cols_to_keep: (dictionary) specific columns containing pertinent
        training data

        Output: a dataframe
    '''
    training_columns = ['service_type', 'description']
    all_city_reqs = pd.DataFrame(columns = training_columns)
    df_list = []
    for data_url in dataset_urls:
        filename = req_cities.pop(0)
        download = requests.get(data_url)

        # Continue if "success" response code
        if download.status_code == 200:

            decoded_dl = download.content.decode('utf-8')
            req_reader = csv.reader(decoded_dl.splitlines(), delimiter = ',')
            city_reqs = list(req_reader)

            city_df = pd.DataFrame(city_reqs[1:], columns = city_reqs[0])
            city_df = city_df[cols_to_keep[filename]]
            city_df.columns = all_city_reqs.columns

            print(filename)
            print(city_df.head())
            df_list.append(city_df)
    all_city_reqs = all_city_reqs.concat(df_list, ignore_index = True)

    return all_city_reqs

def go():
    req_urls = ['https://data.brla.gov/api/views/7ixm-mnvx/rows.csv?accessType=DOWNLOAD',
                'https://data.cincinnati-oh.gov/api/views/4cjh-bm8b/rows.csv?accessType=DOWNLOAD',
                'https://data.cityofgainesville.org/api/views/78uv-94ar/rows.csv?accessType=DOWNLOAD',
                'https://data.nola.gov/api/views/3iz8-nghx/rows.csv?accessType=DOWNLOAD']

    req_cities = ['Baton_Rouge',
                'Cincinnati',
                'Gainesville',
                'New_Orleans']

    cols_to_keep = {'Baton_Rouge': ["TYPE", "COMMENTS"],
                   'Cincinnati': ["SERVICE_NAME", "DESCRIPTION"],
                   'Gainesville': ["Issue Type", "Description"],
                   'New_Orleans': ["issue_type","issue_description"]}

    reqs = import_training_datasets(req_urls, req_cities, cols_to_keep)
    return reqs

if __name__ == "__main__":
    go()
