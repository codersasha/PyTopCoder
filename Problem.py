import json
from UserDict import IterableUserDict

## topcoder problem pieces ##
# main pieces
P_PROBLEM_NUMBER = 'number'
P_PROBLEM_NAME = 'name'
P_PROBLEM_STATEMENT = 'statement'
P_PROBLEM_DEFINITION = 'definition'
P_PROBLEM_CONSTRAINTS = 'constraints'
P_PROBLEM_EXAMPLES = 'examples'
P_PROBLEM_TESTS = 'tests'

# internal processing pieces
P_SUBMISSION_LISTING_LINK = 'submission_list_link'
P_SUBMISSION_LINK = 'submission_link'

# HTML-only pieces
P_PAGE_TITLE = 'page_title'

## topcoder problem structure ##
EMPTY_PROBLEM_DICT = {
    P_PROBLEM_NUMBER: None,
    P_PROBLEM_NAME: None,
    P_PROBLEM_STATEMENT: None,
    P_PROBLEM_DEFINITION: {
        'class': None,
        'method': None,
        'types': {
            'output': None,
            'input': []
        },
        'names': {
            'input': []
        }
    },
    P_PROBLEM_CONSTRAINTS: [],
    P_PROBLEM_EXAMPLES: [], # each example is {'input': [], 'output': None, 'comment': None}
    P_PROBLEM_TESTS: [] # each test is {'input': [], 'output': None}
}

EMPTY_DEFINITIONS_DICT = {
    'class': None,
    'method': None,
    'types': {
        'output': None,
        'input': []
    },
    'names': {
        'input': []
    }
}
EMPTY_EXAMPLE_DICT = {'input': [], 'output': None, 'comment': None}

## html output parameters ##
MAIN_HEADER_LEVEL = 1
HEADER_LEVEL = 2
SUB_HEADER_LEVEL = 3

## JSON output parameters ##
JSON_INDENT_LEVEL = 4

## python output parameters ##
PYTHON_TEMPLATE = """#!/usr/bin/python

def %s:
    pass

"""

