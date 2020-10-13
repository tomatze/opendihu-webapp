import re
import typing

from tokenize import tokenize, untokenize, NUMBER, STRING, NAME, OP
from helpers import Error
import token
from io import BytesIO

# a floating comment within a SettingsDict or SettingsList
class SettingsComment:
    def __init__(self):
        self.comment = None


# a placeholder in a SettingsDict, which can be replaced with some SettingsDictEntrys
# this gets created when parsing python_options from possible_solver_combinations
# it is marked with the floating comment '### CHILD ###'
class SettingsChildPlaceholder(SettingsComment):
    def __init__(self, childnumber):
        super().__init__()
        self.comment = '### CHILD ' + str(childnumber) + ' ###'
        self.childnumber = int(childnumber)


# an empty line within a SettingsDict or SettingsList
# this is used to restore simple formatting
class SettingsEmptyLine: pass

# holds 2 lists, one with default SettingsDictEntrys and one with alternative SettingsDictEntrys
class SettingsChoice:
    def __init__(self, defaults, alternatives):
        self.defaults = defaults
        self.alternatives = alternatives


# if-else block inside a SettingsDictEntry.value or a SettingsListEntry.value
class SettingsConditional():
    def __init__(self):
        self.condition = None
        self.if_block = None
        self.else_block = None
    def repr(self, depth):
        depth = depth - 1
        if isinstance(self.if_block, str):
            value1 = self.if_block
        else:
            value1 = self.if_block.repr(depth + 1)
        if isinstance(self.else_block, str):
            value2 = self.else_block
        else:
            value2 = self.else_block.repr(depth + 1)
        return value1 + ' if ' + self.condition + ' else ' + value2


# this class is the parent of SettingsDict and SettingsList
class SettingsContainer(list):
    # replaces the first found SettingsChildPlaceholder with the entries of child_dict
    def replaceChildPlaceholder(self, child_dict):
        for i in range(len(self)):
            entry = self[i]
            if isinstance(entry, SettingsChildPlaceholder):
                self.pop(i)
                while len(child_dict) > 0:
                    self.insert(i, child_dict.pop())
                return True
            elif (isinstance(entry, SettingsListEntry) or isinstance(entry, SettingsDictEntry)) and isinstance(entry.value, SettingsContainer):
                if entry.value.replaceChildPlaceholder(child_dict):
                    return True

    # counts the SettingsChildPlaceholder that are direct childs of this SettingsContainer
    def count_child_placeholders(self):
        count = 0
        for entry in self:
            if isinstance(entry, SettingsChildPlaceholder):
                count = count + 1
        return count


# normal entry in a SettingsDict
class SettingsDictEntry:
    def __init__(self, key=None, value=None, comment=None):
        if isinstance(key, str) and not key[0] == '"':
            self.key = '"' + key + '"'
        else:
            self.key = key
        self.value = value
        self.comments = []
        if comment:
            self.comments.append('#' + comment)


# normal entry for a SettingsList
class SettingsListEntry:
    def __init__(self, value=None, comment=None):
        self.value = value
        self.comments = []
        if comment:
            self.comments.append('#' + comment)


