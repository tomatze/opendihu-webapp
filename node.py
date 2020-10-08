import copy

from helpers import printe, indent, Error, Info
import possible_solver_combinations
from python_settings import PythonSettings, SettingsDict, SettingsList, SettingsListEntry, SettingsComment, SettingsDictEntry, SettingsChildPlaceholder, SettingsContainer, SettingsMesh, SettingsSolver, SettingsChoice

# this class represents a Node in the structure tree (Example.root e.g. is such a Node)
class Node:
    def __init__(self):
        self.name = ''
        self.comment = ''
        self.can_have_childs = False
        self.childs = []

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
                self.settings_container_default = SettingsDict()
        return self.settings_container_default

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
            for child in self.childs:
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
        for child in self.childs:
            child.delete_python_settings()

    # parse PythonSettings and keep prefix and postfix
    def parse_python_settings(self, python_settings):
        # remove all old python-settings
        self.delete_python_settings()
        self.settings_dict_prefix = python_settings.prefix
        self.settings_dict_postfix = python_settings.postfix
        return self.parse_python_settings_recursive(python_settings.config_dict)

    # parse a python_settings_dict and add it to this Node and its childs
    def parse_python_settings_recursive(self, settings_dict, keep_entries_that_have_no_default=True, self_settings_container=None, settings_dicts_default=None, is_called_on_child=False):
        # TODO SettingsConditional? 
        # TODO Meshes and Solvers e.g. with ### SOLVER ###?
        # TODO if a SettingsDictEntry has no comment, add the default-comment
        # TODO remove add_missing_default_entries and move it to a new function (this also needs to add missing SettingsChildPlaceholders)
        # TODO add a new function to load default settings (if user wants to reset)
        # TODO when adding new solver/mesh - always add it globally and look for the last solver-number and increase it by one
        # these should be given as parameters when recursion happens on the same object again
        # self_settings_container is the 'pointer' to the sub-SettingsDict in self.settings_dict we are currently handling
        # settings_container_default is the 'pointer' to the sub-SettingsDict in settings_container_default we are currently handling
        if self_settings_container == None:
            if self.settings_dict == None:
                self.settings_dict = SettingsDict()
            self_settings_container = self.settings_dict
        if settings_dicts_default == None:
            settings_dicts_default = self.get_default_python_settings_dict()

        # insert all child-placeholders that are in python_options on this level
        # TODO append them to self_settings_container after first use
        child_placeholders = []
        # TODO here we assume that the child_placeholders are the same in all settings_dicts_default
        for entry in settings_dicts_default[0]:
            if isinstance(entry, SettingsChildPlaceholder):
                self_settings_container.append(entry)
                child_placeholders.append(entry)

        #print(self_settings_container)

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

                # always keep Solvers and Meshes
                keep_entries_that_have_no_default_overwrite = keep_entries_that_have_no_default
                if isinstance(entry, SettingsDictEntry) and (entry.key == '"Solvers"' or entry.key == '"Meshes"'):
                    keep_entries_that_have_no_default_overwrite = True

                # check if the entry is a SettingsListEntry or if it is a SettingsDictEntry and its key is in any of the defaults
                if isinstance(entry, SettingsListEntry) or any(s.has_key(entry.key) for s in settings_dicts_default):
                    # key exists in defaults
                    # if the value is a SettingsContainer -> recurse
                    if isinstance(entry.value, SettingsContainer):
                        # create a new entry
                        settings_dicts_default_recurse = []
                        if isinstance(entry, SettingsDictEntry):
                            new_entry = SettingsDictEntry()
                            new_entry.key = entry.key
                            for settings_container_default in settings_dicts_default:
                                if settings_container_default.has_key(entry.key):
                                    settings_dicts_default_recurse.append(settings_container_default.get_value(entry.key))
                        else:
                            new_entry = SettingsListEntry()
                            for settings_container_default in settings_dicts_default:
                                # TODO here we assume that there is only one SettingsListEntry in python_options we just use the first one
                                settings_dicts_default_recurse.append(settings_container_default.get_first_SettingsListEntry().value)
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
                        self.parse_python_settings_recursive(entry.value, self_settings_container=new_entry.value, settings_dicts_default=settings_dicts_default_recurse, keep_entries_that_have_no_default=keep_entries_that_have_no_default_overwrite)
                    else:
                        # if the entry.value is not special -> just append the entry
                        self_settings_container.append(entry)
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
                            new_dict = child.parse_python_settings_recursive(new_dict, keep_entries_that_have_no_default=keep_entries_that_have_no_default, is_called_on_child=True)
                            if len(new_dict) == 0:
                                break
                        if len(new_dict) > 0:
                            #print('the childs did not take this entry')
                            if keep_entries_that_have_no_default:
                                self_settings_container.append(entry)
                    else:
                        # this entry is not in defaults and there is no child at this place
                        if is_called_on_child:
                            rest.append(entry)
                        elif keep_entries_that_have_no_default_overwrite:
                            self_settings_container.append(entry)

            #elif isinstance(entry, SettingsComment):
            else:
                self_settings_container.append(entry)

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
        if len(self.childs) != len(node.childs):
            return False
        for i in range(len(self.childs)):
            if self.childs[i].compare_cpp(node.childs[i]) == False:
                return False
        return True
