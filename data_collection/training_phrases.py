#
# Functions and Code Snippets useful for extracting Training Phrases
#
# NOTE: Code not built for running as a single script,
#  Individual snippets need to be run as and when required, in conjunction
#  with Manual Review of Keywords and Phrases extracted as per practicality
#

import csv
import requests
import io
import argparse
import json
import string
import sys
import pandas as pd
from pandas import ExcelWriter
import os
import re
from stop_words import get_stop_words
import import_ds

# Ignore stop words and punctuations from descriptive text
## Generic list of Punctuations and Stop Words used from Python libraries
## Resource used: https://pypi.python.org/pypi/stop-words
PUNCTUATION = string.punctuation
STOP_WORDS = get_stop_words('english')


# Run the Import Datasets script to download 311 Open Data from 4 cities
#  - Cincinnati, Baton Rouge, Gainesville, New Orleans
# and compile it into a common Pandas DataFrame
SR_df = import_ds.go()


# Initial Data Exploration Scripts to find the most appropriate keywords to
#  use for identifying the relevant 311 Service Requests from the entire
#  datasets available, since each City uses a different phrase or format to
#  indicate a particular Service Request Type, sometimes even putting 
#  descriptive text in the Service_Type fields and alternatively using 
#  SR_numbers as the correct identifiers for the Service Type
SR_df[SR_df.service_type.str.strip(PUNCTUATION).str.lower().\
  str.contains('pothole')].service_type.str.strip().str.replace('"','').\
  str.lower().value_counts()

SR_df[SR_df.service_type.str.strip(PUNCTUATION).str.lower().\
  str.contains('road')].service_type.str.strip().str.replace('"','').\
  str.lower().value_counts()


SR_df[SR_df.service_type.str.strip(PUNCTUATION).str.lower().\
  str.contains('street light')].service_type.str.strip().str.replace('"','').\
  str.lower().value_counts()

SR_df[SR_df.service_type.str.strip(PUNCTUATION).str.lower().\
  str.contains('streetlight')].service_type.str.strip().str.replace('"','').\
  str.lower().value_counts()


SR_df[SR_df.service_type.str.strip(PUNCTUATION).str.lower().\
  str.contains('rodent')].service_type.str.strip().str.replace('"','').\
  str.lower().value_counts()

SR_df[SR_df.service_type.str.strip(PUNCTUATION).str.lower().\
  str.contains('rats')].service_type.str.strip().str.replace('"','').\
  str.lower().value_counts()


# Define Most Common Keywords found from the Initial Data Exploration
## Singular form of words are sufficient since str.contains() is used
keywords = {'pothole':['pothole','pot hole'], \
            'street_light':['street light','streetlight'], \
            'rodent_baiting':['rodent','rat']}


# Define the Service Request Type of interest,
## run below snippets for each Service Request Type separately
issue = 'pothole'
searchfor = '|'.join(keywords[issue])


# Manually Review Distribution & Pareto for Service Type contents
# Extract & Consider only natural language words, ignore numerals, 
#  special characters, punctuations, etc
SR_df[SR_df.service_type.str.strip(PUNCTUATION).str.lower().\
  str.contains(searchfor)].service_type.str.strip(PUNCTUATION).str.lower().\
  value_counts()


# Manually Review descriptive text being filtered to determine next steps
SR_df[SR_df.service_type.str.strip(PUNCTUATION).str.lower().\
  str.contains(searchfor)].description.str.strip(PUNCTUATION).str.lower().\
  value_counts()


# Extract Distribution of Words that occur in Service Request descriptions
#  and identify the Pareto to choose most suitable / most indicative words
#  which would be useful to train the DialogFlow algorithm
regex = re.compile('[^a-zA-Z ]')

pd.Series(' '.join(SR_df[SR_df.service_type.str.replace(regex,'').
  str.lower().str.contains(searchfor)].description.str.replace(regex,'').\
  str.lower()).split()).value_counts()

# Ignore Stop / Common English words which are agnostic to SR context
words = pd.Series(' '.join(SR_df[SR_df.service_type.str.replace(regex,'').
  str.lower().str.contains(searchfor)].description.str.replace(regex,'').\
  str.lower()).split())
words[-words.isin(STOP_WORDS)].value_counts()

# ..........................................................................#
# Manually Review Distribution & Pareto to choose relevant & meaningful words
# ..........................................................................#


def extract_phrases(row, k1, k2):
    '''
    Extract the n-grams from the Service Request Description based on the 
    keyword contained, combining "k1" words before "k2" words after the 
    particular keyword

    Inputs:
        row (Pandas DataFrame row): record/row on which function implemented
        k1 (int): Number of context words to be picked before the keyword
        k2 (int): Number of context words to be picked after the keyword

    Outputs:
        (string): String corresponding to the Training Phrase constructed 
            through an n-gram with keyword identified combined with k1 words
            before and k2 words after
    '''

    service_type = row['service_type'].replace('"','').lower()
    description_list = row['description'].replace('"','').lower().split()

    # Iterate over all Service Request Types
    for issue in keywords:
        
        # Check for each keyword corresponding to the particular Issue / SR
        if any(keyword in service_type for keyword in keywords[issue]):
            indices = [pos for pos, item in enumerate(description_list) \
                       if any(keyword in item for keyword in keywords[issue])]
            
            if len(indices) > 0:
                min_pos = max(0, indices[0]-k1)
                return issue + ' | ' + \
                        ' '.join(description_list[min_pos:(indices[0]+k2+1)])

    # Return blank if row not related to any SR Types, or if none of the 
    #  keywords are in description (generic descriptions agnostic of context)
    return ''


def Get_Training_Phrases(k1, k2, output_filename):
    '''
    Extract Training Phrases from the Available Dataset of 311 Service 
    Requests into an Excel Workbook which will be used for Manual Review

    Inputs:
        k1 (int): Number of context words to be picked before the keyword
        k2 (int): Number of context words to be picked after the keyword
        output_filename: filename/path for the Training Phrases Excel workbook

    Outputs:
        No specific outputs returned to the Command Prompt / Python Intepretor
        Function creates a fresh Excel workbook containing Training Phrases
    '''

    # Run the "Import_DS" Script to extract 311 Open DataSet from all cities
    # NOTE: Commented out to prevent Function to extract DataSet from scratch
    #  Recommended to extract DataSet separately once, and run the rest as is 
    '''
    SR_df = import_ds.go()
    '''

    # Call Function 'Extract_Phrases' on each row to extract Training Phrases
    SR_df['phrases']= SR_df.apply(lambda x: extract_phrases(x, k1, k2),axis=1)

    # Create a New "Training_Phrases" Excel workbook used for Manual Review
    writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')

    # Iterate over all Service Request Types & Export the Training Phrases and 
    #  Frequency Distribution into separate sheets for each Service Request
    for issue in keywords:

        train_phrases = SR_df.phrases[SR_df.phrases.str.contains(issue)].\
                                    value_counts().to_frame()
        train_phrases.to_excel(writer, sheet_name=issue)

    writer.save()
