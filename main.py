from print_simulator import print_event, print_report, print_simulation_state
from my_simulator import MySimulator, SimulatorConfig, SimulatorLaw


def main():
    config = SimulatorConfig(
        target_amount_of_requests = 1000,
        buffer_capacity = 10,
        source_periods = [30, 20, 10],
        device_coefficients = [20, 25, 30, 35, 40]
    )
    simulator = MySimulator(config, SimulatorLaw.STOCHASTIC)
    print("Interactive mode.")
    print_simulation_state(simulator)
    command: str
    while (not simulator.is_completed()):
        command = input()
        if (command == "q"):
            break

        event = simulator.step()
        print_event(event)
        print_simulation_state(simulator)

    simulator.run_to_completion()
    print_report(simulator)

if (__name__ == "__main__"):
    main()