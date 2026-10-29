from enum import StrEnum


class Status(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


def shipping(mode: str) -> int:
    match mode:
        case "standard":
            # Return the standard shipping price.
            return 7
        case "express":
            return 15
        case _:
            return 7


def dashboard(status: Status) -> str:
    match status:
        case Status.PENDING:
            return "Awaiting payment"
        case Status.PAID:
            return "Ready to ship"
    raise ValueError(status)


def shipping_cost(mode: str) -> int:
    return shipping(mode)
