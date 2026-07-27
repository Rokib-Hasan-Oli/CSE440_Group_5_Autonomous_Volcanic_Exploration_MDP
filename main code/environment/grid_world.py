import numpy as np
from config import GRID_SIZE

class GridWorld:
    def __init__(self):
        self.size = GRID_SIZE
        self.grid = np.zeros((self.size, self.size))

    def set_cell(self, x, y, value):
        self.grid[x][y] = value

    def get_cell(self, x, y):
        return self.grid[x][y]

    def is_valid(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size
