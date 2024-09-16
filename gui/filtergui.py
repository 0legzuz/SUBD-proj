import dbmanager as dbm
from PyQt5.QtCore import Qt
from gui.Forms import FormTableWidget, OnlyTableForm,FilterForm
from PyQt5 import QtWidgets, QtCore,QtGui

class Filter(QtWidgets.QDialog, FilterForm.Ui_Dialog,):
    def __init__(self,parent):
        super().__init__()
        self.setupUi(self)
        self.parent = parent


        self.applybtn.clicked.connect(self.applyFilter)
        self.discardbtn.clicked.connect(self.discardFilter)

        self.prog.addItem("")
        self.prog.addItems(dbm.GetProgTuple())

        self.allowgeocombo = True

        self.setupGeofilter()

        self.prog.currentTextChanged.connect(self.checkEnableButtons)
        self.checkprog.stateChanged.connect(self.checkEnableButtons)


        if parent.filter != {}: # заполнение формы текущим фильтром
            if "prog" in parent.filter.keys():
                self.checkprog.setCheckState(Qt.CheckState(2))
                self.prog.setCurrentText(parent.filter["prog"])

        self.checkEnableButtons()

        if self.canApply():
            self.applybtn.setEnabled(True)

    def setupGeofilter(self):
        combo = [self.fedokrug,self.subj,self.city,self.vuz]
        keys = ["region","oblname","city","z2"]
        self.geodict = dict(zip(keys,combo))

        for cmb in self.geodict.values(): # пустые строки в комбо
            cmb.addItem("")


        self.geoinfo = dbm.GetFullGeoinfo()

        for key,cmb in self.geodict.items():# заполнение без ограничений
            cmb.addItems(sorted(self.geoinfo[key]))


        self.fedokrug.currentIndexChanged.connect(self.changefedokrug)
        self.subj.currentIndexChanged.connect(self.changesubj)
        self.city.currentIndexChanged.connect(self.changecity)
        self.vuz.currentIndexChanged.connect(self.changevuz)
        self.checkgeo.stateChanged.connect(self.checkEnableButtons)

        if self.parent.filter != {}: # заполнение формы текущим фильтром
            if "geo" in self.parent.filter.keys():
                self.checkgeo.setCheckState(Qt.CheckState(2))
                gfltr = self.parent.filter['geo']
                for i in range(len(gfltr)):
                    cmb = list(self.geodict.values())[i]
                    key = list(self.geodict.keys())[i]
                    cmb.setCurrentText(gfltr[key])

    def changefedokrug(self):
        if not self.allowgeocombo:
            return
        self.geoinfo = dbm.GetGeoinfo("region",self.fedokrug.currentText())
        self.refillGeofilter(0)


    def changesubj(self):
        if not self.allowgeocombo:
            return
        self.geoinfo = dbm.GetGeoinfo("oblname",self.subj.currentText())
        self.refillGeofilter(1)


    def changecity(self):
        if not self.allowgeocombo:
            return
        self.geoinfo = dbm.GetGeoinfo("city",self.city.currentText())
        self.refillGeofilter(2)


    def changevuz(self):
        if not self.allowgeocombo:
            return
        self.geoinfo = dbm.GetGeoinfo("z2",self.vuz.currentText())
        self.refillGeofilter(3)

    def refillGeofilter(self,i):
        """i - номер комбобокса, который изменен"""

        self.allowgeocombo = False
        # if self.fedokrug.currentText() !="":


        fullgeoinfo = dbm.GetFullGeoinfo()

        for cmb in self.geodict.values(): # очистка комбо
            cmb.clear()

        geofltr = {}

        for j in range(4):
            cmb = list(self.geodict.values())[j]
            key = list(self.geodict.keys())[j]
            if j<=i :
                # cmb.addItem("")
                cmb.addItems(sorted(fullgeoinfo[key]))
                cmb.setCurrentText(list(self.geoinfo[key])[0])
                geofltr[key] = cmb.currentText()
            else:
                cmb.addItem("")
                cmb.addItems(sorted(self.geoinfo[key]))


        self.parent.filter['geo'] = geofltr

        self.allowgeocombo = True

        self.checkEnableButtons()


    def fillGeofilter(self):
        # self.fedokrug.clear()
        # self.subj.clear()
        # self.city.clear()
        # self.vuz.clear()
        pass


    def applyFilter(self):
        if self.checkprog.checkState() == 2 and self.prog.currentText() != "":
            self.parent.filter["prog"] = self.prog.currentText()

        if self.checkprog.checkState() == 0 and "prog" in self.parent.filter.keys():
            self.parent.filter.pop("prog")

        if self.checkgeo.checkState() == 0 and "geo" in self.parent.filter.keys():
            self.parent.filter.pop("geo")


        if self.parent.filter == {}:
            return

        self.fillTable(self.parent.filter)
        self.close()

    def checkEnableButtons(self):
        self.applybtn.setEnabled(self.canApply())
        self.discardbtn.setEnabled(bool(self.parent.filter))


    def discardFilter(self):
        self.checkprog.setCheckState(Qt.CheckState(0))
        self.checkgeo.setCheckState(Qt.CheckState(0))

        if not self.parent.filter:
            return

        self.fillTable()
        self.parent.filter = {}
        self.close()



    def fillTable(self,filter = None):
        table = dbm.GetTableNir(self.parent.sorttype,self.parent.sortdesc,filter)
        self.parent.FillTable(table)
        filtermes = ""

        if filter:
            mes = 'Фильтрация установлена'

            if "prog" in self.parent.filter.keys():
                filtermes+= f" Программа: {self.prog.currentText()}; "
            if "geo" in self.parent.filter.keys():
                title = {"Z2": "Вуз",
                        "REGION": "Фед. округ",
                        "CITY": "Город",
                        "OBLNAME": "Субъект", }
                geofilter = list(self.parent.filter['geo'].items())
                f, n = geofilter[-1]
                filtermes += f"{title[f.upper()]}: {n}"
                # filtermes+= f" Программа: {self.prog.currentText()}"
        else:
            mes = 'Фильтрация отменена'

        self.parent.filterlabel.setText(filtermes)
        self.parent.statusBar().showMessage(mes)


        self.parent.setFocus()
        self.parent.activateWindow()
        self.parent.raise_()

    def canApply(self):
        canprog = self.checkprog.checkState() == 2 and self.prog.currentText() != ""
        cangeo = self.checkgeo.checkState() == 2 and (self.fedokrug.currentText() != "")
        return canprog or cangeo