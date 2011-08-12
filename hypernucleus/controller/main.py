'''
Created on 23 Jul 2011

@author: r
'''

from hypernucleus.view import main_path
from hypernucleus.model.ini_manager import INIManager, WindowDimentions
from hypernucleus.model.tree_model import TreeModel, TreeItem
from hypernucleus.model.xml_model import XmlModel as Model
from hypernucleus.library.module_installer import ModuleInstaller
from hypernucleus.model import (GAME, DEP, INSTALLED, NOT_INSTALLED,
                                INSTALLED_VERSION)
from hypernucleus.controller.helper_mixin import HelperMixin
from hypernucleus.controller.settings import SettingsDialog
from PyQt4.QtGui import QMainWindow
from PyQt4 import uic, QtCore, QtGui
import sys

class MainWindow(QMainWindow, HelperMixin):
    """
    The Main Window.
    """
    
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = uic.loadUi(main_path, self)
        
        # Set the window dimensions from config.
        self.ini_mgr = INIManager()
        dimentions = self.ini_mgr.get_window_dimentions()
        if dimentions:
            self.setGeometry(QtCore.QRect(dimentions.x, dimentions.y,
                                          dimentions.width, 
                                          dimentions.height))
        
        # Fill treeview with content.
        self.reset_models()
            
        # Connect all signals/events
        self.quick_connect("actionExit", "exit")
        self.quick_connect("actionRun", "run")
        self.quick_connect("actionStop", "stop")
        self.quick_connect("actionUninstall", "uninstall")
        self.quick_connect("actionSettings", "settings")
        self.ui.treeGame.doubleClicked.connect(self.game)
        self.ui.treeDep.doubleClicked.connect(self.dep)
        self.ui.treeGame.selectionChanged = self.game_selection_changed
        self.ui.treeDep.selectionChanged = self.dep_selection_changed
        
    def reset_models(self):
        """
        Reload items in treeview
        """
        # Reset dependency model
        list_model = TreeModel(["Name", "Version"])
        self.ui.dependenciesTreeView.setModel(list_model)
        
        # Clear the root/child items
        self.root_items = {GAME: {}, DEP: {}}

        # Make new models
        self.ui.treeGame.setModel(self.configure_model(GAME))
        self.ui.treeDep.setModel(self.configure_model(DEP))
        
        # Expand relevant nodes.
        part_one = [(GAME, self.ui.treeGame), (DEP, self.ui.treeDep)]
        part_two = [INSTALLED, NOT_INSTALLED]
        for one_key, one_tv in part_one:
            for two in part_two:
                self.expand(one_tv, self.root_items[one_key][two])
        
        for dummy, one_tv in part_one:
            one_tv.resizeColumnToContents(0)
            
    def configure_model(self, module_type):
        """
        Add items to a Tree View model.
        """
        # Make the title bar.
        tree_model = TreeModel(["Name", INSTALLED_VERSION])
        root_item = tree_model.rootItem
        
        # Add Installed root item
        ins = TreeItem([INSTALLED, ''], root_item)
        self.root_items[module_type][INSTALLED] = ins
        tree_model.appendChild(ins)
        
        # Add Not Installed root item
        not_ins = TreeItem([NOT_INSTALLED, ''], root_item)
        self.root_items[module_type][NOT_INSTALLED] = not_ins
        tree_model.appendChild(not_ins)
        
        # Populate root items with data, check to see if module is installed.
        m = Model(module_type, self.ini_mgr.get_xml_url())
        installer = ModuleInstaller(None, module_type)
        for m_name in m.list_module_names():
            rev_list = m.list_revisions(m_name)
            is_installed = installer.is_module_installed(m_name, module_type)
            if is_installed:
                tree_item = ins
                installed_version = str(self.ini_mgr.get_installed_version(
                                                                    m_name))
            else:
                tree_item = not_ins
                installed_version = ''
            module_item = TreeItem([m.get_display_name(m_name), 
                                    installed_version], tree_item)
            module_item.tag = (m_name, rev_list[0])
            for rev in rev_list:
                rev_item = TreeItem(str(rev), module_item)
                rev_item.tag = (m_name, rev)
                module_item.appendChild(rev_item)
            tree_item.appendChild(module_item)
        
        # Output the model
        return tree_model
        
    def selection_changed(self, old_selection, new_selection, module_type):
        """
        This is an event.
        Called when a different item was selected on the TreeView.
        """
        # Get the treeview that we are editing
        if module_type == GAME:
            tree_view = self.ui.treeGame
        elif module_type == DEP:
            tree_view = self.ui.treeDep
            
        # Get the currently selected item from model and 
        # init the module installer class
        item = self.get_selected_item(tree_view)
        installer = ModuleInstaller(None, module_type)
        
        # If we are not the parent item...
        if item:
            # Get the module name from selected item's tag
            m_name = item.tag[0]
            
            # Initialise the model class
            m = Model(module_type, self.ini_mgr.get_xml_url())
            
            # Populate the text boxes with data
            self.ui.projectNameLineEdit.setText(
                                        m.get_display_name(m_name))
            self.ui.pythonModuleNameLineEdit.setText(m_name)
            self.ui.projectCreationDateLineEdit.setText(
                                        m.get_created(m_name))
            self.ui.projectDescriptionLineEdit.setText(
                                        m.get_description(m_name))
            
            # Check to see if module is installed and
            # show the installed version if it is.
            if installer.is_module_installed(m_name, module_type):
                i_version = str(self.ini_mgr.get_installed_version(m_name))
                self.ui.installedVersionLineEdit.setText(i_version)
            else:
                self.ui.installedVersionLineEdit.setText(NOT_INSTALLED)
            
            # Load the dependencies from model and 
            # display them in the treeview.
            list_model = TreeModel(["Name", "Version"])
            root_item = list_model.rootItem
            for dep in m.list_dependencies(m_name):
                list_model.appendChild(TreeItem([dep[0], str(dep[1])], 
                                                root_item))
            self.ui.dependenciesTreeView.setModel(list_model)
        
        # Act like nothing ever happened :)
        return QtGui.QTreeView.selectionChanged(tree_view, old_selection, 
                                                new_selection)
            
    def dep_selection_changed(self, old_selection, new_selection):
        """
        Dependency selection changed, call above function.
        """
        return self.selection_changed(old_selection, new_selection, DEP)
    
    def game_selection_changed(self, old_selection, new_selection):
        """
        Game selection changed, call above function.
        """
        return self.selection_changed(old_selection, new_selection, GAME)
        
    @QtCore.pyqtSlot()
    def game(self):
        """
        Game treeview was double clicked, install/run the game.
        """
        item = self.get_selected_item()
        if item:
            self.run_game_dep(item.tag[0], item.tag[1], GAME)

    @QtCore.pyqtSlot()
    def dep(self):
        """
        Dependency treeview was double clicked, 
        install the dependency.
        """
        item = self.get_selected_item()
        if item:
            self.run_game_dep(item.tag[0], item.tag[1], DEP)

    @QtCore.pyqtSlot()
    def exit(self):
        """
        Exit button on toolbar
        """
        sys.exit()

    @QtCore.pyqtSlot()
    def run(self):
        """
        Run button on toolbar was clicked.
        Figure what tab were on, and run/install game/dep
        """
        tab_index = self.ui.tabGameDep.currentIndex()
        if tab_index == 0:
            item = self.get_selected_item(self.ui.treeGame)
            if item:
                self.run_game_dep(item.tag[0], item.tag[1], GAME)
        elif tab_index == 1:
            item = self.get_selected_item(self.ui.treeDep)
            if item:
                self.run_game_dep(item.tag[0], item.tag[1], DEP)
    
    @QtCore.pyqtSlot()
    def stop(self):
        """
        Kill the currently running game.
        """
        print("Method 'stop' executed.")
        
    @QtCore.pyqtSlot()
    def uninstall(self):
        """
        Uninstall button on toolbar was clicked.
        """
        tab_index = self.ui.tabGameDep.currentIndex()
        if tab_index == 0:
            item = self.get_selected_item(self.ui.treeGame)
            if item:
                self.uninstall_game_dep(item.tag[0], GAME)
        elif tab_index == 1:
            item = self.get_selected_item(self.ui.treeDep)
            if item:
                self.uninstall_game_dep(item.tag[0], DEP)
        
    @QtCore.pyqtSlot()
    def settings(self):
        """
        Settings button on toolbar was clicked.
        """
        settings = SettingsDialog()
        settings.show()
        
    def resizeEvent(self, event):
        """
        Window was resized, save position.
        """
        self.move_resize()
    
    def moveEvent(self, event):
        """
        Window was moved, save position.
        """
        self.move_resize()
     
    def move_resize(self):
        """
        Do the processing for a move/resize event.
        """
        ini_mgr = INIManager()
        q_rect = self.geometry()
        dimentions = WindowDimentions(q_rect.x(), q_rect.y(), 
                                      q_rect.width(), q_rect.height())
        ini_mgr.set_window_dimentions(dimentions)