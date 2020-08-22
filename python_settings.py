import re

from tokenize import tokenize, untokenize, NUMBER, STRING, NAME, OP
import token
from io import BytesIO

# a floating comment within a SettingsDict or SettingsList
class SettingsComment:
    def __init__(self):
        self.comment = None

# an empty line within a SettingsDict or SettingsList
# this is used to restore simple formatting
class SettingsEmptyLine: pass

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

# normal entry in a SettingsDict
class SettingsDictEntry:
    def __init__(self):
        self.key = None
        self.value = None
        self.comments = []

# represents a python-settings-dict
class SettingsDict(list):
    def __init__(self, settings = None):
        if settings == None:
            return

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
            #print(token.tok_name[token_type] + token_value)
            #print(stack)
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

# normal entry for a SettingsList
class SettingsListEntry:
    def __init__(self):
        self.value = None
        self.comments = []

# represents a list stored in a SettingsDictEntry.value or a SettingsListEntry.value
class SettingsList(list):
    def __init__(self):
        self.list_comprehension = None
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

class PythonSettings():
    dict = None
    # takes a string of a settings.py and parses its config-dict
    def __init__(self, settings):
        #try:
        # isolate content of config{} to settings and save the rest of the file settings_prefix and settings_postfix
        split1 = settings.split('config = {\n')
        self.settings_prefix = split1[0]
        settings = split1[1]
        split2 = re.compile(r'(?m)^}').split(settings, 1)
        settings = split2[0]
        self.settings_postfix = split2[1]

        # iterate over tokens to create SettingsDict
        self.dict = SettingsDict(settings)
                #print(config)

        #except:
        #    printe('failed to parse settings')

# helper function wrapping pythons untokenize-function to improve readability of the returned string
def tokens_to_string(tokens):
    return untokenize(tokens).splitlines()[-1].strip()

