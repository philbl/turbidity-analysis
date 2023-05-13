from dataclasses import dataclass
from datetime import date
from typing import Tuple


@dataclass
class SentinelAPIQueryInput:
    area: str
    date: Tuple[date]
    platformname: str
    processinglevel: str
    cloudcoverpercentage: Tuple[int]
