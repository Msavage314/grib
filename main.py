import grib
from grib.util.colors import Color

# Create board
board = grib.Board(10, 10)

# Add a colored region
danger_zone = board.add_region("danger", color=Color.BG_RED)
danger_zone.add_rectangle((2, 2), (5, 5))

# Add another region
safe_zone = board.add_region("safe", color=Color.BG_GREEN)
safe_zone.add_position((0, 0))
safe_zone.add_position((0, 1))

# Check if position is in region
if (3, 3) in danger_zone:
    print("Position is in danger zone!")

# Display with colors
print(board)  # Shows colored regions

# Display without colors
print(board)
