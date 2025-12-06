"""
Shapes are compound objects that can be placed on the board
They consist of mutiple cells.
All board objects must define a shape
"""

from .types import Coord


class Shape:
    """
    Represents visual shape of an multi-cellular
    object to be placed on the grid
    """

    def __init__(self, pattern: list[list[str]]) -> None:
        """
        @pattern: 2d grid of display characters
        """
        if not pattern or not pattern[0]:
            raise ValueError("Pattern cannot be empty")

        self.pattern = pattern
        self.height = len(pattern)
        self.width = len(pattern[0])

        # Validate rectangular shape
        if not all(len(row) == self.width for row in pattern):
            raise ValueError("Pattern must be rectangular")

    def get_occupied_positions(self, anchor: Coord) -> list[Coord]:
        positions = []
        for dy in range(self.height):
            for dx in range(self.width):
                positions.append((anchor[0] + dx, anchor[1] + dy))
        return positions

    def get_char_at_offset(self, dx: int, dy: int) -> str:
        """Get the display character at a specific location"""
        if 0 <= dy < self.height and 0 <= dx < self.width:
            return self.pattern[dy][dx]
        raise IndexError(f"Offset ({dx},{dy}) is out of bounds!")
