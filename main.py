"""This is a demo of gribs capabilities so far"""

import grib
from grib.core.grid import Grid

# Grid creation
g = Grid(width=10, height=10)
# assignment
g[0, 0] = "*"
# nice printing
print(g)

# slicing (returns array)
print(g[0:5, 0:8])
