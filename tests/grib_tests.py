import unittest
import sys
import os

# Add the parent directory to the path to import grib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grib.grib import (
    Board,
    BoardObject,
    Player,
    Wall,
    Empty,
    Direction,
    OverwriteBehavior,
)


class TestDirection(unittest.TestCase):
    """Test Direction enum and arithmetic"""

    def test_direction_values(self):
        """Test that directions have correct coordinate offsets"""
        self.assertEqual(Direction.NORTH.value, (0, -1))
        self.assertEqual(Direction.SOUTH.value, (0, 1))
        self.assertEqual(Direction.EAST.value, (1, 0))
        self.assertEqual(Direction.WEST.value, (-1, 0))

    def test_direction_addition(self):
        """Test adding directions to positions"""
        pos = (5, 5)
        self.assertEqual(pos + Direction.NORTH, (5, 4))
        self.assertEqual(pos + Direction.SOUTH, (5, 6))
        self.assertEqual(pos + Direction.EAST, (6, 5))
        self.assertEqual(pos + Direction.WEST, (4, 5))

    def test_direction_reverse_addition(self):
        """Test that direction + position works"""
        pos = (3, 3)
        self.assertEqual(Direction.NORTHEAST + pos, (4, 2))
        self.assertEqual(Direction.SOUTHWEST + pos, (2, 4))


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
