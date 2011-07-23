import sys
from PyQt4 import Qt
from hypernucleus.controller.main import MainWindow

def main():
    app = Qt.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())