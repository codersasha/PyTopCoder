#!/usr/bin/python
import cookielib
import re
import urllib, urllib2
import base64
import urlparse
import os.path
import sys
import json
from BeautifulSoup import BeautifulSoup

SUPPORTED_FORMATS = ['html', 'json']

class TCProblem(object):
    def __init__(self, opener, problem_num):
        url = 'http://community.topcoder.com/stat?c=problem_statement&pm=%s' % problem_num
        soup = BeautifulSoup(open_page(opener, url))

        # save known info
        self.problem_no = problem_num
        self.url = url
        self.soup = soup

        # check the other info exists
        error = soup.findAll(text=re.compile(".*Problem Statement not available.*"))
        if error:
            self.exists = 0
        else:
            self.exists = 1

            # get problem statement
            try:
                self.problem_statement = get_associated_text(soup, "Problem Statement")
            except:
                self.problem_statement = ""

            try:
                self.definition = get_associated_text(soup, "Definition")
            except:
                self.definition = ""

            try:
                self.constraints = get_associated_text(soup, "Constraints")
            except:
                self.constraints = ""

            try:
                examples = get_associated_text(soup, "Examples")

                # for examples, remove the table
                #self.examples = "<ul><li>" + '</li><li>'.join([str(x) for x in self.examples]) + "</li></ul>"
                self.examples = []
                for example in examples:
                    table = example[0]
                    return_val = table.findAll("td", attrs={"class":"statText"}, text=re.compile("Returns"))[0][len("Returns: "):]

                    html_notes = table.findAll("td", attrs={"class":"statText", "colspan": "2"})
                    notes = []
                    for note in html_notes:
                        if note.contents:
                            notes.append(note.contents[0])
                    
                    html_input_lines = table.contents[0].contents[0].contents[0].contents
                    input_lines = [x.text for x in html_input_lines]
                    self.examples.append((input_lines, return_val, notes))
            except:
                self.examples = []

    def to_html(self):
        final_html = ""
        
        problem_statement = ''.join([str(x) for x in self.problem_statement])
        final_html += "<h1>Problem Statement</h1>%s" % problem_statement
        
        definition = ''.join([str(x) for x in self.definition])
        final_html += "<h1>Definition</h1>%s" % definition

        constraints = "<ul><li>" + '</li><li>'.join([str(x) for x in self.constraints]) + "</li></ul>"
        final_html += "<h1>Constraints</h1>%s" % constraints

        examples = "<ul>"
        for example in self.examples:
            examples += "<li>"
            examples += "<pre>%s</pre>" % ('\n'.join(example[0]))
            examples += "Returns: <b>%s</b><br />" % (example[1].strip().strip('&quot;'))
            examples += "%s" % '<br />'.join(example[2])
            examples += "</li>"
        examples += "</ul>"
        final_html += "<h1>Examples</h1>%s" % examples

        return final_html

    def to_json(self):
        return self.to_dict()

    def to_dict(self):
        return {"Problem Statement": self.problem_statement,
            "Definition": self.definition,
            "Constraints": self.constraints,
            "Examples": self.examples,
            "URL": self.url,
            "Problem No.": self.problem_no
        }

def connect_to_topcoder(username, password, VERBOSE = False):
    requestdata = {'username': username,
                    'password': password}

    # open connection
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    login_data = urllib.urlencode(requestdata)

    if VERBOSE: print "Logging in...",
    opener.open('http://community.topcoder.com/tc?&module=Login', login_data)
    if VERBOSE: print "OK"

    return opener

def open_page(opener, url, VERBOSE = False):
    """Opens a topcoder page, returning the page's HTML."""
    if VERBOSE: print "Loading page %s..." % url,
    resp = opener.open(url)
    pagedata = resp.read()
    if VERBOSE: print "OK"
    return pagedata

def get_associated_text(soup, heading):
    """Given a topcoder heading on the Problem Statement page, returns the associated HTML.
    Currently supported headings:
        - Problem Statement
        - Definition
        - Constraints
        - Examples
    """
    if heading == "Problem Statement" or heading == "Definition":
        heading_tag = soup.find(text=re.compile("^" + heading + "$"))
        table_cell = heading_tag.parent.parent.parent.nextSibling.contents[1]
        return table_cell.contents
    elif heading == "Constraints":
        heading_tag = soup.find(text=re.compile("^" + heading + "$"))
        table_row = heading_tag.parent.parent.parent.nextSibling
        constraints_list = []
        while table_row.text != u'&#160;':
            constraints_list.append(''.join([str(x) for x in table_row.contents[1].contents]))
            table_row = table_row.nextSibling
        return constraints_list
    elif heading == "Examples":
        heading_tag = soup.find(text=re.compile("^" + heading + "$"))
        table_row = heading_tag.parent.parent.parent.nextSibling.nextSibling
        examples = []
        while table_row:
            examples.append(table_row.contents[1].contents)
            if table_row.nextSibling:
                table_row = table_row.nextSibling.nextSibling
            else:
                table_row = None
        return examples

    return ""

# get command-line params
params = {"username": None,
    "password": None,
    "problem_no": None,
    "output_file": None,
    "output_format": None}

for i in range(len(sys.argv)):
    if sys.argv[i] == "-u":
        params['username'] = sys.argv[i + 1]
    elif sys.argv[i] == "-p":
        params['password'] = sys.argv[i + 1]
    elif sys.argv[i] == "-n":
        params['problem_no'] = sys.argv[i + 1]
    elif sys.argv[i] == "-o":
        params['output_file'] = sys.argv[i + 1]
    elif sys.argv[i] == "-f":
        params['output_format'] = sys.argv[i + 1]
        if params['output_format'] not in SUPPORTED_FORMATS:
            print "Format %s not supported." % params['output_format']
            sys.exit(1)

for param in params:
    if not params[param]:
        params[param] = raw_input(param + "? ")

opener = connect_to_topcoder(params['username'], params['password'], True)
p = TCProblem(opener, int(params['problem_no']))
if not p.exists:
    print "Problem %s was not found." % params['problem_no']
    sys.exit(2)

if params['output_format'] == 'html':
    htmlfile = open(params['output_file'], "w")
    data = p.to_html()
    htmlfile.write(data)
    htmlfile.close()
    print "Saved OK"
elif params['output_format'] == 'json':
    jsonfile = open(params['output_file'], "w")
    print p.to_json()
    data = p.to_json()
    json.dump(data, jsonfile)
    jsonfile.close()
    print "Saved OK"


