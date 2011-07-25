import sys
from PyQt4 import Qt
from hypernucleus.controller.main import MainWindow
from hypernucleus.view.icons import qInitResources

def main():
    app = Qt.QApplication(sys.argv)
    qInitResources()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())