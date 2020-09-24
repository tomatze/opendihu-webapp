#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')
from gi.repository import Gtk, Gio, GtkSource

from cpp_structure import CPPTree
from python_settings import PythonSettings
from helpers import Message, Error, Info
import possible_solver_combinations

class Window(Gtk.Window):
    def __init__(self):
        super(Window, self).__init__()

        self.init_ui()
        self.init_backend()

    def init_backend(self):
        self.cpp_tree = CPPTree()
        self.redraw_textview_cpp_code()
        self.redraw_treeview_cpp()

    #def on_button_verify_cpp_code(self, _):
    #    ret = self.cpp_tree.validate_cpp_src(self.cpp_tree)
    #    if isinstance(ret, Message):
    #        self.log_append_message(ret)
    #    else:
    #        self.redraw_textview_cpp_code()
    #        self.redraw_treeview_cpp()

    def on_button_apply_cpp_code(self, _):
        text_bounds = self.text_view_cpp_code.get_buffer().get_bounds()
        text = self.text_view_cpp_code.get_buffer().get_text(text_bounds[0], text_bounds[1], True)
        ret = self.cpp_tree.parse_cpp_src(text, validate_semantics=self.checkbox_validate_semantics.get_active())
        self.log_append_message(ret)
        if not isinstance(ret, Error):
            self.redraw_textview_cpp_code()
            self.redraw_treeview_cpp()

    def on_button_undo(self, _):
        ret = self.cpp_tree.undo_stack.undo()
        self.log_append_message(ret)
        if not isinstance(ret, Error):
            self.redraw_treeview_cpp()
            self.redraw_textview_cpp_code()

    def on_button_redo(self, _):
        ret = self.cpp_tree.undo_stack.redo()
        self.log_append_message(ret)
        if not isinstance(ret, Error):
            self.redraw_treeview_cpp()
            self.redraw_textview_cpp_code()

    def on_button_reset(self, _):
        ret = self.cpp_tree.reset()
        self.log_append_message(ret)
        self.redraw_treeview_cpp()
        self.redraw_textview_cpp_code()

    def redraw_textview_cpp_code(self):
        text = str(self.cpp_tree)
        self.text_view_cpp_code.get_buffer().set_text(text)

    def redraw_treeview_cpp(self):
        self.store_treeview_cpp.clear()
        self.redraw_treeview_cpp_recursive(self.cpp_tree.root, None)
        self.treeview_cpp.expand_all()

    def redraw_treeview_cpp_recursive(self, node, parent_row):
        row = self.store_treeview_cpp.append(parent_row, [node.name])
        for child in node.childs:
            self.redraw_treeview_cpp_recursive(child, row)

    def log_append_message(self, message):
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
        self.grid_main = Gtk.Grid(column_homogeneous=True)
        self.add(self.grid_main)

        # log (lower)
        self.text_view_log = Gtk.TextView()
        self.text_view_log.set_editable(False)
        buffer = self.text_view_log.get_buffer()
        iter = buffer.get_end_iter()
        self.log_text_mark_end = buffer.create_mark('the-end', iter, True)
        self.scroll_log = Gtk.ScrolledWindow()
        self.scroll_log.set_min_content_height(100)
        self.scroll_log.set_max_content_height(100)
        self.scroll_log.add(self.text_view_log)
        self.grid_main.add(self.scroll_log)

        # upper grid
        self.grid_upper = Gtk.Grid(column_homogeneous=True)
        self.grid_main.attach_next_to(self.grid_upper, self.scroll_log, Gtk.PositionType.TOP, 1, 1)

        # cpp side
        self.tabs_cpp = Gtk.Notebook()
        self.grid_upper.add(self.tabs_cpp)

        self.grid_cpp_code = Gtk.Grid()

        #self.text_view_cpp_code = Gtk.TextView()
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

        self.tabs_cpp.append_page(self.grid_cpp_code, Gtk.Label(label='cpp-src'))

        self.store_treeview_cpp = Gtk.TreeStore(str)
        self.treeview_cpp = Gtk.TreeView(model=self.store_treeview_cpp)
        self.treeview_cpp.set_vexpand(True)
        self.treeview_cpp.set_hexpand(True)
        tvcolumn = Gtk.TreeViewColumn()
        self.treeview_cpp.append_column(tvcolumn)

        cell = Gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 0)
        self.scroll_cpp_tree = Gtk.ScrolledWindow()
        self.scroll_cpp_tree.add(self.treeview_cpp)
        self.tabs_cpp.append_page(self.scroll_cpp_tree, Gtk.Label(label='cpp-tree'))


        # python side
        #self.text_view_python_code = Gtk.TextView()
        self.text_view_python_code = GtkSource.View()
        self.text_view_python_code.get_buffer().set_language(language_manager.get_language('python3'))
        self.scroll_python_code = Gtk.ScrolledWindow()
        self.scroll_python_code.add(self.text_view_python_code)
        self.grid_upper.attach_next_to(self.scroll_python_code, self.tabs_cpp, Gtk.PositionType.RIGHT, 1, 1)

win = Window()
win.show_all()
win.maximize()
Gtk.main()
