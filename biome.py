from enum import Enum


class Color:
    """ RGBA Color class
    """
    def __init__(self, r, g, b, a=255):
        """Initializer

        Args:
            r (int): Red component
            g (int): Green component
            b (int): Blue component
            a (int, optional): Alpha component. Defaults to 255.
        """
        self.values = (r, g, b, a)


class Biome:
    """Biome class
    """
    def __init__(self, color, name):
        """Initializer

        Args:
            color (Color): Color of the biome
            name (str): Name of the biome
        """
        self.color = color
        self.name = name
        
    def __str__(self):
        return self.name


class Biomes(Enum):
    """Main terrain biomes
    """
    snow = Biome(Color(197,223,230), "snow") 
    plains = Biome(Color(115,148,90), "plains") 
    andes = Biome(Color(207,206,74), "andes") 
    decan = Biome(Color(212,140,92), "decan") 
    
    def __new__(cls, value):
        """Enum object can be instantiated using biome name
        """
        obj = object.__new__(cls)
        obj._value_ = value
        cls._value2member_map_[value.name] = obj
        return obj


class CellType(Enum):
    """Secundary terrain biomes
    """
    water = Biome(Color(74,99,148), "water")
    beach = Biome(Color(220,215,182), "beach") 
    forest = Biome(Color(51,51,34), "forest")
    hunts = Biome(Color(116,48,48), "hunts")
    fish = Biome(Color(109,116,118), "fish")
    whale = Biome(Color(109,85,61), "whale")
    traderoute = Biome(Color(231,231,231), "traderoute")
    OOB = Biome(Color(0,0,0,0), "OOB")




    

