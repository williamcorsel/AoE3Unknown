from copy import deepcopy

import numpy as np

from biome import *
from cell import *
from utils import dist


class MapType(Enum):
    """ Maptype Enum
    """
    island="island"
    land="land"


class Map:
    """Cell Map class 
    """
    
    """
    Constants                          
    """
    VIABLE_MIN_DIST_DIV = 2
    ROUTE_WIDTH = 3
    TC_MAX_RANGE_DIV = 15
    TC_MIN_DIST_DIV = 40
    FOREST_CHUNK_SIZE = 5
    FOREST_MIN_DIST = 15
    FOREST_MAX_DIST = 20
    FOREST_MIN_NO = 30
    FOREST_MAX_NO = 60
    FISH_CHUNK_SIZE = 4
    HUNT_CHUNK_SIZE = 5
    
    def __init__(self, size, rand):
        """Initializer

        Args:
            size (int): Size of the map
            rand (np.random.RandomState): Numpy random class object
        """
        self.size = size
        self.rand = rand
        self.cells = []
        self.placements = []  
    
    
    def set_biome(self, biome):
        """Set main terrain biome and fill initial cells

        Args:
            biome (Biomes): Main terrain biome
        """
        cells = []
        
        # Fill everything with main biome
        for y in range(self.size):
            row = []
            for x in range(self.size):
                row.append(Cell((y,x), biome))
            cells.append(row)
        
        cells = np.array(cells)
        
        # Remove OOB cells
        mask = self.create_circular_mask()
        cells[~mask] = Cell((-1, -1), biome=CellType.OOB.value, status=Status.OOB)
        
        self.cells = cells
    
        
    def create_circular_mask(self):
        """Create a circular mask

        Returns:
            list: List of lists with bool values
        """
        center = (int(self.size/2), int(self.size/2))
        radius = min(center[0], center[1], self.size-center[0], self.size-center[1])
        
        y, x = np.ogrid[:self.size, :self.size]
        dist_from_center = np.sqrt((x - center[0])**2 + (y - center[1])**2)
        mask = dist_from_center <= radius
        return mask
    
    
    def get_viable_cells(self, min_dist=0):
        """Get a list of viable (empty) cells

        Args:
            min_dist (int, optional): Exclude cells within dist of other placements. Defaults to 0.

        Returns:
            list: List of coordinate tuples
        """
        coordinates = []
        
        
        middle = self.size // 2, self.size // 2
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                cell = self.cells[y][x]
                
                # Check cell status and distance to middle
                if cell.status != Status.OOB and cell.status != Status.WATER and dist(middle, (y,x)) < self.size // self.VIABLE_MIN_DIST_DIV:
                    dist_to_buildings = [dist((y,x), val) for val in self.placements]
                    
                    # Check distance to other placements
                    if all(val > min_dist for val in dist_to_buildings):
                        coordinates.append((y,x))

        return coordinates
        
    
    
    def get_viable_border_cells(self):
        """Get list of viable (empty) border cells

        Returns:
            list: List of coordinate tuples
        """
        coordinates = []
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                
                if self.cells[y][x].status != Status.OOB:
                    if self.cells[y][x].status == Status.EMPTY:
                        coordinates.append((y,x))
                    if self.cells[y][self.size-x-1].status == Status.EMPTY:
                        coordinates.append((y,self.size - x))
                    break
                
        return coordinates         
    
        
    def get_values_array(self):
        """Get color values array of the map

        Returns:
            list: List of lists containing color quadruples
        """
        color_values = np.zeros((self.size, self.size, 4), dtype=np.uint8)
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                values = self.cells[y][x].get_values()
                color_values[y][x] = values
                
        return color_values
    
    
    def draw_trade_route(self, pos1, pos2):
        """Draw trade route on the map

        Args:
            pos1 (tuple): Coordinate
            pos2 (tuple): Coordinate
        """
        if pos1[0] < pos2[0]:
            start = deepcopy(list(pos1))
            end = list(pos2)
        else:
            start = deepcopy(list(pos2))
            end = list(pos1)
            
        while not np.array_equal(start, end):
            if start[0] < end[0]:
                start[0] += 1 
            elif start[0] > end[0]:
                start[0] -= 1
                
            if start[1] > end[1]:
                start[1] -= 1
            elif start[1] < end[1]:
                start[1] += 1
            
            for i in range(self.ROUTE_WIDTH):
                for j in range(self.ROUTE_WIDTH):
                    self.set_cell_biome((start[0]+i, start[1]+j), CellType.traderoute.value)
                    self.set_cell_biome((start[0]-i, start[1]-j), CellType.traderoute.value)   
    
    
    def close_to_biome(self, pos, biome, dist):
        """Checks if pos is wihtin dist of a biome

        Args:
            pos (tuple): Start coordinate
            biome (Biome): Biome to search for
            dist (int): Search distance

        Returns:
            bool: True if biome was found, False if not.
        """
        for i in [-dist, dist]:
            for j in range(-dist, dist):
                if self.get_cell_biome((pos[0]+i, pos[1]+j)) == biome or self.get_cell_biome((pos[0]+j, pos[1]+i)) == biome:
                    return True
                   
        return False
    
    
    def get_biome_coords(self, biome):
        """Get a list of coordinates of a given biome

        Args:
            biome (Biome): Biome to check

        Returns:
            list: List of biome coordinates
        """
        coordinates = []
        
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                if self.get_cell_biome((y,x)) == biome:
                    coordinates.append((y,x))
        
        return coordinates
        
    
    def place_tc(self, pos):
        """Place a towncenter on the map and generate starting mine and hunt

        Args:
            pos (tuple): Town center position

        Returns:
            tuple: coordinate of the gold mine
        """
        self.placements.append(pos)
        
        # Get viable coordinates around TC
        coordinates = []
        max_range = self.size // self.TC_MAX_RANGE_DIV
        for y in range(pos[0] - max_range, pos[0] + max_range):
            for x in range(pos[1] - max_range, pos[1] + max_range):
                if self.get_cell_status((y,x)) == Status.EMPTY and dist(pos, (y,x)) > self.size / self.TC_MIN_DIST_DIV:
                    coordinates.append((y,x))
        
        # Place hunt and gold mine
        rand_idx = self.rand.randint(0, len(coordinates))
        gold_coord = coordinates[rand_idx]
        hunt_coord = coordinates[-rand_idx]
        self.place_placement(gold_coord, Status.GOLD)
        self.place_hunt(hunt_coord)
            
        self.set_cell_status(pos, Status.TC)
        return gold_coord
        
        
    def place_forest(self, pos):
        """Place forest on the map with pos coordinate as middle

        Args:
            pos (tuple): Forest middle coordinate
        """
        distance = self.rand.randint(self.FOREST_MIN_DIST, self.FOREST_MAX_DIST)
        amount = self.rand.randint(self.FOREST_MIN_NO, self.FOREST_MAX_NO)
        y1 = self.rand.normal(pos[0], distance, size=(amount,)).astype('int')
        x1 = self.rand.normal(pos[1], distance, size=(amount,)).astype('int')
        
        for i in range(len(y1)):
            for j in range(-self.FOREST_CHUNK_SIZE, self.FOREST_CHUNK_SIZE):
                for k in range(-self.FOREST_CHUNK_SIZE, self.FOREST_CHUNK_SIZE):
                    y = y1[i] + j
                    x = x1[i] + k
                    if self.get_cell_status((y,x)) == Status.EMPTY:
                        self.set_cell_biome((y, x), CellType.forest.value)
    
    
    def place_fish(self, pos, biome):
        """Place fish or whale biome in water cells

        Args:
            pos (tuple): Middle coordinate of fish chunk
            biome (Biome): Biome to full. Use fish or whale.
        """
        for j in range(-self.FISH_CHUNK_SIZE, self.FISH_CHUNK_SIZE):
            for k in range(-self.FISH_CHUNK_SIZE, self.FISH_CHUNK_SIZE):
                cur_pos = pos[0] + j, pos[1] + k
                if self.get_cell_biome(cur_pos) == CellType.water.value:
                    self.set_cell_biome(cur_pos, biome)
    
      
    def close_to_placement(self, pos, min_dist):
        """Check if pos is within min_dist of a placement

        Args:
            pos (tuple): coordinate
            min_dist (float): Distance

        Returns:
            bool: True if a placement is in reach. False if not.
        """
        for placement in self.placements:
            if dist(pos, placement) < min_dist:
                return True
        return False
    
    
    def place_hunt(self, pos):
        """Place hunt on map

        Args:
            pos (tuple): Hunt middle coordinate
        """
        distance = self.rand.randint(5, 10)
        amount = self.rand.randint(5, 10)
        y1 = self.rand.normal(pos[0], distance, size=(amount,)).astype('int')
        x1 = self.rand.normal(pos[1], distance, size=(amount,)).astype('int')
        
        for i in range(len(y1)):
            for j in range(-self.HUNT_CHUNK_SIZE, self.HUNT_CHUNK_SIZE):
                for k in range(-self.HUNT_CHUNK_SIZE, self.HUNT_CHUNK_SIZE):
                    y = y1[i] + j
                    x = x1[i] + k
                    if self.get_cell_status((y,x)) == Status.EMPTY:
                        self.set_cell_biome((y,x), CellType.hunts.value)
         
    
    
    def place_placement(self, pos, status):
        """Add a placement to the map

        Args:
            pos (tuple): Coordinate of placement
            status (Status): Type of placement
        """
        self.placements.append(pos)
        self.set_cell_status(pos, status)
    
    
    def legal_cell(self, pos):
        """Check if cell position is legal

        Args:
            pos (tuple): Position of cell

        Returns:
            bool: True if within bounds. False if not.
        """
        return pos[0] >= 0 and pos[0] < self.size and pos[1] >= 0 and pos[1] < self.size
      
        
    def is_in_bounds(self, pos):
        """Checks whether cell is in playable region or not

        Args:
            pos (tuple): Position of cell

        Returns:
            bool: True if status is not OOB. False if it is.
        """
        return self.cells[pos].status != Status.OOB
    
    
    def set_cell_color(self, pos, color):
        if self.legal_cell(pos): 
            self.cells[pos].set_color(color)
        
    def set_cell_biome(self, pos, biome):
        if self.legal_cell(pos):  
            self.cells[pos].set_biome(biome)
        
    def set_cell_status(self, pos, status):
        if self.legal_cell(pos): 
            self.cells[pos].set_status(status)
            
    def get_cell_status(self, pos):
        if self.legal_cell(pos): 
            return self.cells[pos].get_status()
            
    def get_cell_biome(self, pos):
        if self.legal_cell(pos): 
            return self.cells[pos].get_biome()
