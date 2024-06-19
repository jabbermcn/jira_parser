from enum import StrEnum

__all__ = [
    "IssuePriority",
    "IssueStatus",
    "IssueType"
]


class IssueType(StrEnum):
    BUG = "BUG"
    TASK = "TASK"


class IssuePriority(StrEnum):
    LOWEST = "LOWEST"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    HIGHEST = "HIGHEST"


class IssueStatus(StrEnum):
    CANCELED = "CANCELED"
    PAUSE = "PAUSE"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    READY_FOR_TEST = "READY_FOR_TEST"
    READY_FOR_DEV = "READY_FOR_DEV"
    RETURNED_FROM_CODE_REVIEW = "RETURNED_FROM_CODE_REVIEW"
    RETURNED_FROM_TESTING = "RETURNED_FROM_TESTING"
    CODE_REVIEW = "CODE_REVIEW"
    IN_PROGRESS = "IN_PROGRESS"
    IN_TESTING = "IN_TESTING"
    TESTED = "TESTED"
    TO_DO = "TO_DO"
    DONE = "DONE"
