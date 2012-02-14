import json
import os

problem_ident = raw_input("Problem number or name: ")
if problem_ident.isdigit():
    problem_dir_name = [x for x in os.listdir('.') if os.path.isdir(x) and x.split('_')[0] == problem_ident][0]
else:
    problem_dir_name = [x for x in os.listdir('.') if os.path.isdir(x) and x.split('_')[1] == problem_ident][0]

problem = json.load(open('%s/%s.json' % (problem_dir_name, problem_dir_name.split('_')[1])))

attempt = __import__(
    "%s.%s" % (problem_dir_name, problem['definition']['class']),
    fromlist=[problem['definition']['class']]
)
function = getattr(attempt, problem['definition']['signature']['name'])

# run examples & tests
failed = False
crashed = True
for test_set in ['examples', 'tests']:
    for i, example in enumerate(problem[test_set]):
        try:
            crashed = True
            result = function(*example['input'])
            crashed = False
            if str(result) != str(example['output']): # needed for type differences
                # break out
                raise Exception()
            else:
                print "Passed %s %d: Returned %s with inputs %s." % (test_set[:-1], i, result, example['input'])
        except Exception, e:
            if crashed:
                print "Failed %s %d: Program crashed with error '%s' on inputs %s." % (test_set[:-1], i, e, example['input'])
            else:
                print "Failed %s %d: Result was %s, expecting %s with inputs %s." % (test_set[:-1], i, result, example['output'], example['input'])
            failed = True
            break
    if failed:
        break
    # blank line between examples and tests
    print

if not failed:
    print "Passed all tests!"
