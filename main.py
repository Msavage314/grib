import grib

b = grib.Board(5, 5)
print(b.find_neighbors((2, 2)))
