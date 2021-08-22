VERSION = '0.1.5'

import sys
import ctypes

import icon_rc
import numpy as np
import pyqtgraph as pg

from win import Ui_MainWindow

from PyQt5.QtWinExtras import QtWin
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QPointF

# to show taskbar item...
app_id = u'3N+1.V'+VERSION
QtWin.setCurrentProcessExplicitAppUserModelID(app_id)

# set colors of plots
pg.setConfigOption('background', '#f0f0f0')
pg.setConfigOption('foreground', 'k')

# import custom c function
collatz = ctypes.CDLL('lib/collatz.dll')

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # set title
        self.setWindowTitle('Collatz Conjecture Visualized V'+VERSION)

        # connect signals
        self.actionAbout.triggered.connect(self.about)
        self.actionStopCalculation.triggered.connect(self.terminate_thread)
        self.spinBox.valueChanged.connect(self.plot_single_sequence)

        # configure first plotWidget 
        self.plotWidget.showGrid(x=True, y=True, alpha=0.4)
        self.plotWidget.setLabels(title='single Sequence', left='Value N', bottom='iteration')
        self.curveSingleSequence = self.plotWidget.plot(symbol='o', symbolSize=4, pen=pg.mkPen('r', width=1))

        # configure second plotWidget
        self.plotHisto.showGrid(x=False, y=True, alpha=0.4)
        self.plotHisto.setLabels(title='digit count of full Sequence', left='count', bottom='digit')
        self.BarItem = pg.BarGraphItem(x=np.arange(1,10), height=0, width=0.5, brush=(0,0,255,110))
        self.plotHisto.addItem(self.BarItem)

        # configure third plotWidget
        self.plotLog.showGrid(x=True, y=True, alpha=0.4)
        self.plotLog.setLogMode(False, True)
        self.plotLog.setLabels(title='log of single Sequence', left='log10(N)', bottom='iteration')
        self.curveLogarithmicSequence = self.plotLog.plot(pen=pg.mkPen('#0072FF', width=1))
        self.curveLogarithmicTrend = pg.InfiniteLine(angle=0, pos=0, pen=pg.mkPen('r', width=1))
        self.plotLog.addItem(self.curveLogarithmicTrend)

        self.targetItem2 = pg.TargetItem(size=4, symbol='o', label='max={1:0,.0f}', labelOpts={'color':'#0061FF', 'offset':(4,2)})
        self.plotWidget.addItem(self.targetItem2)

        # create thread for heavy load (compute digit count in full sequence)
        self.thread = QtCore.QThread()
        self.worker = CalculateValues()
        self.worker.moveToThread(self.thread)
        self.worker.data.connect(self.plot_digit_count)
        self.worker.status.connect(self.status_update)

        # connect worker signal to process data
        self.spinBox.valueChanged.connect(self.worker.compute_digit_count)

        # start thread
        self.thread.start()

        # starting value
        self.spinBox.valueChanged.emit(self.spinBox.value())
		
    def status_update(self, status):
        self.plotHisto.setLabels(title='digit count of full sequence'+' '+status)

    def plot_single_sequence(self, val):
        """
        Calculates a single collatz sequence until it hits 1.
        Plots it on the left Graph and on the lower right Graph but with y-axis logarithmic scale.
        Autoscales both graphs if the checkBox is checked by user.

        Parameters
        ----------
        val : int
            Starting Number of Sequence
        """
        new_value = val
        y_values = np.array([new_value], dtype=ctypes.c_ulonglong)

        while new_value != 1:
            if new_value%2 == 0:
                new_value = new_value//2
            else:
                new_value = 3*new_value+1
            y_values = np.append(y_values, new_value)

        x_values = np.arange(1, len(y_values)+1)

        self.curveSingleSequence.setData(x_values, y_values)
        self.curveLogarithmicSequence.setData(x_values, y_values)
        self.targetItem2.setPos((np.where(y_values == np.max(y_values))[0]+1, np.max(y_values)))

        if self.checkGraph.isChecked():
            self.plotWidget.setRange(xRange=x_values, yRange=[1, max(y_values)])

        self.plot_trend(x_values, y_values, val)

    def plot_trend(self, x, y, val):
        """
        Calculates a linear function which fits the logarithmic graph the best.
        Plots it on the left Graph and autoscales it if the checkBox is checked by user.

        Parameters
        ----------
        val : int
            Starting Number of Sequence
        x : list of ints
            x data
        y : list of ints
            y data
        """
        if val > 1:
            m, b = np.polyfit(x, [np.log10(i) for i in y], 1)
        else:
            m, b = 0, 0

        # calculate angle and offset of linear function
        self.curveLogarithmicTrend.setAngle(np.degrees(np.arctan(m*1+b - b)))
        self.curveLogarithmicTrend.setPos(QPointF(0, b))
        
        if self.checkLog.isChecked():
            self.plotLog.setRange(xRange=x, yRange=[0, np.log10(max(y))])

    def plot_digit_count(self, y):
        self.BarItem.setOpts(height=y)

        if self.checkHisto.isChecked():
            self.plotHisto.setRange(xRange=np.arange(1,10), yRange=[0, max(y)])

    def about(self):
        QMessageBox.about(self, "Um was geht es?", '<html><head/><body><p><span style=" font-size:9pt; color:#000000;">&quot;Das Collatz-Problem, auch als (3n+1)-Vermutung bezeichnet, ist ein ungelöstes mathematisches Problem, das 1937 von Lothar Collatz gestellt wurde&quot;<br/></span></p><p><span style=" font-size:9pt; color:#000000;">Bei dem Problem geht es um Zahlenfolge, die nach einem einfachen Bildungsgesetz konstruiert werden:<br/>→ Beginne mit irgendeiner natürlichen Zahl</span><span style=" font-size:9pt; font-weight:600; color:#000000;"> n &gt; 0<br/></span><span style=" font-size:9pt; color:#000000;">→ Ist </span><span style=" font-size:9pt; font-weight:600; color:#000000;">n</span><span style=" font-size:9pt; color:#000000;"> gerade, so nimm als nächstes </span><span style=" font-size:9pt; font-weight:600; color:#000000;">n/2<br/></span><span style=" font-size:9pt; color:#000000;">→ Ist </span><span style=" font-size:9pt; font-weight:600; color:#000000;">n</span><span style=" font-size:9pt; color:#000000;"> ungerade, so nimm als nächstes </span><span style=" font-size:9pt; font-weight:600; color:#000000;">3n+1<br/></span><span style=" font-size:9pt; color:#000000;">→ Wiederhole die Vorgehensweise mit der erhaltenen Zahl<br/></span></p><p><span style=" font-size:9pt; color:#000000;">Quellen:<br/></span><a href="https://de.wikipedia.org/wiki/Collatz-Problem"><span style=" font-size:9pt; text-decoration: underline; color:#1E00FF;">Wikipedia Eintrag<br/></span></a><a href="https://www.youtube.com/watch?v=094y1Z2wpJg&amp;amp;ab_channel=Veritasium"><span style=" font-size:9pt; text-decoration: underline; color:#1E00FF;">Veritasium auf YouTube</span></a></p></body></html>')
    
    def terminate_thread(self):
        if self.worker.busy is True:
            self.thread.terminate()
            self.thread.wait()
            self.status_update('(terminated)')
            self.plot_digit_count(np.linspace(0, 0, 9, dtype=int))
            self.thread.start()

    # reimplement closeEvent method
    def closeEvent(self, event):
        self.thread.terminate()
        self.thread.wait()

class CalculateValues(QObject):

    data   = pyqtSignal(list)
    status = pyqtSignal(str)
    busy = False

    @pyqtSlot(int)
    def compute_digit_count(self, val):
        """
        Calculates the digit count for each digit from 1-9 in a full collatz sequence.
        To speed up the process, i wrote a c function which does the job for us much faster.

        Parameters
        ----------
        val : int
            Starting Number of Sequence
        """
        self.busy = True
        self.status.emit('(calculating...)')

        # C unsigned long long array which is our buffer
        digit_count = (ctypes.c_ulonglong * 9)()
        val = ctypes.c_ulonglong(val)
        # C Function implementation: void get_digit_count(unsigned long long *buf, unsigned long long val){...}
        collatz.get_digit_count(digit_count, val)

        self.busy = False
        self.status.emit('')
        self.data.emit(digit_count[:]) # Bug: every second item is zero?

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(':3n1.ico'))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
