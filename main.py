import grib
from grib.core.board_object import BigBox
from grib.core.types import OverwriteBehavior
from grib.util import UP, DOWN, LEFT, RIGHT
from grib.core.board import Coord
from os import system
import time
import keyboard

b = grib.Board(5, 5)
with open("grid.txt") as file:
    b.load_state(file.read())
print(b)
player = b.find_objects(grib.Player)[0][0]
system("cls")

b.place_object(BigBox(), (0, 0))


def on_key_press(event):
    key = event.name

    if key == "w":
        player.move(UP, OverwriteBehavior.PUSH)
    elif key == "a":
        player.move(LEFT, OverwriteBehavior.PUSH)
    elif key == "s":
        player.move(DOWN, OverwriteBehavior.PUSH)
    elif key == "d":
        player.move(RIGHT, OverwriteBehavior.PUSH)
    else:
        return  # Don't update display for other keys

    # Update display
    print("\033[32A\033[2K", end="")
    print(b)


# Set up event handler - suppress=True prevents key repeat from OS
keyboard.on_press(on_key_press, suppress=True)

# Keep the program running
keyboard.wait()
