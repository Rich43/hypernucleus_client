'''
Created on 23 Jul 2011

@author: r
'''

from hypernucleus.view import main_path
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