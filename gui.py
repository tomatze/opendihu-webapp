#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')
from gi.repository import Gtk, Gio, GtkSource, GObject, Gdk

from cpp_tree import CPPTree
from python_settings import PythonSettings
from helpers import Message, Error, Info
import possible_solver_combinations
from node import PlaceholderNode

# stores a node + its depth to view it in a ListBox
class NodeLine(GObject.GObject):
    def __init__(self, node, depth):
        GObject.GObject.__init__(self)
        self.node = node
        self.depth = depth

class ButtonWithNode(Gtk.Button):
    def add_node(self, node):
        self.node = node

class Window(Gtk.Window):
    def __init__(self):
        super(Window, self).__init__()

        self.init_ui()
        self.init_backend()

    def init_backend(self):
        self.cpp_tree = CPPTree()
        self.redraw_textview_cpp_code()
        self.redraw_treeview_cpp()
        self.redraw_textview_python_code()

    def on_button_add_defaults_python_code(self, _):
        ret = self.cpp_tree.add_missing_default_python_settings()
        self.log_append_message(ret)
        self.redraw_textview_python_code()

    def on_button_apply_python_code(self, _):
        text_bounds = self.text_view_python_code.get_buffer().get_bounds()
        text = self.text_view_python_code.get_buffer().get_text(text_bounds[0], text_bounds[1], True)
        rets = self.cpp_tree.parse_python_settings(text)
        self.log_append_message(rets)
        if not isinstance(rets, Error):
            self.redraw_textview_python_code()

    def on_button_apply_cpp_code(self, _):
        text_bounds = self.text_view_cpp_code.get_buffer().get_bounds()
        text = self.text_view_cpp_code.get_buffer().get_text(text_bounds[0], text_bounds[1], True)
        ret = self.cpp_tree.parse_cpp_src(text, validate_semantics=self.checkbox_validate_semantics.get_active())
        self.log_append_message(ret)
        if not isinstance(ret, Error):
            self.redraw_textview_cpp_code()
            self.redraw_treeview_cpp()
            self.redraw_textview_python_code()

    def on_button_undo(self, _):
        ret = self.cpp_tree.undo_stack.undo()
        self.log_append_message(ret)
        if not isinstance(ret, Error):
            self.redraw_treeview_cpp()
            self.redraw_textview_cpp_code()
            self.redraw_textview_python_code()

    def on_button_redo(self, _):
        ret = self.cpp_tree.undo_stack.redo()
        self.log_append_message(ret)
        if not isinstance(ret, Error):
            self.redraw_treeview_cpp()
            self.redraw_textview_cpp_code()
            self.redraw_textview_python_code()

    def on_button_reset(self, _):
        ret = self.cpp_tree.reset()
        self.log_append_message(ret)
        self.redraw_treeview_cpp()
        self.redraw_textview_cpp_code()
        self.redraw_textview_python_code()

    def redraw_textview_python_code(self):
        text = str(self.cpp_tree.get_python_settings())
        self.text_view_python_code.get_buffer().set_text(text)

    def redraw_textview_cpp_code(self):
        text = str(self.cpp_tree)
        self.text_view_cpp_code.get_buffer().set_text(text)

    def redraw_treeview_cpp(self):
        #self.store_treeview_cpp.clear()
        #self.redraw_treeview_cpp_recursive(self.cpp_tree.root, None)
        #self.treeview_cpp.expand_all()

        self.cpp_treeview_store.remove_all()
        self.redraw_treeview_cpp_recursive(self.cpp_tree.root, 0)

    def redraw_treeview_cpp_recursive(self, node, depth):
        self.cpp_treeview_store.append(NodeLine(node, depth))
        for child in node.childs.get_childs():
            self.redraw_treeview_cpp_recursive(child, depth + 1)
        #self.cpp_treeview_store.append(NodeLine(None, depth + 1))
        #possible_childs = self.cpp_tree.get_possible_childs(node)

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
            def on_button_add_node(button):
                possible_replacements = button.node.get_possible_replacements()
                #print(possible_replacements)
                # TODO let the user select a choice from possible_replacements
                ret = self.cpp_tree.replace_node(node, possible_replacements[0])
                self.log_append_message(ret)
                self.redraw_treeview_cpp()
                self.redraw_textview_cpp_code()
                self.redraw_textview_python_code()
            button_add_node = ButtonWithNode(label=label)
            button_add_node.add_node(node)
            grid.add(button_add_node)
            button_add_node.connect("clicked", on_button_add_node)
        else:
            label = Gtk.Label(label=node.name)
            grid.add(label)
        grid.show_all()
        return grid

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

        #self.store_treeview_cpp = Gtk.TreeStore(str)
        #self.treeview_cpp = Gtk.TreeView(model=self.store_treeview_cpp)
        #self.treeview_cpp.set_vexpand(True)
        #self.treeview_cpp.set_hexpand(True)
        #tvcolumn = Gtk.TreeViewColumn()
        #self.treeview_cpp.append_column(tvcolumn)

        #cell = Gtk.CellRendererText()
        #tvcolumn.pack_start(cell, True)
        #tvcolumn.add_attribute(cell, 'text', 0)
        #self.scroll_cpp_treeview = Gtk.ScrolledWindow()
        #self.scroll_cpp_treeview.add(self.treeview_cpp)
        #self.tabs_cpp_treeview.append_page(self.scroll_cpp_treeview, Gtk.Label(label='C++'))

        self.cpp_treeview_store = Gio.ListStore()
        self.cpp_treeview_listbox = Gtk.ListBox()
        self.cpp_treeview_listbox.set_vexpand(True)
        self.cpp_treeview_listbox.set_hexpand(True)
        self.cpp_treeview_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.cpp_treeview_listbox.bind_model(self.cpp_treeview_store, self.cpp_treeview_listbox_create_widget)

        self.scroll_cpp_treeview = Gtk.ScrolledWindow()
        self.scroll_cpp_treeview.add(self.cpp_treeview_listbox)
        self.tabs_cpp_treeview.append_page(self.scroll_cpp_treeview, Gtk.Label(label='C++'))

        # python tree view
        self.tabs_python_treeview = Gtk.Notebook()
        self.grid_treeview.attach_next_to(self.tabs_python_treeview, self.tabs_cpp_treeview, Gtk.PositionType.RIGHT, 1, 1)
        self.scroll_python_treeview = Gtk.ScrolledWindow()
        self.tabs_python_treeview.append_page(self.scroll_python_treeview, Gtk.Label(label='Python'))

win = Window()
win.show_all()
win.maximize()
Gtk.main()
