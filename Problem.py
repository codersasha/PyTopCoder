from topcoder_common import *

class Problem(object):
    """The class for all TopCoder problems.
    Has methods for both scraping problems from HTML, as well as extracting existing
    problems from a directory."""

    ## init ##
    def __init__(self):
        """Creates a blank problem object."""
        self.__dict__.update(EMPTY_PROBLEM_DICT)
