
"""

@author: Javier

2024
"""

import pyvisa
import numpy as np
import time
from pint import UnitRegistry
ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)
Q_ = ureg.Quantity

rm = pyvisa.ResourceManager()
# print(rm.list_resources())



ANDO = rm.open_resource('GPIB0::3::INSTR')


ANDO.timeout = 40000 #ms

def get_trace(updated_params):
    """updated_params is a dictonary with the parameters to be updated, if a parameter is not in the dictonary, it will be ignored"""
    if 'trace' in updated_params:
        trace = updated_params['trace']
    else:
        trace = 'A'  # Default value if 'trace' is not in the dictionary
    #Trace has to be A,B or C 
    assert trace in ('A','B','C')
    active_trace(trace)

    if 'start' in updated_params and 'stop' in updated_params:
        set_range(updated_params['start'].ito(ureg.nm).magnitude,
                  updated_params['stop'].ito(ureg.nm).magnitude)

    if 'ref_level' in updated_params:
        set_ref(updated_params['ref_level'].ito(ureg.dBm).magnitude)

    if 'resolution' in updated_params:
        set_resolution(updated_params['resolution'].ito(ureg.nm).magnitude)

    if 'sensitivity' in updated_params:
        sensitivity_mode(updated_params['sensitivity'])
    
    if 'trace_points' in updated_params:
        set_trace_points(updated_params['trace_points'])

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
    
    #Get the power data
    power_read = ANDO.query('LDAT'+trace).strip().split(',')
    power = power_read.split(',')[1:]
    power = np.asarray(power,'f').T
    points_read_power = power_read[0].split(' ')[-1]
    assert int(points_read_power) == len(power)
    spectrum_data = {
        'wavelength': Q_(wl,  ureg.nm),
        'power': Q_(power , ureg.dBm),
    }
    return spectrum_data

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
    assert resolution>=0.01 and resolution<=2.0
    ANDO.query(f'RESLN{resolution:.2f}')

def active_trace(trace):
    assert trace in ('A','B','C')
    ANDO.query(f'ACTV{trace}')


def sensitivity_mode(sensitivity):
    assert sensitivity in ('SNHD', 'SNAT', 'SHI1', 'SHI2', 'SHI3')
    ANDO.query(sensitivity)

def set_trace_points(trace_points):
    assert trace_points>=11 and trace_points<=20001
    ANDO.query(f'SMPL{trace_points}')


