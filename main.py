import sys
from gui.guimanager import *

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
def main():
    dbm.checkconfig("config.ini")
    db = dbm.openDatabase("config.ini")
    offline = not db
    if offline:
        print("open app without database connection")

    app = QtWidgets.QApplication([])

    window = MainWindow(app,offline)
    window.projpath = CURRENT_DIR

    window.dbref = db
    window.showMaximized()



    sys.exit(app.exec_())



if __name__ == '__main__':
    main()
