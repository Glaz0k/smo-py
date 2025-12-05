from collections import deque
from copy import copy, deepcopy
from dataclasses import dataclass
from enum import Enum
from random import Random
from typing import Callable, Deque, List, Optional, Tuple

from simulator import Request, SpecialEvent, SpecialEventType, Simulator, DeviceStatistics


@dataclass(frozen=True)
class SimulatorConfig:
    buffer_capacity: int
    target_amount_of_requests: int
    source_periods: Tuple[int]
    device_coefficients: Tuple[int]

class SimulatorLaw(Enum):
    STOCHASTIC = 0
    DETERMINISTIC = 1

class MySimulator(Simulator):
    def __init__(self, config: SimulatorConfig, law: SimulatorLaw):
        super().__init__(
            len(config.source_periods), 
            len(config.device_coefficients), 
            config.target_amount_of_requests
        )
        self._law: SimulatorLaw = law
        self._rangom_gen: Random = Random()

        self._source_periods: List[int] = list(config.source_periods)
        self._device_coefficients: List[int] = list(config.device_coefficients)
        self._buffer_capacity: int = config.buffer_capacity
        self._buffer: List[Optional[Request]] = [None for _ in range(config.buffer_capacity)]

        self.__init_simulator()

    def __init_simulator(self) -> None:
        for i, period in enumerate(self._source_periods):
            self._add_special_event(SpecialEvent(
                period,
                SpecialEventType.GENERATE_NEW_REQUEST,
                i
            ))

    def reset(self, target_amount_of_requests: Optional[int] = None) -> None:
        super().reset(target_amount_of_requests)
        self._buffer = [None for _ in range(self._buffer_capacity)]
        self.__init_simulator()

    @property
    def buffer_capacity(self) -> int:
        return self._buffer_capacity

    @property
    def buffer(self) -> List[Optional[Request]]:
        return deepcopy(self._buffer)
    
    def add_new_device(self, avg_processing_time: int) -> None:
        self._device_coefficients.append(avg_processing_time)
        self._devices.append(DeviceStatistics())
    
    def _put_in_buffer(self, request: Request) -> Optional[Request]:
        for i, buffer_val in enumerate(self._buffer):
            if (buffer_val is None):
                self._buffer[i] = request
                return None
        
        return request

    def _take_from_buffer(self) -> Optional[Request]:
        buffer_requests = [(i, req) for (i, req) in enumerate(self._buffer) if req is not None]
        if (len(buffer_requests) == 0):
            return None
        
        buffer_requests.sort(key=lambda req: (req[1].source_id, req[1].generation_time))
        (i, res) = buffer_requests[0]
        self._buffer[i] = None
        return res
    
    def _pick_device(self) -> Optional[int]:
        for i, device in enumerate(self._devices):
            if (device.current_request is None):
                return i
            
        return None
    
    def _device_processing_time(self, device_id: int, request: Request) -> int:
        match (self._law):
            case SimulatorLaw.DETERMINISTIC:
                return self._device_coefficients[device_id]
            case SimulatorLaw.STOCHASTIC:
                return int(self._device_coefficients[device_id] * self._rangom_gen.expovariate(1.0))
            
        assert False, "Not all SimulatorLaw cases are managed"

    def _source_period(self, source_id: int) -> int:
        return self._source_periods[source_id]