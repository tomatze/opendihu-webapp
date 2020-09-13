import re
import traceback
import inspect
import copy

from helpers import printe, indent
import possible_solver_combinations
from python_settings import PythonSettings, SettingsDict, SettingsList, SettingsListEntry, SettingsComment, SettingsDictEntry, SettingsChildPlaceholder, SettingsContainer, SettingsLinkPlaceholder

# this class represents a Node in the structure tree (Example.root e.g. is such a Node)
class Node:
    def __init__(self):
        self.name = ''
        self.comment = ''
        self.can_have_childs = False
        self.childs = []

        self.settings_dict = None
        self.settings_dict_default = None

    # sets self.settings_dict_default to the values gotten from possible_solver_combinations
    # this is not in __init__(), because self.name (used here) gets defined later
    def get_default_python_settings_dict(self):
        if self.settings_dict_default == None:
            relevant_python_src = get_default_python_settings_src_for_classname(self.name)
            self.settings_dict_default = SettingsDict(relevant_python_src)
        return self.settings_dict_default

    ## returns self.settings_dict with SettingsChildPlaceholders replaced with child dicts
    def get_python_settings_dict_recursive(self):
        # deepcopy self.settings_dict so we don't replace the SettingsChildPlaceholders in it
        own_dict = copy.deepcopy(self.settings_dict)
        for child in self.childs:
            #print('child: ' + child.name)
            # for every child replace the ### CHILD ### placeholder with the childs dict
            try:
                child_dict = child.get_python_settings_dict_recursive()
                #print('replacing ' + child.name + ' placeholder with:\n' + str(child_dict))
                own_dict.replaceChildPlaceholder(child_dict)
            except:
                pass
                #printe('failed to replace SettingsChildPlaceholder ' + child.name)
        return own_dict

    # parse a python_settings_dict and add it to this Node and its childs
    def parse_python_settings_recursive(self, settings_dict, keep_entries_that_have_no_default=False, add_missing_default_entries=False, self_settings_dict=None, settings_dict_default=None, is_called_on_child=False):
        # TODO SettingsConditional? 
        # TODO Meshes and Solvers e.g. with ### SOLVER ###?
        # TODO if a SettingsDictEntry has no comment, add the default-comment
        # TODO remove add_missing_default_entries and move it to a new function (this also needs to add missing SettingsChildPlaceholders)
        # TODO add a new function to load default settings (if user wants to reset)
        # TODO if parsing Solvers or Meshes - just add everything
        # TODO when adding new solver/mesh - always add it globally and look for the last solver-number and increase it by one
        # these should be given as parameters when recursion happens on the same object again
        # self_settings_dict is the 'pointer' to the sub-SettingsDict in self.settings_dict we are currently handling
        # settings_dict_default is the 'pointer' to the sub-SettingsDict in settings_dict_default we are currently handling
        if self_settings_dict == None:
            if self.settings_dict == None:
                self.settings_dict = SettingsDict()
            self_settings_dict = self.settings_dict
        if settings_dict_default == None:
            settings_dict_default = self.get_default_python_settings_dict()

        # resolve SettingsLinkPlaceholders and insert their dict-entries
        for entry in settings_dict_default:
            if isinstance(entry, SettingsLinkPlaceholder):
                link_settings_dict = SettingsDict(get_default_python_settings_src_for_classname(entry.linkname))
                print(link_settings_dict)
                for e in link_settings_dict:
                    self_settings_dict.append(e)

        # insert all child-placeholders that are in python_options on this level
        # TODO append them to self_settings_dict after first use
        child_placeholders = []
        for entry in settings_dict_default:
            if isinstance(entry, SettingsChildPlaceholder):
                self_settings_dict.append(entry)
                child_placeholders.append(entry)

        #print(self_settings_dict)

        if isinstance(settings_dict, SettingsList):
            rest = SettingsList()
        else:
            rest = SettingsDict()

        for i in range(len(settings_dict)):
            entry = settings_dict[i]
            if isinstance(entry, SettingsDictEntry) or isinstance(entry, SettingsListEntry):
                #try:
                #    print(entry.key)
                #except:
                #    print('listEntry')
                # check if the entry is a SettingsListEntry or if it is a SettingsDictEntry and its key is in defaults
                if isinstance(entry, SettingsListEntry) or settings_dict_default.has_key(entry.key):
                    # key exists in defaults
                    # if the value is a SettingsContainer -> recurse
                    if isinstance(entry.value, SettingsContainer):
                        # create a new entry
                        if isinstance(entry, SettingsDictEntry):
                            new_entry = SettingsDictEntry()
                            new_entry.key = entry.key
                            settings_dict_default_recurse = settings_dict_default.get_value(entry.key)
                        else:
                            new_entry = SettingsListEntry()
                            # TODO here we assume that there is only one SettingsListEntry in python_options we just use the first one
                            settings_dict_default_recurse = settings_dict_default.get_first_SettingsListEntry().value
                        new_entry.comments = entry.comments

                        # add an empty list or dict to the new entry
                        if isinstance(entry.value, SettingsDict):
                            new_entry.value = SettingsDict()
                        else:
                            new_entry.value = SettingsList()
                            new_entry.value.list_comprehension = entry.value.list_comprehension
                        # add the new entry
                        self_settings_dict.append(new_entry)

                        # recurse the new entry
                        self.parse_python_settings_recursive(entry.value, self_settings_dict=new_entry.value, settings_dict_default=settings_dict_default_recurse, keep_entries_that_have_no_default=keep_entries_that_have_no_default, add_missing_default_entries=add_missing_default_entries)
                    else:
                        # if the entry.value is not special -> just append the entry
                        self_settings_dict.append(entry)
                else:
                    # entry is a SettingsDictEntry
                    # and the key does not exist in defaults
                    # this entry possibly belongs to a child
                    if len(child_placeholders) > 0:
                        new_dict = SettingsDict()
                        new_dict.append(entry)
                        # try giving the entry to the childs
                        for j in range(len(child_placeholders)):
                            #print('trying to give entry to child ' + str(child_placeholders[j].childnumber))
                            child = self.childs[child_placeholders[j].childnumber]
                            new_dict = child.parse_python_settings_recursive(new_dict, keep_entries_that_have_no_default=keep_entries_that_have_no_default, add_missing_default_entries=add_missing_default_entries, is_called_on_child=True)
                            if len(new_dict) == 0:
                                break
                        if len(new_dict) > 0:
                            #print('the childs did not take this entry')
                            if keep_entries_that_have_no_default:
                                self_settings_dict.append(entry)
                    else:
                        # this entry is not in defaults and there is no child at this place
                        if is_called_on_child:
                            rest.append(entry)
                        elif keep_entries_that_have_no_default:
                            self_settings_dict.append(entry)

            #elif isinstance(entry, SettingsComment):
            else:
                self_settings_dict.append(entry)

        # add missing default entries
        if add_missing_default_entries:
            if isinstance(settings_dict, SettingsList):
                pass
            else:
                for entry in settings_dict_default:
                    if isinstance(entry, SettingsDictEntry) and not self_settings_dict.has_key(entry.key):
                        self_settings_dict.append(entry)

        return rest

    # this function converts the tree under this Node to a pretty string
    # you can print the string to visualize the tree
    # this is also used to created cpp-source-code from a tree
    def __repr__(self):
        comment = ''
        if self.comment != '':
            comment = '//' + self.comment + '\n'
        return comment + self.repr_recursive(0)
    def repr_recursive(self, depth):
        indentation = '  ' * depth
        indentation_child = '  ' * (depth + 1)
        childs_string = ''
        for i in range(len(self.childs)):
            child = self.childs[i]
            #print(child.name + ' : ' + child.comment)
            comment_string = ''
            if child.comment != '':
                comment_string = ' //' + child.comment
            # add ',' if this is not the last child
            if i < len(self.childs) - 1:
                comment_string = ',' + comment_string
            if childs_string == '':
                childs_string = '\n' + indentation_child + child.repr_recursive(depth + 1) + comment_string
            else:
                childs_string = childs_string + '\n' + indentation_child + child.repr_recursive(depth + 1) + comment_string
        if childs_string == '':
            if self.can_have_childs:
                return self.name + '<>'
            else:
                return self.name
        else:
            return self.name + '<' + childs_string + '\n' + indentation + '>'

    # this function can compare this Node to another Node
    # returning True if equal, False otherwise
    def compare(self, node):
        if self.name != node.name:
            return False
        if self.comment != node.comment:
            #print(self.name + ' : ' + self.comment + ' =! ' + node.comment)
            return False
        if self.can_have_childs != node.can_have_childs:
            return False
        if len(self.childs) != len(node.childs):
            return False
        for i in range(len(self.childs)):
            if self.childs[i].compare(node.childs[i]) == False:
                return False
        return True

    ## creates a SettingsDict with default settings recursively
    #def get_default_settings_dict(self):
    #    relevant_src = get_default_python_settings_src_for_classname(self.name)
    #    own_dict = SettingsDict(relevant_src)
    #    for child in self.childs:
    #        # for every child replace the ### CHILD ### placeholder with the childs dict
    #        child_dict = child.get_default_settings_dict()
    #        own_dict.replaceChildPlaceholder(child_dict)
    #    return own_dict


