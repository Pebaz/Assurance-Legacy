import sys
from PyQt4.QtGui import QApplication
from game import Game
import os

def main(args):
    app = QApplication(args)
    assurance = Game()
    assurance.show()
    assurance.start()
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
