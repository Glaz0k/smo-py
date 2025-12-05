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
        self._storage: List[Deque[Request]] = [deque() for _ in range(len(config.source_periods))]
        
        self._buffer_capacity: int = config.buffer_capacity
        self._buffer_size: int = 0
        self._current_packet: int = 0
        self._next_device_index: int = 0

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
        for subbuffer in self._storage:
            subbuffer.clear()
        self._next_device_index = 0
        self.__init_simulator()

    @property
    def buffer_capacity(self) -> int:
        return self._buffer_capacity

    @property
    def fake_buffer(self) -> List[Request]:
        res: List[Request] = []
        for subbuffer in self._storage:
            for req in subbuffer:
                res.append(copy(req))
        res.sort(key=lambda req: (req.generation_time, req.source_id))
        return res
    
    @property
    def real_buffer(self) -> List[Deque[Request]]:
        return deepcopy(self._storage)
    
    def add_new_device(self, avg_processing_time: int) -> None:
        self._device_coefficients.append(avg_processing_time)
        self._devices.append(DeviceStatistics())

    @property
    def current_packet(self) -> int:
        return self._current_packet
    
    def _put_in_buffer(self, request: Request) -> Optional[Request]:
        rejected: Optional[Request] = None
        
        if (self._buffer_size == self._buffer_capacity):
            non_empty = next(filter(lambda b: b, self._storage))
            rejected = non_empty.pop()
            self._buffer_size -= 1
        
        self._storage[request.source_id].append(request)
        self._buffer_size += 1
        return rejected

    def _take_from_buffer(self) -> Optional[Request]:
        if (self._buffer_size == 0):
            return None
        
        subbuffer = self._storage[self._current_packet]
        if (not subbuffer):
            i, non_empty = next(filter(lambda b: b[1], enumerate(self._storage)))
            self._current_packet = i
            subbuffer = non_empty
        
        res = subbuffer.pop()
        self._buffer_size -= 1
        return res
    
    def _pick_device(self) -> Optional[int]:
        res: Optional[int] = None
        check_not_occupied: Callable[[Tuple[int, DeviceStatistics]], bool] = lambda d: d[1].current_request is None
        pick_range = list(enumerate(self._devices))[self._next_device_index:]
        i, candidate = next(filter(check_not_occupied, pick_range), (None, None))
        if (candidate is not None):
            res = i
        if (res is None):
            pick_range = list(enumerate(self._devices))[:self._next_device_index]
            i, candidate = next(filter(check_not_occupied, pick_range), (None, None))
        if (candidate is not None):
            res = i
        if (res is not None):
            i += 1
            self._next_device_index = 0 if (i == len(self._devices)) else i
        return res
    
    def _device_processing_time(self, device_id: int, request: Request) -> int:
        match (self._law):
            case SimulatorLaw.DETERMINISTIC:
                return self._device_coefficients[device_id]
            case SimulatorLaw.STOCHASTIC:
                return int(self._device_coefficients[device_id] * self._rangom_gen.expovariate(1.0))
            
        assert False, "Not all SimulatorLaw cases are managed"

    def _source_period(self, source_id: int) -> int:
        return self._source_periods[source_id]