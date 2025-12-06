from typing import TYPE_CHECKING
from .types import Coord
from grib.util.colors import Color

if TYPE_CHECKING:
    from .board import Board


class Region:
    """Represents a named, colored region on the board"""

    def __init__(
        self,
        name: str,
        positions: set[Coord] | None = None,
        color: Color = Color.BG_BLACK,
    ):
        self.name = name
        self.positions: set[Coord] = positions or set()
        self.color = color
        self.board: Board | None = None

    def __len__(self):
        return len(self.positions)

    def __contains__(self, pos: Coord):
        return pos in self.positions

    def add_position(self, pos: Coord):
        """Add a position to this region"""
        self.positions.add(pos)

    def add_positions(self, positions: list[Coord]):
        for pos in positions:
            self.positions.add(pos)

    def remove_position(self, pos: Coord):
        """Remove a position from this region"""
        self.positions.discard(pos)

    def contains(self, pos: Coord) -> bool:
        """Check if position is in this region"""
        return pos in self.positions

    def add_rectangle(self, start_pos: Coord, end_pos: Coord):
        """Add all positions in a rectangle to this region"""
        x1, y1 = start_pos
        x2, y2 = end_pos
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                print(self.positions)
                self.positions.add((x, y))

    def clear(self):
        """Remove all positions from this region"""
        self.positions.clear()
