from math import sqrt, floor
from ctypes import c_int64


def overflow(x):
    """Enables python int overflow for perm generation

    Args:
        x (int): input int

    Returns:
        int: Output int
    """
    return c_int64(x).value


class Perlin:
    """ Opensimplex Perlin noise Class
    Inspired by: https://github.com/lmas/opensimplex
    """
    
    PERM_SIZE = 256
    STRETCH_CONSTANT = (1/sqrt(2+1)-1)/2
    SQUISH_CONSTANT = (sqrt(2+1)-1)/2
    NORM_CONSTANT = 47
    
    # Gradients for 2D. They approximate the directions to the
    # vertices of an octagon from the center.
    GRADIENTS = (
         5,  2,    2,  5,
        -5,  2,   -2,  5,
         5, -2,    2, -5,
        -5, -2,   -2, -5,
    )
    
    
    def __init__(self, seed):
        """Initializer

        Args:
            seed (int): Random seed
        """
        self.perm = self.get_perm(seed)
        
      
    def get_perm(self, seed):
        """Gets permutation list from seed

        Args:
            seed (int): Random seed

        Returns:
            list: List of permutation value
        """
        perm = [0] * self.PERM_SIZE
        source = [i for i in range(0, self.PERM_SIZE)]
        
        seed = overflow(seed * 6364136223846793005 + 1442695040888963407)
        seed = overflow(seed * 6364136223846793005 + 1442695040888963407)
        seed = overflow(seed * 6364136223846793005 + 1442695040888963407)
        for i in range(self.PERM_SIZE-1, -1, -1):
            seed = overflow(seed * 6364136223846793005 + 1442695040888963407)
            r = int((seed + 31) % (i + 1))
            if r < 0:
                r += i + 1
            perm[i] = source[r]
            source[r] = source[i]
            
        return perm
        
    def extrapolate(self, xsb, ysb, dx, dy):
        """ Extrapolate value between grid and real coordinate

        Args:
            xsb (int): Grid x coordinate
            ysb (int): Grid y coordinate
            dx (float): Distance to grid in x-axis
            dy (float): Distance to grid in y-axis

        Returns:
            float: extrapolated value
        """
        index = self.perm[(self.perm[xsb & 0xFF] + ysb) & 0xFF] & 0x0E

        g1, g2 = self.GRADIENTS[index:index + 2]
        return g1 * dx + g2 * dy
    
    def noise2d(self, x, y):
        """Generate 2d OpenSimplex noise from x and y coordinates

        Args:
            x (float): x coordinate
            y (float): y coordinate

        Returns:
            float: Noise value between -1 and +1
        """
        # Place input coordinates onto grid.
        stretch_offset = (x + y) * self.STRETCH_CONSTANT
        xs = x + stretch_offset
        ys = y + stretch_offset

        # Floor to get grid coordinates of rhombus (stretched square) super-cell origin.
        xsb = floor(xs)
        ysb = floor(ys)

        # Skew out to get actual coordinates of rhombus origin. We'll need these later.
        squish_offset = (xsb + ysb) * self.SQUISH_CONSTANT
        xb = xsb + squish_offset
        yb = ysb + squish_offset

        # Compute grid coordinates relative to rhombus origin.
        xins = xs - xsb
        yins = ys - ysb

        # Sum those together to get a value that determines which region we're in.
        in_sum = xins + yins

        # Positions relative to origin point.
        dx0 = x - xb
        dy0 = y - yb

        value = 0

        # Contribution (1,0)
        dx1 = dx0 - 1 - self.SQUISH_CONSTANT
        dy1 = dy0 - 0 - self.SQUISH_CONSTANT
        attn1 = 2 - dx1 * dx1 - dy1 * dy1
        
        if attn1 > 0:
            attn1 *= attn1
            value += attn1 * attn1 * self.extrapolate(xsb + 1, ysb + 0, dx1, dy1)

        # Contribution (0,1)
        dx2 = dx0 - 0 - self.SQUISH_CONSTANT
        dy2 = dy0 - 1 - self.SQUISH_CONSTANT
        attn2 = 2 - dx2 * dx2 - dy2 * dy2
        if attn2 > 0:
            attn2 *= attn2
            value += attn2 * attn2 * self.extrapolate(xsb + 0, ysb + 1, dx2, dy2)

        if in_sum <= 1: # We're inside the triangle (2-Simplex) at (0,0)
            zins = 1 - in_sum
            if zins > xins or zins > yins: # (0,0) is one of the closest two triangular vertices
                if xins > yins:
                    xsv_ext = xsb + 1
                    ysv_ext = ysb - 1
                    dx_ext = dx0 - 1
                    dy_ext = dy0 + 1
                else:
                    xsv_ext = xsb - 1
                    ysv_ext = ysb + 1
                    dx_ext = dx0 + 1
                    dy_ext = dy0 - 1
            else: # (1,0) and (0,1) are the closest two vertices.
                xsv_ext = xsb + 1
                ysv_ext = ysb + 1
                dx_ext = dx0 - 1 - 2 * self.SQUISH_CONSTANT
                dy_ext = dy0 - 1 - 2 * self.SQUISH_CONSTANT
        else: # We're inside the triangle (2-Simplex) at (1,1)
            zins = 2 - in_sum
            if zins < xins or zins < yins: # (0,0) is one of the closest two triangular vertices
                if xins > yins:
                    xsv_ext = xsb + 2
                    ysv_ext = ysb + 0
                    dx_ext = dx0 - 2 - 2 * self.SQUISH_CONSTANT
                    dy_ext = dy0 + 0 - 2 * self.SQUISH_CONSTANT
                else:
                    xsv_ext = xsb + 0
                    ysv_ext = ysb + 2
                    dx_ext = dx0 + 0 - 2 * self.SQUISH_CONSTANT
                    dy_ext = dy0 - 2 - 2 * self.SQUISH_CONSTANT
            else: # (1,0) and (0,1) are the closest two vertices.
                dx_ext = dx0
                dy_ext = dy0
                xsv_ext = xsb
                ysv_ext = ysb
            xsb += 1
            ysb += 1
            dx0 = dx0 - 1 - 2 * self.SQUISH_CONSTANT
            dy0 = dy0 - 1 - 2 * self.SQUISH_CONSTANT

        # Contribution (0,0) or (1,1)
        attn0 = 2 - dx0 * dx0 - dy0 * dy0
        if attn0 > 0:
            attn0 *= attn0
            value += attn0 * attn0 * self.extrapolate(xsb, ysb, dx0, dy0)

        # Extra Vertex
        attn_ext = 2 - dx_ext * dx_ext - dy_ext * dy_ext
        if attn_ext > 0:
            attn_ext *= attn_ext
            value += attn_ext * attn_ext * self.extrapolate(xsv_ext, ysv_ext, dx_ext, dy_ext)

        return value / self.NORM_CONSTANT