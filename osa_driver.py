
"""

@author: Javier

2024
"""

import pyvisa
import numpy as np

rm = pyvisa.ResourceManager()
# print(rm.list_resources())


# ANDO AQ6315A grey old: 'GPIB0::1::INSTR'
ANDO = rm.open_resource('GPIB0::3::INSTR')
# print(ANDO_6315A.query('*IDN?'))

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
    #Get the data
    wl = ANDO.query('WDAT'+trace).strip().split(',')[1:]
    intensity = ANDO.query('LDAT'+trace).strip().split(',')[1:]
    # list of strings -> numpy array (vector) of floats
    wl = np.asarray(wl,'f').T
    intensity = np.asarray(intensity,'f').T
    return wl, intensity

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


