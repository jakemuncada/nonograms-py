class CellIdx:
    """
    A cell's row-column index.
    """

    def __init__(self, *args) -> None:
        if len(args) == 0:
            row, col = 0, 0
        if len(args) == 1 and type(args[0]) == tuple:
            row, col = args[0]
        elif len(args) == 2 and type(args[0]) == int and type(args[1]) == int:
            row = args[0]
            col = args[1]
        else:
            raise ValueError('Invalid arguments.')

        self.row = row
        self.col = col
        self.r = row
        self.c = col

    def to_tuple(self) -> tuple[int, int]:
        """Convert to tuple."""
        return (self.row, self.col)

    def __iter__(self):
        return iter((self.row, self.col))