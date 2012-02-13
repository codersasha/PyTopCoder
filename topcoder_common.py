"""Some common functions for connecting to and parsing TopCoder pages."""

import cookielib
import re
import urllib, urllib2
import base64
import urlparse
import os
import json
from BeautifulSoup import BeautifulSoup
import string

from htmlentitydefs import name2codepoint

# topcoder problem pieces
P_PROBLEM_NUMBER = 'number'
P_PROBLEM_NAME = 'name'
P_PROBLEM_STATEMENT = 'statement'
P_PROBLEM_DEFINITION = 'definition'
P_PROBLEM_CONSTRAINTS = 'constraints'
P_PROBLEM_EXAMPLES = 'examples'
P_PROBLEM_TESTS = 'tests'
P_SUBMISSION_LISTING_LINK = 'submission_list_link'
P_SUBMISSION_LINK = 'submission_link'

# topcoder problem structure
EMPTY_PROBLEM_DICT = {
    P_PROBLEM_NUMBER: None,
    P_PROBLEM_NAME: None,
    P_PROBLEM_STATEMENT: None,
    P_PROBLEM_DEFINITION: {
        'class': None,
        'method': None,
        'types': {
            'output': None,
            'input': []
        },
        'names': {
            'input': []
        }
    },
    P_PROBLEM_CONSTRAINTS: [],
    P_PROBLEM_EXAMPLES: [], # each example is {'input': [], 'output': None, 'comment': None}
    P_PROBLEM_TESTS: [] # each test is {'input': [], 'output': None}
}

EMPTY_DEFINITIONS_DICT = {
    'class': None,
    'method': None,
    'types': {
        'output': None,
        'input': []
    },
    'names': {
        'input': []
    }
}
EMPTY_EXAMPLE_DICT = {'params': [], 'returns': None, 'comments': None}


# the topcoder pages of interest
TOPCODER_LOGIN_URL = 'http://community.topcoder.com/tc?&module=Login'
TOPCODER_PROBLEM_URL_FORMAT = "http://community.topcoder.com/stat?c=problem_statement&pm=%d"
TOPCODER_LISTING_URL_FORMAT = 'http://community.topcoder.com/tc?module=ProblemArchive&sr=%d&er=%d'
TOPCODER_LISTING_LINK_RE = "/stat\?c=problem_statement&pm=(.*)"

# by default, use this login and password
# taken from www.bugmenot.com
TOPCODER_DEFAULT_USER = 'a4339410'
TOPCODER_DEFAULT_PASS = 'a4339410'

## helper functions ##
def unescape(s):
    "unescape HTML code refs; c.f. http://wiki.python.org/moin/EscapingHtml"
    return re.sub('&(%s);' % '|'.join(name2codepoint),
              lambda m: unichr(name2codepoint[m.group(1)]), s)

def get_numbers_from_list(num_text):
    """Given a list of numbers as text (e.g. '1-2,5,7-9'), returns a list of these
    numbers."""
    nums = set()
    num_tokens = num_text.replace(' ', '').replace('\t', '').split(',')
    for token in num_tokens:
        if '-' in token:
            start, end = token.split('-')
            nums.update(range(int(start), int(end) + 1))
        else:
            nums.add(int(token))
    return sorted(nums)

def open_page(opener, url):
    """Opens a page with the given opener, returning the page's HTML."""
    resp = opener.open(url)
    pagedata = resp.read()
    return unescape(pagedata)

## topcoder-specific functions ##
def connect_to_topcoder(username = TOPCODER_DEFAULT_USER, password = TOPCODER_DEFAULT_PASS):
    """Connect to TopCoder, using the given username and password.
    Returns a connection object that can later be used for other pages that require
    you to be logged in to TopCoder."""
    requestdata = {'username': username,
                    'password': password}

    # open connection
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    login_data = urllib.urlencode(requestdata)
    
    opener.open(TOPCODER_LOGIN_URL, login_data)
    return opener

def get_topcoder_problem_page(opener, n):
    """Attempts to get the HTML for the nth TopCoder problem, using the given opener.
    On success, returns the page's HTML."""
    return open_page(opener, TOPCODER_PROBLEM_URL_FORMAT % n)

def get_all_topcoder_problem_nos(opener, n, end = None):
    """Returns the first n TopCoder problem numbers from the problem listing.
    If given two numbers, returns all topcoder problem numbers found between those
    two numbers."""

    # calculate start and end
    if end == None:
        start = 0
        end = n
    else:
        start = n
    
    # open the problems listing page
    soup = BeautifulSoup(open_page(opener, TOPCODER_LISTING_URL_FORMAT % (start, end)))

    # extract all problem links
    problem_nos = set()
    problem_no_re = re.compile(TOPCODER_LISTING_LINK_RE)
    link_tags = soup.findAll("a", {"class": "statText", "href": problem_no_re})
    for link_tag in link_tags:
        problem_nos.add(int(re.findall(problem_no_re, link_tag['href'])[0]))
        
    return problem_nos

def get_existing_problem_nos(problems_subdirectory):
    """Returns a set of all existing problem numbers in a particular directory."""
    folders = [x for x in os.listdir(problems_subdirectory) if os.path.isdir(problems_subdirectory + os.sep + x)]
    existing_nos = set()
    for folder in folders:
        if '_' in folder:
            existing_nos.add(int(folder.split('_')[0]))
    return existing_nos

def eval_variable(data):
    """Given some data in code format (as a string), returns the data in equivalent Python format."""
    if data.lower() == "true":
        return True
    if data.lower() == "false":
        return False
    if data[0] == "{":
        # preserve order (don't use sets)
        return list(eval("[" + data[1:-1] + "]"))
    if data[0] in ['"', "'"]:
        return str(eval(data)).strip("'\"")
    if data[0] in string.ascii_letters:
        # unquoted string
        return str(data.strip())
    if data[0].isdigit():
        return int(eval(data))
    return eval(data)

def get_json(directory, problem_no):
    """Given a problem number and a parent directory, returns the JSON (as a
    Python object) for that problem.
    Returns None if the problem was not found."""

    # find the folder
    folders = [x for x in os.listdir(directory) if os.path.isdir(directory + os.sep + x) and x.split('_')[0] == str(problem_no)]
    if len(folders) == 0:
        return None

    # get problem name
    folder = folders[0]
    problem_name = folder.split('_')[1]
    
    # find the JSON
    return json.load(open(directory + os.sep + folder + os.sep + problem_name + '.json'))

    
