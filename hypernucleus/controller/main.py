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
from PyQt4 import uic, QtCore
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
            self.run_game_dep(self.get_selected_item(self.ui.treeDep).tag,
                              DEP)
    
    @QtCore.pyqtSlot()
    def stop(self):
        print("Method 'stop' executed.")
        
    @QtCore.pyqtSlot()
    def uninstall(self):
        print("Method 'uninstall' executed.")
        
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