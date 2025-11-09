import copy
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from grib.core.types import Coord, Direction, OverwriteBehavior
from grib.core.shape import Shape

if TYPE_CHECKING:
    from .board import Board


class ObjectRegistry:
    _object_types = []

    @classmethod
    def register(cls, obj_class):
        cls._object_types.append(obj_class)


class BoardObject(ABC):
    def __init__(
        self,
        shape: Shape | str = ".",
        moveable: bool = True,
        replaceable: bool = False,
        pushable: bool = False,
    ):
        if isinstance(shape, str):
            self.shape = Shape([[shape]])
        else:
            self.shape = shape
        # Physical properties
        self.movable: bool = moveable
        self.replaceable: bool = replaceable
        self.pushable: bool = pushable

        self.board: Board | None = None
        self.position: Coord = (-1, -1)

    def __init_subclass__(cls, **kwargs):
        """Automatically register subclasses when they're defined"""
        super().__init_subclass__(**kwargs)
        # Register the class if it has a default display_char

        ObjectRegistry.register(cls)

    def __str__(self) -> str:
        text = ""
        for y, row in enumerate(self.shape.pattern):
            for x, obj in enumerate(row):
                text += obj + " "
            text += "\n"
        return text

    def __repr__(self) -> str:
        return f"BoardObject at position {self.position}, display char = {self.display_char}"

    def get_occupied_positions(self) -> list[Coord]:
        return self.shape.get_occupied_positions(self.position)

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
        """Check if this object can move to a new position (absolute)"""
        new_positions = self.shape.get_occupied_positions(new_pos)
        if not self.board or not self.movable:
            return False
        if not all(self.board.in_bounds(pos) for pos in new_positions):
            return False

        for pos in new_positions:
            target = self.board[pos]
            if target is self:
                continue

            if not isinstance(target, Empty):
                match existing:
                    case OverwriteBehavior.FAIL:
                        return False
                    case OverwriteBehavior.SWAP:
                        if not target.movable:
                            return False
                    case OverwriteBehavior.REPLACE:
                        if not target.replaceable:
                            return False

        return True
        # implement later
        # if target_obj.pushable and abs(dx) <= 1 and abs(dy) <= 1:
        #    return target_obj._can_push_chain(Direction((dx, dy)))
        #

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
        new_positions = [i + direction for i in self.get_occupied_positions()]
        free = []
        for pos in new_positions:
            if (self.board[pos] is self) or (self.board[pos].is_empty()):
                free.append(True)
            else:
                free.append(False)
        if all(free):
            # First, clear all old positions
            for pos in self.get_occupied_positions():
                old_pos = self.position + pos

                self.board[old_pos] = Empty()

            # Update the position
            self.position += direction

            # Then, set all new positions
            for pos in self.get_occupied_positions():
                new_pos = self.position + pos
                self.board[new_pos] = self

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
    def x(self) -> int:
        return self.position[0]

    @property
    def y(self) -> int:
        return self.position[0]

    @property
    def display_char(self) -> str:
        return self.shape.pattern[0][0]

    @property
    def is_single_celled(self) -> bool:
        return self.shape.width == 1 and self.shape.height == 1


class Empty(BoardObject):
    """Represents an empty cell"""

    def __init__(self):
        super().__init__(shape="[]", moveable=False, replaceable=True)

    def get_valid_moves(self) -> list[Coord]:
        return []


class Wall(BoardObject):
    """Represents a wall or obstacle"""

    def __init__(self):
        super().__init__(shape="#", moveable=False)

    def get_valid_moves(self) -> list[Coord]:
        return []


class Symbol(BoardObject):
    """Represents a random symbol"""

    def __init__(self, char: str = "C"):
        super().__init__(shape=char, moveable=False)

    def get_valid_moves(self) -> list[Coord]:
        return []


class Player(BoardObject):
    """Represents a player that can move in all directions"""

    def __init__(self, display_char: str = "@", name: str = "Player"):
        super().__init__(shape=display_char, moveable=True)
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
        super().__init__(shape=display_char, moveable=True, pushable=True)
        self.name = name

    def get_valid_moves(self) -> list[Coord]:
        return [
            self.position + Direction.UP,
            self.position + Direction.DOWN,
            self.position + Direction.LEFT,
            self.position + Direction.RIGHT,
        ]


class BigBox(BoardObject):
    def __init__(self):
        shape = [
            ["+", "-", "+"],
            ["|", " ", "|"],
            ["+", "-", "+"],
        ]
        super().__init__(shape=Shape(shape))

    def get_valid_moves(self) -> list[Coord]:
        return [
            self.position + Direction.UP,
            self.position + Direction.DOWN,
            self.position + Direction.LEFT,
            self.position + Direction.RIGHT,
        ]
