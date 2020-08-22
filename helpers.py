import sys

# use printe() instead of print() to print errors to stderr instead of stdout
def printe(message):
    print('Error: ' + message, file=sys.stderr)
