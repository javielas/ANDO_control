import osa_driver
from pint import UnitRegistry

ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)
Q_ = ureg.Quantity


while(True):
    command = input("Enter command: ")
    if command == "exit":
        break
    elif command == "start":
        start = input("Enter start: ")
        osa_driver.set_start(float(start)))
    elif command == "stop":
        stop = input("Enter stop: ")
        osa_driver.set_stop(float(stop))
    elif command == "ref":  
        ref = input("Enter ref: ")
        osa_driver.set_ref(float(ref))
    elif command == "resolution":
        resolution = input("Enter resolution: ")
        osa_driver.set_resolution(float(resolution))
    elif command == "trace_points":
        trace_points = input("Enter trace_points: ")
        osa_driver.set_trace_points(float(trace_points))
    elif command == "sensitivity":
        sensitivity = input("Enter sensitivity: ")
        osa_driver.sensitivity_mode((sensitivity))
    elif command == "trace":
        result = osa_driver.get_trace(dict())
        print(result)