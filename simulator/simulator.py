from abc import ABC, abstractmethod
from copy import deepcopy
import heapq
from typing import List, Optional

from simulator.components import Request, SpecialEvent, SpecialEventType
from simulator.statistics import MAX_TIME, DeviceStatistics, SourceStatistics


class Simulator(ABC):

    def __init__(self, sources_amount: int, devices_amount: int, target_amount_of_requests: int):
        super().__init__()
        self._sources: List[SourceStatistics] = [SourceStatistics() for _ in range(sources_amount)]
        self._devices: List[DeviceStatistics] = [DeviceStatistics() for _ in range(devices_amount)]
        self.__special_events: List[SpecialEvent] = []
        self.__current_amount_of_request = 0
        self.__target_amount_of_requests = target_amount_of_requests
        self.__rejected_amount = 0
        self.__current_simulation_time = 0
                
    def step(self) -> SpecialEvent:
        if (self.is_completed()):
            return SpecialEvent(event_type=SpecialEventType.END_OF_SIMULATION)
        return self.__step()

    def run_to_completion(self) -> None:
        while (not self.is_completed()):
            self.__step()

    def reset(self) -> None:
        self._sources = [SourceStatistics() for _ in range(len(self._sources))]
        self._devices = [DeviceStatistics() for _ in range(len(self._devices))]
        self.__special_events = []
        self.__current_amount_of_request = 0
        self.__rejected_amount = 0
        self.__current_simulation_time = 0

    def reset(self, target_amount_of_requests: int):
        self.reset()
        self.__target_amount_of_requests = target_amount_of_requests

    def is_completed(self) -> bool:
        return self.__special_events

    @property
    def current_amount_of_requests(self) -> int:
        return self.__current_amount_of_request
    
    @property
    def target_amount_of_requests(self) -> int:
        return self.__target_amount_of_requests
    
    @property
    def rejected_amount(self) -> int:
        return self.__rejected_amount
    
    @property   
    def current_simulation_time(self) -> int:
        return self.__current_simulation_time
    
    @property
    def source_statistics(self) -> List[SourceStatistics]:
        return deepcopy(self._sources)

    @property
    def device_statistics(self) -> List[DeviceStatistics]:
        return deepcopy(self._devices)

    @abstractmethod
    def _put_in_buffer(self, request: Request) -> Optional[Request]:
        pass

    @abstractmethod
    def _take_from_buffer(self) -> Optional[Request]:
        pass

    @abstractmethod
    def _pick_device(self) -> Optional[int]:
        pass

    @abstractmethod
    def _device_processing_time(self, device_id: int, request: Request) -> int:
        pass

    @abstractmethod
    def _source_period(self, source_id: int) -> int:
        pass

    def _add_special_event(self, event: SpecialEvent) -> None:
        match event.event_type:
            case SpecialEventType.GENERATE_NEW_REQUEST:
                self._sources[event.event_id].next_request_time = event.planned_time
            case SpecialEventType.DEVICE_RELEASE:
                self._devices[event.event_id].next_request_time = event.planned_time
        
        heapq.heappush(self.__special_events, event)

    def __step(self) -> SpecialEvent:
        current_event = heapq.heappop(self.__special_events)
        self.__current_simulation_time = current_event.planned_time
        match current_event.event_type:
            case SpecialEventType.GENERATE_NEW_REQUEST:
                self.__handle_new_request(current_event.event_id)
            case SpecialEventType.DEVICE_RELEASE:
                self.__handle_device_release(current_event.event_id)
        return current_event

    def __handle_new_request(self, source_id: int) -> None:
        source = self._sources[source_id]
        request = Request(source_id, source.generated, self.__current_simulation_time)
        source.generated += 1
        self.__current_amount_of_request += 1
        if (not self.__occupy_next_device(request)):
            rejected = self._put_in_buffer(request)
            if (rejected is not None):
                self.__handle_buffer_overflow(rejected)

        if (self.__current_amount_of_request >= self.__target_amount_of_requests):
            self.__special_events = [event for event in self.__special_events if event.event_type != SpecialEventType.GENERATE_NEW_REQUEST]
            for source in self._sources:
                source.next_request_time = MAX_TIME
        else:
            self._add_special_event(SpecialEvent(
                self.__current_simulation_time + self._source_period(source_id),
                SpecialEventType.GENERATE_NEW_REQUEST,
                source_id
            ))

    def __handle_buffer_overflow(self, request: Request) -> None:
        time = self.__current_simulation_time - request.generation_time
        source = self._sources[request.source_id]
        source.buffer_stats.add_time(time)
        source.rejected += 1
        self.__rejected_amount += 1

    def __handle_device_release(self, device_id: int) -> None:
        device = self._devices[device_id]
        device.current_request = None
        request = self._take_from_buffer()
        if (not request):
            device.next_request_time = MAX_TIME
            return
        
        time = self.__current_simulation_time - request.generation_time
        self._sources[request.source_id].buffer_stats.add_time(time)
        self.__occupy_next_device(request)

    def __occupy_next_device(self, request: Request) -> bool:
        device_id = self._pick_device()
        if (not device_id):
            return False
        
        device = self._devices[device_id]
        processing_time = self._device_processing_time(device_id, request)
        self._sources[request.source_id].device_stats.add_time(processing_time)
        device.current_request = request
        device.time_in_usage += processing_time
        self._add_special_event(SpecialEvent(
            self.__current_simulation_time + processing_time,
            SpecialEventType.DEVICE_RELEASE,
            device_id
        ))
        return True