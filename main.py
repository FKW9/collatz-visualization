VERSION = '0.2.0'

import sys
import ctypes
import icon_rc

import numpy as np
import pyqtgraph as pg

from win import Ui_MainWindow

from PyQt5 import QtCore, QtGui
from PyQt5.QtWinExtras import QtWin
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

# to show taskbar item...
app_id = u'3N+1.V'+VERSION
QtWin.setCurrentProcessExplicitAppUserModelID(app_id)

# set colors of plots
pg.setConfigOption('background', '#f0f0f0')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(antialias=True)

# import custom c function
collatz = ctypes.CDLL('collatz_c/x64/Release/collatz.dll')

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #uic.loadUi('resources/win.ui', self)
        self.spinBox.setMaximum(1000000000000)
        self.horizontalSlider.valueChanged.connect(self.spinBox.setValue)

        self.digit_count = []
        self.threads = []
        self.stops_x = []
        self.stops_y = []

        self.message1 = ''
        self.message2 = ''

        # set title
        self.setWindowTitle('Collatz Conjecture Visualized V'+VERSION)
        self.splitter_3.setStyleSheet("background-color: #c7c7c7")
        self.statusbar.setStyleSheet("background-color: #f0f0f0")

        # connect signals
        self.actionAbout.triggered.connect(self.about)
        self.actionStopCalculation.triggered.connect(self.stop_threads)
        self.spinBox.valueChanged.connect(self.plot_single_sequence)

        # configure first plotWidget 
        self.plotFull.showGrid(x=True, y=True, alpha=0.4)
        self.plotFull.setLabels(title='single sequence', left='value N', bottom='iteration')
        self.curve_single_seq = self.plotFull.plot(symbol='o', symbolSize=4, pen=pg.mkPen('r', width=1))
        self.label_max_number = pg.TargetItem(size=4, symbol='o', label='max={1:0,.0f}', labelOpts={'color':'#0061FF', 'offset':(4,2)})
        self.plotFull.addItem(self.label_max_number)

        # configure second plotWidget
        self.plotHisto.showGrid(x=False, y=True, alpha=0.4)
        self.plotHisto.setLabels(title='digit count in full sequence (1 to N)', left='count', bottom='digit')
        self.bar_graph_item    = pg.BarGraphItem(x=np.arange(1,10), height=0, width=0.5, brush=(0,0,255,160), pen=(0,0,0,0))
        self.label_digit_count = pg.TargetItem(size=0)
        self.plotHisto.addItem(self.bar_graph_item)
        self.plotHisto.addItem(self.label_digit_count)

        self.proxy1 = pg.SignalProxy(self.plotHisto.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved_digit)

        # configure third plotWidget
        self.plotLog.showGrid(x=True, y=True, alpha=0.4)
        self.plotLog.setLogMode(False, True)
        self.plotLog.setLabels(title='log of single sequence', left='log10(N)', bottom='iteration')
        self.curve_single_log_seq   = self.plotLog.plot(pen=pg.mkPen('#0072FF', width=1))
        self.curve_single_log_trend = pg.InfiniteLine(angle=0, pos=0, pen=pg.mkPen('r', width=1))
        self.plotLog.addItem(self.curve_single_log_trend)

        # configure fourth plotWidget
        self.plotStoppingTimes.showGrid(x=False, y=True, alpha=0.4)
        self.plotStoppingTimes.setLabels(title='stopping times in full sequence (1 to N)', left='frequency', bottom='stopping time')
        self.bar_graph_2      = pg.BarGraphItem(x=np.arange(1,10), height=0, width=1, brush=(0,0,255,160), pen=(0,0,0,0))
        self.label_stops_freq = pg.TargetItem(size=0)
        self.plotStoppingTimes.addItem(self.bar_graph_2)
        self.plotStoppingTimes.addItem(self.label_stops_freq)

        self.proxy2 = pg.SignalProxy(self.plotStoppingTimes.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved_stop)

        # create thread to compute digit count in full sequence
        self.t1 = QtCore.QThread()
        self.w1 = CalcFirstDigitCount()
        self.w1.moveToThread(self.t1)
        self.w1.data_digits.connect(self.plot_digit_count)
        self.w1.status.connect(self.update_digit_count_histo)
        self.threads.append(self.t1)

        # create thread to compute stopping times in full sequence
        self.t2 = QtCore.QThread()
        self.w2 = CalcStoppingTimes()
        self.w2.moveToThread(self.t2)
        self.w2.data_stopps.connect(self.plot_stopping_times)
        self.w2.status.connect(self.update_stopping_histo)
        self.threads.append(self.t2)

        # connect worker signal to process data_digits
        self.spinBox.valueChanged.connect(self.w1.calculate)
        self.spinBox.valueChanged.connect(self.w2.calculate)

        # start thread
        self.start_threads()

        # starting value
        self.spinBox.valueChanged.emit(int(self.spinBox.value()))
    
    def start_threads(self):
        for t in self.threads:
            t.start()

    def mouse_moved_digit(self, evt):
        pos = evt[0]  # using signal proxy turns original arguments into a tuple
        if self.plotHisto.sceneBoundingRect().contains(pos):
            mousePoint = self.plotHisto.plotItem.vb.mapSceneToView(pos)
            x = mousePoint.x()

            for i in range(1,10):
                if (i-0.22) < x < (i+0.22):
                    self.label_digit_count.setPos((mousePoint.x(), mousePoint.y()))
                    self.label_digit_count.setLabel('c={:0,.0f}'.format(self.digit_count[i-1]), labelOpts={'color':'k'})
                    break
                else:
                    self.label_digit_count.setLabel('')

    def mouse_moved_stop(self, evt):
        pos = evt[0]  # using signal proxy turns original arguments into a tuple
        if self.plotStoppingTimes.sceneBoundingRect().contains(pos):
            mousePoint = self.plotStoppingTimes.plotItem.vb.mapSceneToView(pos)

            x, y = mousePoint.x(), 0
            try:
                idx = self.stops_x.index(int(x+0.5))
                y = self.stops_y[idx]
            except ValueError:
                pass

            self.label_stops_freq.setPos((x, mousePoint.y()))
            self.label_stops_freq.setLabel('t={:0,.0f}\nf={:0,.0f}'.format(x, y), labelOpts={'color':'k'})

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
        y_values = [new_value]

        while new_value != 1:
            if new_value%2 == 0:
                new_value = new_value//2
            else:
                new_value = 3*new_value+1
            y_values.append(new_value)

        x_values = range(1, len(y_values)+1)

        self.curve_single_seq.setData(x_values, y_values)
        self.curve_single_log_seq.setData(x_values, y_values)
        self.label_max_number.setPos((y_values.index(max(y_values))+1, np.max(y_values)))

        if self.checkGraph.isChecked():
            self.plotFull.setRange(xRange=x_values, yRange=[1, max(y_values)])

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
        self.curve_single_log_trend.setAngle(np.degrees(np.arctan(m*1+b - b)))
        self.curve_single_log_trend.setPos((0, b))
        
        if self.checkLog.isChecked():
            self.plotLog.setRange(xRange=x, yRange=[0, np.log10(max(y))])

    def plot_digit_count(self, y):
        
        self.bar_graph_item.setOpts(height=y)
        self.digit_count = y

        if self.checkHisto.isChecked():
            self.plotHisto.setRange(xRange=range(1,10), yRange=[0, max(y)])
        
    def plot_stopping_times(self, xk, yk):
        self.stops_x = xk
        self.stops_y = yk
        self.bar_graph_2.setOpts(x=xk, height=yk)

        if self.checkStop.isChecked():
            self.plotStoppingTimes.setRange(xRange=xk, yRange=yk)

    def about(self):
        QMessageBox.about(self, 'Collatz Conjecture', '<html><head/><body><p><span style=" font-size:9pt; color:#000000;">The Collatz conjecture is a conjecture in mathematics that concerns sequences defined as follows:<br/><br/>Start with any positive integer</span><span style=" font-size:9pt; font-weight:600; color:#000000;"> n &gt; 0. </span><span style=" font-size:9pt; color:#000000;">Then each term is obtained from the previous term as follows:<br/></span><span style=" font-size:9pt; font-weight:600; color:#000000;"><br/></span><span style=" font-size:9pt; color:#000000;">→ is </span><span style=" font-size:9pt; font-weight:600; color:#000000;">n</span><span style=" font-size:9pt; color:#000000;"> even, then the next term is </span><span style=" font-size:9pt; font-weight:600; color:#000000;">n/2<br/></span><span style=" font-size:9pt; color:#000000;">→ if </span><span style=" font-size:9pt; font-weight:600; color:#000000;">n</span><span style=" font-size:9pt; color:#000000;"> is odd, the next term is </span><span style=" font-size:9pt; font-weight:600; color:#000000;">3n+1<br/><br/></span><span style=" font-size:9pt; color:#000000;">The conjecture is that no matter what value of </span><span style=" font-size:9pt; font-weight:600; color:#000000;">n</span><span style=" font-size:9pt; color:#000000;">, the sequence will always reach </span><span style=" font-size:9pt; font-weight:600; color:#000000;">1.<br/><br/>@TODO:<br/></span><span style=" font-size:9pt; color:#000000;">- add benfords law<br/>- stock market comparison / trend<br/>- stopping time<br/><br/></span><span style=" font-size:9pt; color:#000000;">Source:<br/></span><a href="https://en.wikipedia.org/wiki/Collatz_conjecture"><span style=" font-size:9pt; text-decoration: underline; color:#0000ff;">Wikipedia</span></a><a href="https://de.wikipedia.org/wiki/Collatz-Problem"><span style=" font-size:9pt; text-decoration: underline; color:#1e00ff;"><br/></span></a><a href="https://www.youtube.com/watch?v=094y1Z2wpJg&amp;ab_channel=Veritasium"><span style=" font-size:9pt; text-decoration: underline; color:#0000ff;">Veritasium on YouTube</span></a></p></body></html>')

    def update_digit_count_histo(self, status):
        self.message1 = status
        self.update_statusbar()

    def update_stopping_histo(self, status):
        self.message2 = status
        self.update_statusbar()

    def update_statusbar(self, text=None):
        self.statusbar.setStyleSheet("background-color: #FFC300")
        self.statusbar.showMessage('   '+self.message1+' '+self.message2)
        if len(self.statusbar.currentMessage())==4:
            self.statusbar.setStyleSheet("background-color: #f0f0f0")
        
        if text != None:
            self.statusbar.showMessage(text)

    def stop_threads(self):
        for t in self.threads:
            t.terminate()
            t.wait()

        if self.w1.busy is True:
            self.update_statusbar('calculation terminated')
            self.bar_graph_item.setOpts(height=0)

        if self.w2.busy is True:
            self.update_statusbar('calculation terminated')
            self.bar_graph_2.setOpts(height=0)
        
        for t in self.threads:
            t.start()

    # reimplement closeEvent method
    def closeEvent(self, event):
        self.stop_threads()

