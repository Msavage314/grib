import grib
from grib.util import UP, DOWN, LEFT, RIGHT, Coord
from os import system
import time

b = grib.Board(5, 5)
with open("grid.txt") as file:
    b.load_state(file.read())
print(b)
player = b.find_objects(grib.Player)[0][0]
