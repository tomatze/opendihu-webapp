import copy
from root_node import RootNode
from helpers import Error, Info

class UndoStack:
    def __init__(self, cpp_tree):
       self.stack = []
       self.current_index = -1
       self.cpp_tree = cpp_tree

       self.add_new_root_node()

    def duplicate_current_state(self):
        # deepcopy current root
        #self.add(copy.deepcopy(self.stack[self.current_index]))
        self.add(copy.deepcopy(self.cpp_tree.root))

    def add_new_root_node(self):
        self.add(RootNode())

    def undo(self):
        if self.current_index > 0:
            self.current_index = self.current_index - 1
            self.__update_cpp_tree()
            return Info('undo successful')
        else:
            return Error('cannot undo')

    def redo(self):
        if len(self.stack) - 1 > self.current_index:
            self.current_index = self.current_index + 1
            self.__update_cpp_tree()
            return Info('redo successful')
        else:
            return Error('cannot redo')

    def __update_cpp_tree(self):
        self.cpp_tree.root = self.stack[self.current_index]

    def add(self, node):
        self.remove_future()
        self.stack.append(node)
        self.current_index = self.current_index + 1
        self.__update_cpp_tree()

    def remove_future(self):
        # pop everything newer than the current root
        self.stack = self.stack[:self.current_index + 1]


