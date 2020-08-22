#!/usr/bin/python3

import sys
import inspect

from cpp_structure import CPPTree
from python_settings import PythonSettings, SettingsDict
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

    settings = open(str(sys.argv[2]), "r").read()
    python_settings = PythonSettings(settings)
    print(python_settings.dict)

    possible_solver_combinations_src = inspect.getsource(possible_solver_combinations)
    relevant_src = possible_solver_combinations_src.split('"SpatialDiscretization::FiniteElementMethod" : {')[1].split('\n    }')[0].split('"python_options" : {')[1].split('\n        }')[0]
    dict = SettingsDict(relevant_src)
    print(dict)

if __name__ == "__main__":
    main()
