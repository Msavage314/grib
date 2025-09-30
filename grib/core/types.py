from enum import Enum

type Coord = tuple[int, int] | Direction


class OverwriteBehavior(Enum):
    SWAP = 1
    REPLACE = 2
    FAIL = 4
    PUSH = 8


class Direction(Enum):
    """Standard movement directions"""

    NORTH = (0, -11)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NORTHEAST = (1, -1)
    NORTHWEST = (-1, -1)
    SOUTHEAST = (1, 1)
    SOUTHWEST = (-1, 1)

    def __add__(self, other):
        """Add direction to a position tuple"""
        if isinstance(other, (tuple, Direction)) and len(other) == 2:
            dx, dy = self.value
            return (other[0] + dx, other[1] + dy)
        return NotImplemented

    def __radd__(self, other):
        """Support tuple + direction"""
        return self.__add__(other)

    def __getitem__(self, index):
        return self.value[index]

    def __len__(self):
        return len(self.value)
