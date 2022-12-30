import os

from PIL import Image

from utils import resource_path


class IconLoader:
    """Icon loader class
    """
    COMPASS_MULT_FACT = 1.35
    
    def __init__(self, path):
        """Initialzer

        Args:
            path (str): Path to icons folder
        """
        self.tc_blue = Image.open(resource_path(os.path.join(path, "towncenter_blue.png")))
        self.tc_red = Image.open(resource_path(os.path.join(path, "towncenter_red.png")))
        self.tp = Image.open(resource_path(os.path.join(path, "trade.png")))
        self.np = Image.open(resource_path(os.path.join(path, "native.png")))
        self.gold = Image.open(resource_path(os.path.join(path, "gold.png")))
        self.treasure = Image.open(resource_path(os.path.join(path, "treasure.png")))
        self.compass = Image.open(resource_path(os.path.join(path, "compass.png")))
        
    def get_compass(self, size):
        """Get resized compass image

        Args:
            size (int): Image size

        Returns:
            PIL.Image: Rescaled compass picture
        """
        return self.compass.resize((int(size*self.COMPASS_MULT_FACT), int(size*self.COMPASS_MULT_FACT)), Image.ANTIALIAS)
        
        