from enum import Enum

from biome import *


class Status(Enum):
    """Cell status Enum 
    """
    OOB = -1
    EMPTY = 0
    WATER = 1
    TR = 2
    TC = 3
    TP = 4
    NP = 5
    GOLD = 6
    TREASURE = 7


class Cell:
    """Map cell class
    """
    
    def __init__(self, pos, biome, status=Status.EMPTY):
        """Initialzer

        Args:
            pos (tuple): Cell y, x position
            biome (Biome): Cell biome
            status (Status, optional): Cell status. Defaults to Status.EMPTY.
        """
        self.pos = pos
        self.biome = biome
        self.color = biome.color
        self.status = status
        
        
    def set_biome(self, biome):
        if self.biome == CellType.OOB.value:
            return
    
        if biome == CellType.water.value:
            self.status = Status.WATER
        elif biome == CellType.traderoute.value:
            self.status = Status.TR
        
        self.biome = biome
        self.color = biome.color
    
    def set_color(self, color):
        self.color = color
        
    def set_status(self, status):
        self.status = status
        
    def get_status(self):
        return self.status
        
    def get_biome(self):
        return self.biome
    
    def get_values(self):
        return self.color.values
    
    
if __name__ == "__main__":
    from biome import *
    from color import Color
    cell = Cell(PLAINS)
    cell.set_color(Color(0,0,0))
    
    assert cell.color != PLAINS.color
