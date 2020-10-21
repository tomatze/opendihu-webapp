import re
import traceback
import inspect
import copy

from helpers import printe, indent, Error, Info, Warning
import possible_solver_combinations
from python_settings import PythonSettings, SettingsDict, SettingsList, SettingsListEntry, SettingsComment, SettingsDictEntry, SettingsChildPlaceholder, SettingsContainer, SettingsMesh, SettingsSolver, SettingsChoice
from node import Node
from root_node import RootNode
from undo_stack import UndoStack


# this class is the backend
# it holds the cpp-tree and all functions that can be used by an interface
class CPPTree:
    # initialize class varibales
    def __init__(self):
        # read in the template.cpp, so we don't have to read it in multiple times
        file_cpp_template = open("template.cpp", "r")
        self.cpp_template = file_cpp_template.read()
        file_cpp_template.close()

        self.combinations = possible_solver_combinations.possible_solver_combinations

        # create a list of keys
        self.keys = list(self.combinations.keys())

        # create lists of runnable, discretizableInTime, timeSteppingScheme
        # runnable is used in validate_src(), the other lists are used to expand some template_arguments 
        self.runnables = []
        self.discretizableInTime = []
        self.timeSteppingScheme = []
        for i in range(0, len(self.keys)):
            if self.combinations[self.keys[i]].get('runnable', False) == True:
                self.runnables.append(self.keys[i])
            if self.combinations[self.keys[i]].get('discretizableInTime', False) == True:
                self.discretizableInTime.append(self.keys[i])
            if self.combinations[self.keys[i]].get('timeSteppingScheme', False) == True:
                self.timeSteppingScheme.append(self.keys[i])


        # expand all template_arguments sublists of the form:
        # [ "Mesh::" ]
        # to the form:
        # [ "Mesh::StructuredRegularFixedOfDimension", "Mesh::StructuredDeformableOfDimension" ... ]
        # AND
        # expand all template_arguments sublists of the form:
        # [ "discretizableInTime" ]
        # to the form:
        # [ "SpatialDiscretization::FiniteElementMethod", "CellmlAdapter", ... ]
        # AND
        # expand all template_arguments sublists of the form:
        # [ "timeSteppingScheme" ]
        # to the form:
        # [ "OperatorSplitting::Strang", "TimeSteppingScheme::Heun", ... ]
        for _key, value in self.combinations.items():
            template_arguments = value.get("template_arguments", [])
            for i in range(0, len(template_arguments)):
                template_argument = template_arguments[i]
                for item in template_argument:
                    # expand ::
                    if len(item) >= 2 and item[-1] == ':' and item[-2] == ':':
                        # if item ends with '::'
                        template_argument.remove(item)
                        for key_sub in self.keys:
                            if key_sub.startswith(item):
                                template_argument.append(key_sub)
                    # expand discretizableInTime
                    if item == "discretizableInTime":
                        template_argument.remove(item)
                        for key_sub in self.discretizableInTime:
                            template_argument.append(key_sub)
                    # expand timeSteppingScheme
                    if item == "timeSteppingScheme":
                        template_argument.remove(item)
                        for key_sub in self.timeSteppingScheme:
                            template_argument.append(key_sub)

        # add template_arguments for GLOBAL (runnables)
        self.combinations['GLOBAL']["template_arguments"] = [self.runnables]

        self.undo_stack = UndoStack()

    # adds a RootNode with no childs to undo_stack
    # this function has to be called after initializing this class
    # it is not in __init__ so it can return the Info
    # !!! if this is not called the behaviour of the UndoStack is undefined
    def load_empty_simulation(self):
        self.undo_stack.add(RootNode(self.combinations))
        return Info('loaded empty simulation')

    # reads a string (normally the content of a example.cpp) and creates a new tree from it
    # the new tree will not have any python-settings attached to it
    # if you want to attach the python-settings from the old tree to the new one,
    # you have to save them beforehand and parse them after this
    # returns Info if the RootNode changed, Error or Warning otherwise
    def parse_cpp_src(self, problem, validate_semantics=False):
        new_root = RootNode(self.combinations)
        try:
            # remove single-line-comments from problem
            #problem = re.sub(r'(?m)^(.*)//.*\n?', r'\1\n', problem)
            # mark comments with 'α commentβ' instead of '// comment' so they are easy to parse
            problem = re.sub(r'(?m)^(.*)//(.*)\n?', r'\1α\2β\n', problem)
            # TODO maybe also handle multi-line-comments

            # remove LOG(DEBUG) lines
            problem = re.sub(r'(.*)LOG\(DEBUG\)<<(.*)', '', problem)

            # resolve typedefs (e.g. typedef Mesh::StructuredDeformableOfDimension<3> MeshType;)
            # get all lines staring with typedef
            typedef_lines = []
            for line in problem.split(';'):
                line = line.lstrip()
                if line.startswith('typedef'):
                    typedef_lines.append(line)
            # remove typedef lines from problem
            problem = re.sub(r'(.*)typedef (.*);', '', problem)
            # resolve typedefs
            for line in typedef_lines:
                # replace all whitspaces with a simple whitespace
                line = re.sub(r'\s+', ' ', line)
                # resolve the typedef by splitting the typedef-line at the spaces and replacing the strings in problem
                parts = line.split(' ')
                problem = problem.replace(parts[2], parts[1])

            # replace newlines tabs and spaces with spaces
            problem = re.sub(r'\s+', ' ', problem)

            # isolate problem
            problem = problem.split('settings(argc, argv);')[1]
            problem = re.compile(r'>([^>]*)\(settings\);').split(problem)[0] + '>'
            problem = re.compile(r' ([A-Za-z]*)\(settings\);').split(problem)[0]

            # remove spaces
            #problem = re.sub(r' ', '', problem)

            # create tree from problem with a simple parser
            # this populates new_root and its children
            problem = '<' + problem + '>'
            stack = []
            stack.append(Node(self.combinations))
            comment_mode = False
            comment_node = stack[0]
            for char in problem:
                if comment_mode:
                    if char == 'β':
                        comment_mode = False
                    else:
                        comment_node.comment = comment_node.comment + char
                else:
                    if char == ' ':
                            pass
                    elif char == 'α':
                        comment_mode = True
                    elif char == '<':
                        child = Node(self.combinations)
                        stack[-1].can_have_childs = True
                        stack[-1].childs.replace_next_placeholder(child)
                        stack.append(child)
                        comment_node = child
                    elif char == ',':
                        comment_node = stack.pop()
                        child = Node(self.combinations)
                        stack[-1].childs.replace_next_placeholder(child)
                        stack.append(child)
                    elif char == '>':
                        stack.pop()
                        comment_node = stack[-1]
                        # remove empty child in case of <> we have can_have_childs for that
                        if stack[-1].childs.get_real_childs()[0].name == "":
                            stack[-1].childs.clear()
                    else:
                        stack[-1].name = stack[-1].name + char

            child = stack[0].childs.get_real_childs()[0]
            new_root.childs.replace_next_placeholder(child)

            if validate_semantics:
                 ret = new_root.validate_cpp_src_recursive()
                 if isinstance(ret, Error):
                     return ret
            # check if the new tree is different from the old tree
            if not self.undo_stack.get_current_root().compare_cpp(new_root):
                self.undo_stack.add(new_root)
                return Info('cpp-src parsed successfully')
            else:
                return Warning('no changes found in cpp-src')
        except:
            return Error('failed to parse cpp-src (syntax-error)')

    # returns a string, which contains the generated cpp source-code using the tree and the template.cpp
    def __repr__(self):
        if len(self.undo_stack.get_current_root().childs.get_real_childs()) > 0:
            index = self.cpp_template.find(' problem(settings)')
            return self.cpp_template[:index] + indent(str(self.undo_stack.get_current_root().childs.get_real_childs()[0]), '  ') + self.cpp_template[index:]
        else:
            return self.cpp_template

    # replace a node in the tree with another node
    def replace_node(self, node, replacement_node):
        self.undo_stack.duplicate_current_state()
        node.parent.childs.replace(node, replacement_node)
        return Info('replaced node with ' + str(replacement_node.name))

    # delete a node from the tree
    def delete_node(self, node):
        self.undo_stack.duplicate_current_state()
        node.parent.childs.delete(node)
        return Info('deleted node ' + str(node.name))

    # parse a string with python-settings and map the settings to the given node (and its child_nodes recursively)
    # if node is given, the settings are applied to a specific node (if not they are applied to root)
    # to give a PythonSettings object to this function, you have to cast it to a string first
    def parse_python_settings(self, settings, node=None):
        self.undo_stack.duplicate_current_state()
        # save PythonSettings so we also have the prefix and postfix
        try:
            if node:
                python_settings = PythonSettings()
                python_settings.config_dict = SettingsDict(settings)
                n = node
                recurse_childs = False
            else:
                python_settings = PythonSettings(settings)
                n = self.undo_stack.get_current_root()
                recurse_childs = True
        except:
            self.undo_stack.undo()
            self.undo_stack.remove_future()
            return Error('failed to create a PythonSettings object from code (propably a syntax-error)')

        try:
            return n.parse_python_settings(python_settings, keep_entries_that_have_no_default=True, recurse_childs=recurse_childs)
        except:
            self.undo_stack.undo()
            self.undo_stack.remove_future()
            return Error('failed to add PythonSettings object to ' + str(n.name) + ' (most likely a bug)')

    # get the trees PythonSettings object, which holds the global python_settings and its prefix+postfix
    def get_python_settings(self):
        return self.undo_stack.get_current_root().get_python_settings()

    # add missing default-python-settings to a given node
    def add_missing_default_python_settings(self, node=None):
        if node:
            n = node
            recurse_childs = False
        else:
            n = self.undo_stack.get_current_root()
            recurse_childs = True
        self.undo_stack.duplicate_current_state()
        changes = n.add_missing_default_python_settings(self.undo_stack.get_current_root().settings_dict, recurse_childs=recurse_childs)
        if not changes > 0:
            self.undo_stack.undo()
            self.undo_stack.remove_future()
        return Info('added ' + str(changes) + ' missing default python-settings to ' + str(n.name))
