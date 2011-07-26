'''
Created on 23 Jul 2011

@author: r
'''

from hypernucleus.view import main_path
from hypernucleus.model.ini_manager import INIManager, WindowDimentions
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
        ini_mgr = INIManager()
        dimentions = ini_mgr.get_window_dimentions()
        self.setGeometry(QtCore.QRect(dimentions.x, dimentions.y,
                                      dimentions.width, dimentions.height))
        self.q_connect("actionExit", "exit")
        self.q_connect("actionRun", "run")
        self.q_connect("actionStop", "stop")
        self.q_connect("actionUninstall", "uninstall")
        self.q_connect("actionSettings", "settings")
        
    def q_connect(self, action_name, method_name):
        """
        'Quick Connect'
        Use connect with less code :)
        """
        self.connect(getattr(self.ui, action_name), 
                     QtCore.SIGNAL('triggered()'), 
                     self, QtCore.SLOT(method_name + '()'))
        
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