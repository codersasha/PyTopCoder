import json

problem_dir_name = "BuildingReorganization"
problem = json.load(open('%s/%s.json' % (problem_dir_name, problem_dir_name)))

attempt = __import__(
    "%s.%s" % (problem_dir_name, problem['definition']['class']),
    fromlist=[problem['definition']['class']]
)
function = getattr(attempt, problem['definition']['signature']['name'])

# run examples & tests
for test_set in ['examples', 'tests']:
    for i, example in enumerate(problem[test_set]):
        result = function(*example['input'])
        if result != example['output']:
            print "Failed %s %d: result was %s, expecting %s." % (test_set[:-1], i, result, example['output'])
            failed = True
            break
        else:
            print "Passed %s %d, with inputs %s." % (test_set[:-1], i, example['input'])
    if failed:
        break
    # blank line between examples and tests
    print

if not failed:
    print "Passed all tests!"