# this class holds a tree of Node objects
# the tree represents the structure of a example.cpp
class CPPTree:
    def __init__(self):
        # read in the template.cpp, so we don't have to read it in multiple times
        file_cpp_template = open("template.cpp", "r")
        self.cpp_template = file_cpp_template.read()
        file_cpp_template.close()

        #self.root = None

        self.root = Node()
        self.root.name = 'GLOBAL'

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

        self.settings_prefix = ''
        self.settings_postfix = ''


    # this function reads a string (normally the content of a example.cpp) and creates the tree from it
    def parse_cpp_src(self, problem):
        try:
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
            stack.append(Node())
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
                        child = Node()
                        stack[-1].can_have_childs = True
                        stack[-1].childs.append(child)
                        stack.append(child)
                        comment_node = child
                    elif char == ',':
                        comment_node = stack.pop()
                        child = Node()
                        stack[-1].childs.append(child)
                        stack.append(child)
                    elif char == '>':
                        stack.pop()
                        comment_node = stack[-1]
                        # remove empty child in case of <> we have can_have_childs for that
                        if stack[-1].childs[0].name == "":
                            stack[-1].childs = []
                    else:
                        stack[-1].name = stack[-1].name + char

            child = stack[0].childs[0]
            self.root.childs.append(child)
            #self.root = stack[0].childs[0]
        except:
            printe('failed to parse src')
            #traceback.print_exc()

    # this creates a string which contains the whole generated example.cpp source-code using the tree and the template.cpp
    def __repr__(self):
        index = self.cpp_template.find(' problem(settings)')
        return self.cpp_template[:index] + indent(str(self.root.childs[0]), '  ') + self.cpp_template[index:]

    # this checks if the tree is a valid combination of templates
    def validate_cpp_src(self):
        # not valid, if the root.childs[0] is not a runnable
        try:
            if self.root.childs[0].name not in self.runnables:
                printe(self.root.childs[0].name + ' does not exist or is not runnable')
                return False
            return self.validate_cpp_src_recursive(self.root.childs[0])
        except:
            # return false if self.root.name is None
            return False

    # helper function to make validate_src() recursive
    def validate_cpp_src_recursive(self, node):
        try:
            wanted_childs = self.combinations[node.name].get("template_arguments", [])
            argument_count_max = len(wanted_childs)
            argument_count_min = self.combinations[node.name].get("template_arguments_needed", argument_count_max)
        except:
            # if the key node.name does not exist, we are at the bottom
            return True
        if "template_arguments" not in self.combinations[node.name] and node.can_have_childs:
            printe(node.name + ' can not have any template_arguments (not even <>)')
            return False
        if argument_count_min > len(node.childs) or len(node.childs) > argument_count_max:
            printe(node.name + ' has the wrong number of template_arguments')
            return False
        for i in range(len(node.childs)):
            if wanted_childs[i] == ["Integer"]:
                try:
                    int(node.childs[i].name)
                except:
                    printe(node.childs[i].name + ' is not an Integer')
                    return False
            elif node.childs[i].name not in wanted_childs[i]:
                printe(node.childs[i].name + ' is not in the list of possible template_arguments:\n' + str(wanted_childs[i]))
                return False
            if self.validate_cpp_src_recursive(node.childs[i]) == False:
                return False
        return True

    # this function returns a list of all possible childs of a given class
    def get_possible_childs(self, name):
        return self.combinations[name]["template_arguments"]

    ## after parsing the cpp_src, we can parse the python settings and map them to the nodes
    def parse_python_settings(self, settings):
        # save PythonSettings so we also have the prefix and postfix
        self.python_settings = PythonSettings(settings)
        self.root.parse_python_settings_recursive(self.python_settings.config_dict)

    def get_python_settings_dict(self):
        config_dict = self.root.get_python_settings_dict_recursive()
        self.python_settings.config_dict = config_dict
        return config_dict


# returns the python-src of the python_options for a given classname from possible_solver_combinations
def get_default_python_settings_src_for_classname(name):
    try:
        # TODO save possible_solver_combinations_src in a global variable, so its only loaded once and not every time this function is called
        possible_solver_combinations_src = inspect.getsource(possible_solver_combinations)
        return possible_solver_combinations_src.split('"' + name + '" : {')[1].split('\n    }')[0].split('"python_options" : {')[1].split('\n        }')[0]
    except:
        if '::' in name:
            #print(name[:-2].rsplit('::', 1, )[0] + '::')
            if name.split('::')[1] == '':
                return
            return get_default_python_settings_src_for_classname(name[:-2].rsplit('::', 1, )[0] + '::')
        return
