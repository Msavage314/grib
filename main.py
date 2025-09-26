import grib
from grib.util import UP, DOWN, LEFT, RIGHT, Coord
from os import system
import time

b = grib.Board(5, 5)
b.import_board_from_text(open("grid.txt").read())
player = b.find_objects(grib.Player)[0][0]

system("cls")
print(b)
time.sleep(1)
player.move(UP)
system("cls")
print(b)
time.sleep(1)
player.move(UP, grib.OverwriteBehavior.PUSH)
print(b)