class Problem(object, IterableUserDict):
    """The class for all TopCoder problems.
    Inherits from IterableUserDict, and supports all regular dictionary
    access."""

    ## init ##
    def __init__(self):
        """Creates a blank problem object."""
        self.data = dict(EMPTY_PROBLEM_DICT)

    ## private object methods ##
    def _generate_signature(self):
        """Returns the method signature for the problem, in the form
            <return type> <name>(<type> <name>, <type> <name>, ...)
        e.g. long MyFunc(int A, int B)
        """
        signature = "%s %s(" % (self['definition']['types']['output'], self['definition']['method'])
        
        for i in range(len(self['definition']['types']['input'])):
            signature += str(self['definition']['types']['input'][i])
            signature += ' '
            signature += str(self['definition']['names']['input'][i])

            # add a comma, if its not the last one
            if i != len(self['definition']['types']['input']) - 1:
                signature += ', '

        signature += ")"
        return signature

    def _generate_mini_signature(self):
        """Returns the method signature for the problem, in the form
            <name>(<name>, <name>, ...)
        e.g. MyFunc(A, B)
        """
        signature = "%s(" % self['definition']['method']
        signature += ", ".join([str(x) for x in self['definition']['names']['input']])
        signature += ")"
        return signature

    def _generate_filled_signature(self, inputs, output):
        """Returns the method signature for the problem with the given inputs
        and output, in the form
            <name>(<name>, <name>, ...) = <output>
        e.g. MyFunc("A", 1) = 12"""
        signature = "%s(" % self['definition']['method']
        signature += ", ".join([str(x) for x in inputs])
        signature += ") = %s" % output
        return signature
        
    def _piece_to_html(self, piece):
        """Converts the given piece to HTML, returning it as a string.
        Does NOT return the HTML header for the piece, just the content."""

        if piece == P_PROBLEM_NUMBER:
            return html_text(self[piece])
            
        elif piece == P_PROBLEM_NAME:
            return html_text(self[piece])
            
        elif piece == P_PROBLEM_STATEMENT:
            return html_text(self[piece])

        elif piece == P_PROBLEM_DEFINITION:
            html = ""
            html += html_header(SUB_HEADER_LEVEL, "Filename")
            html += html_text("%s.py" % self[piece]['class'])
            
            html += html_header(SUB_HEADER_LEVEL, "Signature")
            html += html_text(self._generate_signature())

            return html

        elif piece == P_PROBLEM_CONSTRAINTS:
            return "<ul><li>" + "</li><li>".join(self[piece]) + "</li></ul>"

        elif piece == P_PROBLEM_EXAMPLES:
            html = ""
            html += "<ul>"
            for example in self[piece]:
                html += "<li>"
                html += self._generate_filled_signature(example['input'], example['output'])

                if example['comment']:
                    html += html_text(example['comment'])
                
                html += "</li>"

            html += "</ul>"
            return html

        elif piece == P_SUBMISSION_LISTING_LINK:
            # not needed for HTML
            return None
            
        elif piece == P_SUBMISSION_LINK:
            # not needed for HTML
            return None
            
        elif piece == P_PROBLEM_TESTS:
            # not shown in HTML
            return None

        elif piece == P_PAGE_TITLE:
            return "%s. %s" % (self[P_PROBLEM_NUMBER], self[P_PROBLEM_NAME])

        else:
            # not recognised
            return None


    def _pieces_to_html(self, pieces):
        """Converts the given pieces to HTML, returning them as a list."""
        return [_piece_to_html(x) for x in pieces]

    ## public object methods ##

    # python output #
    def to_python(self, template = PYTHON_TEMPLATE):
        """Returns a Python file, with the method header, according to the
        specified python template."""
        return PYTHON_TEMPLATE % self._generate_mini_signature()
        
    def to_python_file(self, filename, template = PYTHON_TEMPLATE):
        """Saves Python text to a file, with the method header, according to the
        specified python template."""
        python_file = open(filename, 'w')
        python_file.write(self.to_python())
        python_file.close()

    # json output #
    def to_json(self):
        """Returns the problem, as a JSON string."""
        return json.dumps(self.data, indent=JSON_INDENT_LEVEL)

    def to_json_file(self, filename):
        """Saves the problem in JSON format to the given filename."""
        json_file = open(filename, 'w')
        json.dump(self.data, json_file, indent=JSON_INDENT_LEVEL)
        json_file.close()

    # html output #
    def to_html(self):
        """Returns the problem, as an HTML string."""

        html = ""

        # add title
        html += "<html><head><title>%s</title></head><body>" % self._piece_to_html(P_PAGE_TITLE)
        html += html_header(1, self._piece_to_html(P_PAGE_TITLE))

        # add each piece
        html += html_header(2, "Problem")
        html += self._piece_to_html(P_PROBLEM_STATEMENT)

        html += html_header(2, "Definition")
        html += self._piece_to_html(P_PROBLEM_DEFINITION)

        if self[P_PROBLEM_CONSTRAINTS]:
            html += html_header(2, "Constraints")
            html += self._piece_to_html(P_PROBLEM_CONSTRAINTS)

        if self[P_PROBLEM_EXAMPLES]:
            html += html_header(2, "Examples")
            html += self._piece_to_html(P_PROBLEM_EXAMPLES)

        return html

    def to_html_file(self, filename):
        """Saves the problem in HTML format to the given filename."""
        html_file = open(filename, 'w')
        html_file.write(self.to_html())
        html_file.close()

## helper functions ##
def html_header(level, text):
    """Returns an HTML header, containing the specified text.
    The level indicates the size of the header (1 for the largest header, larger
    numbers for deeper headers)."""
    return "<h%d>%s</h%d>" % (level, text, level)

def html_text(text):
    """Returns some text in HTML format."""
    return "<p>%s</p>" % text
