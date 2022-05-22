from ipaddress import collapse_addresses
from pydoc import classname
from statisticalDataBigArray import Statistic
import numpy as np
from PyQt5 import QtWidgets, QtCore
from ui import Ui_MainWindow
from dialog import Ui_EnterDialog
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys
from enum import Enum
import re

class PoligonType(Enum):
    FREQUENCY = 0
    PERIODICITY = 1

class dialogwindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_EnterDialog()
        self.ui.setupUi(self)
        
        self.mainwindow = parent

        self.buttons = self.ui.buttonBox.buttons()
        self.buttons[0].setText("Ок")
        self.buttons[1].setText("Отмена")

        self.setTable()
        self.buttons[0].clicked.connect(self.getButton)
        self.ui.intervalAmountBox.valueChanged.connect(self.setTable)

    
    def getButton(self):
        amount = self.ui.intervalsTable.columnCount()
        intervals= []
        frequency = []
            
        try:
            row_1 = self.ui.intervalsTable.item(0, 0).text()
            row_2 = self.ui.intervalsTable.item(1, 0).text()
            interval = [float(s) for s in re.findall(r'-?\d+\.?\d*', row_1)]
            frequency.append(int(row_2))
            
            if len(interval) != 2:
                raise str("ERROR")

            h = interval[1] - interval[0]
            intervals.append(interval)

            for i in range(1, amount):
                row_1 = self.ui.intervalsTable.item(0, i).text()
                row_2 = self.ui.intervalsTable.item(1, i).text()
                interval = [float(s) for s in re.findall(r'-?\d+\.?\d*', row_1)]
                frequency.append(int(row_2))
                
                if len(interval) != 2:
                    raise str("ERROR")

                if interval[1] - interval[0] != h:
                    raise str("ERROR")

                if intervals[i - 1][1] != interval[0]:
                    raise str("ERROR")
                
                intervals.append(interval)
            
            self.mainwindow.statistic.setIntervals(intervals, frequency)
        
        except:
            QtWidgets.QMessageBox.warning(self, "Ошибка ввода", "Некорректное значение")
        


    
    def setTable(self):
        columnCount = self.ui.intervalAmountBox.value()

        if columnCount < self.ui.intervalsTable.columnCount():
            self.ui.intervalsTable.setColumnCount(columnCount)
        else:
            for i in range(self.ui.intervalsTable.columnCount(), columnCount):
                self.ui.intervalsTable.insertColumn(i)    

                variation = "[%g, %g]" % (i, i + 1)
                
                self.ui.intervalsTable.horizontalHeader().resizeSection(i, len(variation) * 12)
                self.ui.intervalsTable.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(''))

                self.ui.intervalsTable.setItem(0, i, QtWidgets.QTableWidgetItem(variation))
                self.ui.intervalsTable.setItem(1, i, QtWidgets.QTableWidgetItem("5"))


