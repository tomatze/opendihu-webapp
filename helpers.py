import sys

# use printe() instead of print() to print errors to stderr instead of stdout
def printe(message):
    print('Error: ' + message, file=sys.stderr)

# helper function to indent a multiline-string by a given indentation
def indent(lines, indentation):
    return indentation + lines.replace('\n', '\n' + indentation)
