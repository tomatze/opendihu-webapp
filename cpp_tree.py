import re
import traceback
import inspect
import copy

from helpers import printe, indent, Error, Info
import possible_solver_combinations
from python_settings import PythonSettings, SettingsDict, SettingsList, SettingsListEntry, SettingsComment, SettingsDictEntry, SettingsChildPlaceholder, SettingsContainer, SettingsMesh, SettingsSolver, SettingsChoice
from node import Node
from root_node import RootNode
from undo_stack import UndoStack


# this class holds a tree of Node objects
# the tree represents the structure of a example.cpp
class CPPTree:
    #combinations = None
    def __init__(self):
        # read in the template.cpp, so we don't have to read it in multiple times
        file_cpp_template = open("template.cpp", "r")
        self.cpp_template = file_cpp_template.read()
        file_cpp_template.close()

        self.combinations = possible_solver_combinations.possible_solver_combinations

        self.root = None
        self.undo_stack = UndoStack(self)

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

    def reset(self):
        self.undo_stack.add_new_root_node()
        return Info('loaded empty simulation')

    # this function reads a string (normally the content of a example.cpp) and creates the tree from it
    def parse_cpp_src(self, problem, validate_semantics=False):
        new_root = RootNode(self.combinations)
        #try:
        if 1 == 1:
            # remove single-line-comments from problem
            #problem = re.sub(r'(?m)^(.*)//.*\n?', r'\1\n', problem)
            # mark comments with 'α commentβ' instead of '// comment' so they are easy to parse
            problem = re.sub(r'(?m)^(.*)//(.*)\n?', r'\1α\2β\n', problem)
            # TODO save comments in tree and print them in repr
            # TODO maybe also remove multi-line-comments

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
                        # TODO can this really be removed?
                        if stack[-1].childs.get_real_childs()[0].name == "":
                            stack[-1].childs.clear()
                    else:
                        stack[-1].name = stack[-1].name + char

            child = stack[0].childs.get_real_childs()[0]
            new_root.childs.replace_next_placeholder(child)

            if validate_semantics:
                 ret = new_root.validate_cpp_src(self)
                 if isinstance(ret, Error):
                     return ret
            if not self.root.compare_cpp(new_root):
                self.undo_stack.add(new_root)
                return Info('cpp-src parsed successfully')
            else:
                return Info('no changes found in cpp-src')
        #except:
        #    return Error('failed to parse cpp-src (syntax-error)')

    # this creates a string which contains the whole generated example.cpp source-code using the tree and the template.cpp
    def __repr__(self):
        if len(self.root.childs.get_real_childs()) > 0:
            index = self.cpp_template.find(' problem(settings)')
            return self.cpp_template[:index] + indent(str(self.root.childs.get_real_childs()[0]), '  ') + self.cpp_template[index:]
        else:
            return self.cpp_template

    def add_new_child_to_node(self, node, childname):
        self.undo_stack.duplicate_current_state()
        child = Node(self.combinations)
        child.name = childname
        if "template_arguments" in self.combinations[childname]:
            child.can_have_childs = True
        # TODO add_missing_default_python_settings
        node.childs.replace_next_placeholder(child)

    def add_missing_placeholder_nodes(self):
        self.root.childs

    def get_possible_replacements_for_node(self, node):
        if isinstance(node, RootNode):
            return []
        for i in range(len(node.parent.childs.get_real_childs())):
            if node == node.parent.childs.get_real_childs()[i]:
                child_index = i
        possible_node_names = self.combinations[node.parent.name]["template_arguments"][child_index]
        possible_replacements = []
        for name in possible_node_names:
            possible_replacement = Node(self.combinations)
            possible_replacement.name = name
            if "template_arguments" in self.combinations[name]:
                possible_replacement.can_have_childs = True
            possible_replacements.append(possible_replacement)
        # TODO sort by occurence in examples
        return possible_replacements



    # this function returns a list of all possible childs of a given class
    def get_possible_childs(self, name):
        return self.combinations[name]["template_arguments"]

    ## after parsing the cpp_src, we can parse the python settings and map them to the nodes
    def parse_python_settings(self, settings):
        self.undo_stack.duplicate_current_state()
        # save PythonSettings so we also have the prefix and postfix
        try:
            python_settings = PythonSettings(settings)
        except:
            self.undo_stack.undo()
            self.undo_stack.remove_future()
            return Error('failed to create a PythonSettings object from code (propably a syntax-error)')
        try:
            return self.root.parse_python_settings(python_settings, keep_entries_that_have_no_default=True)
        except:
            self.undo_stack.undo()
            self.undo_stack.remove_future()
            return Error('failed to add PythonSettings object to ' + str(self.root.name) + ' (most likely a bug)')

    def get_python_settings(self):
        return self.root.get_python_settings()

    def add_missing_default_python_settings(self):
        changes = self.root.add_missing_default_python_settings()
        if changes > 0:
            self.undo_stack.duplicate_current_state()
        return Info('added ' + str(changes) + ' missing default python-settings')
