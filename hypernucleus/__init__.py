import sys
import argparse
from gettext import ngettext
from PyQt4 import Qt
from PyQt4.QtGui import QMessageBox
from hypernucleus.controller.main import MainWindow
from hypernucleus.controller.settings import SettingsDialog
from hypernucleus.view.icons import qInitResources
from hypernucleus.model.ini_manager import INIManager, WindowDimentions
from hypernucleus.model.xml_model import XmlModel as Model, InvalidURL
from hypernucleus.library.game_manager import GameManager

# work around a debian bug.
argparse.ngettext = ngettext

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
    """
    Launch hypernucleus
    """
    # Before we do anything, we need to check for command line arguments.
    parser = argparse.ArgumentParser(description='A Python Game Database.')
    parser.add_argument('-r', "--run-game", 
                        metavar='MODULE_NAME',
                        action="store",
                        help='Run a Python game.')
    args = parser.parse_args()
    if args.run_game:
        game_mgr = GameManager()
        game_mgr.execute_game(args.run_game)
        sys.exit()
        
    # Get QApplication object.
    app = Qt.QApplication(sys.argv)
    
    # Load image resources
    qInitResources()
    
    # Check to make sure config is set correctly.
    ini_mgr = INIManager()
    try:
        m = Model(ini_mgr.get_xml_url())
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
    main_window = MainWindow(app, m)
    main_window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()