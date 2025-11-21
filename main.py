import sys
from PyQt5 import QtWidgets
from gui import MainWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.resize(1000,700)
    w.show()
    sys.exit(app.exec_())
