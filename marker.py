import json

problem_no = 11777
problem = json.load(open('tc_%s.json' % problem_no))

attempt = __import__(problem['definition']['class'], fromlist=[problem['definition']['signature']['name']])
function = getattr(attempt, problem['definition']['signature']['name'])

# run examples
for i, example in enumerate(problem['examples']):
    result = function(*example['params'])
    if result != example['returns']:
        print "Failed example %d: result was %s, expecting %s." % (i, result, example['returns'])
    else:
        print "Passed test %d, with inputs %s." % (i, example['params'])


