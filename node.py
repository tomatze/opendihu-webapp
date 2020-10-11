import copy

from helpers import printe, indent, Error, Info, Warning
import possible_solver_combinations
from python_settings import PythonSettings, SettingsDict, SettingsList, SettingsListEntry, SettingsComment, SettingsDictEntry, SettingsChildPlaceholder, SettingsContainer, SettingsMesh, SettingsSolver, SettingsChoice

class Childs():
    def __init__(self, node):
        self.node = node
        # node.name is not populated yet, so we can't populate self.__childs with placeholders
        self.populated = False

    def populate(self):
        self.populated = True

        self.__childs = []
        self.combinations = self.node.combinations

        if not isinstance(self.node, PlaceholderNode) and self.node.name in self.node.combinations and "template_arguments" in self.node.combinations[self.node.name]:
            template_arguments = self.node.combinations[self.node.name]["template_arguments"]
            childs_count = len(template_arguments)
            if "template_arguments_needed" in self.node.combinations[self.node.name]:
                childs_count_needed = self.node.combinations[self.node.name]["template_arguments_needed"]
            else:
                childs_count_needed = childs_count

            for i in range(childs_count):
                if i <= childs_count_needed:
                    self.__childs.append(PlaceholderNode(self.combinations, needed=True))
                else:
                    self.__childs.append(PlaceholderNode(self.combinations, needed=False))

    def get_childs(self):
        if not self.populated:
            self.populate()
        return self.__childs

    def get_real_childs(self):
        if not self.populated:
            self.populate()
        ret = []
        for child in self.__childs:
            if not isinstance(child, PlaceholderNode):
                ret.append(child)
        return ret

    def replace(self, i, child):
        if not self.populated:
            self.populate()
        self.__childs[i] = child
        child.parent = self.node

    # normally gets called first
    def replace_next_placeholder(self, child):
        if not self.populated:
            self.populate()
        for i in range(len(self.__childs)):
            if isinstance(self.__childs[i], PlaceholderNode):
                self.replace(i, child)
                return
        # force adding the child if no PlaceholderNodes are left in self.__childs (in case of unknown templates)
        # TODO maybe message if this happens
        self.__childs.append(child)

    def clear(self):
        self.populate()


