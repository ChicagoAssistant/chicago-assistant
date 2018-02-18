import csv
import requests
import io
import pandas as pd
import os

def import_training_datasets(dataset_urls, save_to_filenames):
    '''
    Retrieve a static dataset (ex: CSV) from a website.

    Inputs:
        dataset_url: (str) URL from which the dataset can be downloaded
        save_to_filename: (str) .csv filename to save data pulled from URL

        Output: a dataframe
    '''
    all_city_reqs = []
    for data_url in dataset_urls:
        filename = save_to_filenames.pop(0)
        if not os.path.isfile(filename):
            #     with requests.Session() as sesh:
            #     download = sesh.get(dataset_url)
            #     decoded_content = download.content.decode('utf-8')
            download = requests.get(data_url)

            # Continue if "success" response code
            if download.status_code == 200:
                with open(filename, 'wb') as f:
                    # A chunk of 128 bytes
                    for chunk in download:
                        f.write(chunk)
                        # f.writelines(download.content)

                # df = pd.read_csv(io.StringIO(download.text))
                # df = pd.read_csv(decoded_content, header = 0)
                print()
                print(filename)
                df = pd.read_csv(filename, header = 0)
                print()
                print(df.head())
                all_city_reqs.append(df)

        else:
            print('There is already a file in this directory with that name.')

    return all_city_reqs

def go():
    req_urls = ['https://data.brla.gov/api/views/7ixm-mnvx/rows.csv?accessType=DOWNLOAD',
                'https://data.cincinnati-oh.gov/api/views/4cjh-bm8b/rows.csv?accessType=DOWNLOAD',
                'https://data.cityofgainesville.org/api/views/78uv-94ar/rows.csv?accessType=DOWNLOAD',
                'https://data.nola.gov/api/views/3iz8-nghx/rows.csv?accessType=DOWNLOAD']

    req_csvs = ['Baton_Rouge_svc_reqs_2016_to_pres.csv',
                'Cincinnati_svc_reqs_2015_to_pres.csv',
                'Gainesville_svc_reqs_2016_to_pres.csv',
                'New_Orleans_svc_reqs_2012_to_pres.csv']
    br, cinci, gainesville, nola = import_training_datasets(req_urls, req_csvs)
    return (br, cinci, gainesville, nola)

if __name__ == "__main__":
    go()
