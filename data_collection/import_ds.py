import csv
import requests
import pandas as pd


def import_training_datasets(city_details):
    '''
    Retrieve service request types and descriptions from static dataset 
    available on a website.

    Inputs:
        city_details: dictionary containing a city name, URL from which the 
        dataset can be downloaded, and specific columns containing pertinent
        training data

    Output: dataframe of all cities' training data
    '''
    training_columns = ['service_type', 'description']
    all_city_reqs = pd.DataFrame(columns = training_columns)
    df_list = [all_city_reqs]
    
    for city in city_details.keys():

        download = requests.get(city_details[city]['url'])

        # Continue if "success" response code
        if download.status_code == 200:

            decoded_dl = download.content.decode('utf-8')
            req_reader = csv.reader(decoded_dl.splitlines(), delimiter = ',')
            city_reqs = list(req_reader)

            city_df = pd.DataFrame(city_reqs[1:], columns = city_reqs[0])
            city_df = city_df[ city_details[city]['cols_to_keep'] ]
            city_df.columns = all_city_reqs.columns

            print(city)
            print(city_df.head())
            df_list.append(city_df)
        else:
            print("Request error...")
            return None
    

    all_city_reqs = pd.concat(df_list, ignore_index = True)
    return all_city_reqs


def go():
    city_details = {'Baton Rouge': {'cols_to_keep': ["TYPE", "COMMENTS"], 
                    'url': 'https://data.brla.gov/api/views/7ixm-mnvx/rows.csv?accessType=DOWNLOAD'},
                    'Cincinnati': {'cols_to_keep': ["SERVICE_NAME", "DESCRIPTION"], 
                    'url': 'https://data.cincinnati-oh.gov/api/views/4cjh-bm8b/rows.csv?accessType=DOWNLOAD'},
                    'Gainesville': {'cols_to_keep': ["Issue Type", "Description"], 
                    'url': 'https://data.cityofgainesville.org/api/views/78uv-94ar/rows.csv?accessType=DOWNLOAD'},
                    'New Orleans': {'cols_to_keep': ["issue_type","issue_description"], 
                    'url': 'https://data.nola.gov/api/views/3iz8-nghx/rows.csv?accessType=DOWNLOAD'}
                   }

    reqs = import_training_datasets(city_details)
    return reqs

if __name__ == "__main__":
    go()