# represents a python-settings-dict
class SettingsDict(SettingsContainer):
    # init an empty SettingsDict or parse a settings-string to a SettingsDict
    # you can also give this a list with entries
    def __init__(self, settings=None):
        if settings == None:
            return
        elif isinstance(settings, typing.List):
            for entry in settings:
                self.append(entry)
            return

        # remove outer braces
        settings = settings[1:][:-1]

        # split settings into tokens using tokenize from the stdlib
        tokens = tokenize(BytesIO(settings.encode('utf-8')).readline)

        stack = []
        stack.append(self)
        mode_stack = []
        mode_stack.append("dict_key")
        nested_counter = 0

        token_buffer = []
        append_comment = False
        token_type_last = None
        for t in tokens:
            token_value = t.string
            token_type = t.exact_type
            #print()
            #try:
            #    print(stack[0])
            #except: pass
            #print(type(stack[-1]))
            #print(mode_stack)
            #print(token.tok_name[token_type] + token_value)
            if token_type == token.NL or token_type == token.NEWLINE:
                # don't append comments to SettingsDictEntry or SettingsListEntry after newline
                append_comment = False
                # handle empty lines
                if token_type_last == token.NL or token_type_last == token.NEWLINE:
                    stack[-1].append(SettingsEmptyLine())
            # handle comments
            elif token_type == token.COMMENT:
                if append_comment:
                    # append the comment to the last list entry
                    stack[-1][-1].comments.append(token_value)
                else:
                    reg_child_placeholder = re.compile('### CHILD [0-9] ###')
                    match_child_placeholder = reg_child_placeholder.match(token_value)
                    #reg_link_placeholder = re.compile('### [A-Z]+ ###')
                    #match_link_placeholder = reg_link_placeholder.match(token_value)
                    if match_child_placeholder:
                        c = SettingsChildPlaceholder(token_value[10:-4])
                    #elif match_link_placeholder:
                    #    c = SettingsLinkPlaceholder(token_value[4:-4])
                    else:
                        # add floating comment to the current SettingsDict or SettingsList
                        c = SettingsComment()
                        c.comment = token_value
                    stack[-1].append(c)
            # handle curly braces '{}'
            elif token_type == token.LBRACE:
                if mode_stack[-1] == "list_comprehension" or mode_stack[-1] == 'conditional':
                    nested_counter = nested_counter + 1
                elif nested_counter == 0:
                    mode_stack.append("dict_key")
                    dict = SettingsDict()
                    if isinstance(stack[-1], SettingsList):
                        stack[-1].append(SettingsListEntry())
                    if isinstance(mode_stack[-1], SettingsConditional):
                        stack[-1].else_block = list
                    else:
                        stack[-1][-1].value = dict
                    stack.append(dict)
                    append_comment = False
            elif token_type == token.RBRACE:
                if mode_stack[-1] == "list_comprehension" or mode_stack[-1] == 'conditional':
                    nested_counter = nested_counter - 1
                elif nested_counter == 0:
                    if len(token_buffer) > 0:
                        stack[-1][-1].value = tokens_to_string(token_buffer)
                        token_buffer = []
                    # pop 2 times because of key+value on mode_stack
                    mode_stack.pop()
                    mode_stack.pop()
                    stack.pop()
                    append_comment = True
            # handle square brackets '[]'
            elif token_type == token.LSQB:
                if mode_stack[-1] == "list_comprehension" or mode_stack[-1] == 'conditional':
                    nested_counter = nested_counter + 1
                elif nested_counter == 0:
                    mode_stack.append("list")
                    # detected child list
                    list = SettingsList()
                    if isinstance(stack[-1], SettingsList):
                        stack[-1].append(SettingsListEntry())
                    if isinstance(stack[-1], SettingsConditional):
                        stack[-1].else_block = list
                    else:
                        stack[-1][-1].value = list
                    stack.append(list)
                    append_comment = False
            elif token_type == token.RSQB:
                if mode_stack[-1] == "list_comprehension":
                    if nested_counter == 1:
                        stack[-1].list_comprehension = tokens_to_string(token_buffer)
                        token_buffer = []
                        nested_counter = 0
                        stack.pop()
                        mode_stack.pop()
                        mode_stack.pop()
                    else:
                        nested_counter = nested_counter - 1
                elif mode_stack[-1] == 'conditional':
                    nested_counter = nested_counter - 1
                elif nested_counter == 0:
                    if len(token_buffer) > 0:
                        if isinstance(stack[-1], SettingsList):
                            list_entry = SettingsListEntry()
                            list_entry.value = tokens_to_string(token_buffer)
                            stack[-1].append(list_entry)
                        token_buffer = []
                    mode_stack.pop()
                    stack.pop()
                    append_comment = True
                    if isinstance(stack[-1], SettingsConditional):
                        # also pop the SettingsConditional, we are done with that
                        stack.pop()

            # handle dictionary keys
            elif mode_stack[-1] == "dict_key":
                if token_type == token.STRING or token_type == token.NUMBER:
                    # we got a new key (keys are always token.STRING or token.NUMBER)
                    stack[-1].append(SettingsDictEntry())
                    append_comment = True
                    stack[-1][-1].key = token_value
                elif token_type == token.COLON:
                    mode_stack.append("dict_value")

            # handle dictionary values and list entries
            elif mode_stack[-1] == "dict_value" or mode_stack[-1] == "list" or mode_stack[-1] == "list_comprehension" or mode_stack[-1] == "conditional":
                # handle comma ',' (only if we are not in nested braces)
                if nested_counter == 0 and token_type == token.COMMA:
                    append_comment = True
                    if isinstance(stack[-1], SettingsDict):
                        if len(token_buffer) > 0:
                            stack[-1][-1].value = tokens_to_string(token_buffer)
                            token_buffer = []
                        mode_stack.pop()
                    else:
                        if len(token_buffer) > 0:
                            list_entry = SettingsListEntry()
                            list_entry.value = tokens_to_string(token_buffer)
                            stack[-1].append(list_entry)
                            token_buffer = []
                elif nested_counter == 0 and token_type == token.NAME and token_value == 'if':
                    nested_counter = nested_counter + 1
                    mode_stack.append('conditional')
                    # get the value of the last entry we added and replace it with a SettingsConditional containing the old value
                    first_condition_value = stack[-1][-1].value
                    stack[-1][-1].value = SettingsConditional()
                    stack[-1][-1].value.if_block = first_condition_value

                    stack.append(stack[-1][-1].value)
                elif mode_stack[-1] == 'conditional' and nested_counter == 1 and token_type == token.NAME and token_value == 'else':
                    nested_counter = 0
                    mode_stack.pop()
                    stack[-1].condition = tokens_to_string(token_buffer)
                    token_buffer = []
                else:
                    # handle list-comprehensions like [ ... for i in range 10]
                    if nested_counter == 0 and token_type == token.NAME and token_value == 'for':
                        nested_counter = nested_counter + 1
                        mode_stack.append('list_comprehension')

                    # handle other tokens
                    # if not already continued, token_value must be part of the value
                    token_buffer.append(t)

                    # handle parentheses '()'
                    if token_type == token.LPAR:
                        nested_counter = nested_counter + 1
                    if token_type == token.RPAR:
                        nested_counter = nested_counter - 1

            token_type_last = token_type


    def __repr__(self):
        return self.repr(0)
    def repr(self, depth):
        if len(self) == 0:
            return '{}'
        indentation = '  '
        r = ''
        for i in range(len(self)):
            entrie = self[i]
            if isinstance(entrie, SettingsDictEntry):
                comments = ''
                for comment in entrie.comments:
                    comments = comments + ' ' + comment
                if isinstance(entrie.value, str):
                    value = entrie.value
                else:
                    value = entrie.value.repr(depth + 1)
                optional_comma = ','
                if i == len(self) - 1:
                    optional_comma = ''
                entrie_r = indentation * (depth + 1) + entrie.key + ' : '+ value + optional_comma + comments
            elif isinstance(entrie, SettingsComment):
                entrie_r = indentation * (depth + 1) + entrie.comment
            elif isinstance(entrie, SettingsEmptyLine):
                entrie_r = ''
            r = r + '\n' + entrie_r
        return '{' + r + '\n' + indentation * depth + '}'

    def has_key(self, key):
        return any(isinstance(entry, SettingsDictEntry) and key == entry.key for entry in self)
    def get_value(self, key):
        for entry in self:
            if isinstance(entry, SettingsDictEntry) and entry.key == key:
                return entry.value
        return


