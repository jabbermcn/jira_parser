from enum import StrEnum

__all__ = ["CalendarType"]


class CalendarType(StrEnum):
    SICK_DAY = "SICK_DAY"
    SICK = "SICK"
    VOCATION = "VOCATION"
    OVERTIME = "OVERTIME"
    WEEKEND = "WEEKEND"
