import sys
from time import sleep
from PyQt4 import Qt
from PyQt4.QtGui import QMessageBox
from hypernucleus.controller.main import MainWindow
from hypernucleus.controller.settings import SettingsDialog
from hypernucleus.view.icons import qInitResources
from hypernucleus.model.ini_manager import INIManager, WindowDimentions
from hypernucleus.model.xml_model import XmlModel as Model, InvalidURL

INVALID_REPO = """The repository URL must be set for Hypernucleus to 
function. A settings dialog will open to allow you to set 
this correctly.""".replace("\n", "")

INVALID_REPO_FAIL = """You failed to set the repository URL correctly. 
Hypernucleus will now exit.""".replace("\n", "")

INVALID_OS_ARCH = """You are running Hypernucleus for the first time. 
Hypernucleus runs on a wide variety of hardware and operating systems. 
Before you can start using Hypernucleus, you must select your 
operating system and processor architecture from the settings dialog 
that will follow this message.""".replace("\n", "")

INVALID_OS_ARCH_FAIL = """You failed to select an operating system and 
architecture. Hypernucleus will now exit.""".replace("\n", "")

def main():
    app = Qt.QApplication(sys.argv)
    
    # Load image resources
    qInitResources()
    
    # Check to make sure config is set correctly.
    ini_mgr = INIManager()
    try:
        Model(None, ini_mgr.get_xml_url())
    except InvalidURL:
        settings = SettingsDialog()
        QMessageBox.critical(settings,"Invalid Repository URL", INVALID_REPO)
        result = settings.exec_()
        if not result:
            QMessageBox.critical(settings,"Exiting...", INVALID_REPO_FAIL)
            sys.exit()
    if not ini_mgr.get_operating_system() or not ini_mgr.get_architecture():
        settings = SettingsDialog(1)
        QMessageBox.information(settings,"Setup Required", INVALID_OS_ARCH)
        result = settings.exec_()
        if not result:
            QMessageBox.critical(settings,"Exiting...", INVALID_OS_ARCH_FAIL)
            sys.exit()
    # Open the main window.
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())