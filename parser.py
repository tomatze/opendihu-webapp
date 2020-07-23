#!/usr/bin/python3
import re
import sys
import traceback

from tokenize import tokenize, untokenize, NUMBER, STRING, NAME, OP
import token
from io import BytesIO

#TODO
class SettingsComment:
    def __init__(self):
        pass
# this class represents a python-setting with potential subsettings
class SettingsDictEntry:
    def __init__(self):
        self.key = None
        self.value = None
        self.comment = None

    def __repr__(self):
        return str(self.key) + ' : ' + str(self.value)

class SettingsListEntry:
    def __init__(self):
        self.value = None
        self.comment = None

    def __repr__(self):
        return str(self.value)

class SettingsDict(list):
    def dummy_function(self):
        pass
class SettingsList(list):
    def dummy_function(self):
        pass

# this class represents a Node in the structure tree (Example.root e.g. is such a Node)
class Node:
    def __init__(self):
        self.name = ''
        self.comment = ''
        self.can_have_childs = False
        self.childs = []

    # this function converts the tree under this Node to a pretty string
    # you can print the string to visualize the tree
    # this is also used to created cpp-source-code from a tree
    def __repr__(self):
        root_comment = ''
        if self.comment != '':
            root_comment = '//' + self.comment + '\n'
        return root_comment + self.repr_recursive(0)
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


# this class holds a tree of Node objects
# the tree represents the structure of a example.cpp
class Example:
    def __init__(self):
        # read in the template.cpp, so we don't have to read it in multiple times
        file_cpp_template = open("template.cpp", "r")
        self.cpp_template = file_cpp_template.read()
        file_cpp_template.close()

        self.root = None

        # import possible combinations
        from possible_solver_combinations import possible_solver_combinations
        self.combinations = possible_solver_combinations

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
    def parse_src(self, problem):
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

            self.root = stack[0].childs[0]
        except:
            printe('failed to parse src')
            #traceback.print_exc()

    # this creates a string which contains the whole generated example.cpp source-code using the tree and the template.cpp
    def create_src(self):
        index = self.cpp_template.find(' problem(settings)')
        return self.cpp_template[:index] + indent(str(self.root), '  ') + self.cpp_template[index:]

    # this checks if the tree is a valid combination of templates
    def validate_src(self):
        # not valid, if the root is not a runnable
        try:
            if self.root.name not in self.runnables:
                printe(self.root.name + ' does not exist or is not runnable')
                return False
            return self.validate_src_recursive(self.root)
        except:
            # return false if self.root.name is None
            return False

    # helper function to make validate_src() recursive
    def validate_src_recursive(self, node):
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
            if self.validate_src_recursive(node.childs[i]) == False:
                return False
        return True

    # this function returns a list of all possible childs of a given class
    def get_possible_childs(self, name):
        return self.combinations[name]["template_arguments"]


    def parse_settings(self, settings):
        #try:
        # isolate content of config{} to settings and save the rest of the file settings_prefix and settings_postfix
        split1 = settings.split('config = {\n')
        self.settings_prefix = split1[0]
        settings = split1[1]
        split2 = re.compile(r'(?m)^}').split(settings, 1)
        settings = split2[0]
        self.settings_postfix = split2[1]
        # split settings into tokens using tokenize from the stdlib
        tokens = tokenize(BytesIO(settings.encode('utf-8')).readline)

        # iterate over tokens to create SettingsDict
        config = SettingsDict()
        stack = []
        stack.append(config)
        mode_stack = []
        mode_stack.append("key")
        nested_counter = 0
        for t in tokens:
            token_value = t.string
            token_type = t.exact_type
            #print(token.tok_name[token_type] + token_value)
            if mode_stack[-1] == "key":
                if token_type == token.STRING or token_type == token.NUMBER:
                    # we got a new key (keys are always token.STRING or token.NUMBER)
                    if len(stack[-1]) == 0 or stack[-1][-1].key is not None:
                        # list is empty or last entry has key already -> add entry
                        stack[-1].append(SettingsDictEntry())
                    stack[-1][-1].key = token_value
                elif token_type == token.COMMENT:
                    # add the comment to the last list entry
                    # TODO this will fail on empty list
                    try:
                        stack[-1][-1].comment = token_value
                    except:
                        printe("cannot add comment. list is empty")
                elif token_type == token.COLON:
                    mode_stack.append("value")
                elif token_type == token.ENCODING or token_type == token.INDENT or token_type == token.NEWLINE or token_type == token.NL or token_type == token.DEDENT or token_type == token.ENDMARKER:
                    # ignore some tokens
                    pass
                elif token_type == token.COMMA:
                    # ignore comma if not in value or list mode
                    pass
                else:
                    printe("should not be reached " + token_value + " " + t.line)

            elif mode_stack[-1] == "value" or mode_stack[-1] == "list":
                # handle comma ',' (only if we are not in nested braces)
                if nested_counter == 0 and token_type == token.COMMA:
                    if isinstance(stack[-1], SettingsDict):
                        mode_stack.pop()
                    else:
                        stack[-1].append(SettingsListEntry())
                    continue

                # handle curly braces '{}'
                if token_type == token.LBRACE:
                    if nested_counter == 0:
                        mode_stack.append("key")
                        value = SettingsDict()
                        stack[-1][-1].value = value
                        stack.append(value)
                        continue
                if token_type == token.RBRACE:
                    if nested_counter == 0:
                        # pop 2 times because of key+value on mode_stack
                        mode_stack.pop()
                        mode_stack.pop()
                        stack.pop()
                        continue

                # handle square brackets '[]'
                if token_type == token.LSQB:
                    if nested_counter == 0:
                        mode_stack.append("list")
                        # detected child list
                        value = SettingsList()
                        value.append(SettingsListEntry())
                        stack[-1][-1].value = value
                        stack.append(value)
                        continue
                if token_type == token.RSQB:
                    if nested_counter == 0:
                        mode_stack.pop()
                        stack.pop()
                        continue

                # handle parentheses '()'
                if token_type == token.LPAR:
                    nested_counter = nested_counter + 1
                if token_type == token.RPAR:
                    nested_counter = nested_counter - 1

                # ignore newlines
                if token_type == token.NEWLINE or token_type == token.NL:
                    continue
                # if not already continued, token_value must be part of the value
                # TODO don't always add a space (e.g. not before and after '.')
                if stack[-1][-1].value == None:
                    stack[-1][-1].value = str(token_value)
                else:
                    stack[-1][-1].value = str(stack[-1][-1].value) + " " + token_value


        print(config)

        #except:
        #    printe('failed to parse settings')

def main():
    src = open(str(sys.argv[1]), "r").read()
    settings = open(str(sys.argv[2]), "r").read()

    example = Example()

    example.parse_src(src)
    #print(example.root)
    #print(example.combinations)
    print(example.validate_src())
    print('\n')
    print(example.create_src())
    #print(example.get_possible_childs('SpatialDiscretization::FiniteElementMethod'))

    example.parse_settings(settings)

# helper function to indent a multiline-string by a given indentation
def indent(lines, indentation):
    return indentation + lines.replace('\n', '\n' + indentation)

def printe(message):
    print('Error: ' + message, file=sys.stderr)

if __name__ == "__main__":
    main()