class SettingsMesh(SettingsDict):
    def __init__(self, options):
        for entry in options:
            self.append(entry)
        self.name_key = '"meshName"'
        self.name_prefix = 'mesh'
        self.global_key = '"Meshes"'

class SettingsSolver(SettingsDict):
    def __init__(self, options):
        for entry in options:
            self.append(entry)
        self.name_key = '"solverName"'
        self.name_prefix = 'solver'
        self.global_key = '"Solvers"'


# represents a list stored in a SettingsDictEntry.value or a SettingsListEntry.value
class SettingsList(SettingsContainer):
    def __init__(self, entries=None):
        self.list_comprehension = None
        if entries:
            for entry in entries:
                self.append(entry)
    def __repr__(self):
        return self.repr(0)
    def repr(self, depth):
        if len(self) == 0:
            return '[]'
        indentation = '  '
        r = ''
        for i in range(len(self)):
            entrie = self[i]
            if isinstance(entrie, SettingsListEntry):
                comments = ''
                for comment in entrie.comments:
                    comments = comments + ' ' + comment
                if isinstance(entrie.value, str):
                    value = entrie.value
                else:
                    value = entrie.value.repr(depth + 1)
                optional_comma = ','
                comprehension = ''
                if i == len(self) - 1:
                    optional_comma = ''
                    if self.list_comprehension:
                        comprehension = ' ' + self.list_comprehension
                entrie_r = indentation * (depth + 1) + value + comprehension + optional_comma + comments
            elif isinstance(entrie, SettingsComment):
                entrie_r = indentation * (depth + 1) + entrie.comment
            elif isinstance(entrie, SettingsEmptyLine):
                entrie_r = ''
            r = r + '\n' + entrie_r
        return '[' + r + '\n' + indentation * depth + ']'

    def get_first_SettingsListEntry(self):
        for entry in self:
            if isinstance(entry, SettingsListEntry):
                return entry
        return


# this holds a complete settings.py by parsing its config-dict and storing the rest of the file in prefix and postfix
class PythonSettings():
    prefix = ''
    config_dict = None
    postfix = ''
    # takes a string of a settings.py and parses it
    def __init__(self, settings=None):
        if settings:
            # isolate content of config{} to settings and save the rest of the file settings_prefix and settings_postfix
            split1 = settings.split('config = {')
            self.prefix = split1[0][:-1]
            settings = split1[1]
            split2 = re.compile(r'(?m)^}').split(settings, 1)
            settings = split2[0]
            settings = '{' + settings + '}'
            self.postfix = split2[1][1:]

            # iterate over tokens to create SettingsDict
            self.config_dict = SettingsDict(settings)
            return None

    def __repr__(self):
        return self.prefix + '\nconfig = ' + str(self.config_dict) + self.postfix


# helper function wrapping pythons untokenize-function to improve readability of the returned string
def tokens_to_string(tokens):
    return untokenize(tokens).splitlines()[-1].strip()
