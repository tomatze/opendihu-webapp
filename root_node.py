from node import Node
from helpers import printe, indent, Error, Info
from python_settings import PythonSettings, SettingsDict, SettingsList, SettingsListEntry, SettingsComment, SettingsDictEntry, SettingsChildPlaceholder, SettingsContainer, SettingsMesh, SettingsSolver, SettingsChoice

# specialized Node with some extra stuff
class RootNode(Node):
    def __init__(self, combinations, runnables):
        super().__init__(combinations)

        self.runnables = runnables

        self.name = 'GLOBAL'

        self.settings_dict_prefix = ''
        self.settings_dict_postfix = ''

        self.add_missing_default_python_settings(self.settings_dict)

    def get_python_settings(self):
        settings_dict = self.get_python_settings_dict_recursive()
        if not settings_dict:
            settings_dict = SettingsDict()
        python_settings = PythonSettings()
        python_settings.config_dict = settings_dict
        python_settings.prefix = self.settings_dict_prefix
        python_settings.postfix = self.settings_dict_postfix
        return python_settings

    # returns if the tree is a valid combination of templates or not
    def validate_cpp_src(self):
        # not valid, if the root.childs[0] is not a runnable
        try:
            if self.childs.get_real_childs()[0].name not in self.runnables:
                return Error(self.childs.get_real_childs()[0].name + ' does not exist or is not runnable')
            return self.validate_cpp_src_recursive(self.childs.get_real_childs()[0])
        except:
            # return false if self.childs[0].name is None
            return Error(self.name + ' needs exactly 1 child (0 given)')

    # helper function to make validate_src() recursive
    def validate_cpp_src_recursive(self, node):
        try:
            wanted_childs = self.combinations[node.name].get("template_arguments", [])
            argument_count_max = len(wanted_childs)
            argument_count_min = self.combinations[node.name].get("template_arguments_needed", argument_count_max)
        except:
            # if the key node.name does not exist, we are at the bottom
            return Info('cpp-src is valid')
        if "template_arguments" not in self.combinations[node.name] and node.can_have_childs:
            return Error(node.name + ' can not have any template_arguments (not even <>)')
        if argument_count_min > len(node.childs.get_real_childs()) or len(node.childs.get_real_childs()) > argument_count_max:
            return Error(node.name + ' has the wrong number of template_arguments')
        for i in range(len(node.childs.get_real_childs())):
            if wanted_childs[i] == ["Integer"]:
                try:
                    int(node.childs.get_real_childs()[i].name)
                except:
                    return Error(node.childs.get_real_childs()[i].name + ' is not an Integer')
            elif node.childs.get_real_childs()[i].name not in wanted_childs[i]:
                return Error(node.childs.get_real_childs()[i].name + ' is not in the list of possible template_arguments for ' + node.name + '\n' + 'possible template_arguments are: ' + str(wanted_childs[i]))
            res = self.validate_cpp_src_recursive(node.childs.get_real_childs()[i])
            if isinstance(res, Error):
                return res
        return Info('cpp-src is valid')
