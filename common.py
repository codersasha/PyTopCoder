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

def unescape(s):
    "unescape HTML code refs; c.f. http://wiki.python.org/moin/EscapingHtml"
    return re.sub('&(%s);' % '|'.join(name2codepoint),
              lambda m: unichr(name2codepoint[m.group(1)]), s)

def get_number_list(num_text):
    """Given a list of numbers as text (e.g. '1-2,5,7-9'), returns a list of these numbers."""
    nums = set()
    num_tokens = num_text.replace(' ', '').replace('\t', '').split(',')
    for token in num_tokens:
        if '-' in token:
            start, end = token.split('-')
            nums.update(range(int(start), int(end) + 1))
        else:
            nums.add(int(token))
    return sorted(nums)

def connect_to_topcoder(username, password, VERBOSE = False):
    requestdata = {'username': username,
                    'password': password}

    # open connection
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    login_data = urllib.urlencode(requestdata)
    
    opener.open('http://community.topcoder.com/tc?&module=Login', login_data)
    return opener

def open_page(opener, url, VERBOSE = False):
    """Opens a topcoder page, returning the page's HTML."""
    if VERBOSE: print "Loading page %s..." % url,
    resp = opener.open(url)
    pagedata = resp.read()
    if VERBOSE: print "OK"
    return unescape(pagedata)

def get_all_topcoder_problem_nos(opener, n):
    """Returns a set of up to n topcoder problem numbers."""
    # open the problems listing page
    soup = BeautifulSoup(open_page(opener, 'http://community.topcoder.com/tc?module=ProblemArchive&sr=0&er=%d' % n))

    # extract all problem links
    problem_nos = set()
    problem_no_re = re.compile("/stat\?c=problem_statement&pm=(.*)")
    link_tags = soup.findAll("a", {"class": "statText", "href": problem_no_re})
    for link_tag in link_tags:
        problem_nos.add(int(re.findall(problem_no_re, link_tag['href'])[0]))
        
    return problem_nos

def get_existing_problem_nos(problems_subdirectory):
    """Returns a set of all existing problem numbers."""
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

    
