import sys, traceback
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import QTimer, QRunnable, Slot, Signal, QObject, QThreadPool, QModelIndex, QAbstractListModel,Qt
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import numpy as np
import time, datetime
from pint import UnitRegistry
import csv, pickle


from MainWindow import Ui_MainWindow

ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)
Q_ = ureg.Quantity

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
        self.SavePushButton.clicked.connect(self.saveChecked)
        self.model.check_state_changed.connect(self.handle_check_state_changed)

        #Initialize values for comparison of parameters between sweep calls
        self.start = np.nan
        self.stop = np.nan
        self.resolution = np.nan
        self.reference  = np.nan
        self.sensitivity = np.nan
        self.trace = np.nan

    def get_spectrum(self, updated_params):
        wl, power = osa_driver.get_trace(updated_params)
        return dict(wl = wl, power = power)



    @Slot()
    def get_fake_spectrum(self, updated_params):
        """This is a fake spectrum, it is used to test the GUI"""
        #Generate fake data
        x = np.arange(100)
        y = np.random.rand(100)
        time.sleep(1)
        spectrum_data = {
        'wavelength': Q_(x,  ureg.nm),
        'power': Q_(y , ureg.dBm),
        }
        return spectrum_data

    @Slot() 
    def getAndPlotSpectrum(self):
        """Triggers the plot acquisition in a different thread. When the spectrum sweep is finished, it plots it"""
        updated_params = dict()
        #Get the parameters from the GUI
        start = self.startWavlengthDoubleSpinBox.value() * ureg.nm
        stop = self.stopWavelengthDoubleSpinBox.value() * ureg.nm
        resolution = self.resoltuionNmDoubleSpinBox.value() * ureg.nm
        reference = self.referenceLevelDoubleSpinBox.value() * ureg.dBm
        sel_sensitivity = self.sensitivityComboBox.currentText()
        sensitivity = self.sens_dict[sel_sensitivity]
        trace = 'A'
        
        self.current_params = dict(start = start, stop = stop, resolution = resolution, reference = reference,
                                    sensitivity = sensitivity, trace = trace)

        #Check if the parameters have changed since the last sweep
        if self.start != start or self.stop != stop:
            updated_params['start'] = start
            self.start = start
            updated_params['stop'] = stop
            self.stop = stop
        if self.resolution != resolution:
            updated_params['resolution'] = resolution
            self.resolution = resolution
        if self.reference != reference:
            updated_params['reference'] = reference
            self.reference = reference
        if self.sensitivity != sensitivity:
            updated_params['sensitivity'] = sensitivity
            self.sensitivity = sensitivity
        if self.trace != trace:
            updated_params['trace'] = trace
            self.trace = trace

        #Create a worker for the spectrum acquisition
        if offline_mode:
            worker_get_spectrum = Worker(self.get_fake_spectrum, updated_params)
        else:
            worker_get_spectrum = Worker(self.get_spectrum, updated_params)
        worker_get_spectrum.signals.result.connect(self.plotSpectrum)
        self.threadpool.start(worker_get_spectrum)


    @Slot()
    def plotSpectrum(self, spectrum: dict):
        """Plots the spectrum and adds it to the list of spectra"""
        #Get the previous color from the list or start with the first one
        if len(self.model.spectraList) != 0:
            previous_color = self.model.spectraList[-1]['color']
            color = QtGui.QColor(colors[(colors.index(previous_color)+1) % len(colors)]) 
        else:
            color = QtGui.QColor(colors[0])
        #Get the color that's the next from the last one in the list
        pen = pg.mkPen(color= QtGui.QColor(color))
        wavelength = spectrum['wavelength'].to(ureg.nm).magnitude
        power = spectrum['power'].to(ureg.dBm).magnitude
        plot = self.plotWidget.plot(wavelength, power, 
                                    name = f'Trace {len(self.model.spectraList)}', pen = pen)
        #Add the trace to the list of traces
        trace_info = {
            'plot': plot,
            'color': color,
            'name': f'Trace {len(self.model.spectraList)}',
            'pen': pen,
            'visible': True,
            'plot': plot,
            **spectrum,
            **self.current_params
        }
        self.model.spectraList.append(trace_info)
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
    def saveChecked(self):
        """Save all the checked traces to a file, asking for name and format"""
        #Get the checked traces
        checked_traces = [trace for trace in self.model.spectraList if trace['visible']]
        if len(checked_traces) == 0:
            QtWidgets.QMessageBox.warning(self, "No traces selected", "Please select at least one trace to save")
            return
        #Ask the user for additional notes
        notes, ok = QtWidgets.QInputDialog.getText(self, "Additional notes", "Please enter additional notes for the file (optional)")  
        if not ok:
            return
        #Add the date and time  to the notes
        date = f' - Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

        #Ask the user for the name and format of the file
        file_type, ok = QtWidgets.QInputDialog.getItem(self, "File format", "Please select the file format\nSelect Pickle for processing in python",
                                                       ["Pickle", "CSV"], 0, False)
        if not ok:
            return
        if file_type == "Pickle":
            #Ask the user for the name of the file
            name, ok = QtWidgets.QFileDialog.getSaveFileName(self, "Save file", "", "Pickle Files (*.pkl);;All Files (*)")
            if not ok:
                return
            if not name.endswith('.pkl'):
                name += '.pkl'
            #Save the traces to the file
            with open(name, 'wb') as f:
                traces_to_save = []
                keys_to_exclude = ['plot', 'pen', 'visible', 'color']
                for trace in checked_traces:
                    for key in keys_to_exclude:
                        trace_to_save = {k: v for k, v in trace.items() if k not in keys_to_exclude}
                        traces_to_save.append(trace_to_save)
                dict_to_save = {
                    'traces': traces_to_save,
                    'notes': notes,
                    'date': date
                }
                pickle.dump(dict_to_save, f)

        elif file_type == "CSV":
            #Ask the user for the name of the file
            #Get the name and format from the user
            name, ok = QtWidgets.QFileDialog.getSaveFileName(self, "Save file", "", "CSV Files (*.csv);;All Files (*)")
            if not ok:
                return
            if not name.endswith('.csv'):
                name += '.csv'
            #Save the traces to the file
            with open(name, 'w', newline='') as f:
                writer = csv.writer(f)

                writer.writerow(['Notes: ' + notes + date])
                
                # Write header
                header = []
                for trace in checked_traces:
                    header.extend([f'Wavelength {trace["name"]} (nm)', f'Power {trace["name"]} (dBm) - Resolution {trace["resolution"].magnitude} (nm)'])
                writer.writerow(header)
                
                # Prepare data
                data = []
                for trace in checked_traces:
                    data.append(trace['wavelength'].to(ureg.nm).magnitude)
                    data.append(trace['power'].to(ureg.dBm).magnitude)
                
                # Write data rows
                for row in zip(*data):
                    writer.writerow(row)

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

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion' )

    window = MainWindow()
    window.show()
    app.exec()