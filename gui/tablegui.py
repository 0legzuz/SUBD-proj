from gui.guimanager import *
from gui.onerecordgui import *
from gui.filtergui import *
from fielddict import *
from reportmanager import report
import dbmanager as dbm
from PyQt5.QtCore import Qt
from gui.Forms import FormTableWidget, OnlyTableForm
from PyQt5 import QtWidgets, QtCore,QtGui
# pyuic5 Forms/name.ui -o Forms/name.py
# pyuic5 gui/Forms/orderform.ui -o gui/Forms/OrderForm.py
# pyuic5 gui/Forms/OnlyTable.ui -o gui/Forms/OnlyTableForm.py
# pyuic5 gui/Forms/Main.ui -o gui/Forms/Main.py

class TableClass():
    cRow = -1
    cRec = ("","")
    wparent = None

    def setColortoRow(self,table, rowIndex, color):
        for j in range(table.columnCount()):
            table.item(rowIndex, j).setBackground(color)

    def rowselection(self):
        r = self.tableWidget.currentRow()
        self.selectirow(r)


    def selectirow(self,r):
        try:
            self.setColortoRow(self.tableWidget, r, QtGui.QColor(0x6E86D6))
            if self.cRow != -1 and self.cRow !=r:
                self.setColortoRow(self.tableWidget, self.cRow, QtGui.QColor(0xFFFFFF))
            self.cRow = r
            if QtWidgets.QMainWindow in self.__class__.__bases__:
                self.statusBar().showMessage(f'Строка {r+1}')
                self.cRec = (self.tableWidget.item(r, 0).text(),self.tableWidget.item(r, 1).text())
                # print(self.cRec)
        except BaseException:
            print("something wrong! try again")
            return

    def FillTable(self,table):
        if len(table) ==0:
            print("empty table")
            self.tableWidget.setRowCount(0)
            return

        n, m = len(table[0]), len(table)

        self.tableWidget.setRowCount(m)
        for i in range(0, m):
            j = 0
            for cname in table[0].keys():
                item = QtWidgets.QTableWidgetItem(str(table[i][cname]))
                item.setFlags(Qt.ItemIsEnabled)
                self.tableWidget.setItem(i, j, item)
                j += 1

    def SetUpTable(self, table):
        n, m = len(table[0]), len(table)
        self.tableWidget.setColumnCount(n)
        self.tableWidget.setHorizontalHeaderLabels(GetTupleOfFullName(table[0].keys()))
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.verticalHeader().setVisible(False)

        self.tableWidget.clicked.connect(self.rowselection)
        self.FillTable(table)

    def closeEvent(self, event):
    
        if "mdi" in dir(self.wparent):
            self.wparent.mdi.closeAllSubWindows()




class FuncTable(QtWidgets.QMainWindow, FormTableWidget.Ui_MainWindow,TableClass):
    def __init__(self, table, name,wparent = None):
        super().__init__()
        self.setupUi(self)
        self.sortdesc = False
        self.sorttype = 0
        self.filter = {}
        self.dialog = None
        self.wparent = wparent

        self.sortbox.currentIndexChanged.connect(self.sort)
        self.sortbtn.clicked.connect(self.togglesort)
        self.addbtn.clicked.connect(self.addrec)
        self.editbtn.clicked.connect(self.editrec)
        self.deletebtn.clicked.connect(self.removeRec)
        self.filterbtn.clicked.connect(self.setFilter)

        self.setupanalys()

        self.setWindowTitle(name)
        self.SetUpTable(table)

    def setFilter(self):
        window = Filter(self)
        window.show()
        self.dialog = window

    def removeRec(self):
        if self.selectioncheck():
            return
        window = RemoveRecord(self.cRec,self)
        window.show()
        self.dialog = window

    def findrec(self,prog,f):
        progs = self.tableWidget.findItems(prog, Qt.MatchExactly)
        progsind = tuple((pr.row()) for pr in progs)
        print("find " + prog + str(f))
        for i in progsind:
            if int(self.tableWidget.item(i,1).text())==f:
                # print(i)
                self.selectirow(i)
                self.tableWidget.scrollToItem(self.tableWidget.item(i,0))
                return i

    def sort(self,i):
        self.sorttype = i

        table = dbm.GetTableNir(self.sorttype,self.sortdesc,self.filter)
        self.FillTable(table)
        if self.cRec[1]!="":
            self.findrec(self.cRec[0],int(self.cRec[1]))
        # print(i)

    def addrec(self):
        window = AddRecord(self)
        window.show()
        self.dialog = window

    def editrec(self):
        if self.selectioncheck():
            return
        window = EditRecord(self)
        window.show()
        self.dialog = window

    def selectioncheck(self):
        if self.cRow ==-1:
            self.statusBar().showMessage(f'Выберите запись!')
        return self.cRow ==-1

    def togglesort(self):
        self.sortdesc = not self.sortdesc
        table = dbm.GetTableNir(self.sorttype,self.sortdesc,self.filter)
        self.FillTable(table)
        if self.cRec[1] != "":
            self.findrec(self.cRec[0],int(self.cRec[1]))

        if not self.sortdesc:
            self.sortbtn.setText("↑")
        else:
            self.sortbtn.setText("↓")

    def setupanalys(self):
        self.wparent.analys1.triggered.connect(self.openanalys1)
        self.wparent.analys2.triggered.connect(self.openanalys2)
        self.wparent.analys3.triggered.connect(self.openanalys3)

        self.wparent.analys1.setEnabled(True)
        self.wparent.analys2.setEnabled(True)
        self.wparent.analys3.setEnabled(True)

    def openanalys1(self):
        table = dbm.GetAnalisTable(0, self.filter)
        if table == -1: return

        self.openAnalysTable(table, self.wparent.analys1.text(), self.filterlabel.text())

    def openanalys2(self):
        table = dbm.GetAnalisTable(1, self.filter)
        if table == -1: return

        self.openAnalysTable(table, self.wparent.analys2.text(), self.filterlabel.text())

    def openanalys3(self):
        table = dbm.GetAnalisTable(2,self.filter)
        if table == -1 :return
        self.openAnalysTable(table,self.wparent.analys3.text(),self.filterlabel.text())



    def openAnalysTable(self,table,name,filtertext):
        window = OnlyTable(table,name,self,True,filtertext)
        window.tableWidget.resizeColumnsToContents()
        window.show()

        self.dialog = window

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        # self.filter = {}
        self.wparent.mdi.closeAllSubWindows()
        self.wparent.analys1.setEnabled(False)
        self.wparent.analys2.setEnabled(False)
        self.wparent.analys3.setEnabled(False)

        if self.dialog:
            self.dialog.close()


class OnlyTable(QtWidgets.QDialog, OnlyTableForm.Ui_Dialog, TableClass):
    def __init__(self, table,name,wparent = None,analys = False,filtertext = ""):
        super().__init__()
        self.setupUi(self)
        self.wparent = wparent
        self.setWindowTitle(name)
        self.title.setText(name)
        self.SetUpTable(table)
        self.tablesrc = table

        if not analys:
            self.filterlabel.hide()
            self.savebtn.hide()
        elif not filtertext:
            self.filterlabel.hide()
        else:
            self.filterlabel.setText(filtertext)

        self.savebtn.clicked.connect(self.doreport)


    def doreport(self):
        path = QtWidgets.QFileDialog.getExistingDirectory()
        mes = report(self.windowTitle(),self.filterlabel.text(),self.tablesrc,path)
        self.wparent.statusBar().showMessage(f"Отчет сохранен в {mes}")

        
