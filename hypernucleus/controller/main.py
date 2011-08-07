'''
Created on 23 Jul 2011

@author: r
'''

from hypernucleus.view import main_path
from hypernucleus.model.ini_manager import INIManager, WindowDimentions
from hypernucleus.model.tree_model import TreeModel, TreeItem
from hypernucleus.model.xml_model import XmlModel as Model
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
        self.setGeometry(QtCore.QRect(dimentions.x, dimentions.y,
                                      dimentions.width, dimentions.height))
        
        # Fill treeview with content.
        self.root_items = {GAME: {}, DEP: {}}
        self.ui.treeGame.setModel(self.configure_model(GAME))
        self.ui.treeDep.setModel(self.configure_model(DEP))
        
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
        
        # Populate root items with data.
        m = Model(module_type, self.ini_mgr.get_xml_url())
        for m_name in m.list_module_names():
            module_item = TreeItem(m.get_display_name(m_name), not_ins)
            module_item.tag = m_name
            not_ins.appendChild(module_item)
        # Output the model
        return tree_model

    def get_selected_item(self):
        ci = self.sender().currentIndex()
        parent_row = ci.parent().row()
        if parent_row > -1:
            item = ci.model().rootItem.child(parent_row).childItems[ci.row()]
            return item
        else:
            return None

    @QtCore.pyqtSlot()
    def game(self):
        print(self.get_selected_item().tag)

    @QtCore.pyqtSlot()
    def dep(self):
        print(self.get_selected_item().tag)

    @QtCore.pyqtSlot()
    def exit(self):
        sys.exit()

    @QtCore.pyqtSlot()
    def run(self):
        print("Method 'run' executed.")
    
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