from Problem import *
from TopCoderParser import *

import os
import json
import shutil

## naming formats ##
FOLDER_NAME_FORMAT = "%d_%s"
JSON_FILE_FORMAT = "%s.json"
HTML_FILE_FORMAT = "%s.html"
PYTHON_FILE_FORMAT = "%s.py"
INIT_FILE_FORMAT = "__init__.py"

class ProblemFolder(object):
    """The class for TopCoder problem directories, which contain TopCoder
    problems.
    Has methods for adding and removing Problem objects from the directory."""

    ## init ##
    def __init__(self, directory):
        """Creates a new Problem Folder in the given directory.
        If problems already exist in that directory, adds them to the object."""
        self.loc = directory

        # get existing problems
        self.problems = load_existing_problems(self.loc)

    ## public methods ##
    def get_problem_numbers(self):
        """Returns a list of all problem numbers in this directory."""
        return [x[1] for x in self.problems]
    
    def scrape_and_add_problem(self, n, force = False, opener = None):
        """Given a problem number, scrapes the problem and adds it to the
        directory.

        If provided with an opener, uses that instead of re-connecting.

        If force is True, overwrites any existing Python files for this problem."""

        # get problem
        problem = scrape_problem(n, opener)

        if problem:
            # save problem
            print "Saving files...",
            self.add_problem(problem, force)
            print "OK"
        
    def find_problem(self, name = None, number = None, path = None):
        """Returns a list of problem tuples that match the search query."""

        # how many search terms were specified?
        rule_num = len([x for x in [name, number, path] if x != None])
        
        matches = []
        for problem in self.problems:
            score = 0
            if path != None:
                if problem[0] == path:
                    score += 1
            if number != None:
                if problem[1] == number:
                    score += 1
            if name != None:
                if problem[2] == name:
                    score += 1

            if score == rule_num:
                matches.append(problem)
                
        return matches
        
    def add_problem(self, problem, force = False):
        """Adds a new problem to this folder.
        If this problem already exists, overwrites the description files (but
        not any Python scripts, unless force is True).
        """

        # decide where to save this problem
        problem_foldername = FOLDER_NAME_FORMAT % (problem[P_PROBLEM_NUMBER], problem[P_PROBLEM_NAME])
        target_dir = self.loc + os.sep + problem_foldername

        # decide on filenames
        json_filename = JSON_FILE_FORMAT % problem[P_PROBLEM_NAME]
        html_filename = HTML_FILE_FORMAT % problem[P_PROBLEM_NAME]
        python_filename = PYTHON_FILE_FORMAT % problem[P_PROBLEM_DEFINITION]['class']
        init_filename = INIT_FILE_FORMAT

        # does this problem directory already exist?
        directory_exists = self.find_problem(path=target_dir)
        if not directory_exists:
            # create folder
            os.mkdir(target_dir)

            # save problem
            self.problems.append((target_dir, problem[P_PROBLEM_NUMBER], problem[P_PROBLEM_NAME]))

        # save JSON and HTML files, regardless
        problem.to_json_file(target_dir + os.sep + json_filename)
        problem.to_html_file(target_dir + os.sep + html_filename)

        # check if python file exists: if it doesn't, create it
        if force or not os.access(target_dir + os.sep + python_filename, os.F_OK):
            problem.to_python_file(target_dir + os.sep + python_filename)

        # create init file, if it doesn't exist
        if force or not os.access(target_dir + os.sep + init_filename, os.F_OK):
            open(target_dir + os.sep + init_filename, 'w').close()

    def del_problem(self, problem):
        """Deletes all problems with the same name and number as the given problem.
        Removes the problem directory from the file system, including any files
        in it.

        Returns the number of problems deleted."""

        problems_to_delete = self.find_problem(name=problem[P_PROBLEM_NAME], number=problem[P_PROBLEM_NUMBER])
        for p in problems_to_delete:
            # delete entire folder
            shutil.rmtree(p[0])
            
            # delete from list
            self.problems.remove(p)

        return len(problems_to_delete)

    def test_problems(self, problems):
        """Given a list of problem tuples (rel_path, number, name), runs the tests
        for each problem.
        Uses the method provided in the Python file in the problem directory."""

        for rel_path, number, name in problems:
            # load problem
            problem = Problem(rel_path + os.sep + (JSON_FILE_FORMAT % name))
            print "  * Running tests for problem %d: %s *  " % (problem[P_PROBLEM_NUMBER], problem[P_PROBLEM_NAME])
            
            # execute python file text
            python_filename = rel_path + os.sep + (PYTHON_FILE_FORMAT % problem[P_PROBLEM_DEFINITION]['class'])
            exec open(python_filename, 'rU')
            
            # get method
            method = locals()[problem[P_PROBLEM_DEFINITION]['method']]

            # run tests
            problem.test_method(method)
        

## helper functions ##
def load_existing_problems(directory):
    """Given a directory, finds all problem folders.
    Returns a list of tuples (rel_path, number, name) for each problem in the directory.
    e.g. [('./47_WordFilter/problem', 47, 'WordFilter']

    A problem directory is valid if there is a single JSON file inside the
    directory, in the correct format.
    """

    problems = []

    for root, dirs, files in os.walk(directory):
        # is there only 1 JSON file?
        json_files = [x for x in files if os.path.splitext(x)[1].lower() == '.json']
        if len(json_files) == 1:
            # load json file
            try:
                json_file = open(root + os.sep + json_files[0], 'r')
                data = json.load(json_file)
            
                # get name and number
                n = data[P_PROBLEM_NUMBER]
                name = data[P_PROBLEM_NAME]

                # close json file
                json_file.close()
                del data

                # add to list
                problems.append((root, n, name))

            except Exception, e:
                print "Could not load file %s: %s" % (root + os.sep + json_files[0], e)
            
    return problems
