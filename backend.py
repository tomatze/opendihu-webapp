#!/usr/bin/python3

import sys

from cpp_structure import CPPTree
from python_settings import PythonSettings
import possible_solver_combinations

def main():
    src = open(str(sys.argv[1]), "r").read()
    cpp_tree = CPPTree()
    cpp_tree.parse_cpp_src(src)
    #print(example.root)
    #print(example.combinations)
    #print(cpp_tree.validate_cpp_src())
    #print('\n')
    #print(cpp_tree)
    #print(example.get_possible_childs('SpatialDiscretization::FiniteElementMethod'))

    settings = open(str(sys.argv[2]), "r").read()
    cpp_tree.parse_python_settings(settings)

    print(cpp_tree.get_python_settings_dict())
    #print()
    #print(cpp_tree.python_settings)

    #print('rootNode: ' + cpp_tree.root.name + '\n' + str(cpp_tree.root.settings_dict))
    #print('\nchild0Node: ' + cpp_tree.root.childs[0].name + '\n' + str(cpp_tree.root.childs[0].settings_dict))

    #python_settings = PythonSettings(settings)
    #print(python_settings)


if __name__ == "__main__":
    main()
