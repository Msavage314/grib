from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .grid import Grid, Coord


@dataclass
class GameObject:
    """Base class for objects that can live on the grid"""

    display_char: str = "?"
    _grid: Grid | None = None
    _row: int = -1
    _col: int = -1

    movable: bool = True
    solid: bool = False

    @property
    def position(self) -> Coord:
        """Get current position on grid"""
        return (self._row, self._col)

    @position.setter
    def position(self, value: Coord):
        self._row, self._col = value

    @property
    def grid(self) -> Grid | None:
        """Get the grid this object is on"""
        return self._grid

    def on_place(self, grid: Grid, row: int, col: int):
        """Called when placed on grid"""
        self._grid = grid
        self._row = row
        self._col = col

    def on_remove(self, grid: Grid, row: int, col: int):
        """Called when removed from grid"""
        self._grid = None
        self._row = -1
        self._col = -1

    def move(self, offset: Coord) -> bool:
        """
        Attempt to move by offset. Returns success.

        """
        if not self._grid:
            return False
        pos = self._row + offset[0], self._col + offset[1]
        return self._grid.move_object(self, pos)

    def move_to(self, position: Coord) -> bool:
        """
        Move to absolute position
        """
        if self._grid is None or not self.movable:
            return False

        return self._grid.move_object(self, position)

    def move_up(self) -> bool:
        return self.move((-1, 0))

    def move_down(self) -> bool:
        return self.move((1, 0))

    def move_left(self) -> bool:
        return self.move((0, -1))

    def move_right(self) -> bool:
        return self.move((0, 1))

    def update(self, grid: Grid):
        """Override for per-frame game logic"""
        pass

    def __str__(self):
        return self.display_char

    def can_move_to(self, pos: Coord) -> bool:
        """
        Override this to implement custom collision logic.

        Example:
            def can_move_to(self, row, col):
                target = self.grid[row, col]
                return target is None or isinstance(target, Pickup)
        """
        row, col = pos
        if not self._grid or not self._grid.in_bounds((row, col)):
            return False

        target = self._grid[row, col]

        # Empty cell
        if target is None:
            return True

        # Blocked by solid object
        if hasattr(target, "solid"):
            if target.solid:  # type: ignore
                return False

        return True
