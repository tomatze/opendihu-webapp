#!/usr/bin/python3
import re
import sys

# this class represents a Node in the structure tree (Example.root e.g. is such a Node)
class Node:
    def __init__(self):
        self.name = ''
        self.childs = []

    # this function converts the tree under this Node to a pretty string
    # you can print the string to visualize the tree
    # this is also used to created cpp-source-code from a tree
    def __repr__(self):
        return self.repr_recursive(0)
    def repr_recursive(self, depth):
        indentation = '  ' * depth
        indentation_child = '  ' * (depth + 1)
        childs_string = ''
        for child in self.childs:
            if childs_string == '':
                childs_string = '\n' + indentation_child + child.repr_recursive(depth + 1)
            else:
                childs_string = childs_string + ',\n' + indentation_child + child.repr_recursive(depth + 1)
        if childs_string == '':
            return self.name
        else:
            return self.name + '<' + childs_string + '\n' + indentation + '>'


# this class holds a tree of Node objects
# the tree represents the structure of a example.cpp
class Example:
    def __init__(self):
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


    # this function reads a string (normally the content of a example.cpp) and creates the tree from it
    def parse_src(self, src):
        try:
            # isolate problem
            #problem = src.split('settings(argc, argv);')[1].split(' problem(')[0]
            problem = src.split('settings(argc, argv);')[1]
            problem = re.compile('(.*)>(.*);').split(problem)[0] + '>'
            # remove comments from problem
            problem = re.sub(r'(?m)(^.*)//.*\n?', r'\1\n', problem)
            # TODO maybe also remove multi-line comments
            # remove newlines tabs and spaces from problem
            problem = re.sub(r'\s+', '', problem)

            # create tree from problem with a simple parser
            problem = '<' + problem + '>'
            stack = []
            stack.append(Node())
            name = ''
            for char in problem:
                if char == '<':
                    child = Node()
                    stack[-1].childs.append(child)
                    stack.append(child)
                elif char == ',':
                    stack.pop()
                    child = Node()
                    stack[-1].childs.append(child)
                    stack.append(child)
                elif char == '>':
                    stack.pop()
                else:
                    stack[-1].name = stack[-1].name + char

            self.root = stack[0].childs[0]
        except:
            print('Error: failed to parse ' + src, file=sys.stderr)

    # this creates a string which contains the whole generated example.cpp source-code using the tree and the template.cpp
    def create_src(self):
        cpp_template = open("template.cpp", "r").read()
        index = cpp_template.find(' problem(settings)')
        return cpp_template[:index] + indent(str(self.root), '  ') + cpp_template[index:]

    # this checks if the tree is a valid combination
    def validate_src(self):
        # not valid, if the root is not a runnable
        if self.root.name not in self.runnables:
            return False
        return self.validate_src_recursive(self.root)

    # helper function to make validate_src() recursive
    def validate_src_recursive(self, node):
        try:
            wanted_childs = self.combinations[node.name].get("template_arguments", [])
        except:
            # if the key node.name does not exist, we are at the bottom
            return True
        if len(wanted_childs) != len(node.childs):
            print('len does not match')
            return False
        for i in range(len(wanted_childs)):
            if wanted_childs[i] == ["Integer"]:
                try:
                    int(node.childs[i].name)
                except:
                    return False
            elif node.childs[i].name not in wanted_childs[i]:
                print(node.childs[i].name + ' not in wanted_childs[i]: ' + str(wanted_childs[i]))
                return False
            if self.validate_src_recursive(node.childs[i]) == False:
                return False
        return True

    # this function returns a list of all possible childs of a given class
    def get_possible_childs(self, name):
        return self.combinations[name]["template_arguments"]


    def parse_settings(self):
        pass

def main():
    #path_example = "../opendihu/examples/"
    #settings = open(path_example + "laplace/laplace1d/settings_linear_quadratic_dirichlet.py", "r").read()
    src = open(str(sys.argv[1]), "r").read()
    #src = open(path_example + "laplace/laplace1d/src/laplace_linear.cpp", "r").read()
    #src = open(path_example + "laplace/laplace3d_surface/src/laplace_surface.cpp", "r").read()
    #src = open(path_example + "electrophysiology/biceps_contraction/opendihu/src/biceps_contraction.cpp", "r").read()

    example = Example()

    example.parse_src(src)
    #print(example.root)
    #print(example.create_src())
    #print(example.combinations)
    print(example.validate_src())
    #print(example.get_possible_childs('SpatialDiscretization::FiniteElementMethod'))

# helper function to indent a multiline-string by a given indentation
def indent(lines, indentation):
    return indentation + lines.replace('\n', '\n' + indentation)

if __name__ == "__main__":
    main()
