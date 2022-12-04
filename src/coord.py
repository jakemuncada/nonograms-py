from __future__ import annotations

from typing import Union


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

    def move(self, amount: Union[Coord, tuple, int, float]) -> Coord:
        """
        Returns a new Coord that was moved by the specified amount.
        """
        if (type(amount) == Coord):
            return Coord((self.x + amount.x, self.y + amount.y))
        if (type(amount) == tuple):
            return Coord((self.x + amount[0], self.y + amount[1]))
        if (type(amount) == int or type(amount) == float):
            return Coord((self.x + amount, self.y + amount))
        raise TypeError()

    def move_ip(self, amount: Union[Coord, tuple, int, float]) -> None:
        """
        Move this coord in-place.
        """
        if (type(amount) == Coord):
            self.x += amount.x
            self.y += amount.y
        if (type(amount) == tuple):
            self.x += amount[0]
            self.y += amount[1]
        if (type(amount) == int or type(amount) == float):
            self.x += amount
            self.y += amount
        raise TypeError()

    def __add__(self, other):
        if (type(other) == Coord):
            return Coord((self.x + other.x, self.y + other.y))
        if (type(other) == tuple):
            return Coord((self.x + other[0], self.y + other[1]))
        if (type(other) == int or type(other) == float):
            return Coord((self.x + other, self.y + other))
        raise TypeError()
        
    def __sub__(self, other):
        if (type(other) == Coord):
            return Coord((self.x - other.x, self.y - other.y))
        if (type(other) == tuple):
            return Coord((self.x - other[0], self.y - other[1]))
        if (type(other) == int or type(other) == float):
            return Coord((self.x - other, self.y - other))
        raise TypeError()
        
    def __mul__(self, other):
        if (type(other) == Coord):
            return Coord((self.x * other.x, self.y * other.y))
        if (type(other) == tuple):
            return Coord((self.x * other[0], self.y * other[1]))
        if (type(other) == int or type(other) == float):
            return Coord((self.x * other, self.y * other))
        raise TypeError()
        
    def __truediv__(self, other):
        if (type(other) == Coord):
            return Coord((self.x / other.x, self.y / other.y))
        if (type(other) == tuple):
            return Coord((self.x / other[0], self.y / other[1]))
        if (type(other) == int or type(other) == float):
            return Coord((self.x / other, self.y / other))
        raise TypeError()
        
    def __floordiv__(self, other):
        if (type(other) == Coord):
            return Coord((self.x // other.x, self.y // other.y))
        if (type(other) == tuple):
            return Coord((self.x // other[0], self.y // other[1]))
        if (type(other) == int or type(other) == float):
            return Coord((self.x // other, self.y // other))
        raise TypeError()