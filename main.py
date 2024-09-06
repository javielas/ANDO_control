import sys, traceback
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import QTimer, QRunnable, Slot, Signal, QObject, QThreadPool, QModelIndex, QAbstractListModel,Qt
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import numpy as np
import time


from MainWindow import Ui_MainWindow

offline_mode = True

if not offline_mode: import osa_driver

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


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        #Create a threadpool for multithreading
        self.threadpool = QThreadPool()  

        self.model = SpectraViewList() # Set the model to be used and link it to the list of spectra
        self.listView.setModel(self.model) # Assign to the listView widget the model

        self.sens_dict = {
            'Hold': 'SNHD',
            'Auto': 'SNAT',
            'High 1': 'SHI1',
            'High 2': 'SHI2',
            'High 3': 'SHI3'
        }

        #Plot Attributes
        self.plotWidget.setBackground('w')
        styles = {"color": "k", "font-size": "25px"}
        self.plotWidget.setLabel('left', 'Power (dBm)', **styles)
        self.plotWidget.setLabel('bottom', 'Wavelength (nm)', **styles)
        self.plotWidget.showGrid(x=True, y=True)

        #XY label coordinates for the plot
        self.x_label = pg.LabelItem("X:   ", color = 'k', size = '15pt')
        self.y_label = pg.LabelItem("Y:   ", color = 'k', size = '15pt')
        self.x_label.setParentItem(self.plotWidget.graphicsItem())
        self.y_label.setParentItem(self.plotWidget.graphicsItem())
        self.x_label.anchor(itemPos=(0.15, 0.9), parentPos=(0.03, 0.97))
        self.y_label.anchor(itemPos=(0.15, 0.9), parentPos=(0.03, 1))

        #Cross Cursor with lines
        cursor = Qt.CursorShape.CrossCursor
        self.plotWidget.setCursor(cursor)
        self.crosshair_en = True
        self.crosshair_v = pg.InfiniteLine(angle=90, movable=False)
        self.crosshair_h = pg.InfiniteLine(angle=0, movable=False)
        self.plotWidget.addItem(self.crosshair_v, ignoreBounds=True)
        self.plotWidget.addItem(self.crosshair_h, ignoreBounds=True)
        # Assign slot to the mousemovement
        self.proxy = pg.SignalProxy(self.plotWidget.scene().sigMouseMoved, rateLimit=60, slot=self.update_crosshair)

        #Buttons slot connections
        self.SweepPushButton.clicked.connect(self.getAndPlotSpectrum)
        self.DeletePushButton.clicked.connect(self.deleteTrace)
        self.model.check_state_changed.connect(self.handle_check_state_changed)

    def get_spectrum(self):
        start = self.startWavlengthDoubleSpinBox.value()
        stop = self.stopWavelengthDoubleSpinBox.value()
        resolution = self.resoltuionNmDoubleSpinBox.value()
        reference = self.referenceLevelDoubleSpinBox.value()
        sel_sensitivity = self.sensitivityComboBox.currentText()
        sensitivity = self.sens_dict[sel_sensitivity]
        trace = 'A'
        wl, power = osa_driver.get_trace(trace, start, stop, reference, resolution, sensitivity)
        return dict(wl = wl, power = power, start = start, stop = stop, resolution = resolution, 
                    reference = reference, sel_sensitivity = sel_sensitivity)

    @Slot()
    def get_fake_spectrum(self):
        start = self.startWavlengthDoubleSpinBox.value()
        stop = self.stopWavelengthDoubleSpinBox.value()
        resolution = self.resoltuionNmDoubleSpinBox.value()
        reference = self.referenceLevelDoubleSpinBox.value()
        sel_sensitivity = self.sensitivityComboBox.currentText()
        x = np.arange(100)
        y = np.random.rand(100)
        time.sleep(1)
        return dict(wl = x, power = y, start = start, stop = stop, resolution = resolution, 
                    reference = reference, sel_sensitivity = sel_sensitivity)

    @Slot() 
    def getAndPlotSpectrum(self):
        """Triggers the plot acquisition in a different thread. When the spectrum sweep is finished, it plots it"""
        if offline_mode:
            worker_get_spectrum = Worker(self.get_fake_spectrum)
        else:
            worker_get_spectrum = Worker(self.get_spectrum)
        worker_get_spectrum.signals.result.connect(self.plotSpectrum)
        self.threadpool.start(worker_get_spectrum)


    @Slot()
    def plotSpectrum(self, spectrum):
        """Plots the spectrum and adds it to the list of spectra"""
        wavelength, power = spectrum['wl'], spectrum['power']
        #Get the previous color from the list or start with the first one
        if len(self.model.spectraList) != 0:
            previous_color = self.model.spectraList[-1]['color']
            color = QtGui.QColor(colors[(colors.index(previous_color)+1) % len(colors)]) 
        else:
            color = QtGui.QColor(colors[0])
        #Get the color that's the next from the last one in the list
        pen = pg.mkPen(color= QtGui.QColor(color))
        plot = self.plotWidget.plot(wavelength, power, name = f'Trace {len(self.model.spectraList)}', pen = pen)
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


    @Slot()
    def handle_check_state_changed(self, index, state):
        """Show or hide the trace in the plot"""
        trace = self.model.spectraList[index.row()]['plot']
        if state == Qt.CheckState.Checked: #If checked make it visible
            self.plotWidget.addItem(trace)
        else:
            self.plotWidget.removeItem(trace) 
    
    @Slot()
    def update_crosshair(self, e):
        pos = e[0]
        if self.plotWidget.sceneBoundingRect().contains(pos):
            mousePoint = self.plotWidget.getPlotItem().vb.mapSceneToView(pos)
            self.crosshair_v.setPos(mousePoint.x())
            self.crosshair_h.setPos(mousePoint.y())
            self.x_label.setText(f'X: {mousePoint.x():.2f}')
            self.y_label.setText(f'Y: {mousePoint.y():.2f}')

app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion' )

window = MainWindow()
window.show()
app.exec()