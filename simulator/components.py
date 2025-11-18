from dataclasses import dataclass
from enum import Enum
from typing import Self


@dataclass
class Request:
    source_id: int
    number: int
    generation_time: int

class SpecialEventType(Enum):
    END_OF_SIMULATION = 0
    GENERATE_NEW_REQUEST = 1
    DEVICE_RELEASE = 2

@dataclass
class SpecialEvent:
    planned_time: int
    event_type: SpecialEventType
    id: int

    def __lt__(self, other: Self):
        if (self.planned_time != other.planned_time):
            return self.planned_time < other.planned_time
        if (self.event_type != other.event_type):
            return self.event_type < other.event_type
        return self.id < other.id
    
