from typing import Optional, Tuple
from tabulate import tabulate
from my_simulator import MySimulator
from simulator import Request, SpecialEvent, SpecialEventType, MAX_TIME

def print_simulation_state(sim: MySimulator) -> None:
    print("Sources calendar:")
    print_sources_calendar(sim)
    print("Devices calendar:")
    print_devices_calendar(sim)
    print("Buffer:")
    print_fake_buffer(sim)

def print_sources_calendar(sim: MySimulator) -> None:
    headers = ["i", "Next event", "Sign"]
    rows = []
    for i, source_stat in enumerate(sim.source_statistics):
        time, sign = get_time_and_sign(source_stat.next_request_time)
        rows.append([i, time, sign])

    print(tabulate(tabular_data=rows, headers=headers))

def print_devices_calendar(sim: MySimulator) -> None:
    headers = ["i", "Next event", "Sign", "Request"]
    rows = []
    for i, device_stat in enumerate(sim.device_statistics):
        time, sign = get_time_and_sign(device_stat.next_request_time)
        rows.append([i, time, sign, format_request(device_stat.current_request)])

    print(tabulate(tabular_data=rows, headers=headers))

def print_fake_buffer(sim: MySimulator) -> None:
    index_row = ["i:"]
    value_row = ["Values:"]

    for i, request in enumerate(sim.buffer):
        index_row.append(i)
        value = format_request(request)
        value_row.append(value)

    table = [value_row]
    print(tabulate(tabular_data=table, headers=index_row))
    
def print_event(event: SpecialEvent) -> None:
    print(f"Time: {event.planned_time}")
    match (event.event_type):
        case SpecialEventType.GENERATE_NEW_REQUEST:
            print(f"Source {event.event_id} made new request")
        case SpecialEventType.DEVICE_RELEASE:
            print(f"Device {event.event_id} is released")
        case SpecialEventType.END_OF_SIMULATION:
            print("Simulation ended")

def print_report(sim: MySimulator) -> None:
    print("General report:")
    print_general_report(sim)
    print("Source report:")
    print_source_report(sim)
    print("Device report:")
    print_device_report(sim)

def print_general_report(sim: MySimulator) -> None:
    headers = [
        "Total\nsimulation\ntime", 
        "Requests\nrecieved", 
        "Requests\nprocessed", 
        "Requests\nrejected", 
        "Rejection\nprobability"
    ]
    recieved = sim.current_amount_of_requests
    rejected = sim.rejected_amount
    table = [[
        sim.current_simulation_time, 
        recieved, 
        recieved - rejected, 
        rejected, 
        rejected / recieved
    ]]
    print(tabulate(tabular_data=table, headers=headers))

def print_source_report(sim: MySimulator) -> None:
    headers = [
        "i", 
        "Request\namount", 
        "Rejection\nprobability", 
        "Time\nfull", 
        "Time\nbuffer", 
        "Time\nprocessing", 
        "Variance\nbuffer", 
        "Variance\nprocessing"
    ]
    rows = []
    for i, source_stat in enumerate(sim.source_statistics):
        buffer_time = source_stat.avg_buffer_time()
        device_time = source_stat.avg_device_time()
        rows.append([
            i, 
            source_stat.generated, 
            source_stat.rejected / source_stat.generated,
            buffer_time + device_time,
            buffer_time,
            device_time,
            source_stat.variance_buffer_time(),
            source_stat.variance_device_time()
        ])

    print(tabulate(tabular_data=rows, headers=headers))

def print_device_report(sim: MySimulator) -> None:
    headers = ["i", "Usage\ncoefficient"]
    rows = []
    for i, device_stat in enumerate(sim.device_statistics):
        rows.append([i, device_stat.time_in_usage / sim.current_simulation_time])
    
    print(tabulate(tabular_data=rows, headers=headers))

def get_time_and_sign(request_time: int) -> Tuple[Optional[int], int]:
    if (request_time == MAX_TIME):
        return (None, 1)
    else:
        return (request_time, 0)

def format_request(request: Optional[Request]) -> str:
    if (request is None):
        return ""
    return f"{request.source_id}-{request.number}"