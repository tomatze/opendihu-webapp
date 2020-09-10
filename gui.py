#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

from cpp_structure import CPPTree
from python_settings import PythonSettings
import possible_solver_combinations

class Window(Gtk.Window):
    def __init__(self):
        super(Window, self).__init__()

        self.init_backend()
        self.init_ui()

    def init_backend(self):
        self.cpp_tree = CPPTree()

    def on_button_load_cpp_code(self, _):
        text_bounds = self.text_view_cpp_code.get_buffer().get_bounds()
        text = self.text_view_cpp_code.get_buffer().get_text(text_bounds[0], text_bounds[1], True)
        self.cpp_tree.parse_cpp_src(text)

        self.redraw_treeview_cpp()

    def redraw_treeview_cpp(self):
        root = self.cpp_tree.root

        self.redraw_treeview_cpp_recursive(root, None)
        #row1 = self.store_treeview_cpp.append(None, ['JAVA'])
        #self.store_treeview_cpp.append(row1,['AWT'])
        #self.store_treeview_cpp.append(row1,['Swing'])
        #self.store_treeview_cpp.append(row1,['JSF'])

        #row2 = self.store_treeview_cpp.append(None, ['Python'])
        #self.store_treeview_cpp.append(row2,['PyQt'])
        #self.store_treeview_cpp.append(row2,['WxPython'])
        #self.store_treeview_cpp.append(row2,['PyGTK'])

        self.treeview_cpp.expand_all()

    def redraw_treeview_cpp_recursive(self, node, parent_row):
        row = self.store_treeview_cpp.append(parent_row, [node.name])
        for child in node.childs:
            self.redraw_treeview_cpp_recursive(child, row)

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
        self.header_bar.pack_start(self.button_undo)

        self.button_redo = Gtk.Button()
        icon = Gio.ThemedIcon(name="edit-redo-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.button_redo.add(image)
        self.header_bar.pack_start(self.button_redo)


        # main grid
        self.grid_main = Gtk.Grid(column_homogeneous=True)
        self.add(self.grid_main)

        # cpp side
        self.tabs_cpp = Gtk.Notebook()
        self.grid_main.add(self.tabs_cpp)

        self.grid_cpp_code = Gtk.Grid()

        self.text_view_cpp_code = Gtk.TextView()
        self.text_view_cpp_code.set_vexpand(True)
        self.text_view_cpp_code.set_hexpand(True)
        self.scroll_cpp_code = Gtk.ScrolledWindow()
        self.scroll_cpp_code.add(self.text_view_cpp_code)
        self.grid_cpp_code.add(self.scroll_cpp_code)

        self.button_load_cpp_code = Gtk.Button(label='load code')
        self.button_load_cpp_code.connect("clicked", self.on_button_load_cpp_code)
        self.grid_cpp_code.attach_next_to(self.button_load_cpp_code, self.scroll_cpp_code, Gtk.PositionType.BOTTOM, 1, 1)

        self.tabs_cpp.append_page(self.grid_cpp_code, Gtk.Label('cpp-src'))

        self.store_treeview_cpp = Gtk.TreeStore(str)
        self.treeview_cpp = Gtk.TreeView(self.store_treeview_cpp)
        self.treeview_cpp.set_vexpand(True)
        self.treeview_cpp.set_hexpand(True)
        tvcolumn = Gtk.TreeViewColumn('cpp-structure')
        self.treeview_cpp.append_column(tvcolumn)

        cell = Gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 0)
        self.scroll_cpp_tree = Gtk.ScrolledWindow()
        self.scroll_cpp_tree.add(self.treeview_cpp)
        self.tabs_cpp.append_page(self.scroll_cpp_tree, Gtk.Label('cpp-tree'))


        # python side
        self.text_view_python_code = Gtk.TextView()
        self.scroll_python_code = Gtk.ScrolledWindow()
        self.scroll_python_code.add(self.text_view_python_code)
        self.grid_main.attach_next_to(self.scroll_python_code, self.tabs_cpp, Gtk.PositionType.RIGHT, 1, 1)

win = Window()
win.show_all()
win.maximize()
Gtk.main()
