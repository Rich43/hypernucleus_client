'''
Created on 23 Jul 2011

@author: r
'''

from hypernucleus.view import main_path
from hypernucleus.model.ini_manager import INIManager, WindowDimentions
from hypernucleus.model.tree_model import TreeModel, TreeItem
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
        self.dummy_count = 0
        self.ui.treeGame.setModel(self.configure_model())
        self.ui.treeDep.setModel(self.configure_model())
        ini_mgr = INIManager()
        dimentions = ini_mgr.get_window_dimentions()
        self.setGeometry(QtCore.QRect(dimentions.x, dimentions.y,
                                      dimentions.width, dimentions.height))
        self.quick_connect("actionExit", "exit")
        self.quick_connect("actionRun", "run")
        self.quick_connect("actionStop", "stop")
        self.quick_connect("actionUninstall", "uninstall")
        self.quick_connect("actionSettings", "settings")
        
    def quick_connect(self, action_name, method_name):
        """
        'Quick Connect'
        Use connect with less code :)
        """
        self.connect(getattr(self.ui, action_name), 
                     QtCore.SIGNAL('triggered()'), 
                     self, QtCore.SLOT(method_name + '()'))
        
    def configure_model(self):
        """
        Add items to a Tree View model.
        """
        # Make the title bar.
        tree_model = TreeModel("")
        root_item = tree_model.rootItem
        append_child = tree_model.appendChild
        
        # Dummy item list and counter
        dummies = []
        
        # Add Installed root item
        installed = append_child(TreeItem("Installed", root_item))
        installed_append = installed.appendChild
        for i in range(50):
            self.dummy_count += 1
            dummy = installed_append(TreeItem(
                            "Dummy " + str(self.dummy_count), installed))
            dummies.append(dummy)
            
        # Add Not Installed root item
        not_installed = append_child(TreeItem("Not Installed", root_item))
        not_ins_append = not_installed.appendChild
        for i in range(50):
            self.dummy_count += 1
            dummy = not_ins_append(TreeItem(
                            "Dummy " + str(self.dummy_count), not_installed))
            dummies.append(dummy)
            
        # Output the model
        return tree_model
        
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