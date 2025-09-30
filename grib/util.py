"""Helpful things to always have imported for grib"""

from .core.types import Direction

UP = Direction.UP
DOWN = Direction.DOWN
LEFT = Direction.LEFT
RIGHT = Direction.RIGHT
NORTH = Direction.NORTH
SOUTH = Direction.SOUTH
RIGHT = Direction.RIGHT
WEST = Direction.WEST


def depreciated(func):
    def wrapper(*args, **kwargs):
        raise DeprecationWarning(
            f"This method {func.__name__} is depreciated for now. This feature has been removed until complex objects have been added"
        )

    return wrapper()