class CalcFirstDigitCount(QObject):

    data_digits = pyqtSignal(list)
    status = pyqtSignal(str)
    busy = False

    @pyqtSlot(float)
    def calculate(self, val):
        """
        Calculates the digit count for each digit from 1-9 in a full collatz sequence.
        To speed up the process, i wrote a c++ function which does the job for us much faster.

        Parameters
        ----------
        val : int
            Starting Number of Sequence
        """
        self.busy = True
        self.status.emit('calculating digit count...')

        val = ctypes.c_ulonglong(int(val))
        digit_count = (ctypes.c_ulonglong * 9)()
        # void get_digit_count(unsigned long long *buf, unsigned long long val){...}
        collatz.get_digit_count(digit_count, val)

        self.busy = False
        self.status.emit('')
        self.data_digits.emit(digit_count[:])


class CalcStoppingTimes(QObject):

    data_stopps = pyqtSignal(list, list)
    status = pyqtSignal(str)
    busy = False

    @pyqtSlot(float)
    def calculate(self, val):
        """
        Calculates the digit count for each digit from 1-9 in a full collatz sequence.
        To speed up the process, i wrote a c++ function which does the job for us much faster.

        Parameters
        ----------
        val : int
            Starting Number of Sequence
        """
        self.busy = True
        self.status.emit('calculating stopping times...')

        val = ctypes.c_ulonglong(int(val))
        arr_size = collatz.get_arr_size(val)
        stops, frequ = (ctypes.c_ulonglong * arr_size)(), (ctypes.c_ulonglong * arr_size)()
        collatz.get_stopping_times(stops, frequ)

        self.busy = False
        self.status.emit('')
        self.data_stopps.emit(stops[:], frequ[:])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(':3n1.ico'))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
