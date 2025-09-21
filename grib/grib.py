"""Python library for working with grid problems"""

from abc import ABC, abstractmethod
from enum import Enum


type Coord = tuple[int, int]

def register()


class OverwriteBehavior(Enum):
    SWAP = 0
    REPLACE = 1
    FAIL = 2


class Direction(Enum):
    """Standard movement directions"""

    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)
    NORTHEAST = (1, -1)
    NORTHWEST = (-1, -1)
    SOUTHEAST = (1, 1)
    SOUTHWEST = (-1, 1)

    def __add__(self, other):
        """Add direction to a position tuple"""
        if isinstance(other, tuple) and len(other) == 2:
            dx, dy = self.value
            return (other[0] + dx, other[1] + dy)
        return NotImplemented

    def __radd__(self, other):
        """Support tuple + direction"""
        return self.__add__(other)


class BoardObject(ABC):
    def __init__(
        self, display_char: str = "?", moveable: bool = True, replaceable: bool = False
    ):
        self.display_char = display_char
        self.movable = moveable
        self.position: Coord | None = None
        self.board: Board | None = None
        self.replaceable: bool = replaceable

    @abstractmethod
    def get_valid_moves(self) -> list[Coord]:
        pass

    def is_empty(self):
        if self is Empty:
            return True
        else:
            return False

    def can_move_to(
        self, new_pos, existing: OverwriteBehavior = OverwriteBehavior.FAIL
    ) -> bool:
        if not self.board or not self.movable:
            return False

        if not self.board.in_bounds(new_pos):
            return False
        if self.position is not None:
            if isinstance(self.board[new_pos], Empty):
                # swap cells
                return True
            else:
                match existing:
                    case OverwriteBehavior.FAIL:
                        return False
                    case OverwriteBehavior.SWAP:
                        if self.board[new_pos].movable:
                            return True
                    case OverwriteBehavior.REPLACE:
                        if self.board[new_pos].replaceable:
                            return True
        return False

    def move(
        self, new_pos: Coord, existing: OverwriteBehavior = OverwriteBehavior.FAIL
    ):
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

    def __str__(self) -> str:
        return self.display_char


class Empty(BoardObject):
    """Represents an empty cell"""

    def __init__(self):
        super().__init__(display_char=".", moveable=False)

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


class Board:
    """
    Objects stores a list of known objects for the board. 
    this is for functions like import, which need to know all possible token types
    """
    objects = []
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board: list[list[BoardObject]] = [
            [Empty() for _ in range(width)] for _ in range(height)
        ]
        self.objects: list[BoardObject] = []

    def __str__(self) -> str:
        return "\n".join(" ".join(i.display_char for i in j) for j in self.board)

    def __getitem__(self, pos: Coord) -> BoardObject:
        """When a tuple is passed, get the specific cell"""
        try:
            self.board[pos[0]]
        except IndexError:
            raise IndexError(
                f"Invalid row {pos[0]}. Value must be between 0 and {self.width}"
            )

        try:
            return self.board[pos[0]][pos[1]]
        except IndexError:
            raise IndexError(
                f"Invalid column {pos[1]}. Value must be between 0 and {self.height}"
            )

    def __setitem__(self, pos: Coord, value: BoardObject) -> None:
        try:
            self.board[pos[0]]
        except IndexError:
            raise IndexError(
                f"Invalid row {pos[0]}. Value must be between 0 and {self.width}"
            )
        try:
            self.board[pos[1]]
        except IndexError:
            raise IndexError(
                f"Invalid col {pos[1]}. Value must be between 0 and {self.height}"
            )
        self.board[pos[0]][pos[1]] = value

    def in_bounds(self, pos: Coord):
        x, y = pos[0], pos[1]
        if x < 0 or x >= self.width:
            return False
        if y < 0 or x >= self.height:
            return False

    def place_object(self, obj: BoardObject, x: int, y: int) -> bool:
        try:
            self[x, y] = obj
            return True
        except IndexError:
            return False

    def find_objects(self, obj_type: type) -> list[tuple[BoardObject, Coord]]:
        results = []
        for obj in self.objects:
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
    
    def import_board_from_text(self, text: str):
        chars = list(text)
        for i in chars:


