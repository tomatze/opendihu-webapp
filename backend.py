#!/usr/bin/python3

import sys

from cpp_structure import CPPTree
from python_settings import PythonSettings

def main():
    src = open(str(sys.argv[1]), "r").read()
    cpp_tree = CPPTree()
    cpp_tree.parse_src(src)
    #print(example.root)
    #print(example.combinations)
    print(cpp_tree.validate_src())
    print('\n')
    print(cpp_tree.create_src())
    #print(example.get_possible_childs('SpatialDiscretization::FiniteElementMethod'))

    settings = open(str(sys.argv[2]), "r").read()
    python_settings = PythonSettings(settings)
    print(python_settings.dict)

# use printe() instead of print() to print errors to stderr instead of stdout
def printe(message):
    print('Error: ' + message, file=sys.stderr)

if __name__ == "__main__":
    main()
