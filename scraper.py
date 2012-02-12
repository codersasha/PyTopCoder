#!/usr/bin/python
from common import *

default_subdirectory = "./problems"
smart_mode = False

problem_nos = raw_input("Problem number(s) [enter a dash '-' to enter smart mode]: ")
if problem_nos == '-':
    max_num = int(raw_input("How many problems would you like to look for? "))
    smart_mode = True
else:
    problem_nos = get_number_list(problem_nos)

problems_subdirectory = raw_input("Subdirectory [%s]: " % default_subdirectory) or default_subdirectory
opener = connect_to_topcoder('a4339410', 'a4339410') # taken from www.bugmenot.com

if smart_mode:
    # find problem numbers
    print "Looking for problem numbers...",
    all_nos = get_all_topcoder_problem_nos(opener, max_num)
    print "OK"

    # don't redownload already-found ones
    print "Examining existing problem numbers...",
    existing_nos = get_existing_problem_nos(problems_subdirectory)
    print "OK"

    # take the difference
    problem_nos = all_nos.difference(existing_nos)
    print "Going to download %d new problems." % len(problem_nos)

for problem_no in problem_nos:
    print "Loading problem %d..." % problem_no,
    
    url = 'http://community.topcoder.com/stat?c=problem_statement&pm=%s' % problem_no
    soup = BeautifulSoup(open_page(opener, url))

    problem_info = {
        'number': None,
        'name': None,
        'statement': None,
        'definition': {
            'class': None,
            'method': None,
            'params': None,
            'returns': None,
            'signature': {
                'name': None,
                'returns': None,
                'params': []
            }
        },
        'constraints': [],
        'examples': [], # each example is {'input': [], 'output': None, 'comments': None}
        'tests': [] # each test is {'input': [], 'output': None}
    }

    # try to find Problem Statement not available message
    if soup.find("td", {"class": "problemText"}).getText() == u"Problem Statement not available.":
        print "That problem number does not exist."
    else:

        # save number
        problem_info['number'] = problem_no

        # get problem name (with HTML)
        problem_name_text = soup.find("td", {"class": "statTextBig"}).getText()
        problem_info['name'] = re.findall("Problem statement for (.+)", problem_name_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)[0]

        # get problem statement (with HTML)
        problem_statement_tag = soup.find("td", {"class": "problemText"}).findAll("td", {"class": "statText"})[2]
        problem_info['statement'] = problem_statement_tag.renderContents()

        # get parts of the definition (no HTML)
        definitions_header = soup.find("h3", text="Definition")
        if definitions_header:
            definitions_table = definitions_header.parent.parent.parent.nextSibling.find("table")
            class_row, method_row, params_row, returns_row, signature_row, ensure_public_row = definitions_table.findAll("tr")
            problem_info['definition']['class'] = class_row.findAll("td")[1].text
            problem_info['definition']['method'] = method_row.findAll("td")[1].text
            problem_info['definition']['params'] = params_row.findAll("td")[1].text
            problem_info['definition']['returns'] = returns_row.findAll("td")[1].text

            # parse signature
            signature = signature_row.findAll("td")[1].text
            parts = re.findall("(.+?) (.+?)\((.+?)\)", signature)[0]
            problem_info['definition']['signature']['returns'] = parts[0]
            problem_info['definition']['signature']['name'] = parts[1]
            problem_info['definition']['signature']['params'] = parts[2].split(', ')

        # get constraints (with HTML)
        constraints_header = soup.find("h3", text="Constraints")
        if constraints_header:
            constraint_bullets = constraints_header.parent.parent.parent.findAllNext("td", text="-")
            for bullet in constraint_bullets:
                problem_info['constraints'].append(bullet.parent.parent.findAll("td")[1].renderContents())

        # get examples
        examples_header = soup.find("h3", text="Examples")
        if examples_header:
            examples_numbers = examples_header.parent.parent.parent.findAllNext("td", text=re.compile("^\d+\)$"))
            for number in examples_numbers:
                new_example = {'params': [], 'returns': None, 'comments': None}
                
                example_table = number.parent.parent.nextSibling.find("table")
                
                # get input (without HTML)
                params_table = example_table.findAll("tr")[0].find("table")
                new_example['input'] = [eval_variable(x.getText()) for x in params_table.findAll("td")]

                # get output (without HTML)
                returns_row = example_table.findAll("tr")[1 + len(new_example['input'])]
                new_example['output'] = eval_variable(re.findall("Returns: (.+)", returns_row.getText(), re.DOTALL | re.IGNORECASE | re.MULTILINE)[0])

                # get comment (with HTML)
                comments_row = example_table.findAll("tr")[2 + len(new_example['input'])]
                new_example['comments'] = comments_row.find("td").renderContents()

                # save example
                problem_info['examples'].append(new_example)

        # follow the links through to a submission page
        contest_link = soup.find("a", {"href": re.compile("/tc\?module=ProblemDetail&.+")})['href']
        soup = BeautifulSoup(open_page(opener, 'http://community.topcoder.com' + contest_link))

        # follow the links to any submission (if there is one)
        submission_link = soup.find("a", {"href": re.compile("/stat\?c=problem_solution&.+")})
        if submission_link:
            soup = BeautifulSoup(open_page(opener, 'http://community.topcoder.com' + submission_link['href']))

            # get the system tests (no HTML)
            test_inputs = soup.findAll("td", {"class": "statText", "align": "left"})
            for i in range(len(test_inputs)):
                new_test = {'input': [], 'output': None}

                # parse test input
                test_input_cell = test_inputs[i]
                new_test['input'] = [eval_variable(x) for x in test_input_cell.getText().split(',\n')]

                # extract test output
                test_output_cell = test_inputs[i].parent.findAll("td")[3]
                new_test['output'] = eval_variable(test_output_cell.getText())

                # save test
                problem_info['tests'].append(new_test)

        # make a directory with the problem name (if it doesn't exist)
        problem_dir_name = "%s/%s_%s" % (problems_subdirectory, problem_info['number'], problem_info['definition']['class'])
        if not os.access(problem_dir_name, os.F_OK):
            os.mkdir(problem_dir_name)

        # save to a JSON file in this directory
        json_file_path = "%s/%s.json" % (problem_dir_name, problem_info['definition']['class'])
        output_file = open(json_file_path, 'w')
        json.dump(problem_info, output_file, indent=4)
        output_file.close()

        # make an empty __init__.py file in this directory (if it doesn't exist)
        init_file_path = "%s/__init__.py" % problem_dir_name
        if not os.access(init_file_path, os.F_OK):
            open(init_file_path, "w").close()

        # make a .py script in this directory (if it doesn't exist) with the function header
        python_file_path = "%s/%s.py" % (problem_dir_name, problem_info['definition']['class'])
        if not os.access(python_file_path, os.F_OK):
            python_file = open(python_file_path, "w")
            python_file.write("#!/usr/bin/python\n\n")
            python_file.write("def %s(%s):\n    pass\n" %
                            (
                                problem_info['definition']['signature']['name'],
                                ', '.join(x.split()[-1] for x in problem_info['definition']['signature']['params'])
                            ))
            python_file.close()

        print "OK"

