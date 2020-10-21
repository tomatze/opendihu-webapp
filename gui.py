#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')
from gi.repository import Gtk, Gio, GtkSource, GObject, Gdk

from cpp_tree import CPPTree
from python_settings import PythonSettings
from helpers import Message, Error, Info, Warning
import possible_solver_combinations
from node import PlaceholderNode
from root_node import RootNode

# stores a node + its depth to view it in a ListBox
class NodeLine(GObject.GObject):
    def __init__(self, node, depth):
        GObject.GObject.__init__(self)
        self.node = node
        self.depth = depth

class ListBoxRowWithNode(Gtk.ListBoxRow):
    def add_node(self, node):
        self.node = node

class NodeReplaceWindow(Gtk.Window):
    def __init__(self, node, main_window):
        super(NodeReplaceWindow, self).__init__()

        grid = Gtk.Grid()
        self.add(grid)

        possible_replacements = node.get_possible_replacements()

        if [r for r in possible_replacements if r.name == 'Integer']:
            # Integer
            grid_entry = Gtk.Grid()
            grid_entry.add(Gtk.Label(label='Integer: '))
            entry = Gtk.Entry()
            if not isinstance(node, PlaceholderNode):
                text = str(node.name)
            else:
                text = '0'
            entry.set_text(text)
            grid_entry.add(entry)
            grid.add(grid_entry)

            def on_button_replace(_):
                integer = entry.get_text()
                try:
                    int(integer)
                except:
                    main_window.log_append_message(Error(str(integer) + ' is not a valid Integer'))
                    return
                replacement = node.get_int_replacement(integer)
                ret = main_window.cpp_tree.replace_node(node, replacement)
                main_window.log_append_message(ret)
                main_window.redraw_all()
                self.close()

            button_replace = Gtk.Button(label='replace')
            button_replace.connect("clicked", on_button_replace)
            grid.attach_next_to(button_replace, grid_entry, Gtk.PositionType.BOTTOM, 1, 1)

            def on_keypress(_, event):
                if event.keyval == Gdk.KEY_Escape:
                    self.close()
                elif event.keyval == Gdk.KEY_Return:
                    on_button_replace(_)
            self.connect('key-press-event', on_keypress)
        else:
            # no Integer
            def listbox_create_widget(node_line):
                listbox_row = ListBoxRowWithNode()
                listbox_row.add_node(node_line.node)
                grid = Gtk.Grid()
                grid.add(Gtk.Label(label=node_line.node.name))
                listbox_row.add(grid)
                return listbox_row

            store = Gio.ListStore()
            listbox = Gtk.ListBox()
            listbox.set_vexpand(True)
            listbox.set_hexpand(True)
            listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
            listbox.bind_model(store, listbox_create_widget)

            scroll = Gtk.ScrolledWindow()
            scroll.add(listbox)
            scroll.set_min_content_height(500)
            scroll.set_min_content_width(500)
            grid.add(scroll)

            def on_button_replace(_):
                replacement = listbox.get_selected_row().node
                replacement.add_missing_default_python_settings(main_window.cpp_tree.undo_stack.get_current_root().settings_dict)
                ret = main_window.cpp_tree.replace_node(node, replacement)
                main_window.log_append_message(ret)
                main_window.redraw_all()
                self.close()

            button_replace = Gtk.Button(label='replace')
            button_replace.connect("clicked", on_button_replace)

            listbox.set_activate_on_single_click(False)
            def row_double_clicked(_, row):
                on_button_replace(_)
            listbox.connect('row-activated', row_double_clicked)

            grid.attach_next_to(button_replace, scroll, Gtk.PositionType.BOTTOM, 1, 1)

            for replacement in possible_replacements:
                store.append(NodeLine(replacement, 0))

            def on_keypress(_, event):
                if event.keyval == Gdk.KEY_Escape:
                    self.close()
                elif event.keyval == Gdk.KEY_Return:
                    on_button_replace(_)
            self.connect('key-press-event', on_keypress)

        self.show_all()

