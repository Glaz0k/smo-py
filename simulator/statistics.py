from dataclasses import dataclass, field
import sys
from typing import Final, Optional

from simulator.components import Request

MAX_TIME: Final[int] = sys.maxsize

def calc_variance(time_sqr: int, avg_time: float, amount: int) -> float:
    return time_sqr / amount - avg_time ** 2

@dataclass
class ElementStatistics:
    time: int = 0
    time_sqr: int = 0

    def avg_time(self, generated: int) -> float:
        return self.time / generated
    
    def variance_time(self, generated: int) -> float:
        return self.time_sqr / generated - self.avg_time(generated) ** 2
    
    def add_time(self, time: int) -> None:
        self.time += time
        self.time_sqr += time ** 2

@dataclass
class SourceStatistics:
    generated: int = 0
    rejected: int = 0
    next_request_time: int = 0
    buffer_stats: ElementStatistics = field(default_factory=ElementStatistics)
    device_stats: ElementStatistics = field(default_factory=ElementStatistics)

    def avg_buffer_time(self) -> float:
        return self.buffer_stats.avg_time(self.generated)
    
    def avg_device_time(self) -> float:
        return self.device_stats.avg_time(self.generated)

    def variance_buffer_time(self) -> float: 
        return self.buffer_stats.variance_time(self.generated)
    
    def variance_device_time(self) -> float: 
        return self.device_stats.variance_time(self.generated)

@dataclass
class DeviceStatistics:
    next_request_time: int = MAX_TIME
    time_in_usage: int = 0
    current_request: Optional[Request] = None
