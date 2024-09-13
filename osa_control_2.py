import osa_driver

while(True):
    command = input("Enter command: ")
    if command == "exit":
        break
    elif command == "start":
        start = input("Enter start: ")
        osa_driver.set_start(start)
    elif command == "stop":
        stop = input("Enter stop: ")
        osa_driver.set_stop(stop)
    elif command == "ref":
        ref = input("Enter ref: ")
        osa_driver.set_ref(ref)
    elif command == "resolution":
        resolution = input("Enter resolution: ")
        osa_driver.set_resolution(resolution)
    elif command == "trace_points":
        trace_points = input("Enter trace_points: ")
        osa_driver.set_trace_points(trace_points)
    elif command == "sensitivity":
        sensitivity = input("Enter sensitivity: ")
        osa_driver.sensitivity_mode(sensitivity)