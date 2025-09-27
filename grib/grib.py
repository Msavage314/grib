"""Python library for working with grids.

Contains functions and classes for working with grid problems,
like those commonly found in the BIO, advent of code, Project Euler...
"""

from abc import ABC, abstractmethod
from enum import Enum
import copy

type Coord = tuple[int, int] | Direction


class OverwriteBehavior(Enum):
    SWAP = 1
    REPLACE = 2
    FAIL = 4
    PUSH = 8


class Direction(Enum):
    """Standard movement directions"""

    NORTH = (0, -1)
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


class ObjectRegistry:
    _object_types = []

    @classmethod
    def register(cls, obj_class):
        cls._object_types.append(obj_class)


class BoardObject(ABC):
    def __init__(
        self,
        display_char: str = "?",
        moveable: bool = True,
        replaceable: bool = False,
        pushable: bool = False,
    ):
        self.display_char = display_char
        # Physical properties
        self.movable: bool = moveable
        self.replaceable: bool = replaceable
        self.pushable: bool = pushable

        self.board: Board | None = None

    def __init_subclass__(cls, **kwargs):
        """Automatically register subclasses when they're defined"""
        super().__init_subclass__(**kwargs)
        # Register the class if it has a default display_char

        ObjectRegistry.register(cls)

    def __str__(self) -> str:
        return self.display_char

    def __repr__(self) -> str:
        return f"BoardObject at position {self.position}, display char = {self.display_char}"

    @abstractmethod
    def get_valid_moves(self) -> list[Coord]:
        pass

    def is_empty(self):
        if isinstance(self, Empty):
            return True
        else:
            return False

    def _can_push_chain(self, direction: Direction, chain_length: int = 0) -> bool:
        """Check if a chain of pushable objects can be pushed in the given direction"""
        if chain_length > 50:
            return False
        if not self.position or not self.board:
            return False

        target_pos = self.position + direction
        if not self.board.in_bounds(target_pos):
            return False

        target_obj = self.board[target_pos]

        if isinstance(target_obj, Empty):
            return True
        # continue chain
        if target_obj.pushable:
            return target_obj._can_push_chain(direction, chain_length + 1)

        # chain can push through it
        if target_obj.replaceable:
            return True

        return False

    def _push_chain(self, direction: Direction):
        """Actually push the chain of objects"""
        if not self.position or not self.board:
            return False

        target_pos = self.position + direction
        target_obj = self.board[target_pos]
        if target_obj.pushable:
            if not target_obj._push_chain(direction):
                return False
        # refresh in case box in front has moved
        target_obj = self.board[target_pos]
        if isinstance(target_obj, Empty) or target_obj.replaceable:
            old_pos = self.position
            self.board[target_pos] = self
            self.board[old_pos] = Empty()
            return True
        return False

    def can_move_to(
        self, new_pos: Coord, existing: OverwriteBehavior = OverwriteBehavior.FAIL
    ) -> bool:
        if not self.board or not self.movable:
            return False

        if not self.board.in_bounds(new_pos):
            return False

        if not self.position:
            return False

        dx = new_pos[0] - self.position[0]
        dy = new_pos[1] - self.position[1]

        target_obj = self.board[new_pos]

        if isinstance(target_obj, Empty):
            return True

        # Handle pushable objects
        if target_obj.pushable and abs(dx) <= 1 and abs(dy) <= 1:
            return target_obj._can_push_chain(Direction((dx, dy)))

        match existing:
            case OverwriteBehavior.FAIL:
                return False
            case OverwriteBehavior.SWAP:
                return target_obj.movable
            case OverwriteBehavior.REPLACE:
                return target_obj.replaceable

        return False

    def move_to(
        self, new_pos: Coord, existing: OverwriteBehavior = OverwriteBehavior.FAIL
    ) -> None:
        """attempt to move a square to a new location"""

        if self.board is not None and self.position is not None:
            if self.can_move_to(new_pos, existing):
                match existing:
                    case OverwriteBehavior.REPLACE:
                        self.board[new_pos] = self
                        self.board[self.position] = Empty()
                    case OverwriteBehavior.SWAP:
                        self.board[new_pos], self.board[self.position] = (
                            self.board[self.position],
                            self.board[new_pos],
                        )
                    case OverwriteBehavior.FAIL:
                        self.board[self.position] = Empty()
                        self.board[new_pos] = self
                    case OverwriteBehavior.PUSH:
                        raise ValueError(
                            "Cannot push when moving to. Use relative move"
                        )

    def move(
        self,
        new_pos: Coord,
        existing: OverwriteBehavior = OverwriteBehavior.FAIL,
    ) -> bool:
        """attempt to move a square to a new location (relative)"""
        if not self.board or not self.position:
            return False

        if not self.can_move_to(self.position + new_pos, existing):
            return False

        direction = Direction(new_pos)
        new_pos = self.position + new_pos
        target_obj = self.board[new_pos]
        # handle pushable objects
        if target_obj.pushable and direction:
            if target_obj._can_push_chain(direction):
                target_obj._push_chain(direction)
                # Now move to target pos
                old_pos = self.position
                self.board[new_pos] = self
                self.board[old_pos] = Empty()
                return True
        if isinstance(target_obj, Empty):
            old_pos = copy.deepcopy(self.position)
            self.board[new_pos] = self
            self.board[old_pos] = Empty()
            return True

        match existing:
            case OverwriteBehavior.REPLACE:
                if target_obj.replaceable:
                    old_pos = self.position
                    self.board[new_pos] = self
                    self.board[old_pos] = Empty()
                    return True
            case OverwriteBehavior.SWAP:
                if target_obj.movable:
                    # Swap positions
                    self.board[new_pos], self.board[self.position] = (
                        self.board[self.position],
                        self.board[new_pos],
                    )
                    # Update positions
                    return True

        return False

    @property
    def position(self) -> Coord:
        if self.board is None:
            return (-1, -1)
        else:
            for r_index, row in enumerate(self.board.board):
                for c_index, col in enumerate(row):
                    if col is self:
                        return (c_index, r_index)

        return (-1, 1)


