
"""

@author: Javier

2024
"""

import pyvisa
import numpy as np
import time
import pint
ureg = pint.UnitRegistry()


rm = pyvisa.ResourceManager()
# print(rm.list_resources())



ANDO = rm.open_resource('GPIB0::3::INSTR')


ANDO.timeout = 40000 #ms

def get_trace(trace, start, stop, ref_level, resolution, sensitivity):
    #Trace has to be A,B or C
    # remove the leading and the trailing characters, split values, remove the first value showing number of values in a dataset
    assert trace in ('A','B','C')
    active_trace(trace)
    set_range(start, stop)
    set_ref(ref_level)
    set_resolution(resolution)
    sensitivity_mode(sensitivity)
    #Perform a sweep
    ANDO.query('SGL')
    #Ensure that the sweep is finished
    sweep_status = ANDO.query('SWEEP?')
    while sweep_status != '0':
        time.sleep(1)
        sweep_status = ANDO.query('SWEEP?')
    #Get the wavelength data
    wl_read = ANDO.query('WDAT'+trace).strip().split(',')
    wl = wl_read[1:]
    # list of strings -> numpy array (vector) of floats
    wl = np.asarray(wl,'f').T
    points_read_wl = wl_read[0].split(' ')[-1]
    assert int(points_read_wl) == len(wl)
    unit_wl = ureg.nm
    


    #Get the power data
    power_read = ANDO.query('LDAT'+trace).strip().split(',')
    power = power_read.split(',')[1:]
    power = np.asarray(power,'f').T
    points_read_power = power_read[0].split(' ')[-1]
    assert int(points_read_power) == len(power)
    unit_read_power = power_read[0].split(' ')[0]
    assert unit_read_power in ('DBM', 'LNW') #Only absolute values can be received
    if unit_read_power == 'DBM':
        unit_power = ureg.dBm
    else:
        unit_power = ureg.W
    return wl, power, unit_wl ,unit_power

def set_range(start, stop):
    assert start>=600 and start<=1750
    assert stop>=600 and stop<=1750
    assert stop>start
    ANDO.query(f'STAWL{start:.2f}')
    ANDO.query(f'STPWL{stop:.2f}')

def set_ref(ref_level):
    assert ref_level>=-90 and ref_level<=20
    ANDO.query(f'REFL{ref_level:.1f}')

def set_resolution(resolution):
    assert resolution>=0.05 and resolution<=10.0
    ANDO.query(f'RESLN{resolution:.2f}')

def active_trace(trace):
    assert trace in ('A','B','C')
    ANDO.query(f'ACTV{trace}')


def sensitivity_mode(sensitivity):
    assert sensitivity in ('SNHD', 'SNAT', 'SHI1', 'SHI2', 'SHI3')
    ANDO.query(sensitivity)


