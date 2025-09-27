import grib
from grib.util import UP, DOWN, LEFT, RIGHT, Coord
from os import system
import time

b = grib.Board(5, 5)
with open("grid.txt") as file:
    b.import_board_from_text(file.read())
player = b.find_objects(grib.Player)[0][0]

with open("instructions.txt") as file:
    instructions = file.read()

instructions = list(instructions)
for inst in instructions:
    print(inst)
    match inst:
        case ">":
            player.move(RIGHT)
        case "<":
            player.move(LEFT)
        case "V":
            player.move(DOWN)
        case "^":
            player.move(UP)
    print(b)
    print(player.position)
