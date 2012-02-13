from common import *

default_subdirectory = "./problems"

problem_no = int(raw_input("Enter a problem number: "))
problems_subdirectory = raw_input("Subdirectory [%s]: " % default_subdirectory) or default_subdirectory

# get JSON file
json = get_json(problems_subdirectory, problem_no)

if not json:
    print "That problem has not been scraped."
else:
    print "Writing...",

    # begin HTML and add header
    title = "%s. %s" % (json['number'], json['name'])
    html = "<html><head><title>%s</title></head><body>" % title
    html += "<h1>%s</h1>" % title

    # add statement
    html += "<h2>Problem Statement</h2>"
    html += "<p>%s</p>" % json['statement']

    # add definition
    html += "<h2>Definition</h2>"
    html += "<h3>Filename</h3><p>%s.py</p>" % json['definition']['class']
    html += "<h3>Method</h3><p>%s</p>" % json['definition']['method']
    html += "<h3>Parameters</h3><p>%s</p>" % json['definition']['params']
    html += "<h3>Returns</h3><p>%s</p>" % json['definition']['returns']

    s = json['definition']['signature']
    signature = "%s %s(%s)" % (s['returns'], s['name'], ', '.join(s['params']))
    html += "<h3>Signature</h3><p>%s</p>" % signature

    # add constraints
    if json['constraints']:
        html += "<h2>Constraints</h2><ul>"
        for c in json['constraints']:
            html += "<li>%s</li>" % c
        html += "</ul>"

    # add examples
    if json['examples']:
        html += "<h2>Examples</h2><ol>"
        for e in json['examples']:
            html += "<li>"
            html += "<h3>Input</h3><p>%s</p>" % ', '.join(str(x) for x in e['input'])
            html += "<h3>Output</h3><p>%s</p>" % e['output']
            if e['comments']:
                html += "<h3>Comments</h3><p>%s</p>" % e['comments']
            html += "</li>"
        html += "</ol>"

    # end HTML
    html += "</body></html>"

    # write to file
    htmlfile = open('%s_%s.html' % (json['number'], json['name']), 'w')
    htmlfile.write(html)
    htmlfile.close()
    print "OK"
    