class Empty(BoardObject):
    """Represents an empty cell"""

    def __init__(self):
        super().__init__(display_char=".", moveable=False, replaceable=True)

    def get_valid_moves(self) -> list[Coord]:
        return []


class Wall(BoardObject):
    """Represents a wall or obstacle"""

    def __init__(self):
        super().__init__(display_char="#", moveable=False)

    def get_valid_moves(self) -> list[Coord]:
        return []


class Player(BoardObject):
    """Represents a player that can move in all directions"""

    def __init__(self, display_char: str = "@", name: str = "Player"):
        super().__init__(display_char=display_char, moveable=True)
        self.name = name

    def get_valid_moves(self) -> list[Coord]:
        return [
            self.position + Direction.EAST,
            self.position + Direction.NORTH,
            self.position + Direction.SOUTH,
            self.position + Direction.WEST,
        ]


class Box(BoardObject):
    def __init__(self, display_char: str = "O", name: str = "Box"):
        super().__init__(display_char=display_char, moveable=True, pushable=True)
        self.name = name

    def get_valid_moves(self) -> list[Coord]:
        return [
            self.position + Direction.UP,
            self.position + Direction.DOWN,
            self.position + Direction.LEFT,
            self.position + Direction.RIGHT,
        ]


class Board:
    """
    Objects stores a list of known objects for the board.
    this is for functions like import, which need to know all possible token types
    """

    _object_types: list[type] = ObjectRegistry._object_types

    def __init__(self, width, height):
        self.board: list[list[BoardObject]] = [
            [Empty() for _ in range(width)] for _ in range(height)
        ]
        self.width = width
        self.height = height

    def __str__(self) -> str:
        return "\n".join(" ".join(i.display_char for i in j) for j in self.board)

    def __getitem__(self, pos: Coord) -> BoardObject:
        """When a tuple is passed, get the specific cell"""
        try:
            self.board[pos[1]]
        except IndexError:
            raise IndexError(
                f"Invalid row {pos[1]}. Value must be between 0 and {self.width}"
            )

        try:
            return self.board[pos[1]][pos[0]]
        except IndexError:
            raise IndexError(
                f"Invalid column {pos[0]}. Value must be between 0 and {self.height}"
            )

    def __setitem__(self, pos: Coord, value: BoardObject) -> None:
        try:
            self.board[pos[1]]
        except IndexError:
            raise IndexError(
                f"Invalid row {pos[1]}. Value must be between 0 and {self.width}"
            )
        try:
            self.board[pos[1]]
        except IndexError:
            raise IndexError(
                f"Invalid col {pos[0]}. Value must be between 0 and {self.height}"
            )
        self.board[pos[1]][pos[0]] = value

    @classmethod
    def get_object_for_char(cls, char):
        """Get the appropriate object class for a display character"""
        possible = []
        for obj in cls._object_types:
            if obj().display_char == char:
                possible.append(obj)

        if len(possible) > 1:  # more than 1 with same display char
            raise ValueError(
                f"Ambiguous display char '{char}'. Multiple objects share '{char}' as their display:\n -> {'\n -> '.join(i.__name__ for i in possible)}"
            )
        elif len(possible) < 1:
            raise ValueError(
                f"Unknown display char '{char}'. No objects found to use '{char}'"
            )
        else:
            return possible[0]

    def in_bounds(self, pos: Coord):
        x, y = pos[0], pos[1]
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False
        return True

    def place_object(self, obj: BoardObject, x: int, y: int) -> bool:
        try:
            self[x, y] = obj
            return True
        except IndexError:
            return False

    def find_objects(self, obj_type: type) -> list[tuple[BoardObject, Coord]]:
        results = []
        for obj in self.objects:
            # print(obj)
            if isinstance(obj, obj_type):
                results.append((obj, obj.position))
        return results

    def find_neighbors(self, pos: Coord, include_diagonals: bool = True):
        x, y = pos
        neighbors = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        if include_diagonals:
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((self.board[ny][nx], (nx, ny)))

        return neighbors

    def clear(self):
        """Clear the board"""
        for i in self.board:
            i.clear()

    def import_board_from_text(self, text: str):
        self.board = []
        lines = text.split("\n")
        for l_index, line in enumerate(lines):
            self.board.append([])
            for c_index, char in enumerate(line):
                obj = Board.get_object_for_char(char)
                to_place: BoardObject = obj()
                to_place.board = self
                self.board[-1].append(to_place)

    @property
    def objects(self, include_empty=False) -> list[BoardObject]:
        l = []
        for row in self.board:
            for cell in row:
                if not isinstance(cell, Empty):
                    l.append(cell)
        return l

    @property
    def width(self):
        return len(self.board[0])

    @width.setter
    def width(self, value, force=False):
        if value < self.width:
            if not force:
                print(
                    "Warning: shrinking board results in data loss and unknown results"
                )
                print("please pass force as an argument to continue")
            else:
                for row in self.board:
                    while len(row) != value:
                        row.pop()
        else:
            for row in self.board:
                row.extend(Empty() for i in range(value - self.width))

    @property
    def height(self):
        return len(self.board)

    @height.setter
    def height(self, value, force=False):
        if value < self.height:
            if not force:
                print(
                    "Warning: shrinking board results in data loss and unknown results"
                )
                print("please pass force as an argument to continue")
            else:
                while self.height != value:
                    self.board.pop()

        else:
            while self.height != value:
                self.board.append([Empty() for _ in range(self.width)])
