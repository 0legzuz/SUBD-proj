import dbmanager as dbm
from fielddict import *
from reportmanager import order
from PyQt5.QtCore import Qt
from gui.Forms import FormTableWidget, OnlyTableForm,OrderForm
from PyQt5 import QtWidgets, QtCore,QtGui

class Order(QtWidgets.QDialog, OrderForm.Ui_Dialog,):
    def __init__(self,parent):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.currentordersum = 0
        self.currentquartal = [0,'']

        self.setWindowTitle("Финансирование НИР")
        self.countcurrentfin()

        rx = QtCore.QRegExp("-*\\d{0,30}\\.*\\d{0,10}")
        validator = QtGui.QRegExpValidator(rx, self)
        # self.onlyDouble = QtGui.QDoubleValidator()
        self.sumfin.setValidator(validator)
        self.percentfin.setValidator(validator)
        self.allowfin = {'sum':True,'percent':True}

        self.discard.clicked.connect(self.close)
        self.acceptbtn.clicked.connect(self.acceptorder)
        self.countbtn.clicked.connect(self.countorder)
        self.acceptbtn.setEnabled(False)
        self.countbtn.setEnabled(False)

        self.sumfin.textChanged.connect(self.changesumfin)
        self.percentfin.textChanged.connect(self.changepercentfin)
        self.quartcombo.currentIndexChanged.connect(self.checkcorrectfill)


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if "mdi" in dir(self.parent):
            self.parent.mdi.closeAllSubWindows()


    def countcurrentfin(self):
        fin = dbm.getSumFin()
        self.fin = fin
        perc = round(float(fin['ffin'] / fin['pfin']) * 100, 5)
        self.ffinlabel.setText(f"{fin['ffin']} руб.; {perc}%")

        self.pfinlabel.setText(f"{fin['pfin']} руб.")


    def changesumfin(self):
        if not self.allowfin['sum']: return

        self.allowfin['percent'] = False
        self.recountsumpercent('sum')
        self.allowfin['percent'] = True

        self.checkcorrectfill()

    def changepercentfin(self):
        if not self.allowfin['percent']: return

        self.allowfin['sum'] = False
        self.recountsumpercent('percent')
        self.allowfin['sum'] = True

        self.checkcorrectfill()

    def recountsumpercent(self,field):
        if field =="sum":
            text = self.sumfin.text()
            try:
                sum = float(text)
            except:
                return

            percent = sum/float(self.fin['pfin'])*100
            self.percentfin.setText(str(round(percent,5)))
        elif field =="percent":
            text = self.percentfin.text()
            try:
                percent = float(text)
            except:
                return

            sum = percent/100*float(self.fin['pfin'])
            self.sumfin.setText(str(round(sum,5)))
        else:
            print("wrong field")

        try:
            self.currentordersum = float(self.sumfin.text())
        except:
            self.currentordersum = 0


    def checkcorrectfill(self):
        correct = self.quartcombo.currentIndex()>0 and self.sumfin.text()!="" and self.percentfin.text()!=""
        self.countbtn.setEnabled(correct)
        self.currentquartal[0] = self.quartcombo.currentIndex()
        self.currentquartal[1] = self.quartcombo.currentText()

        self.acceptbtn.setEnabled(False)
        self.tableWidget.setEnabled(False)

    def countorder(self):
        self.ffintables = dbm.NirVuzFinDistribute(float(self.fin['pfin']),self.currentordersum)
        self.tableWidget.setEnabled(True)
        self.acceptbtn.setEnabled(True)
        self.FillTable(self.ffintables['vuz'])

        self.countbtn.setEnabled(False)


    def acceptorder(self):
        dbm.AddFFinToNir(self.ffintables['nir'],self.currentquartal[0])
        dbm.SumFFinInProg()
        # self.countcurrentfin()
        path = QtWidgets.QFileDialog.getExistingDirectory()
        order(self.ffintables['vuz'],f'Распоряжение на финанисрование {self.currentquartal[1]}',path)
        self.parent.statusbar.showMessage(f"Распоряжение сохранено в {path}")
        print("apply fin order")
        self.close()


    def FillTable(self, table):
        n, m = 2, len(table)
        self.tableWidget.setColumnCount(n)
        self.tableWidget.setHorizontalHeaderLabels(("Вуз",f"Фин. за {self.currentquartal[1]}"))
        self.tableWidget.verticalHeader().setVisible(False)

        if len(table) == 0:
            print("empty table")
            self.tableWidget.setRowCount(0)
            return

        self.tableWidget.setRowCount(m+1)

        sum = 0

        for i in range(0, m):
            j = 0
            for cname in table[0].keys():
                if cname == "ffin":
                    sum+=table[i][cname]
                item = QtWidgets.QTableWidgetItem(str(table[i][cname]))
                item.setFlags(Qt.ItemIsEnabled)
                self.tableWidget.setItem(i, j, item)
                j += 1

        vsegoitem = QtWidgets.QTableWidgetItem('Всего')
        sumitem = QtWidgets.QTableWidgetItem(str(sum))
        self.tableWidget.setItem(m, 0, vsegoitem)
        self.tableWidget.setItem(m, 1, sumitem)

        self.tableWidget.resizeColumnsToContents()
