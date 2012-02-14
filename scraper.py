#!/usr/bin/python

from ProblemFolder import *
import argparse
import sys

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



DEFAULT_PROBLEMS_DIRECTORY = "problems"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetches problems from TopCoder.com. See the README for more information.")
    parser.add_argument('problems', action="store",
                        help="The problems to fetch. Can be a list (e.g. 1-3, 5).")
    parser.add_argument('-o', '--output_dir', action="store", dest="output_dir",
                        help="The output directory (without a trailing slash).",
                        default=DEFAULT_PROBLEMS_DIRECTORY)
    args = parser.parse_args()

    problem_numbers = get_numbers_from_list(args.problems)

    # create output directory
    folder = ProblemFolder(args.output_dir)

    # connect to TopCoder
    print "Connecting to TopCoder...",
    opener = connect_to_topcoder()
    print "OK"

    print "--- Scraping %d problems ---" % len(problem_numbers)

    # scrape problems
    for n in problem_numbers:
        print " * Scraping problem %d." % n
        folder.scrape_and_add_problem(n, opener=opener)

    print "--- OK ---"

