import urllib.parse
import requests
import os
import bs4
import pandas as pd
import csv
import queue
import re
from datetime import datetime

KC_URL = 'https://data.kcmo.org/api/views/7at3-sxhp/rows.csv?accessType=DOWNLOAD'

def import_kc(kc_url):
    '''
    Create pandas data frame from list of 500,000 Kansas City service requests
    Inputs:
        - kc_url (str): URL from which to download CSV of historical Kansas 
            City service request data 
    Outputs:
        - kc_requests (dataframe): dataframe of CSV data

    Attribution: GET request decoding and reformatting (lines 33-36) follow
                 example provided on StackOverflow "Use python requests to
                 download CSV:" (https://stackoverflow.com/questions/35371043/use-python-requests-to-download-csv)
    '''
    kc_cols_to_keep = ['CASE ID','REQUEST TYPE', 'CATEGORY', 'TYPE','CASE URL']

    download = requests.get(kc_url)
    
    # Continue if "success" response code
    if download.status_code == 200:
        decoded_dl = download.content.decode('utf-8')
        req_reader = csv.reader(decoded_dl.splitlines(), delimiter = ',')
        kc_reqs = list(req_reader)

        # create dataframe
        kc_requests = pd.DataFrame(kc_reqs[1:], columns = kc_reqs[0])
        kc_requests = kc_requests[kc_requests["REQUEST TYPE"].str.lower().str.contains(" rat|rodent|mouse| pot | hole |pothole|potholes|street light|streetlight|light out")]
        kc_requests = kc_requests[kc_cols_to_keep]
        
        # format dataframe
        for col_name in ["REQUEST TYPE", "CATEGORY", "TYPE"]:
            kc_requests[col_name] = kc_requests[col_name].astype("category")
       
        # remove rows with no URLs to scrape for text descriptions
        kc_requests.dropna(subset=["CASE URL"], inplace = True)
        
        # add blank column to store comments found via webscraping
        kc_requests['COMMENT_TEXT'] = pd.Series()
        kc_requests.set_index('CASE ID', inplace = True)

        return kc_requests



def queue_kc_links(kc_link, kc_queue, visited_set):
    '''
    Add URLs that meet a set of criteria (absolute URLS without fragments in a 
    given domain) and have not already been visited to a queue of URLs to visit

    Inputs:
        - kc_link (string): a URL to evaluate and follow
        - kc_queue (queue): a queue of links to visit and from which to pull 
            raw text comments 
        - visited_set (set): a set of links that have already been evaluated 
            and/ or visited
    '''
    # get request object from case description link url
    if (kc_link == ''):
        kc_req = None

    elif urllib.parse.urlparse(kc_link).netloc == '':
        kc_req = None

    else:
        # check if link is an actual URL (no @s, emails) within correct domain
        limiting_domain = "webfusion.kcmo.org"
        link_approval = is_url_ok_to_follow(kc_link, limiting_domain)

        if link_approval:
            try:
                 kc_req = requests.get(kc_link)
                 
                 if kc_req.status_code == 404 or kc_req.status_code == 403:
                     print("404 error", c_req.status_code)
                     kc_req = None

            except Exception as e:
                print("link_approval exception error:", e)
                kc_req = None
        else:
            kc_req = None

        if kc_req:
            # print("Request object created:", kc_req.url)
            abs_url = convert_if_relative_url(kc_link, kc_req.url)
            clean_link, frag = urllib.parse.urldefrag(abs_url)

            if clean_link not in visited_set:
                # print("New clean link:", clean_link)
                kc_queue.put(clean_link)


def kc_soup(clean_link, visited_set):
    '''

    '''
    # get read request from case URL description link
    if clean_link not in visited_set:
        clean_req = requests.get(clean_link)

        if clean_req and (clean_req.url not in visited_set):
            try:
                soup_string = clean_req.text.encode('iso-8859-1')
                visited_set.add(clean_req.url)
            
            except Exception:
                print('read failed: ' + clean_req.url)
                soup_string =  None
                visited_set.add(clean_req.url)

            if soup_string:
                case_soup = bs4.BeautifulSoup(soup_string, "html5lib")
                return case_soup



def pull_comments(case_soup, case_df):
    '''
    Parse a Beautiful Soup object for specific tags holding raw text 
    descriptions of service requests and add to a dataframe

    Inputs:
        - case_soup (BeautifulSoup object): a URL's HTML content
        - case_df (dataframe): a dataframe holding Kansas City service request
            data to which to add raw text comments
    '''
    b_tag = case_soup.find('b', text=re.compile(r'Case ID:'))
    desc = case_soup.find('rc_descrlong')
    
    if b_tag and desc:
        case_num = int(b_tag.next_sibling)
        comments = desc.text
        
        if not re.match("^.*(dupe|duplicate|test).*$", comments):
            case_df["COMMENT_TEXT"].loc[case_num] = comments


