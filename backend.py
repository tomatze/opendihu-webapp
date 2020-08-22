#!/usr/bin/python3

import sys

from cpp_structure import CPPTree
from python_settings import PythonSettings
import possible_solver_combinations

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

    print(cpp_tree.get_default_python_settings())

    #settings = open(str(sys.argv[2]), "r").read()
    #python_settings = PythonSettings(settings)
    #print(python_settings.dict)


if __name__ == "__main__":
    main()
