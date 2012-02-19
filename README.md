PYTHON TOP-CODER SCRAPER
=================

A scraper for the website www.topcoder.com.

Given a problem number, this script downloads all information about the problem from the website, and creates:

* A directory with the class name and problem number
* An __init__.py file
* A .json file with all problem information
* A .html file with all problem information
* A .py file (with the method header)

The scraper.py script accepts problem numbers in the form '1,2,3-4'. You can also enter a dash '-', after which you'll be asked how many problems you wish to download. The program will then look through TopCoder problem listings and find problems you do not already have, and download those.
 
The marker.py script needs to be in the subdirectory that contains all the TopCoder problems. It can then, given a problem name or number, automatically run all the tests for that problem.

Includes one TopCoder problem as an example.

Requires
--------

* Python 2.7+
* BeautifulSoup

Features
--------

* After parsing, creates a file tc_<problem number>.json with all problem information
* Saves all examples and tests in JSON-friendly format
* Comes with an automated marking script, marker.py, which can read the JSON file and mark a TopCoder.com problem attempt written in Python
* Can be used for building Python TopCoder testing suites

Examples
--------
1. See more help for the scraper.py script:
    $ scraper.py --help
2. Fetch problems 1, 2, 3 and 5 if I don't have them, and save them in the problems directory:
    $ scraper.py 1-3,5
3. Fetch problem 11777 and save it in /usr/var/problems:
    $ scraper.py -o /usr/var/problems 11777
4. Fetch problems 11777 and 117779, even if I already have them, and overwrite everything, even the python file if it exists already:
    $ scraper.py 11777,11779 --force
5. Fetch up to 10 new problems from TopCoder, unless I already have them
    $ scraper.py 10 --smart
6. Fetch 10 new problems from TopCoder, downloading them even if I have them already, and overwriting everything:
    $ scraper.py 10 --smart --force
7. Fetch all problems between 10 and 50 on the TopCoder listing, overwriting everything:
    $ scraper.py 10,50 --smart --force
8. Test problems 8, 9 and 10
    $ scraper.py 8-10 --test
9. Test problem 8, cleaning the problems directory first
	$ scraper.py 8 --test --clean