from enum import Enum

class Status(Enum):
    INACTIVE: int = 0
    ACTIVE: int = 1
    PAPER_TRADING: int = 2
    # TODO: GRADIANT_EXIT isn't implemented
    GRADIANT_EXIT: int = 3
    UNKNOWN_ERROR = 99


