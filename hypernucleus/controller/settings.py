from hypernucleus.view import settings_path
from PyQt4.QtGui import QDialog
from PyQt4 import uic

class SettingsDialog(QDialog):
    """
    The Settings Dialog.
    """
    
    def __init__(self):
        QDialog.__init__(self)
        self.ui = uic.loadUi(settings_path, self)