"""
Contains all error codes
0: UNKNOWN_ERROR
100-199: Profile errors
200-299: Indicator errors
300-399: Plugin errors
400-499: Database errors
"""

from enum import Enum

class ErrorCode(Enum):
    UNKNOWN_ERROR: int = 0

    INVALID_STATUS: int = 100
