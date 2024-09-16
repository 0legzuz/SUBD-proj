# pyuic5 gui/Forms/filterform.ui -o gui/Forms/FilterForm.py
# pyuic5 gui/Forms/addform.ui -o gui/Forms/OneRecordForm.py
from gui.guimanager import *
import dbmanager as dbm
from PyQt5.QtCore import Qt
from gui.Forms import RemoveForm, OneRecordForm
from PyQt5 import QtWidgets, QtCore,QtGui
import re

class OneRecord(QtWidgets.QDialog, OneRecordForm.Ui_Dialog):
    ctypes = "ФПР"

    def __init__(self,name,parent):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(name)
        self.parent = parent
        self.setupfields()


    def setupfields(self):
        self.errorlabel.setHidden(True)
        self.dateerror.setHidden(True)
        self.numerror.setHidden(True)
        self.finerror.setHidden(True)
        self.grntierror.setHidden(True)

        self.prog.addItem("")
        self.prog.addItems(dbm.GetProgTuple())
        self.setprojnumtip()
        self.prog.currentIndexChanged.connect(self.setprojnumtip)
        self.isp.addItem("")
        self.isp.addItems(dbm.GetVuzTuple())
        self.onlyInt = QtGui.QIntValidator()
        self.pfin.setValidator(self.onlyInt)
        self.srok_k.setValidator(self.onlyInt)
        self.srok_n.setValidator(self.onlyInt)

        self.discardbtn.clicked.connect(self.discard)
        mask = "00.00.00;_"
        self.GRNTI.setInputMask(mask)
        self.GRNTI2.setInputMask(mask)
        self.GRNTI2.setHidden(True)
        self.grntibtn.clicked.connect(self.togglegrnti)

    def togglegrnti(self):
        if self.grntibtn.text() == "+":
            self.GRNTI2.setHidden(False)
            self.grntibtn.setText("-")
        else:
            self.GRNTI2.setHidden(True)
            self.grntibtn.setText("+")

    def check(self,oldnum):
        correct  = True
        self.errorlabel.setHidden(True)
        self.dateerror.setHidden(True)
        self.numerror.setHidden(True)
        self.finerror.setHidden(True)
        self.grntierror.setHidden(True)

        noempty = (self.pfin,self.ruk,self.ruk2,self.srok_k,self.srok_n)

        if  self.f.value() != oldnum and not dbm.CheckProjNum(self.prog.currentText(), self.f.value()):
            self.numerror.setHidden(False)
            correct = False

        for fld in noempty:
            if fld.text() == "" or "_" in fld.text():
                correct = False
                self.errorlabel.setHidden(False)

        if self.NIR.toPlainText() == "" or self.prog.currentText() == "" or self.isp.currentText() == "" :
            correct = False
            self.errorlabel.setHidden(False)

        if len(self.GRNTI.text()) !=8:
            correct = False
            self.grntierror.setHidden(False)

        if not self.GRNTI2.isHidden() and len(self.GRNTI2.text()) !=8:
            correct = False
            self.grntierror.setHidden(False)

        sk, sn = int(self.srok_k.text()), int(self.srok_n.text())

        if correct:
            if sk < sn or not sk in range(2000,2100) or not sn in range(2000,2100):
                self.dateerror.setHidden(False)
                correct = False

            if int(self.pfin.text()) <= 0:
                self.finerror.setHidden(False)
                correct = False

        return correct

    def commitrecord(self,action,oldnum = -1):
        if self.check(oldnum):

            ctype = self.ctypes[self.CODTYPE.currentIndex()]
            grnti = self.GRNTI.text()
            if not self.GRNTI2.isHidden():
                grnti+= "; "+ self.GRNTI2.text()

            if oldnum>-1:
                dbm.RemoveRecord(self.parent.cRec[0], self.parent.cRec[1])

            action(self.prog.currentText(),self.f.value(),self.NIR.toPlainText(),self.isp.currentText(),self.srok_n.text(),self.srok_k.text(),self.ruk.text(),self.ruk2.text(),grnti,ctype,self.pfin.text())

            prog, f = self.prog.currentText(),self.f.value()

            self.parent.FillTable(dbm.GetTableNir(sort=self.parent.sorttype, desc=self.parent.sortdesc))
            self.parent.findrec(prog, f)
            dbm.countNPROJ()
            dbm.SumPFinInProg()
            self.close()

    def discard(self):
        self.close()



    def setprojnumtip(self):
        # print(self.prog.currentText())
        i = dbm.GetMaxProjInProg(self.prog.currentText())
        self.f.setValue(int(i) + 1)
        # print(i)

class AddRecord(OneRecord):
    def __init__(self,parent):
        super().__init__("Добавление записи",parent)
        self.savebtn.clicked.connect(self.saverecord)

    def saverecord(self):
        self.commitrecord(dbm.AddRecord)


class EditRecord(OneRecord):
    def __init__(self,parent):
        super().__init__("Редактирование записи",parent)
        self.cRow = parent.cRow
        self.cRec = parent.cRec
        self.savebtn.clicked.connect(self.editrecord)
        self.fillform()

    def fillform(self):
        table = self.parent.tableWidget
        if not (table.item(self.cRow, 0)):
            return
        record = dbm.GetRecord(table.item(self.cRow, 0).text(),table.item(self.cRow, 1).text())
        print(record)
        self.prog.setCurrentText(table.item(self.cRow, 0).text())
        self.f.setValue(int(table.item(self.cRow, 1).text()))
        self.isp.setCurrentText(record["ISP"])
        self.pfin.setText(str(record["PFIN"]))
        self.srok_k.setText(record["SROK_K"])
        self.srok_n.setText(record["SROK_N"])
        self.CODTYPE.setCurrentIndex(self.ctypes.find(record["CODTYPE"]))
        self.ruk.setText(record["RUK"])
        self.ruk2.setText(record["RUK2"])
        self.NIR.setPlainText(record["NIR"])
        grnti = record["GRNTI"].strip()
        pattern = ";|,| "
        if any((c in set(pattern)) for c in grnti):
            grnti= re.split(pattern,grnti)
            if "" in grnti:
                grnti.remove("")
            self.togglegrnti()
            self.GRNTI.setText(grnti[0])
            self.GRNTI2.setText(grnti[1])
        else:
            self.GRNTI.setText(grnti)

    def editrecord(self):
        self.commitrecord(dbm.EditRecord,int(self.cRec[1]))


class RemoveRecord(QtWidgets.QDialog, RemoveForm.Ui_Dialog):
    def __init__(self,cRec,parent):
        super().__init__()
        self.setupUi(self)
        self.cRec  = cRec
        self.parent = parent
        self.setWindowTitle("Подтвержедние удаления")
        self.rec.setText(f"Программа: '{cRec[0]}'\n№ {cRec[1]}")
        self.ok.clicked.connect(self.removerec)
        self.cancel.clicked.connect(self.close)

    def removerec(self):
        dbm.RemoveRecord(self.cRec[0],self.cRec[1])
        self.parent.FillTable(dbm.GetTableNir(sort=self.parent.sorttype, desc=self.parent.sortdesc))
        self.parent.cRec = ("","")
        self.parent.cRow = -1
        dbm.countNPROJ()
        dbm.SumPFinInProg()

        self.close()