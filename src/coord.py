class Coord(tuple):
    """
    Coordinate class.
    """

    @property
    def x(self):
        return self[0]
        
    @property
    def y(self):
        return self[1]

    def __add__(self, other):
        if (type(other) == Coord):
            return Coord(self.x + other.x, self.y + other.y)
        if (type(other) == int or type(other) == float):
            return Coord(self.x + other, self.y + other)
        raise TypeError()
        
    def __sub__(self, other):
        if (type(other) == Coord):
            return Coord(self.x - other.x, self.y - other.y)
        if (type(other) == int or type(other) == float):
            return Coord(self.x - other, self.y - other)
        raise TypeError()
        
    def __mul__(self, other):
        if (type(other) == Coord):
            return Coord(self.x * other.x, self.y * other.y)
        if (type(other) == int or type(other) == float):
            return Coord(self.x * other, self.y * other)
        raise TypeError()
        
    def __truediv__(self, other):
        if (type(other) == Coord):
            return Coord(self.x / other.x, self.y / other.y)
        if (type(other) == int or type(other) == float):
            return Coord(self.x / other, self.y / other)
        raise TypeError()
        
    def __floordiv__(self, other):
        if (type(other) == Coord):
            return Coord(self.x // other.x, self.y // other.y)
        if (type(other) == int or type(other) == float):
            return Coord(self.x // other, self.y // other)
        raise TypeError()