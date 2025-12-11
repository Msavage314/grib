"""This is a demo of gribs capabilities so far"""

from grib.core.grid import Grid
from grib.core.gameobject import GameObject

# Grid creation
g = Grid(width=10, height=10)
# assignment
g[0, 0] = "*"
# nice printing
print(g)
print()
# slicing (returns array)
print(g[0:5, 0:8])
print()


# More complex objects
Board = Grid[GameObject](10, 10, default=GameObject("."))


class Player(GameObject):
    display_char = "#"


p = Player()
Board[5, 5] = p
print(Board)
print(p.position)
p.move_up()
print(p.position)
p.move_up()
print()
print(Board)

print("hi")
