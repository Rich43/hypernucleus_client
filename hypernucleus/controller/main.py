'''
Created on 23 Jul 2011

@author: r
'''

from hypernucleus.view import main_path
from PyQt4.QtGui import QMainWindow
from PyQt4 import uic

class MainWindow(QMainWindow):
    """
    The Main Window.
    """
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = uic.loadUi(main_path, self)