import sys, traceback
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import QTimer, QRunnable, Slot, Signal, QObject, QThreadPool, QModelIndex, QAbstractListModel,Qt
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import numpy as np
import time

from MainWindow import Ui_MainWindow


#Matplotlib default set of colors
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2',
 '#7f7f7f', '#bcbd22', '#17becf']

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)

class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    see https://www.pythonguis.com/tutorials/multithreading-pyqt6-applications-qthreadpool/

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

class SpectraViewList(QAbstractListModel):
    """Abstract view list of the spectra, handles the view of them in the widget
    see: https://www.pythonguis.com/tutorials/pyqt6-modelview-architecture/"""

    check_state_changed = Signal(QModelIndex, Qt.CheckState) #Custom signal to toggle visibility in the plot

    def __init__(self, *args, spectraList = None, **kwargs):
        super(SpectraViewList, self).__init__(*args, **kwargs)
        self.spectraList = spectraList or []

    #The data to be displayed
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            name = self.spectraList[index.row()]['name']
            return name
        
        if role == Qt.ItemDataRole.DecorationRole:
            color = self.spectraList[index.row()]['color']
            return color
        
        if role == Qt.ItemDataRole.CheckStateRole:
            visible = self.spectraList[index.row()]['visible']
            if visible:
                return Qt.CheckState.Checked
            else:
                return Qt.CheckState.Unchecked
    
    #Change the data of the spectraList when the user interacts with
    #the widget
    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.EditRole:
            if value != "":
                self.spectraList[index.row()]['name'] = value
                return True 
            else:
                return False
        
        if role == Qt.ItemDataRole.CheckStateRole:
            self.spectraList[index.row()]['visible'] = value
            
             # Emit signal when check state changes
            check_state = Qt.CheckState(value)
            self.check_state_changed.emit(index, check_state)
            return True
    
    #Return the maximum rows for the count   
    def rowCount(self, index):
        return len(self.spectraList)
    
    #Enable the flags so that the items are editable and checkable
    def flags(self, index):
        return super(SpectraViewList, self).flags(index)|Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEditable

def get_fake_spectrum():
    x = np.arange(100)
    y = np.random.rand(100)
    time.sleep(1)
    return (x, y)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        #Create a threadpool for multithreading
        self.threadpool = QThreadPool()  

        #Plot Attributes
        self.plotWidget.setBackground('w')
        self.plotWidget.setLabel('left', 'Power (dBm)')
        self.plotWidget.setLabel('bottom', 'Wavelength (nm)')

        #Buttons slot connections
        self.SweepPushButton.clicked.connect(self.getAndPlotSpectrum)
        self.DeletePushButton.clicked.connect(self.deleteTrace)

        self.model = SpectraViewList() # Set the model to be used and link it to the list of spectra
        self.listView.setModel(self.model) # Assign to the listView widget the model



    @Slot()
    def getAndPlotSpectrum(self):
        """Triggers the plot acquisition in a different thread. When the spectrum sweep is finished, it plots it"""
        worker_get_spectrum = Worker(get_fake_spectrum)
        worker_get_spectrum.signals.result.connect(self.plotSpectrum)
        self.threadpool.start(worker_get_spectrum)


    @Slot()
    def plotSpectrum(self, spectrum):
        """Plots the spectrum and adds it to the list of spectra"""
        power, wavelength = spectrum[0], spectrum[1]
        color = QtGui.QColor(colors[len(self.model.spectraList)])
        pen = pg.mkPen(color= color)
        plot = self.plotWidget.plot(power, wavelength, name = f'Trace {len(self.model.spectraList)}', pen = pen)
        list_item_dict = dict(name = f'Trace {len(self.model.spectraList)}', color = color, visible =True, plot = plot)
        self.model.spectraList.append(list_item_dict)
        # Trigger refresh.
        self.model.layoutChanged.emit()

        
    @Slot()
    def deleteTrace(self):
        """Delete the selected spectrum in the list, but first asks for confirmation"""
        #Dialog that asks for confirmation
        button = QtWidgets.QMessageBox.question(self, "Delete confirmation", "Do you want to delete the selected trace?")

        if button == QtWidgets.QMessageBox.StandardButton.Yes: #Get the sel index from the view

            indexes = self.listView.selectedIndexes()
            if indexes:
                # Indexes is a list of a single item in single-select mode.
                index = indexes[0]
                #Remove the spectrum from the plot
                self.plotWidget.removeItem(self.model.spectraList[index.row()]['plot'])
                # Remove the item and refresh.
                del self.model.spectraList[index.row()]
                self.model.layoutChanged.emit()
                # Clear the selection (as it is no longer valid).
                self.listView.clearSelection()

    




app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion' )

window = MainWindow()
window.show()
app.exec()