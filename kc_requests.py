import urllib.parse
import requests
import os
import bs4
import pandas as pd
import csv
import queue
import re

KC_URL = 'https://data.kcmo.org/api/views/7at3-sxhp/rows.csv?accessType=DOWNLOAD'

def import_kc(kc_url):
    '''
    Create pandas data frame from list of Kansas City service requests
    '''
    kc_cols_to_keep = ['CASE ID','SOURCE', 'REQUEST TYPE', 'CATEGORY', 'TYPE',
                       'CREATION DATE', 'CREATION TIME', 'ADDRESS WITH GEOCODE', 
                       'ZIP CODE', 'NEIGHBORHOOD', 'LATITUDE', 'LONGITUDE', 
                       'CASE URL']

    download = requests.get(kc_url)

    # Continue if "success" response code
    if download.status_code == 200:
        decoded_dl = download.content.decode('utf-8')
        req_reader = csv.reader(decoded_dl.splitlines(), delimiter = ',')
        kc_reqs = list(req_reader)

        kc_requests = pd.DataFrame(kc_reqs[1:], columns = kc_reqs[0])
        kc_requests = kc_requests[kc_cols_to_keep]

        return kc_requests


def categorize(kc_requests):
    for col_name in ["REQUEST TYPE", "CATEGORY", "TYPE"]:
        kc_requests[col_name] = kc_requests[col_name].astype("category")
    kc_requests.dropna(subset=["CASE URL"], inplace = True)
    kc_requests['COMMENT_TEXT'] = pd.Series()
    kc_requests.set_index('CASE ID', inplace = True)
    return kc_requests


def queue_kc_links(kc_link, kc_queue, visited_set):
    # get request object from case description link url
    # print(urllib.parse.urlparse(kc_link).netloc)
    print(kc_link)
    if (kc_link == ''):
        print("first error in queueing")
        kc_req = None

    elif urllib.parse.urlparse(kc_link).netloc == '':
        kc_req = None

    else:
        # check if link is an actual URL (no @s, emails) within correct domain
        limiting_domain = "webfusion.kcmo.org"
        # print("set limiting domain")
        link_approval = is_url_ok_to_follow(kc_link, limiting_domain)
        # print(link_approval)

        if link_approval:
            try:
                 kc_req = requests.get(kc_link)
                 # print("tried:", kc_req.url)
                 if kc_req.status_code == 404 or kc_req.status_code == 403:
                     print("404 error")
                     kc_req = None
                # else:
                #     print(kc_req.status_code)
            except Exception:
                print("link_approval exception error")
                kc_req = None
        else:
            kc_req = None
            print("link not approved:", kc_req.url)

        if kc_req:
            print("Request object created:", kc_req.url)
            abs_url = convert_if_relative_url(kc_link, kc_req.url)
            clean_link, frag = urllib.parse.urldefrag(abs_url)

            if clean_link not in visited_set:
                print("New clean link:", clean_link)
                kc_queue.put(clean_link)


def kc_soup(clean_link, visited_set):
    # read request from case description link
    if clean_link not in visited_set:
        clean_req = requests.get(clean_link)

        if clean_req and (clean_req.url not in visited_set):
            try:
                soup_string = clean_req.text.encode('iso-8859-1')
                visited_set.add(clean_req.url)
                print("Made soup!")
            except Exception:
                print('read failed: ' + clean_req.url)
                soup_string = ''
                visited_set.add(clean_req.url)

            if soup_string != '':
                case_soup = bs4.BeautifulSoup(soup_string, "html5lib")
                return case_soup
            else:
                print("Blank soup")
        else:
            print("Already vistied?", (clean_req.url in visited_set))
    else:
        print("Already vistied!")



def pull_comments(case_soup, case_df):
    b_tag = case_soup.find('b', text=re.compile(r'Case ID:'))
    if b_tag:
        case_num = int(b_tag.next_sibling)

    desc = case_soup.find('rc_descrlong')
    print("got comments!")
    if desc:
        comments = desc.text

        if not re.match("^.*(dupe|duplicate|test).*$", comments):
            print("Adding comments")
            case_df["COMMENT_TEXT"].loc[case_num] = comments




def convert_if_relative_url(current_url, new_url):
    '''
    Attribution: Part of utility code written by Anne Rogers of the
    University of Chicago, inspired by an assignment written by
    Mari Hearst at UC Berkeley

    Attempt to determine whether new_url is a relative URL and if so,
    use current_url to determine the path and create a new absolute
    URL.  Will add the protocol, if that is all that is missing.

    Inputs:
        current_url: absolute URL
        new_url:

    Outputs:
        new absolute URL or None, if cannot determine that
        new_url is a relative URL.
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
        or a file that has no extension or ends in .html. URLs
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

    # if parsed_url.query != "":
    #     return False

    loc = parsed_url.netloc
    ld = len(limiting_domain)
    trunc_loc = loc[-(ld+1):]
    if not (limiting_domain == loc or (trunc_loc == "." + limiting_domain)):
        print("loc error")
        return False

    # does it have the right extension
    (filename, ext) = os.path.splitext(parsed_url.path)
    return (ext == "" or ext == ".cfm")




def go(kc_url):
    '''
    Crawl Kansas City URLs and generate a pandas dataframe of service request
    details.

    Inputs:
        kc_csv: a csv of service request details including a URL

    Outputs: (dataframe) a pandas dataframe of 311 service request details
             including raw text comments
    '''

    kc_df = import_kc(kc_url)

    max_pages = kc_df.shape[0]

    # initialize queue to hold links to scrape
    kc_queue = queue.Queue()

    # initialize set to check whether a link has been visited
    visited_set = set()

    # initialize counter for pages visited
    pages_visited = 0

    for link in kc_df["CASE URL"]:
        queue_kc_links(link, kc_queue, visited_set)

    print("Is queue empty?", kc_queue.empty())

    while not kc_queue.empty() and (pages_visited <= max_pages):
        print("Entering while loop")
        case_url = kc_queue.get()
        print("To make soup:", case_url)
        case_soup = kc_soup(case_url, visited_set)

        if case_soup:
            # if soup was created (URL was ok to follow), add one to page
            # counter and add comments on page to case dataframe
            pages_visited += 1
            print("To pull comments:", case_url)
            pull_comments(case_soup, kc_df)

    print("Crawler visited {} pages".format(pages_visited))

    return kc_df["COMMENT_TEXT"].count()


if __name__ == "__main__":
    go(KC_URL)
