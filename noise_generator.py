from math import ceil, cos, floor, pi, sin, sqrt

import numpy as np

from perlin import Perlin
from utils import dist


class NoiseGenerator:
    """Noise generation class
    """
    
    def __init__(self, size, rand):
        """Initializer

        Args:
            size (int): Map size
            rand (np.random.RandomState): Numpy random object
        """
        self.size = size
        self.rand = rand
        #self.gen = OpenSimplex(seed=self.rand.randint(0, 100000))
        self.gen = Perlin(self.rand.randint(0, 100000))
    
    
    def noise(self, nx, ny):
        """Convert [-1, 1] noise to [0,1]

        Args:
            nx (float): x coord
            ny (float): y coord

        Returns:
            float: Noise value
        """
        return self.gen.noise2d(nx, ny) / 2.0 + 0.5
    
    
    def lake_noise(self, freq=1.0):
        """Generate Perlin noise for lakes

        Args:
            freq (float, optional): Frequency. Defaults to 1.0.

        Returns:
            list: List of lists containing noise values
        """
        values = []
        for y in range(self.size):
            values.append([0] * self.size)
            for x in range(self.size):
                nx = x/self.size - 0.5
                ny = y/self.size - 0.5
                
                value = self.noise(freq*nx, freq*ny)
                values[y][x] = value
                
        return values
    
    
    def ocean_noise(self, freq=1.0, dist=1.0):
        """Generate Perlin noise for ocean

        Args:
            freq (float, optional): Frequency. Defaults to 1.0.
            dist (float, optional): Distance factor. Defaults to 1.0.

        Returns:
            list: List of lists containing noise values
        """
        values = []
        for y in range(self.size):
            values.append([0] * self.size)
            for x in range(self.size):
                nx = x/self.size - 0.5
                ny = y/self.size - 0.5
                d = sqrt(nx*nx + ny*ny) / sqrt(0.5) * dist
                value = self.noise(freq*nx, freq*ny)
                values[y][x] = (1 + value - d) / 2
                
        return values
    
    
    


    def poisson_disc_samples(self, r, k=10):
        """ Generate random samples for current image size using Poisson Disk sampling
        Inspired by: https://github.com/emulbreh/bridson

        Args:
            r (float): Minimum distance between samples
            k (int, optional): Number of attempts for points to be placed. Defaults to 10.

        Returns:
            list: List of generated samples
        """
        tau = 2 * pi
        cellsize = r / sqrt(2)

        grid_size = int(ceil(self.size / cellsize))
        grid = [None] * (grid_size * grid_size)

        def grid_coords(p):
            return int(floor(p[0] / cellsize)), int(floor(p[1] / cellsize))

        def fits(p, gx, gy):
            yrange = list(range(max(gy - 2, 0), min(gy + 3, grid_size)))
            for x in range(max(gx - 2, 0), min(gx + 3, grid_size)):
                for y in yrange:
                    g = grid[x + y * grid_size]
                    if g is None:
                        continue
                    if dist(p, g) <= r:
                        return False
            return True

        p = int(self.size * self.rand.rand()), int(self.size * self.rand.rand())
        queue = [p]
        grid_x, grid_y = grid_coords(p)
        grid[grid_x + grid_y * grid_size] = p

        while queue:
            qi = int(self.rand.rand() * len(queue))
            qx, qy = queue[qi]
            queue[qi] = queue[-1]
            queue.pop()
            for _ in range(k):
                alpha = tau * self.rand.rand()
                d = r * sqrt(3 * self.rand.rand() + 1)
                px = int(qx + d * cos(alpha))
                py = int(qy + d * sin(alpha))
                if not (0 <= px < self.size and 0 <= py < self.size):
                    continue
                p = (px, py)
                grid_x, grid_y = grid_coords(p)
                if not fits(p, grid_x, grid_y):
                    continue
                queue.append(p)
                grid[grid_x + grid_y * grid_size] = p
                
        return [p for p in grid if p is not None]
