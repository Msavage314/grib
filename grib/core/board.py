"""Python library for working with grids.

Contains functions and classes for working with grid problems,
like those commonly found in the BIO, advent of code, Project Euler...
"""

import math

from .board_object import BoardObject, ObjectRegistry, Empty, Box
from .types import Coord


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
        self.board[pos[0]][pos[1]] = value

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

    def get_row(self, y: int) -> list[BoardObject]:
        """Get all objects in a row"""
        if 0 <= y <= self.height:
            return self.board[y]
        raise IndexError(f"Row {y} out of bounds")

    def get_column(self, x: int) -> list[BoardObject]:
        """Get all objects in a column"""
        if 0 <= x <= self.width:
            return [self.board[row][x] for row in range(self.height)]
        raise IndexError(f"Column {x} out of bounds")

    def get_area(self, start_pos: Coord, end_pos: Coord) -> list[list[BoardObject]]:
        """Return a 2d array of objects in the specified rectangular area"""
        x1, y1 = start_pos
        x2, y2 = end_pos
        area = []
        for y in range(min(y1, y2), max(y1, y2) + 1):
            row = []
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if self.in_bounds((x, y)):
                    row.append(self[x, y])
                else:
                    row.append(Empty())
            area.append(row)
        return area

    def set_area(self, start_pos: Coord, objects: list[list[BoardObject]]):
        """Set a rectangular area with a 2D array of objects"""
        x, y = start_pos
        for row_offset, row in enumerate(objects):
            for col_offset, obj in enumerate(row):
                pos = (x + col_offset, y + row_offset)
                if self.in_bounds(pos):
                    self[pos] = obj

    def clear_area(self, start_pos: Coord, end_pos: Coord):
        x1, y1 = start_pos
        x2, y2 = end_pos
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if self.in_bounds((x, y)):
                    self[x, y] = Empty()

    def save_state(self) -> list[list[str]]:
        return [[obj.display_char for obj in row] for row in self.board]

    def load_state(self, text: str):
        self.board = []
        lines = text.split("\n")
        for l_index, line in enumerate(lines):
            self.board.append([])
            for c_index, char in enumerate(line):
                obj = Board.get_object_for_char(char)
                to_place: BoardObject = obj()
                to_place.board = self
                self.board[-1].append(to_place)

    def get_line(
        self, start_pos: Coord, end_pos: Coord, block_types: list[type] = []
    ) -> list[BoardObject]:
        """get all objects in a straight line between two points"""
        objects = []
        x1, y1 = start_pos
        x2, y2 = end_pos
        # differences
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        err = dx - dy
        x, y = x1, y1

        while True:
            if self.in_bounds((x, y)):
                obj = self[x, y]
                objects.append(obj)
                if any(isinstance(obj, block_type) for block_type in block_types):
                    break
            else:
                break

            if x == x2 and y == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        return objects

    def place_object(self, obj: BoardObject, pos: Coord):
        """Place object at given anchor position"""
        positions = obj.shape.get_occupied_positions(pos)
        if not all(self.in_bounds(pos) for pos in positions):
            return
        for pos in positions:
            self[pos + obj.position] = Box(
                display_char=obj.shape.pattern[pos[0]][pos[1]]
            )

    @staticmethod
    def manhattan_distance(pos1: Coord, pos2: Coord) -> int:
        """Calculate manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    @staticmethod
    def euclidean_distance(pos1: Coord, pos2: Coord) -> float:
        return math.sqrt(abs(pos1[0] - pos2[0]) ** 2 + abs(pos1[1] - pos2[1]) ** 2)

    @property
    def objects(self, include_empty=False) -> list[BoardObject]:
        objects = []
        for row in self.board:
            for cell in row:
                if not isinstance(cell, Empty):
                    objects.append(cell)
        return objects

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
