'''
Created on 23 Jul 2011

@author: r
'''

from hypernucleus.view import main_path
from hypernucleus.model.ini_manager import INIManager, WindowDimentions
from hypernucleus.model.tree_model import TreeModel, TreeItem
from hypernucleus.model.xml_model import XmlModel as Model
from hypernucleus.library.module_installer import ModuleInstaller
from hypernucleus.model import GAME, DEP, INSTALLED, NOT_INSTALLED
from PyQt4.QtGui import QMainWindow
from PyQt4 import uic, QtCore, QtGui
import sys

class MainWindow(QMainWindow):
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
                                      dimentions.width, dimentions.height))
        
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
        
    def quick_connect(self, action_name, method_name):
        """
        'Quick Connect'
        Use connect with less code :)
        """
        self.connect(getattr(self.ui, action_name), 
                     QtCore.SIGNAL('triggered()'), 
                     self, QtCore.SLOT(method_name + '()'))
    
    def reset_models(self):
        """
        Reload items in treeview
        """
        self.root_items = {GAME: {}, DEP: {}}
        self.ui.treeGame.setModel(self.configure_model(GAME))
        self.ui.treeDep.setModel(self.configure_model(DEP))
        self.ui.treeGame.expandAll()
        self.ui.treeDep.expandAll()
    
    def configure_model(self, module_type):
        """
        Add items to a Tree View model.
        """
        # Make the title bar.
        tree_model = TreeModel("")
        root_item = tree_model.rootItem
        
        # Add Installed root item
        ins = TreeItem(INSTALLED, root_item)
        self.root_items[module_type][INSTALLED] = ins
        tree_model.appendChild(ins)
        
        # Add Not Installed root item
        not_ins = TreeItem(NOT_INSTALLED, root_item)
        self.root_items[module_type][NOT_INSTALLED] = not_ins
        tree_model.appendChild(not_ins)
        
        # Populate root items with data, check to see if module is installed.
        m = Model(module_type, self.ini_mgr.get_xml_url())
        installer = ModuleInstaller(None, module_type)
        for m_name in m.list_module_names():
            is_installed = installer.is_module_installed(m_name, module_type)
            if is_installed:
                tree_item = ins
            else:
                tree_item = not_ins
            module_item = TreeItem(m.get_display_name(m_name), tree_item)
            module_item.tag = m_name
            tree_item.appendChild(module_item)
        
        # Output the model
        return tree_model

    def get_selected_item(self, treeview=None):
        """
        Get currently selected item in treeview
        """
        if treeview:
            ci = treeview.currentIndex()
        else:
            ci = self.sender().currentIndex()
        parent_row = ci.parent().row()
        if parent_row > -1:
            item = ci.model().rootItem.child(parent_row).childItems[ci.row()]
            return item
        else:
            return None
    
    def run_game_dep(self, module_name, module_type):
        """
        Run/Install a Game/Dependency
        """
        if not module_type in [GAME, DEP]:
            raise Exception("Invalid module type")
        if module_type == GAME:
            m = Model(module_type, self.ini_mgr.get_xml_url())
            revisions = m.list_revisions(module_name)
            source_url = m.get_revision_source(module_name, 
                                               revisions[0], True)
            installer = ModuleInstaller(source_url, module_type)
            is_installed = installer.is_module_installed(module_name, 
                                                         module_type)
            if is_installed:
                print("TODO: Run code")
            else:
                installer.install()
                self.reset_models()
        elif module_type == DEP:
            print("dep", module_name)
            
    def uninstall_game_dep(self, module_name, module_type):
        """
        Uninstall a Game/Dependency
        """
        installer = ModuleInstaller(None, module_type)
        is_installed = installer.is_module_installed(module_name, 
                                                     module_type)
        if is_installed:
            installer.uninstall_module(module_name, module_type)
            self.reset_models()
    
    def selection_changed(self, old_selection, new_selection, module_type):
        if module_type == GAME:
            tree_view = self.ui.treeGame
        elif module_type == DEP:
            tree_view = self.ui.treeDep
        item = self.get_selected_item(tree_view)
        if item:
            m = Model(module_type, self.ini_mgr.get_xml_url())
            self.ui.projectNameLineEdit.setText(
                                        m.get_display_name(item.tag))
            self.ui.pythonModuleNameLineEdit.setText(item.tag)
            self.ui.projectCreationDateLineEdit.setText(
                                        m.get_created(item.tag))
            self.ui.projectDescriptionLineEdit.setText(
                                        m.get_description(item.tag))
        return QtGui.QTreeView.selectionChanged(tree_view, old_selection, 
                                                new_selection)
            
    def dep_selection_changed(self, old_selection, new_selection):
        return self.selection_changed(old_selection, new_selection, DEP)
    
    def game_selection_changed(self, old_selection, new_selection):
        return self.selection_changed(old_selection, new_selection, GAME)
    
    @QtCore.pyqtSlot()
    def test(self):
        print("woo")
            
    @QtCore.pyqtSlot()
    def game(self):
        item = self.get_selected_item()
        if item:
            self.run_game_dep(item.tag, GAME)

    @QtCore.pyqtSlot()
    def dep(self):
        item = self.get_selected_item()
        if item:
            self.run_game_dep(item.tag, DEP)

    @QtCore.pyqtSlot()
    def exit(self):
        sys.exit()

    @QtCore.pyqtSlot()
    def run(self):
        tab_index = self.ui.tabGameDep.currentIndex()
        if tab_index == 0:
            item = self.get_selected_item(self.ui.treeGame)
            if item:
                self.run_game_dep(item.tag, GAME)
        elif tab_index == 1:
            item = self.get_selected_item(self.ui.treeDep)
            if item:
                self.run_game_dep(item.tag, DEP)
    
    @QtCore.pyqtSlot()
    def stop(self):
        print("Method 'stop' executed.")
        
    @QtCore.pyqtSlot()
    def uninstall(self):
        tab_index = self.ui.tabGameDep.currentIndex()
        if tab_index == 0:
            item = self.get_selected_item(self.ui.treeGame)
            if item:
                self.uninstall_game_dep(item.tag, GAME)
        elif tab_index == 1:
            item = self.get_selected_item(self.ui.treeDep)
            if item:
                self.uninstall_game_dep(item.tag, DEP)
        
    @QtCore.pyqtSlot()
    def settings(self):
        print("Method 'settings' executed.")
        
    def resizeEvent(self, event):
        self.move_resize()
    
    def moveEvent(self, event):
        self.move_resize()
     
    def move_resize(self):
        ini_mgr = INIManager()
        q_rect = self.geometry()
        dimentions = WindowDimentions(q_rect.x(), q_rect.y(), 
                                      q_rect.width(), q_rect.height())
        ini_mgr.set_window_dimentions(dimentions)