def convert_if_relative_url(current_url, new_url):
    '''
    Determine whether new_url is a relative URL and if so, use the
    current_url to determine the path and create a new absolute
    URL.  Will add the protocol, if that is all that is missing.

    Inputs:
        current_url: absolute URL
        new_url:

    Outputs:
        new absolute URL or None, if cannot determine that
        new_url is a relative URL.

    Attribution: Part of utility code written by Anne Rogers of the
    University of Chicago, inspired by an assignment written by
    Mari Hearst at UC Berkeley
    '''
    if new_url == "" or urllib.parse.urlparse(current_url).netloc == "":
        return None

    if urllib.parse.urlparse(current_url).netloc != "":
        return new_url

    parsed_url = urllib.parse.urlparse(new_url)
    path_parts = parsed_url.path.split("/")

    if len(path_parts) == 0:
        return None

    ext = path_parts[0][-4:]
    if ext in [".edu", ".org", ".com", ".net"]:
        return "http://" + new_url
    elif new_url[:3] == "www":
        return "http://" + new_path
    else:
        return urllib.parse.urljoin(current_url, new_url)



def is_url_ok_to_follow(url, limiting_domain):
    '''
    Attribution: Part of utility code written by Anne Rogers of the
    University of Chicago, inspired by an assignment written by
    Mari Hearst at UC Berkeley

    Inputs:
        url: absolute URL
        limiting domain: domain name

    Outputs:
        Returns True if the protocol for the URL is HTTP, the domain
        is in the limiting domain, and the path is either a directory
        or a file that has no extension or ends in .html--URLs
        that include an "@" are not OK to follow.
    '''
    if "mailto:" in url:
        print("email address error")
        return False

    if "@" in url:
        print("@ sign error")
        return False

    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme != "http" and parsed_url.scheme != "https":
        print("http/ https error")
        return False

    if parsed_url.netloc == "":
        print("netloc error")
        return False

    if parsed_url.fragment != "":
        print("fragment error")
        return False

    loc = parsed_url.netloc
    ld = len(limiting_domain)
    trunc_loc = loc[-(ld+1):]
    if not (limiting_domain == loc or (trunc_loc == "." + limiting_domain)):
        print("loc error")
        return False

    # check for correct extension
    (filename, ext) = os.path.splitext(parsed_url.path)
    return (ext == "" or ext == ".cfm")


def go():
    '''
    Crawl Kansas City URLs and generate a pandas dataframe of service request
    details.

    Outputs: (dataframe) a pandas dataframe of 311 service request details
             including raw text comments
    '''
    kc_df = import_kc(KC_URL)
    max_pages = kc_df.shape[0]

    # initialize queue to hold links to scrape
    kc_queue = queue.Queue()

    # initialize set to check whether a link has been visited
    visited_set = set()

    # initialize counter for pages visited
    pages_visited = 0

    for link in kc_df["CASE URL"]:
        queue_kc_links(link, kc_queue, visited_set)

    while not kc_queue.empty() and (pages_visited <= max_pages):
        case_url = kc_queue.get()
        case_soup = kc_soup(case_url, visited_set)

        if case_soup:
            # if soup was created (URL was ok to follow), add one to page
            # counter and add comments on page to case dataframe
            pages_visited += 1
            pull_comments(case_soup, kc_df)

    print("{}: formatting...".format(datetime.now()))
    kc_df.dropna(axis = 0, how = 'any', subset = ["COMMENT_TEXT"], inplace = True)
    
    # drop records unrelated to service request types in question
    kc_df = kc_df[kc_df["COMMENT_TEXT"].str.contains("rat | mouse | pot | hole | pothole | potholes | light | streetlight | streetlights")]
    kc_df = kc_df[["REQUEST TYPE", "COMMENTS"]]

    return kc_df


def chicago_df(chi_csv):
    '''
    From a CSV file of service request data, create pandas dataframe and filter 
    for service request type and raw text columns corresponding to specific 
    service request types.

    Inputs:
        - chi_csv (CSV file): a CSV containing raw text data from service 
            requests in the city of Chicago
    Outputs:
        - chi (dataframe): pandas dataframe containing service request type
            and comments for specific service request types
    '''
    chi = pd.read_excel(chi_csv, sheet_name=0) 
    chi2 = pd.read_excel(chi_csv, sheet_name=1)
    chi = chi.append(chi2)
    chi = chi[chi["Comments"].str.contains("rat | mouse | pot | hole | pothole | potholes | light | streetlight | streetlights")]
    chi = chi[['SR Type Description', 'Comments']]

    return chi


if __name__ == "__main__":
    go()
    chicago_df('Open311SRs.xls')
