# Yokogawa ANDO AQ6315A control
GUI Software for controlling Yokogawa ANDO optical spectrum analyzer via GPIB cable


https://github.com/user-attachments/assets/0df979c6-2ea4-454c-9687-215361f5ee7d

The program was developed so that it can easily be adapted to any OSA for spectrum acquisition. 
To adapt to any other OSA, just change the osa_driver.py file with the relevant functions of the OSA.

## Required components:
1. Drivers for GPIB to USB cable
2. Anaconda (Python distribution) 
3. Packages for Python:
    * Pyvisa (for communication with the device)
    * Numpy
    * PySide6 (for GUI)
    * Pint (for unit handling)
    * Pyqtgraph (for plotting in the GUI)
    * Xarray (for data management and storage)

Additionally, there is an analysis.py file that uses jupyter notebooks and matplotlib to plot the saved files.

## Usage
You set the start and stop wavelength, sensitivity, reference level, resolution, and points/nm for the sweep. You cannot change these values once you sweep and get a trace. This is to ensure that all the traces that are saved in the same file have the same configuration values. In order to change them, you can save all the current traces and then delete all of them, or restart the program.

The code includes an offline_mode parameter, which can be set to True to ignore the communication with the device to test the GUI. In addition, it has a save_every_sweep parameter, which can be set to True, to save all traces immediately after the sweep into a temp folder, to prevent missing a spectrum when closing the program without saving it.

A spectrum trace can be deleted by selecting a single trace(it would be highlighted in the list), and then clicking the delete button. It always asks for confirmation. The traces can be set as visible or invisible with the corresponding checkbox in the list. The names of the traces can be changed by double-clicking its name. The save button saves only the checked(visible) traces. It can be saved in csv format or NetCDF. NetCDF is the preferred format as it holds all the information of the configuration parameters and units and is easier to handle for data processing.
The analysis.py file shows an example of opening a file in NetCDF format and plotting it with matplotlib.






