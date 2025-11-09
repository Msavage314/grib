import grib
from grib.core.board_object import BoardObject, Empty
from grib.core.types import Coord, Direction
from grib.util.colors import Color


class Queen(BoardObject):
    """Represents queen"""

    def __init__(self, display_char: str = "👑"):
        super().__init__(shape=display_char, moveable=True)

    def get_valid_moves(self) -> list[Coord | Direction]:
        return super().get_valid_moves()


class QueensGame:
    def __init__(self, board: grib.Board):
        self.queens: list[Queen] = []
        self.board: grib.Board = board

    def is_valid_placement(self, pos: Coord) -> bool:
        if not isinstance(self.board[pos], Empty):
            return False

        region_id = self.board.get_region_at(pos)
        if region_id == None:
            raise ValueError("All cells must have a region")

        for queen in self.queens:
            qx, qy = queen.position

            if qy == pos[1]:
                return False

            if qx == pos[0]:
                return False

            if self.board.get_region_at(queen.position) == region_id:
                return False
        return True

    def place_queen(self, pos: Coord) -> bool:
        """Attempt to place a queen at the given position"""
        if self.is_valid_placement(pos):
            queen = Queen()
            queen.board = self.board
            self.board[pos] = queen
            self.queens.append(queen)
            return True
        return False

    def remove_queen(self, pos: Coord) -> bool:
        """Remove a queen from the given position"""
        obj = self.board[pos]
        if isinstance(obj, Queen):
            self.queens.remove(obj)
            self.board[pos] = Empty()
            return True
        return False

    def is_solved(self) -> bool:
        """Check if the puzzle is solved"""
        # Check we have the right number of queens
        if len(self.queens) != len(self.board.regions):
            return False

        # Check each region has exactly one queen
        for region_id in self.board.regions.keys():
            region_queens = sum(
                1
                for queen in self.queens
                if self.board.get_region(queen.position) == region_id
            )
            if region_queens != 1:
                return False

        # Check each row has at most one queen
        row_counts = {}
        for queen in self.queens:
            y = queen.position[1]
            row_counts[y] = row_counts.get(y, 0) + 1
            if row_counts[y] > 1:
                return False

        # Check each column has at most one queen
        col_counts = {}
        for queen in self.queens:
            x = queen.position[0]
            col_counts[x] = col_counts.get(x, 0) + 1
            if col_counts[x] > 1:
                return False

        return True

    def get_valid_positions(self) -> list[tuple[int, int]]:
        """Get all valid positions where a queen can be placed"""
        valid = []
        for y in range(self.board.height):
            for x in range(self.board.width):
                pos = (x, y)
                if self.is_valid_placement(pos):
                    valid.append(pos)
        return valid

    def solve(self) -> bool:
        """Attempt to solve the puzzle using backtracking"""
        if self.is_solved():
            return True

        # Try to place a queen in each region that doesn't have one yet
        for region_id in self.board.regions.keys():
            # Check if this region already has a queen
            has_queen = any(
                self.board.get_region(queen.position) == region_id
                for queen in self.queens
            )

            if not has_queen:
                # Try each position in this region
                for pos in self.board.get_region(region_id).positions:
                    if self.is_valid_placement(pos):
                        self.place_queen(pos)

                        if self.solve():
                            return True

                        # Backtrack
                        self.remove_queen(pos)

                # If no valid position found in this region, backtrack
                return False

        return False


if __name__ == "__main__":
    board = grib.Board(8, 8)
    purple = board.add_region("purple", color=Color.BG_MAGENTA)
    purple.add_positions(
        [
            (0, 0),
            (1, 0),
            (2, 0),
            (3, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
            (0, 6),
            (0, 7),
            (1, 7),
            (2, 7),
            (3, 7),
        ]
    )
    blue = board.add_region("blue", color=Color.BG_BLUE)
    blue.add_positions(
        [(1, 1), (2, 1), (1, 2), (2, 2), (1, 3), (2, 3), (1, 4), (1, 5), (2, 5), (1, 6)]
    )

    cyan = board.add_region("cyan", color=Color.BG_CYAN)
    cyan.add_positions(
        [
            (4, 0),
            (5, 0),
            (6, 0),
            (7, 0),
            (7, 6),
            (7, 1),
            (7, 2),
            (7, 3),
            (7, 4),
            (7, 5),
            (4, 7),
            (5, 7),
            (6, 7),
            (7, 7),
        ]
    )
    green = board.add_region("green", color=Color.BG_GREEN)
    green.add_positions([(3, 1), (4, 1), (3, 2), (4, 2)])
    yellow = board.add_region("yellow", color=Color.BG_YELLOW)
    yellow.add_positions([(6, 3), (6, 4), (6, 5), (5, 6), (6, 6)])
    red = board.add_region("red", color=Color.BG_RED)
    red.add_positions([(3, 3), (4, 3), (5, 3), (2, 4), (3, 4), (5, 4), (3, 5)])
    gray = board.add_region("gray", color=Color.BG_WHITE)
    gray.add_positions([(6, 1), (5, 1), (6, 2), (5, 2)])
    d_gray = board.add_region("d_gray", color=Color.DARK_GRAY)
    d_gray.add_positions([(5, 5), (4, 4), (4, 5), (4, 6), (3, 6), (2, 6)])

    print(board)

    game = QueensGame(board)

    if game.solve():
        print()
        print(board)