# this class represents a Node in the structure tree (Example.root e.g. is such a Node)
class Node:
    def __init__(self, combinations):
        self.combinations = combinations
        self.name = ''
        self.comment = ''
        self.can_have_childs = False
        self.childs = Childs(self)

        self.parent = None

        self.settings_dict = None
        self.settings_container_default = None

    # sets self.settings_container_default to the values gotten from possible_solver_combinations
    # this is not in __init__(), because self.name (used here) gets defined later
    def get_default_python_settings_dict(self):
        if self.settings_container_default == None:
            try:
                self.settings_container_default = possible_solver_combinations.possible_solver_combinations[self.name]["python_options"]
            except:
                # return an empty SettingsDict if nothing found
                print(self.name)
                self.settings_container_default = SettingsDict()
        return self.settings_container_default

    ## returns self.settings_dict with SettingsChildPlaceholders replaced with child dicts
    def get_python_settings_dict_recursive(self):
        # deepcopy self.settings_dict so we don't replace the SettingsChildPlaceholders in it
        own_dict = copy.deepcopy(self.settings_dict)
        for child in self.childs.get_real_childs():
            #print('child: ' + child.name)
            # for every child replace the ### CHILD ### placeholder with the childs dict
            try:
                child_dict = child.get_python_settings_dict_recursive()
                #print('replacing ' + child.name + ' placeholder with:\n' + str(child_dict))
                own_dict.replaceChildPlaceholder(child_dict)
            except:
                pass
                #print('failed to replace SettingsChildPlaceholder ' + child.name)
        return own_dict

    # this function recursively adds missing python-settings to self.settings_dict
    # returns number of added settings
    # TODO handle SettingsConditional (maybe with has_key?)
    def add_missing_default_python_settings(self, self_settings_container=None, settings_container_default=None, self_settings_global_dict=None):
        # counter for added settings
        changes = 0

        # init stuff and recurse childs if we are on the outer level of a node
        if self_settings_container == None and settings_container_default == None:
            # init settings_container_default
            settings_container_default = self.get_default_python_settings_dict()

            # init self_settings_container
            if self.settings_dict == None:
                self.settings_dict = SettingsDict()
            self_settings_container = self.settings_dict

            # init self_settings_global_dict if we are the root_node (e.g. if None)
            if self_settings_global_dict == None:
                self_settings_global_dict = self_settings_container

            # recurse childs
            childs_recurse= []
            # ignore childs that have an Integer as name
            for child in self.childs.get_real_childs():
                try:
                    int(child.name)
                except:
                    childs_recurse.append(child)
            for child in childs_recurse:
                changes = changes + child.add_missing_default_python_settings(self_settings_global_dict=self_settings_global_dict)

        # handle SettingsList
        if isinstance(self_settings_container, SettingsList):
            # add default_entry if missing
            if len(self_settings_container) == 0:
                default_entry = copy.deepcopy(settings_container_default[0])
                if not isinstance(default_entry.value, str):
                    default_entry.value = type(default_entry.value)()
                self_settings_container.append(default_entry)
            # recurse
            # if we have multiple entries just use settings_container_default[0] for all of them
            for entry in self_settings_container:
                if isinstance(entry, SettingsListEntry):
                    if not isinstance(entry.value, str):
                        settings_container_default_recurse = settings_container_default[0].value
                        changes = changes + self.add_missing_default_python_settings(self_settings_container=entry.value, settings_container_default=settings_container_default_recurse, self_settings_global_dict=self_settings_global_dict)
        # handle SettingsDict
        elif isinstance(self_settings_container, SettingsDict):
            # resolve all SettingsChoice to defaults
            if isinstance(settings_container_default, SettingsDict):
                settings_container_default_resolved = SettingsDict()
                for entry in settings_container_default:
                    if isinstance(entry, SettingsChoice):
                        add_alternatives = False
                        # look if some settings from alternatives already exist, in that case add alternatives instead of defaults
                        for e in entry.alternatives:
                            if self_settings_container.has_key(e.key):
                                add_alternatives = True
                                break
                        if add_alternatives:
                            for e in entry.alternatives:
                                settings_container_default_resolved.append(e)
                        else:
                            for e in entry.defaults:
                                settings_container_default_resolved.append(e)
                    else:
                        settings_container_default_resolved.append(entry)
                settings_container_default = settings_container_default_resolved

            # add missing default settings to this level (NOT recursive)
            for entry in settings_container_default:
                if isinstance(entry, SettingsChildPlaceholder):
                    placeholder_already_added = False
                    for e in self_settings_container:
                        if isinstance(e, SettingsChildPlaceholder) and e.childnumber == entry.childnumber:
                            placeholder_already_added = True
                            break
                    if not placeholder_already_added: self_settings_container.append(entry)

                elif isinstance(entry, SettingsDictEntry):
                    # add default-entry if we don't have the key already
                    if not self_settings_container.has_key(entry.key):
                        entry_copy = copy.deepcopy(entry)
                        if not isinstance(entry_copy.value, str):
                            # if entry_copy.value is not a string (then it is SettingsDict or SettingsList) -> replace it with empty one
                            entry_copy.value = type(entry_copy.value)()
                        else:
                            changes = changes + 1
                            print('added: ' + entry_copy.key + ':' + entry_copy.value)
                        self_settings_container.append(entry_copy)

                elif isinstance(entry, SettingsMesh) or isinstance(entry, SettingsSolver):
                    dict_to_append_to = None
                    # assume mesh is defined locally, if the first key exists already (the first key should be unique (e.g. not inputMeshIsGlobal))
                    if self_settings_container.has_key(entry[0].key):
                        # local
                        # add all missing keys
                        dict_to_append_to = self_settings_container
                    else:
                        # global
                        # add e.g. Meshes : {} if not there
                        if not self_settings_global_dict.has_key(entry.global_key):
                            self_settings_global_dict.append(SettingsDictEntry(entry.global_key, SettingsDict()))
                        dict = self_settings_global_dict.get_value(entry.global_key)
                        if not isinstance(dict, SettingsDict):
                            printe('we have to add to global,but global is not a dict')
                            # create a new dict it can add to so we don't have to break controlflow
                            # TODO counter gets broken by this hack
                            dict = SettingsDict()
                        # get the name e.g. mesh0
                        if self_settings_container.has_key(entry.name_key):
                            name = self_settings_container.get_value(entry.name_key)
                        else:
                            i = 0
                            name = ''
                            while True:
                                name = '"' + entry.name_prefix + str(i) + '"'
                                if not dict.has_key(name):
                                    break
                                i = i+1
                            self_settings_container.append(SettingsDictEntry(entry.name_key, name))
                            #changes = changes + 1
                        # add global dict entry if not there (e.g. Meshes : { mesh0 : {} })
                        if not dict.has_key(name):
                            dict.append(SettingsDictEntry(name, SettingsDict()))
                            #changes = changes + 1
                        dict_to_append_to = dict.get_value(name)

                    # add all missing keys recursively
                    changes = changes + self.add_missing_default_python_settings(self_settings_container=dict_to_append_to, settings_container_default=entry, self_settings_global_dict=self_settings_global_dict)

            # recurse levels
            for entry in self_settings_container:
                if isinstance(entry, SettingsDictEntry):
                    # recurse all keys that are no strings, those are SettingsDict and SettingsList
                    if not isinstance(entry.value, str) and settings_container_default.has_key(entry.key):
                        settings_container_default_recurse = settings_container_default.get_value(entry.key)
                        changes = changes + self.add_missing_default_python_settings(self_settings_container=entry.value, settings_container_default=settings_container_default_recurse, self_settings_global_dict=self_settings_global_dict)
        #except:
        #    printe('something went wrong while adding missing python-settings')

        return changes

    # delete self.settings_dict recursively
    def delete_python_settings(self):
        self.settings_dict = None
        for child in self.childs.get_real_childs():
            child.delete_python_settings()

    # parse PythonSettings and keep prefix and postfix
    # returns a list of Warnings
    def parse_python_settings(self, python_settings, keep_entries_that_have_no_default):
        # remove all old python-settings
        self.delete_python_settings()
        self.settings_dict_prefix = python_settings.prefix
        self.settings_dict_postfix = python_settings.postfix
        (_, warnings) = self.parse_python_settings_recursive(python_settings.config_dict, keep_entries_that_have_no_default=keep_entries_that_have_no_default)
        warnings.append(Info('added python-settings to ' + str(self.name)))
        return warnings

    # parse a python_settings_dict and add it to this Node and its childs
    # returns (rest, warnings)
    # rest is only not None in recursive calls on childs and can be ignored if called from outside
    # warnings is a list of Warnings
    def parse_python_settings_recursive(self, settings_container, keep_entries_that_have_no_default=False, self_settings_container=None, settings_container_default=None, is_called_on_child=False, warnings=[]):
        # TODO SettingsConditional? 
        # TODO if a SettingsDictEntry has no comment, add the default-comment (extra function)
        # these should be given as parameters when recursion happens on the same object again
        # self_settings_container is a reference to the sub-SettingsDict in self.settings_dict we are currently handling
        # settings_container_default is a reference to the sub-SettingsDict in settings_container_default we are currently handling
        if self_settings_container == None:
            if self.settings_dict == None:
                self.settings_dict = SettingsDict()
            self_settings_container = self.settings_dict
        if settings_container_default == None:
            settings_container_default = self.get_default_python_settings_dict()

        # create a list with all child_placeholders at this level
        child_placeholders = []
        # here we assume that SettingsChildPlaceholders never accur inside SettingsChoice (SettingsChoice of settings_container_default are not resolved here)
        for entry in settings_container_default:
            if isinstance(entry, SettingsChildPlaceholder):
                child_placeholders.append(entry)

        #if is_called_on_child:
        rest = SettingsDict()

        for i in range(len(settings_container)):
            entry = settings_container[i]

            # always keep Solvers and Meshes
            if isinstance(entry, SettingsDictEntry) and (entry.key == '"Solvers"' or entry.key == '"Meshes"'):
                self_settings_container.append(entry)
                continue

            if isinstance(entry, SettingsDictEntry) or isinstance(entry, SettingsListEntry):
                # resolve SettingsChoice inside settings_container_default
                # TODO maybe do this a little bit smarter (do not accept all things from the SettingsChoice (either defaults or alternatives))
                if isinstance(settings_container_default, SettingsDict):
                    settings_container_default_resolved = SettingsDict()
                    for e in settings_container_default:
                        if isinstance(e, SettingsChoice):
                            for default_e in e.defaults:
                                settings_container_default_resolved.append(default_e)
                            for alternative_e in e.alternatives:
                                settings_container_default_resolved.append(alternative_e)
                        else:
                            settings_container_default_resolved.append(e)
                    settings_container_default = settings_container_default_resolved

                # check if the entry is a SettingsListEntry or if it is a SettingsDictEntry and its key is in the defaults
                if isinstance(entry, SettingsListEntry) or settings_container_default.has_key(entry.key):
                    # key exists in defaults
                    # if the value is a SettingsContainer -> recurse
                    if isinstance(entry.value, SettingsContainer):
                        # create a new entry
                        settings_container_default_recurse = None
                        if isinstance(entry, SettingsDictEntry):
                            new_entry = SettingsDictEntry()
                            new_entry.key = entry.key
                            settings_container_default_recurse = settings_container_default.get_value(entry.key)
                        else:
                            new_entry = SettingsListEntry()
                            # TODO here we assume that there is only one SettingsListEntry in python_options we just use the first one
                            settings_container_default_recurse = settings_container_default.get_first_SettingsListEntry().value
                        new_entry.comments = entry.comments

                        # add an empty list or dict to the new entry
                        if isinstance(entry.value, SettingsDict):
                            new_entry.value = SettingsDict()
                        else:
                            new_entry.value = SettingsList()
                            new_entry.value.list_comprehension = entry.value.list_comprehension
                        # add the new entry
                        self_settings_container.append(new_entry)

                        # recurse the new entry
                        (_, warnings) = self.parse_python_settings_recursive(entry.value, self_settings_container=new_entry.value, settings_container_default=settings_container_default_recurse, keep_entries_that_have_no_default=keep_entries_that_have_no_default, warnings=warnings)
                    else:
                        # if the entry.value is no SettingsContainer -> just append the entry
                        self_settings_container.append(entry)
                else:
                    # entry is a SettingsDictEntry
                    # and the key does not exist in defaults
                    # this entry possibly belongs to a child
                    new_dict = SettingsDict()
                    new_dict.append(entry)
                    # try giving the entry to the childs
                    for j in range(len(child_placeholders)):
                        #print('trying to give ' + str(entry.key) + ' to child ' + str(child_placeholders[j].childnumber))
                        # TODO does this work with the new child implementation?
                        child = self.childs.get_real_childs()[child_placeholders[j].childnumber]
                        print(child.name)
                        (new_dict, warnings) = child.parse_python_settings_recursive(new_dict, keep_entries_that_have_no_default=keep_entries_that_have_no_default, is_called_on_child=True)
                        if len(new_dict) == 0:
                            break

                    if len(new_dict) > 0:
                        # this entry is not in defaults and does not belong to a child
                        if is_called_on_child:
                            rest.append(entry)
                        elif keep_entries_that_have_no_default:
                            warnings.append(Warning(entry.key + ' is an unknown setting -> added it anyways'))
                            self_settings_container.append(entry)
                        else:
                            warnings.append(Warning(entry.key + ' is an unknown setting -> it was NOT added'))

            else:
                # always add SettingsComments
                self_settings_container.append(entry)

        # insert all SettingsChildPlaceholders that are in python_options on this level
        # we do this here, to always have the childs on the bottom for consistency
        # TODO append them to self_settings_container after first use and only the not used ones here at the bottom
        for child_placeholder in child_placeholders:
            self_settings_container.append(child_placeholder)

        return (rest, warnings)

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
        for i in range(len(self.childs.get_real_childs())):
            child = self.childs.get_real_childs()[i]
            #print(child.name + ' : ' + child.comment)
            comment_string = ''
            if child.comment != '':
                comment_string = ' //' + child.comment
            # add ',' if this is not the last child
            if i < len(self.childs.get_real_childs()) - 1:
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

    # this function can compare the cpp of this Node to another Node
    # returning True if equal, False otherwise
    def compare_cpp(self, node):
        if self.name != node.name:
            return False
        if self.comment != node.comment:
            #print(self.name + ' : ' + self.comment + ' =! ' + node.comment)
            return False
        if self.can_have_childs != node.can_have_childs:
            return False
        if len(self.childs.get_real_childs()) != len(node.childs.get_real_childs()):
            return False
        for i in range(len(self.childs.get_real_childs())):
            if self.childs.get_real_childs()[i].compare_cpp(node.childs.get_real_childs()[i]) == False:
                return False
        return True

class PlaceholderNode(Node):
    def __init__(self, combinations, needed):
        self.needed = needed
        super().__init__(combinations)