class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()
        self.init_backend()

    def init_backend(self):
        self.cpp_tree = CPPTree()
        self.load_empty_simulation()

    def load_empty_simulation(self):
        ret = self.cpp_tree.load_empty_simulation()
        self.log_append_message(ret)
        self.redraw_all()


    def redraw_python(self):
        self.redraw_textview_python_code()
        self.redraw_treeview_python()

    def redraw_all(self):
        self.redraw_textview_cpp_code()
        self.redraw_treeview_cpp()
        self.redraw_python()

    def redraw_textview_python_code(self):
        text = str(self.cpp_tree.get_python_settings())
        self.text_view_python_code.get_buffer().set_text(text)

    def redraw_textview_cpp_code(self):
        text = str(self.cpp_tree)
        self.text_view_cpp_code.get_buffer().set_text(text)

    def redraw_treeview_cpp(self):
        self.cpp_treeview_store.remove_all()
        self.redraw_treeview_cpp_recursive(self.cpp_tree.undo_stack.get_current_root(), 0)

    def redraw_treeview_cpp_recursive(self, node, depth):
        self.cpp_treeview_store.append(NodeLine(node, depth))
        for child in node.childs.get_childs():
            self.redraw_treeview_cpp_recursive(child, depth + 1)

    def redraw_treeview_python(self):
        try:
            node = self.cpp_treeview_listbox.get_selected_row().node
            text = str(node.settings_dict)
        except:
            text = ''
        self.python_treeview_code.get_buffer().set_text(text)


    # binded to self.cpp_treeview_listbox
    # if we append item to self.cpp_treeview_store this function gets called and creates the widget
    def cpp_treeview_listbox_create_widget(self, list_node):
        node = list_node.node
        depth = list_node.depth

        grid = Gtk.Grid()
        for _ in range(depth):
            grid.add(Gtk.Label(label='  '))
        if isinstance(node, PlaceholderNode):
            if node.needed:
                color = Gdk.RGBA(1,0,0,.5)
                label = 'add necessary template'
            else:
                color = Gdk.RGBA(0,1,0,.5)
                label = 'add optional template'
            grid.override_background_color(Gtk.StateType.NORMAL, color)

            def on_button_add_node(_):
                self.cpp_treeview_replace_node(node)

            button_add_node = Gtk.Button(label=label)
            button_add_node.connect("clicked", on_button_add_node)
            grid.add(button_add_node)
        else:
            label = Gtk.Label(label=node.name)
            grid.add(label)
            if not isinstance(node, RootNode):
                spacer = Gtk.Label(label=' ')
                grid.add(spacer)
                button_delete_node = Gtk.Button()
                icon = Gio.ThemedIcon(name="edit-delete-symbolic")
                image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
                button_delete_node.add(image)
                def on_button_delete_node(_):
                    self.cpp_treeview_delete_node(node)
                button_delete_node.connect("clicked", on_button_delete_node)
                grid.add(button_delete_node)

            errors = node.validate_cpp_src()
            if errors:
                color = Gdk.RGBA(1,0,0,.5)
                s = ''
                for error in errors:
                   s = s + str(error) + '\n'
                grid.set_tooltip_text(s[:-1])
                #grid.connect("query-tooltip", on_row_tooltip)
            else:
                color = Gdk.RGBA(0,1,0,.5)
            grid.override_background_color(Gtk.StateType.NORMAL, color)
        grid.show_all()
        row = ListBoxRowWithNode()
        row.node = node
        row.add(grid)
        return row

    def cpp_treeview_replace_node(self, node):
        _window = NodeReplaceWindow(node, self)

    def cpp_treeview_delete_node(self, node):
        ret = self.cpp_tree.delete_node(node)
        self.log_append_message(ret)
        self.redraw_all()

    def log_append_message(self, message):
        if isinstance(message, list):
            for m in message:
                self.log_append_line(str(m), m.color)
        else:
            self.log_append_line(str(message), message.color)

    def log_append_line(self, text, color=None):
        buffer = self.text_view_log.get_buffer()
        iter = buffer.get_end_iter()
        col = ''
        if color:
            col = ' color="' + color + '"'
        for line in str(text).splitlines():
            if buffer.get_char_count() > 0:
                buffer.insert(iter, '\n')
            # move mark
            buffer.move_mark(self.log_text_mark_end, iter)
            buffer.insert_markup(iter, '<span' + col + '>' + line + '</span>', -1)
        # scroll to end
        self.text_view_log.scroll_to_mark(self.log_text_mark_end, 0, False, 0, 0)


    def on_button_add_defaults_python_code(self, _):
        ret = self.cpp_tree.add_missing_default_python_settings()
        self.log_append_message(ret)
        self.redraw_python()

    def on_button_apply_python_code(self, _):
        text_bounds = self.text_view_python_code.get_buffer().get_bounds()
        text = self.text_view_python_code.get_buffer().get_text(text_bounds[0], text_bounds[1], True)
        rets = self.cpp_tree.parse_python_settings(text)
        self.log_append_message(rets)
        if not isinstance(rets, Error):
            self.redraw_python()

    def on_button_apply_cpp_code(self, _):
        text_bounds = self.text_view_cpp_code.get_buffer().get_bounds()
        text = self.text_view_cpp_code.get_buffer().get_text(text_bounds[0], text_bounds[1], True)
        rets = self.cpp_tree.parse_cpp_src(text, validate_semantics=self.checkbox_validate_semantics.get_active())
        self.log_append_message(rets)
        if not any(isinstance(ret, Error) or isinstance(ret, Warning) for ret in rets):
            self.redraw_all()

    def on_button_undo(self, _):
        ret = self.cpp_tree.undo_stack.undo()
        self.log_append_message(ret)
        if not isinstance(ret, Error):
            self.redraw_all()

    def on_button_redo(self, _):
        ret = self.cpp_tree.undo_stack.redo()
        self.log_append_message(ret)
        if not isinstance(ret, Error):
            self.redraw_all()

    def on_button_reset(self, _):
        self.load_empty_simulation()

    def on_python_treeview_button_apply(self, _):
        try:
            node = self.cpp_treeview_listbox.get_selected_row().node

            text_bounds = self.python_treeview_code.get_buffer().get_bounds()
            text = self.python_treeview_code.get_buffer().get_text(text_bounds[0], text_bounds[1], True)

            rets = self.cpp_tree.parse_python_settings(text, node)
            self.log_append_message(rets)
            if not isinstance(rets, Error):
                self.redraw_treeview_python()
                self.redraw_textview_python_code()
        except:
            self.log_append_message(Error('Can\'t apply settings if no Node is selected'))

    def on_python_treeview_button_add_defaults(self, _):
        try:
            node = self.cpp_treeview_listbox.get_selected_row().node

            rets = self.cpp_tree.add_missing_default_python_settings(node)
            self.log_append_message(rets)
            if not isinstance(rets, Error):
                self.redraw_treeview_python()
                self.redraw_textview_python_code()
        except:
            self.log_append_message(Error('Can\'t add default settings if no Node is selected'))

    def init_ui(self):
        self.set_title("opendihu - webapp")
        self.connect("destroy", Gtk.main_quit)

        # header_bar
        self.header_bar = Gtk.HeaderBar()
        self.set_titlebar(self.header_bar)

        self.button_undo = Gtk.Button()
        icon = Gio.ThemedIcon(name="edit-undo-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.button_undo.add(image)
        self.button_undo.connect("clicked", self.on_button_undo)
        self.header_bar.pack_start(self.button_undo)

        self.button_redo = Gtk.Button()
        icon = Gio.ThemedIcon(name="edit-redo-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.button_redo.add(image)
        self.button_redo.connect("clicked", self.on_button_redo)
        self.header_bar.pack_start(self.button_redo)

        self.button_reset = Gtk.Button(label='load empty simulation')
        self.button_reset.connect("clicked", self.on_button_reset)
        self.header_bar.pack_start(self.button_reset)


        # main grid
        self.paned_main = Gtk.Paned.new(Gtk.Orientation.VERTICAL)
        self.add(self.paned_main)

        # log (lower)
        self.text_view_log = Gtk.TextView()
        self.text_view_log.set_editable(False)
        buffer = self.text_view_log.get_buffer()
        iter = buffer.get_end_iter()
        self.log_text_mark_end = buffer.create_mark('the-end', iter, True)
        self.scroll_log = Gtk.ScrolledWindow()
        self.scroll_log.set_min_content_height(100)
        self.scroll_log.add(self.text_view_log)
        self.tabs_log = Gtk.Notebook()
        self.tabs_log.append_page(self.scroll_log, Gtk.Label(label='log'))
        self.paned_main.pack2(self.tabs_log, resize=False, shrink=False)


        # upper tabs
        self.tabs_main = Gtk.Notebook()
        self.paned_main.pack1(self.tabs_main, resize=True, shrink=False)


        # code view
        self.grid_code_view = Gtk.Grid(column_homogeneous=True)
        self.tabs_main.append_page(self.grid_code_view, Gtk.Label(label='Code'))

        # cpp code view
        self.tabs_cpp_code = Gtk.Notebook()
        self.grid_code_view.add(self.tabs_cpp_code)

        self.grid_cpp_code = Gtk.Grid()

        self.text_view_cpp_code = GtkSource.View()
        language_manager = GtkSource.LanguageManager()
        self.text_view_cpp_code.get_buffer().set_language(language_manager.get_language('cpp'))
        self.text_view_cpp_code.set_vexpand(True)
        self.text_view_cpp_code.set_hexpand(True)
        self.scroll_cpp_code = Gtk.ScrolledWindow()
        self.scroll_cpp_code.add(self.text_view_cpp_code)
        self.grid_cpp_code.add(self.scroll_cpp_code)

        self.grid_cpp_code_buttons = Gtk.Grid()
        self.button_apply_cpp_code = Gtk.Button(label='apply changes')
        self.button_apply_cpp_code.connect("clicked", self.on_button_apply_cpp_code)
        #self.button_verify_cpp_code = Gtk.Button(label='validate')
        #self.button_verify_cpp_code.connect("clicked", self.on_button_verify_cpp_code)
        self.checkbox_validate_semantics = Gtk.CheckButton()
        self.checkbox_validate_semantics.set_label("check code for semantic errors")
        self.checkbox_validate_semantics.set_active(True)
        self.grid_cpp_code_buttons.add(self.button_apply_cpp_code)
        self.grid_cpp_code_buttons.attach_next_to(self.checkbox_validate_semantics, self.button_apply_cpp_code, Gtk.PositionType.RIGHT, 1, 1)
        self.grid_cpp_code.attach_next_to(self.grid_cpp_code_buttons, self.scroll_cpp_code, Gtk.PositionType.BOTTOM, 1, 1)

        self.tabs_cpp_code.append_page(self.grid_cpp_code, Gtk.Label(label='C++'))

        # python code view
        self.tabs_python_code = Gtk.Notebook()
        self.grid_code_view.attach_next_to(self.tabs_python_code, self.tabs_cpp_code, Gtk.PositionType.RIGHT, 1, 1)

        self.grid_python_code = Gtk.Grid()
        self.tabs_python_code.append_page(self.grid_python_code, Gtk.Label(label='Python'))

        self.text_view_python_code = GtkSource.View()
        self.text_view_python_code.get_buffer().set_language(language_manager.get_language('python3'))
        self.text_view_python_code.set_vexpand(True)
        self.text_view_python_code.set_hexpand(True)
        self.scroll_python_code = Gtk.ScrolledWindow()
        self.scroll_python_code.add(self.text_view_python_code)
        self.grid_python_code.add(self.scroll_python_code)

        self.grid_python_code_buttons = Gtk.Grid()
        self.grid_python_code.attach_next_to(self.grid_python_code_buttons, self.scroll_python_code, Gtk.PositionType.BOTTOM, 1, 1)

        self.button_apply_python_code = Gtk.Button(label='apply changes')
        self.button_apply_python_code.connect("clicked", self.on_button_apply_python_code)
        self.grid_python_code_buttons.add(self.button_apply_python_code)

        self.button_add_defaults_python_code = Gtk.Button(label='add default settings')
        self.button_add_defaults_python_code.connect("clicked", self.on_button_add_defaults_python_code)
        self.grid_python_code_buttons.attach_next_to(self.button_add_defaults_python_code, self.button_apply_python_code, Gtk.PositionType.RIGHT, 1, 1)


        # tree view
        self.grid_treeview = Gtk.Grid(column_homogeneous=True)
        self.tabs_main.append_page(self.grid_treeview, Gtk.Label(label='Tree'))

        # cpp tree view
        self.tabs_cpp_treeview = Gtk.Notebook()
        self.grid_treeview.add(self.tabs_cpp_treeview)

        self.cpp_treeview_store = Gio.ListStore()
        self.cpp_treeview_listbox = Gtk.ListBox()
        self.cpp_treeview_listbox.set_vexpand(True)
        self.cpp_treeview_listbox.set_hexpand(True)
        self.cpp_treeview_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.cpp_treeview_listbox.bind_model(self.cpp_treeview_store, self.cpp_treeview_listbox_create_widget)

        self.cpp_treeview_listbox.set_activate_on_single_click(False)
        def row_double_clicked(_, row):
            node = self.cpp_treeview_listbox.get_selected_row().node
            self.cpp_treeview_replace_node(node)
        self.cpp_treeview_listbox.connect('row-activated', row_double_clicked)
        def row_clicked(_, row):
            self.redraw_treeview_python()
        self.cpp_treeview_listbox.connect('row-selected', row_clicked)

        self.scroll_cpp_treeview = Gtk.ScrolledWindow()
        self.scroll_cpp_treeview.add(self.cpp_treeview_listbox)
        self.tabs_cpp_treeview.append_page(self.scroll_cpp_treeview, Gtk.Label(label='C++'))

        # python tree view
        self.python_treeview_tabs = Gtk.Notebook()
        self.grid_treeview.attach_next_to(self.python_treeview_tabs, self.tabs_cpp_treeview, Gtk.PositionType.RIGHT, 1, 1)
        self.python_treeview_grid = Gtk.Grid()
        self.python_treeview_tabs.append_page(self.python_treeview_grid, Gtk.Label(label='Python'))
        self.python_treeview_scroll = Gtk.ScrolledWindow()
        self.python_treeview_grid.add(self.python_treeview_scroll)

        self.python_treeview_code = GtkSource.View()
        self.python_treeview_code.get_buffer().set_language(language_manager.get_language('python3'))
        self.python_treeview_code.set_vexpand(True)
        self.python_treeview_code.set_hexpand(True)
        self.python_treeview_scroll.add(self.python_treeview_code)

        self.python_treeview_buttons = Gtk.Grid()
        self.python_treeview_grid.attach_next_to(self.python_treeview_buttons, self.python_treeview_scroll, Gtk.PositionType.BOTTOM, 1, 1)

        self.python_treeview_button_apply = Gtk.Button(label='apply changes')
        self.python_treeview_button_apply.connect("clicked", self.on_python_treeview_button_apply)
        self.python_treeview_buttons.add(self.python_treeview_button_apply)

        self.python_treeview_button_add_defaults = Gtk.Button(label='add default settings')
        self.python_treeview_button_add_defaults.connect("clicked", self.on_python_treeview_button_add_defaults)
        self.python_treeview_buttons.add(self.python_treeview_button_add_defaults)

win = MainWindow()
win.show_all()
win.maximize()
Gtk.main()