class mywindow(QtWidgets.QMainWindow):
    '''Конструктор гловного окна'''
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.dialog = dialogwindow(parent=self)

        self.pen = pg.mkPen(color='r', width=3)
        self.pen1 = pg.mkPen(color='r', width=2, style=QtCore.Qt.DashLine)
        self.style1 = {'font-size':'30px'}
        
        self.ui.graphWidget.setBackground((225, 225, 225))
        self.ui.graphWidget.showGrid(x=True, y=True, alpha=1)

        self.ui.plotType.currentIndexChanged.connect(self.buildPlot)
        self.ui.openFileAction.triggered.connect(self.openFile)
        self.ui.rangeType.currentIndexChanged.connect(self.changeRangeType)
        self.ui.interval_amount_button.clicked.connect(self.setIntervalAmount)
        self.ui.dialogBtn.clicked.connect(self.openDialog)

        self.statistic = Statistic()
        self.rangeType = 0
        

    def openDialog(self):
        if self.dialog.exec():
            try:
                self.solve()
                self.ui.interval_amount_button.setEnabled(False)
                self.ui.interval_amount_spin_box.setEnabled(False)
                self.ui.interval_amount_spin_box.setValue(len(self.statistic.interval_series))
                self.ui.variationSeriesText.setText("Задан интервальный ряд")
            except:
                pass
        else:
            print("Cansel")

    def openFile(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Открыть файл", "./", "Text file (*.txt)")
        fileName = fileName[0]
        interval_amount = self.ui.interval_amount_spin_box.value()

        try:
            file = open(fileName, 'r', encoding='utf-8')
            line = file.readline()
            
            serias = line.split(' ')
            serias = [float(var) for var in serias]
            self.statistic.setSeries(serias, interval_amount)
            
            string_serias = ", ".join(str(var) for var in self.statistic.series)
            self.ui.variationSeriesText.setText(string_serias)
            self.ui.interval_amount_button.setEnabled(True)
            self.ui.interval_amount_spin_box.setEnabled(True)
            self.solve()

        except:
            QtWidgets.QMessageBox.warning(self, "Ошибка ввода", "Ошибка ввода!\nПроверьте корректность входного файла")


    
    def changeRangeType(self):
        self.rangeType = self.ui.rangeType.currentIndex()

        if (self.rangeType == 0):
            self.ui.plotType.setItemText(0, 'Гистограмма частот')
            self.ui.plotType.setItemText(1, 'Гистограмма относительных частот')
        else:
            self.ui.plotType.setItemText(0, 'Полигон частот')
            self.ui.plotType.setItemText(1, 'Полигон относительных частот')
        
        if (len(self.statistic.interval_series) > 0):
            self.solve()

    
    def setIntervalAmount(self):
        interval_amount = self.ui.interval_amount_spin_box.value()
        self.statistic.setSeries(self.statistic.series, interval_amount)
        if (len(self.statistic.interval_series) > 0):
            self.solve()


    def solve(self):
        self.setTables()
        self.setDistributionFunction()
        self.setCharacteristic()
        self.buildPlot()       
    
    def buildPlot(self):
        plotType = self.ui.plotType.currentIndex()
        self.ui.graphWidget.clear()

        if (self.rangeType == 0):
            h = self.statistic.interval_series[0][1] - self.statistic.interval_series[0][0]
            var = self.statistic.interval_series
            n = [round((i / h), 4) for i in self.statistic.frequency]
            w = [round((i / h), 4) for i in self.statistic.relative_frequency]
            f = self.statistic.distribution_function

            if (plotType == 0):
                self.plotHistogramma(var, n, PoligonType.FREQUENCY)
            elif (plotType == 1):
                self.plotHistogramma(var, w, PoligonType.PERIODICITY)
            else:
                self.plotDistributionFunction([interval[1] for interval in self.statistic.interval_series], f)
        else:
            var = self.statistic.grouped
            n = self.statistic.frequency
            w = self.statistic.relative_frequency
            f = self.statistic.distribution_function

            if (plotType == 0):
                self.plotPoligon(var, n, PoligonType.FREQUENCY)
            elif (plotType == 1):
                self.plotPoligon(var, w, PoligonType.PERIODICITY)
            else:
                self.plotDistributionFunction(var, f)
        

    def setTables(self):
        columnCount = self.statistic.intervals_amount
        self.ui.frequencyTable.setColumnCount(columnCount)
        self.ui.periodicityTable.setColumnCount(columnCount)

        frequency = self.statistic.frequency
        periodicity = self.statistic.relative_frequency

        if (self.rangeType == 0):
            variationSerias = self.statistic.interval_series
        else:
            variationSerias = self.statistic.grouped

        for i in range(columnCount):
            if (self.rangeType == 0):
                variation = "[%g, %g]" % (variationSerias[i][0], variationSerias[i][1])
            else:
                variation = "%g" % variationSerias[i]

            self.ui.frequencyTable.horizontalHeader().resizeSection(i, len(variation) * 12)
            self.ui.frequencyTable.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(''))

            self.ui.frequencyTable.setItem(0, i, QtWidgets.QTableWidgetItem(variation))
            self.ui.frequencyTable.item(0, i).setFlags(QtCore.Qt.ItemIsEnabled)

            self.ui.frequencyTable.setItem(1, i, QtWidgets.QTableWidgetItem(str(frequency[i])))
            self.ui.frequencyTable.item(1, i).setFlags(QtCore.Qt.ItemIsEnabled)

            self.ui.periodicityTable.horizontalHeader().resizeSection(i, max(len(variation) * 12, 72))
            self.ui.periodicityTable.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(''))

            self.ui.periodicityTable.setItem(0, i, QtWidgets.QTableWidgetItem(variation))
            self.ui.periodicityTable.item(0, i).setFlags(QtCore.Qt.ItemIsEnabled)
            
            self.ui.periodicityTable.setItem(1, i, QtWidgets.QTableWidgetItem(str(periodicity[i])))
            self.ui.periodicityTable.item(1, i).setFlags(QtCore.Qt.ItemIsEnabled)


    def setDistributionFunction(self):
        string_function = ""
        patern_string = "%g, при %g < x ≤ %g"
        amount = self.statistic.intervals_amount
        f = self.statistic.distribution_function

        if (self.rangeType == 0):
            interval_series = self.statistic.interval_series
            var = [interval[1] for interval in interval_series]   
        else:
            var = self.statistic.grouped

        string_function += "0, при x ≤ %g" % var[0] + "\n"
        for i in range(amount - 1):
            string_function += patern_string % (f[i + 1], var[i], var[i + 1]) + "\n"
        string_function += "1, при x > %g" % var[amount - 1]

        self.ui.functionEdit.setText(string_function)


    def setCharacteristic(self):
        midX = "{:01.8}".format(self.statistic.average_sample)
        d = "{:01.8}".format(self.statistic.dispersion)
        cigma = "{:01.8}".format(self.statistic.deviation)
        s = "{:01.8}".format(self.statistic.corrected_deviation)

        self.ui.middleXEdit.setText(midX)
        self.ui.dispersionEdit.setText(d)
        self.ui.cigmaEdit.setText(cigma)
        self.ui.sEdit.setText(s)

    
    def plotDistributionFunction(self, variationSeries : list, function : list):
        amount = len(variationSeries)
        
        self.ui.graphWidget.setXRange(variationSeries[0], variationSeries[amount - 1])
        self.ui.graphWidget.setYRange(0, 1)
        self.ui.graphWidget.setTitle("Эмпирическая функция распределения", color=(0, 0, 0), size="15pt")
        self.ui.graphWidget.setLabel('left', "F*(x)", **self.style1)
        self.ui.graphWidget.setLabel('bottom', "x", **self.style1)

        for i in range(amount - 1):
            xi = [variationSeries[i], variationSeries[i + 1]]
            yi = [function[i + 1], function[i + 1]]
            self.ui.graphWidget.plot(xi, yi, pen=self.pen)

        self.ui.graphWidget.plot([-100 * variationSeries[amount - 1], variationSeries[0]], [0, 0], pen=self.pen)    
        self.ui.graphWidget.plot([variationSeries[amount - 1], 100 * variationSeries[amount - 1]], [1, 1], pen=self.pen)

        for i in range(amount):
            xi = [variationSeries[i], variationSeries[i]]
            yi = [function[i + 1], function[i + 1]]
            self.ui.graphWidget.plot(xi, yi, symbol='t3', symbolSize=15, symbolBrush='r')

    
    def plotPoligon(self, variationSeries : list, periodicity : list, type : PoligonType):
        symbols = ["n", "w"]
        texts = ["частот", "относительной частот"]

        symbol = symbols[type.value]
        text = texts[type.value]

        self.ui.graphWidget.setXRange(variationSeries[0], variationSeries[len(variationSeries) - 1])
        self.ui.graphWidget.setYRange(min(periodicity), max(periodicity))
        self.ui.graphWidget.setTitle("Полигон " + text, color=(0, 0, 0), size="15pt")
        self.ui.graphWidget.setLabel('left', symbol + "(x)", **self.style1)
        self.ui.graphWidget.setLabel('bottom', "x", **self.style1)
                
        self.ui.graphWidget.plot(variationSeries, periodicity, pen=self.pen, symbol='d', symbolSize=15, symbolBrush='r')

    
    def plotHistogramma(self, interlans, periodicity, type : PoligonType):
        symbols = ["n(x)/h", "w(x)/h"]
        texts = ["частот", "относительной частот"]

        symbol = symbols[type.value]
        text = texts[type.value]
        amount = len(interlans)
        
        self.ui.graphWidget.setXRange(interlans[0][0], interlans[len(interlans) - 1][1])
        self.ui.graphWidget.setYRange(0, max(periodicity))
        self.ui.graphWidget.setTitle("Гистограмма " + text, color=(0, 0, 0), size="15pt")
        self.ui.graphWidget.setLabel('left', symbol, **self.style1)
        self.ui.graphWidget.setLabel('bottom', "x", **self.style1)

        for i in range(len(interlans)):
            xi = [interlans[i][0], interlans[i][1]]
            yi = [periodicity[i], periodicity[i]]
            self.ui.graphWidget.plot(xi, yi, pen=self.pen)

        for i in range(amount):
            xi = [interlans[i][0], interlans[i][0]]
            
            if (i  == 0):
                yi = [0, periodicity[i]]
            else:
                yi = [0, max(periodicity[i - 1], periodicity[i])]
            
            self.ui.graphWidget.plot(xi, yi, pen=self.pen)

        xi = [interlans[amount - 1][1], interlans[amount - 1][1]]
        yi = [0, periodicity[amount - 1]]
        self.ui.graphWidget.plot(xi, yi, pen=self.pen)
        
    
    
def main():
    app = QtWidgets.QApplication([])
    application = mywindow()
    application.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()