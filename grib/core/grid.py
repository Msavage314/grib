from typing import Callable, Generator
from .gameobject import GameObject
from collections import deque
from typing import Callable
import heapq
import math

type Coord = tuple[int, int]


def is_rectangular(matrix: list[list]) -> bool:
    for i in matrix:
        if len(i) != len(matrix[0]):
            return False
    return True


class Grid[T]:
    """
    Represents a grid that can hold any type of value.
    Simple mode: Grid[str] can hold characters or numbers
    Complex mode: Grid[GameObject] can hold interactive objects
    """

    def __init__(self, width: int, height: int, default: T | str = "."):
        self._grid: list[list[T | str]] = [
            [default for _ in range(width)] for __ in range(height)
        ]
        self.default = default
        self.width = width
        self.height = height
        self.dimensions = (width, height)

        self._track_objects = False
        self._objects: list[GameObject] = []

        if type(T) is not str:
            self.enable_object_tracking()

    def __str__(self):
        return "\n".join(" ".join(str(i) for i in j) for j in self._grid)

    def __getitem__(
        self, position: tuple[int, int] | tuple[slice, slice]
    ) -> Grid | T | None:
        """
        Traditional 2d array access: grid[row,col]
        slicing can be used to extract subgrids
        """
        # extract row and column
        row, col = position

        if isinstance(row, int) and isinstance(col, int):
            self.check_bounds((row, col))
            return self._grid[row][col]

        elif isinstance(row, slice) or isinstance(col, slice):
            return self._get_slice(row, col)

        return self._grid[row][col]

    def __setitem__(self, position: tuple[int | slice, int | slice], value: T | Grid):
        """
        Traditional 2d array access: grid[row,col]

        ### More advanced use
        You can also assign slices, subgrids, or fill values

        Examples:
         - direct assigment: ```grid[0,0] = "#" ```
         - Region from subgrid: ```grid[1:3,2:5] = subgrid```
         - Region with value: ```grid[1:3,2:5] = "X"```
        """
        row, col = position
        if isinstance(row, int) and isinstance(col, int):
            self.check_bounds((row, col))
            old_value = self[row, col]
            if isinstance(old_value, GameObject):
                if self._track_objects and hasattr(old_value, "on_remove"):
                    old_value.on_remove(self, row, col)
                    if old_value in self._objects:
                        self._objects.remove(old_value)
            if isinstance(value, Grid):
                raise TypeError("Cannot assign a Grid to a single cell")
            if isinstance(value, GameObject):
                value.position = position
                value._grid = self
            self._grid[row][col] = value
            return
        if isinstance(row, slice) or isinstance(col, slice):
            self._set_slice(row, col, value)
            return
        raise TypeError(f"Invalid index types: row={type(row)}, col={type(col)}")

    def move_object(self, obj: T, position: Coord) -> bool:
        """
        Move an object from its current position to a new one.
        Returns True if successful.
        """
        new_row, new_col = position
        if not self._track_objects:
            raise RuntimeError(
                "Object tracking not enabled. Call enable_object_tracking()"
            )

        if isinstance(obj, GameObject):
            if not hasattr(obj, "position"):
                raise TypeError("Object must have position attribute")

            old_row, old_col = obj.position

            # Check bounds
            if not self.in_bounds((new_row, new_col)):
                return False

            # Check if target is empty or has collision logic
            target = self._grid[new_row][new_col]
            if target is not None and target is not obj:
                # Allow custom collision handling
                if hasattr(obj, "can_move_to"):
                    if not obj.can_move_to((new_row, new_col)):
                        return False
                else:
                    return False  # Blocked by default

            # Perform move
            self._grid[old_row][old_col] = self.default
            self._grid[new_row][new_col] = obj

            # Update object position
            if hasattr(obj, "on_place"):
                obj.on_place(self, new_row, new_col)

            return True
        return False

    def find_objects(self, obj_type: type | str) -> list[tuple[T, Coord]]:
        """
        Find all objects of a specific type
        If they are not grid objects, you can search by string
        also returns their coordinates
        """
        results = []
        for row in range(self.height):
            for col in range(self.width):
                obj = self._grid[row][col]
                if isinstance(obj_type, type):
                    if isinstance(obj, obj_type):
                        results.append((obj, (row, col)))
                else:
                    if obj == obj_type:
                        results.append((obj, (row, col)))
        return results

    def get_objects(self) -> list[T]:
        """Get all tracked objects"""
        objects = []
        for row in self._grid:
            for cell in row:
                if cell is not None:
                    objects.append(cell)
        return objects

    def enable_object_tracking(self):
        """Enable features for game objects"""
        self._track_objects = True

    def line(self, p1: Coord, p2: Coord) -> Generator[Coord]:
        """yield list of coordinates between the two points"""
        # only works for horizontal/vertical lines for now
        drow = p2[0] - p1[0]
        dcol = p2[1] - p1[1]
        if drow == 0:  # Horizontal line
            step = 1 if dcol > 0 else -1
            for i in range(0, dcol + step, step):
                yield (p1[0], p1[1] + i)
        elif dcol == 0:  # Vertical line
            step = 1 if drow > 0 else -1
            for i in range(0, drow + step, step):
                yield (p1[0] + i, p1[1])

    def update_objects(self):
        """Call update() on all objects that have it"""
        if not self._track_objects:
            return

        # Copy list to allow objects to modify _objects during update
        for obj in self._objects.copy():
            if hasattr(obj, "update"):
                obj.update(self)

    def row(self, index):
        return self._grid[index]

    def col(self, index):
        return [self._grid[i][index] for i in range(self.width)]

    def at(self, x, y):
        """
        return the cell at the given x,y
        In comparison to direct access, this is x,y, not row, col

        It also is from bottom left being (0,0)

        Generally, you should normally use direct grid access with
        `grid[row,col]`
        """
        return self[self.height - y - 1, x]

    def get_cardinal_directions(self, pos):
        """Get valid cardinal directions (N, S, E, W) from a position."""
        row, col = pos
        directions = [
            (row, col - 1),  # North
            (row, col + 1),  # South
            (row + 1, col),  # East
            (row - 1, col),  # West
        ]

        return [d for d in directions if self.in_bounds(d)]

    def get_ordinal_directions(self, pos):
        """Get valid ordinal directions (NE, SE, SW, NW) from a position."""
        x, y = pos
        directions = [
            (x + 1, y - 1),  # Northeast
            (x + 1, y + 1),  # Southeast
            (x - 1, y + 1),  # Southwest
            (x - 1, y - 1),  # Northwest
        ]

        return [d for d in directions if self.in_bounds(d)]

    def get_all_directions(self, pos):
        """Get all valid directions (cardinal + ordinal) from a position.

        Args:
            pos: Tuple (x, y) representing current position
            grid: Grid object with is_valid(x, y) or width/height attributes

        Returns:
            List of valid (x, y) positions in all 8 directions
        """
        return self.get_cardinal_directions(pos) + self.get_ordinal_directions(pos)

    def in_bounds(self, pos):
        row, col = pos
        if not (0 <= row < self.height):
            return False
        if not (0 <= col < self.width):
            return False

        return True

    def check_bounds(self, *args):
        """
        args is any number of random coordinates

        Raises a value error (use inbounds for just a bool)
        """
        for i in args:
            row, col = i
            if not (0 <= row < self.height):
                raise IndexError(
                    f"Row index {row} out of bounds for grid with height {self.height} "
                    f"(valid range: 0 to {self.height - 1})"
                )
            if not (0 <= col < self.width):
                raise IndexError(
                    f"Column index {col} out of bounds for grid with width {self.width} "
                    f"(valid range: 0 to {self.width - 1})"
                )

    def _get_slice(self, row: int | slice, col: int | slice) -> Grid:
        """obtain a section of the grid"""
        # Convert indices to ranges
        if isinstance(row, slice):
            row_range = range(*row.indices(self.height))
        else:
            self.check_bounds(row, 0)
            row_range = range(row, row + 1)

        if isinstance(col, slice):
            col_range = range(*col.indices(self.width))
        else:
            self.check_bounds(0, col)
            col_range = range(col, col + 1)

        # Extract data
        data = []
        for r in row_range:
            row_data = []
            for c in col_range:
                row_data.append(self._grid[r][c])
            data.append(row_data)

        # Create new Grid
        new_grid = Grid(len(col_range), len(row_range))
        new_grid._grid = data
        return new_grid

    def _set_slice(self, row: int | slice, col: int | slice, value: T | Grid):
        """Sets a slice from either  Grid or a fill value"""
        # Convert to ranges
        if isinstance(row, slice):
            row_range = range(*row.indices(self.height))
        else:
            self.check_bounds(row, 0)
            row_range = range(row, row + 1)
        if isinstance(col, slice):
            col_range = range(*col.indices(self.width))
        else:
            self.check_bounds(0, col)
            col_range = range(col, col + 1)

        if isinstance(value, Grid):
            if value.height != len(row_range) or value.width != len(col_range):
                raise ValueError(
                    f"Shape mismatch: trying to assign {value.height}x{value.width} Grid "
                    f"to {len(row_range)}x{len(col_range)} region"
                )
            for i, r in enumerate(row_range):
                for j, c in enumerate(col_range):
                    self._grid[r][c] = value._grid[i][j]

        # Fill with single value
        else:
            for r in row_range:
                for c in col_range:
                    self._grid[r][c] = value

    def copy(self) -> "Grid":
        """Create a deep copy of the grid"""
        new_grid = Grid(self.width, self.height)
        new_grid._grid = [row.copy() for row in self._grid]
        return new_grid

    def rect(self, row: int, col: int, height: int, width: int) -> Grid | T | None:
        """Extract rectangular region as new Grid"""
        return self[row : row + height, col : col + width]

    def paste(self, other: Grid, at_row: int, at_col: int):
        """Paste another grid at specified position"""
        self[at_row : at_row + other.height, at_col : at_col + other.width] = other

    def pathfind(
        self,
        start: Coord,
        end: Coord,
        cost_fn: Callable[[Coord, Coord, Coord], float] | None = None,
        heuristic: Callable[[Coord, Coord], float] | None = None,
        walls: list[type] | None = None,
        walkable: list[type] | None = None,
        diagonal: bool = False,
    ) -> tuple[list[Coord], float | int] | None:
        """
        Pathfind from start to end using the A* algorithm
        It is highly customisable
        Args:
            start: Starting position
            goal: Goal position
            cost_fn: Function(current, neighbor, goal) -> cost. Can be used to set higher costs for certain actions
            heuristic: Function(pos, goal) -> estimated cost (default: Manhattan or Euclidean)
            walls: List of object types that block movement (e.g., [Wall, Box])
            walkable: List of object types that allow movement through (e.g., [Empty, Player])
            diagonal: Allow diagonal movement (default: False)
        """
        if walkable is not None:
            can_traverse = lambda obj: any(isinstance(obj, t) for t in walkable)
        elif walls is not None:
            can_traverse = lambda obj: not any(isinstance(obj, t) for t in walls)
        else:
            can_traverse = lambda obj: True

        if diagonal:
            directions = [
                (0, 1),
                (0, -1),
                (1, 0),
                (-1, 0),
                (1, 1),
                (1, -1),
                (-1, 1),
                (-1, -1),
            ]
        else:
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        def get_neighbors(pos):
            return [
                (pos[0] + dx, pos[1] + dy)
                for dx, dy in directions
                if self.in_bounds((pos[0] + dx, pos[1] + dy))
            ]

        if cost_fn is None:

            def cost_fn(current, neighbor, goal):
                return 1.0

        if heuristic is None:
            # Use Euclidean distance for diagonal, Manhattan for cardinal
            heuristic = self.distance if diagonal else self.manhattan_distance

        counter = 0
        priority_queue: list[tuple[float, int, tuple[int, int]]] = [(0, counter, start)]

        came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        g_score: dict[tuple[int, int], float] = {start: 0}

        while priority_queue:
            _, _, current = heapq.heappop(priority_queue)

            if current == end:
                # Reconstruct the path
                path = []
                total_cost = g_score[current]

                while current is not None:
                    path.append(current)
                    current = came_from[current]
                return (list(reversed(path)), total_cost)

            for neighbor in get_neighbors(current):
                if not can_traverse(self[neighbor]):
                    continue

                tentative_g = g_score[current] + cost_fn(current, neighbor, end)

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, end)
                    counter += 1
                    heapq.heappush(priority_queue, (f_score, counter, neighbor))
        return None

    @staticmethod
    def distance(p1: Coord, p2: Coord):
        """Return euclidean distance"""
        return math.dist(p1, p2)

    @staticmethod
    def manhattan_distance(p1: Coord, p2: Coord):
        return abs(p1[0] - p2[0]) + abs(p2[1] - p1[1])

    @staticmethod
    def from_matrix(matrix: list[list]) -> Grid:
        if not is_rectangular(matrix):
            raise ValueError(
                "How dare you pass me in a non rectangular matrix!! What do you suppose I do with this?"
            )
        height = len(matrix)
        width = len(matrix[0])
        g = Grid(width, height)
        g._grid = matrix

        return g

    @staticmethod
    def from_string(text: str, parser: Callable | None = None) -> Grid:
        """Parser can be a special object that returns a matrix based on the string"""
        if parser is not None:
            matrix = parser(text)
        else:
            lines = text.strip().split("\n")
            matrix = [list(line) for line in lines]
        if not matrix or not matrix[0]:
            raise ValueError("Cannot create grid from empty matrix")
        if not is_rectangular(matrix):
            raise ValueError(
                f"Matrix must be rectangular. Found rows with varying lengths: "
                f"{[len(row) for row in matrix]}"
            )

        height = len(matrix)
        width = len(matrix[0])
        g = Grid(width, height)
        g._grid = matrix

        return g
