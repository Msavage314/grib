from typing import Callable


def is_rectangular(matrix: list[list]) -> bool:
    for i in matrix:
        if len(i) != len(matrix[0]):
            return False
    return True


class Grid:
    def __init__(self, width: int, height: int):
        self._grid = [["." for _ in range(width)] for __ in range(height)]
        self.width = width
        self.height = height
        self.dimensions = (width, height)

    def __str__(self):
        return "\n".join(" ".join(str(i) for i in j) for j in self._grid)

    def __getitem__(
        self, position: tuple[int, int] | tuple[slice, slice]
    ) -> str | Grid:
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

    def __setitem__(self, position: tuple[int | slice, int | slice], value: str | Grid):
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
            if isinstance(value, Grid):
                raise TypeError(
                    "Cannot assign Grid to single cell. Use grid[r:r+h, c:c+w] = subgrid"
                )
            self.check_bounds((row, col))
            self._grid[row][col] = value
            return
        if isinstance(row, slice) or isinstance(col, slice):
            self._set_slice(row, col, value)
            return
        raise TypeError(f"Invalid index types: row={type(row)}, col={type(col)}")

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
            self._check_bounds(row, 0)
            row_range = range(row, row + 1)

        if isinstance(col, slice):
            col_range = range(*col.indices(self.width))
        else:
            self._check_bounds(0, col)
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

    def _set_slice(self, row: int | slice, col: int | slice, value: str) -> Grid:
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

    def rect(self, row: int, col: int, height: int, width: int) -> str | Grid:
        """Extract rectangular region as new Grid"""
        return self[row : row + height, col : col + width]

    def paste(self, other: Grid, at_row: int, at_col: int):
        """Paste another grid at specified position"""
        self[at_row : at_row + other.height, at_col : at_col + other.width] = other

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
