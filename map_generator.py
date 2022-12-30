import numpy as np
from PIL import Image

from biome import *
from cell import *
from cell_map import *
from icon_loader import IconLoader
from noise_generator import NoiseGenerator
from utils import dist, midpoint


class MapGenerator:
    """Main map generation class
    """
    
    """
    Constants                          
    """
    OCEAN_NOISE_FREQ = 7.0
    OCEAN_NOISE_DIST = 2.7
    OCEAN_WATER_BOUND = 0.1
    OCEAN_BEACH_BOUND = 0.14
    LAKE_NOISE_FREQ = 7.0
    LAKE_WATER_BOUND = 0.2
    LAKE_TRADE_DIST = 10
    FISH_WHALE_CHANCE = 0.8
    FISH_MIN_DIST_DIV = 20
    WHALE_CHANCE = 0.3
    TRADE_NO_POINTS = 3
    TRADE_RANDOMNESS = 50
    TRADE_MIN_POSTS = 2
    TRADE_MAX_POSTS = 4
    TRADE_MIN_DIST_DIV = 7
    NATIVE_MIN_POSTS = 1
    NATIVE_MAX_POSTS = 4
    NATIVE_MIN_DIST_DIV = 6
    NATIVE_MIN_DIST_PLACE_DIV = 10
    GOLD_MIN_DIST_DIV = 5.5
    GOLD_MIN_DIST_PLACE_DIV = 60
    FOREST_MIN_DIST_DIV = 8
    HUNT_MIN_DIST_DIV = 6
    TREASURE_MIN_DIST_DIV = 4.5
    TREASURE_MIN_DIST_PLACE_DIV = 30
    TC_NO = 2
    TC_MIN_DIST_DIV = 3
    TC_MIN_DIST_DIST_PLACE_DIV = 20 
    
    
    def __init__(self, size, seed, icon_path="icons"):
        """Initializer

        Args:
            size (int): Map size
            seed (int): Map seed
            icon_path (str, optional): Path to icons folder. Defaults to "icons".
        """
        if seed == None:
            self.seed = np.random.randint(0, 10000000)
        else:
            self.seed = seed
            
        self.size = size
        self.rand = np.random.RandomState(self.seed)
        self.map = Map(size, self.rand)
        self.noise_gen = NoiseGenerator(size, self.rand)
        self.icons = IconLoader(icon_path)
        
    
    def generate(self, type_str=None, biome_str=None, paste_compass=False):
        """Main generate function

        Args:
            type_str (str, optional): Map type to generate, randomly selected if None. Defaults to None.
            biome_str (str, optional): Biome type to generate, randomly selected if None. Defaults to None.
            paste_compass (bool, optional): Whether to add compass graphic to maps. Defaults to False.

        Returns:
            PIL.Image: Map image file
        """
        """
        Generating map
        """
        biome = self.generate_biome(biome_str)
        self.map.set_biome(biome)
        print("Biome selected: {}".format(biome))
        
        map_type = self.generate_map_type(type_str)
        print("Map type selected: {}".format(map_type))
        
        trade_pos = []
        if map_type == MapType.island:
            print("Generating Ocean...")
            self.generate_ocean()

        elif map_type == MapType.land:
            print("Generating Trade Route...")
            trade_pos = self.generate_trade_route()
            print("Generating Lakes...")
            self.generate_lakes()
            
        print("Generating Fish...")
        self.generate_fish()
            
        print("Generating Forests...")
        self.generate_forest()
        
        print("Generating Hunts...")
        self.generate_hunts()
        
        print("Generating Town Centers...")
        tc_pos, gold_pos = self.generate_tc()
        
        print("Generating Native Settlements...")
        native_pos = self.generate_natives()
        
        print("Generating Gold Mines...")
        gold_pos2 = self.generate_gold()
        
        gold_pos.extend(gold_pos2)
        
        print("Generating Treasures...")
        treasure_pos = self.generate_treasures()
        
        
        """
        Generating Image from map data
        """
        values = self.map.get_values_array()
        im = Image.fromarray(values)
        
        for pos in native_pos:
            self.paste_icon(im, self.icons.np, pos)
            
        for pos in trade_pos:
            self.paste_icon(im, self.icons.tp, pos)
        
        self.paste_icon(im, self.icons.tc_blue, tc_pos[0])
        self.paste_icon(im, self.icons.tc_red, tc_pos[1])
        
        for pos in gold_pos:
            self.paste_icon(im, self.icons.gold, pos)
            
        for pos in treasure_pos:
            self.paste_icon(im, self.icons.treasure, pos)
        
        if paste_compass:
            im = self.paste_compass(im)
       
        return im
        
    
    def generate_biome(self, biome_str):
        """Select biome to generate from biome_str. Chosen randomly if None.

        Args:
            biome_str (str): Biome type to generate.

        Returns:
            Biome: Selected biome
        """
        biomes = [b.name for b in Biomes]
        if biome_str in biomes:
            biome = Biomes(biome_str).value
        else:
            biome = Biomes(self.rand.choice(biomes, replace=False)).value
        
        return biome 
    
    
    def generate_map_type(self, type_str):
        """Select map type to generate from type_str. Chosen randomly if None.

        Args:
            type_str (str): Map type to generate

        Returns:
            MapType: Selected map type
        """
        map_types = [t.name for t in MapType]
        if type_str in map_types:
            map_type = MapType(type_str)
        else:
            map_type = MapType(self.rand.choice(map_types, replace=False))
    
        return map_type
        
    
    def generate_ocean(self):
        """Generate an ocean using an Adjusted Perlin noise function
        """
        noise = self.noise_gen.ocean_noise(self.OCEAN_NOISE_FREQ, self.OCEAN_NOISE_DIST)
        
        for y in range(len(noise)):
            for x in range(len(noise[y])):
                if self.map.is_in_bounds((y,x)) and noise[y][x] < self.OCEAN_WATER_BOUND:
                    self.map.set_cell_biome((y,x), CellType.water.value)
                elif self.map.is_in_bounds((y,x)) and noise[y][x] < self.OCEAN_BEACH_BOUND:
                    self.map.set_cell_biome((y,x), CellType.beach.value)
                    
    
    def generate_lakes(self):
        """Generate lakes using a Perlin noise function
        """
        noise = self.noise_gen.lake_noise(self.LAKE_NOISE_FREQ)
        
        for y in range(len(noise)):
            for x in range(len(noise[y])):
                if noise[y][x] < self.LAKE_WATER_BOUND:
                    if not self.map.close_to_biome((y,x), CellType.traderoute.value, self.LAKE_TRADE_DIST):
                        self.map.set_cell_biome((y,x), CellType.water.value)
    
    
    def generate_fish(self):
        """Generate fish and whales using Poisson Disc
        """
        coordinates = self.noise_gen.poisson_disc_samples(r=self.size/self.FISH_MIN_DIST_DIV)
        
        for coord in coordinates:
            if self.map.get_cell_biome(coord) == CellType.water.value:
                if self.rand.rand() < self.FISH_WHALE_CHANCE:
                    biome = CellType.fish.value
                else:
                    biome = CellType.whale.value
                self.map.place_fish(coord, biome)
        
    
    def generate_trade_route(self):
        """Generate a trade route with trade posts.

        Returns:
            list: List of trade post coordinates.
        """
        # Get two border points to act as begin and end
        coordinates1 = self.map.get_viable_border_cells()
        rand_coord1 = coordinates1[self.rand.randint(0, len(coordinates1))]
        coordinates2 = [coord for coord in coordinates1 if dist(rand_coord1, coord) > self.size/2]
        rand_coord2 = coordinates2[self.rand.randint(0, len(coordinates2))]
        
        trade_coords = [rand_coord1, rand_coord2]
        
        # Place more points between these and connect them
        for _ in range(self.TRADE_NO_POINTS):
            start = self.rand.randint(0, len(trade_coords)-1)
            middle = midpoint(trade_coords[start], trade_coords[start+1])
            middle[0] += self.rand.randint(-self.TRADE_RANDOMNESS, self.TRADE_RANDOMNESS)
            middle[1] += self.rand.randint(-self.TRADE_RANDOMNESS, self.TRADE_RANDOMNESS)
            trade_coords.insert(start+1, middle)
        
        # Draw the route on the map
        for i in range(len(trade_coords) -1):
            self.map.draw_trade_route(trade_coords[i], trade_coords[i+1])
            
        # Generate trade posts
        return self.generate_trade_posts()
    
    
    def generate_trade_posts(self):
        """Generate trade posts along the trade route.

        Returns:
            list: List of trade post coordinates.
        """
        trade_post_pos = []
        no_posts = self.rand.randint(self.TRADE_MIN_POSTS,self.TRADE_MAX_POSTS+1)
            
        route_coords = self.map.get_biome_coords(CellType.traderoute.value)
        for _ in range(no_posts):
            rand_coord = route_coords[self.rand.randint(0, len(route_coords))]
            self.map.place_placement(rand_coord, Status.TP)
            trade_post_pos.append(rand_coord)
            
            # Only consider points with enough distance
            route_coords = [coord for post_coord in trade_post_pos for coord in route_coords if dist(coord, post_coord) > self.size/self.TRADE_MIN_DIST_DIV]
        
        return trade_post_pos  
    
    
    def generate_natives(self):
        """Generate natives using Poisson Disc sampling

        Returns:
            list: List of native locations
        """
        native_pos = []
        no_natives = self.rand.randint(self.NATIVE_MIN_POSTS, self.NATIVE_MAX_POSTS+1)
        
        coordinates = self.noise_gen.poisson_disc_samples(r=self.size/self.NATIVE_MIN_DIST_DIV)
        
        for coord in coordinates:
          
            if self.map.get_cell_status(coord) == Status.EMPTY and not self.map.close_to_placement(coord, self.size/self.NATIVE_MIN_DIST_PLACE_DIV):
                native_pos.append(coord)
       
        
        native_pos = np.array(native_pos)[self.rand.choice(len(native_pos), no_natives, replace=False)]
            
        return native_pos
        
        
    def generate_gold(self):
        """Generate gold mines using Poisson Disc sampling

        Returns:
            list: List of gold mine locations
        """
        gold_pos = []
        coordinates = self.noise_gen.poisson_disc_samples(r=self.size/self.GOLD_MIN_DIST_DIV)
        
        for coord in coordinates:
            if self.map.get_cell_status(coord) == Status.EMPTY and not self.map.close_to_placement(coord, self.size/self.GOLD_MIN_DIST_PLACE_DIV):
                self.map.place_placement(coord, Status.GOLD)
                gold_pos.append(coord)
                
        return gold_pos
    
    
    def generate_forest(self):
        """Generate forests using Poisson Disc sampling
        """
        coordinates = self.noise_gen.poisson_disc_samples(r=self.size/self.FOREST_MIN_DIST_DIV)
        
        for coord in coordinates:
            if self.map.get_cell_status(coord) == Status.EMPTY:
                self.map.place_forest(coord)
                            
                            
    def generate_hunts(self):
        """Generate hunts using Poisson Disc sampling
        """
        coordinates = self.noise_gen.poisson_disc_samples(r=self.size/self.HUNT_MIN_DIST_DIV)
      
        for coord in coordinates:
            if self.map.get_cell_status(coord) == Status.EMPTY:
                self.map.place_hunt(coord)
    
    
    def generate_treasures(self):
        """Generate treasures using Poisson Disc sampling

        Returns:
            list: List of treasure positions
        """
        treasure_pos = []
        coordinates = self.noise_gen.poisson_disc_samples(r=self.size/self.TREASURE_MIN_DIST_DIV)
        
        for coord in coordinates:
            if self.map.get_cell_status(coord) == Status.EMPTY and not self.map.close_to_placement(coord, self.size/self.TREASURE_MIN_DIST_PLACE_DIV):
                self.map.place_placement(coord, Status.TREASURE)
                treasure_pos.append(coord)
                
        return treasure_pos
    
    
    def generate_tc(self):
        """Generate towncenters

        Returns:
            list: List of towncenter locations
            list: List of goldmine locations
        """
        tc_pos = []
        gold_pos = []
        
        coordinates = self.map.get_viable_cells(self.size/self.TC_MIN_DIST_DIST_PLACE_DIV)
        rand_coord = coordinates[self.rand.randint(0, len(coordinates))]
        tc_pos.append(rand_coord)
        gold_pos.append(self.map.place_tc(tuple(rand_coord)))
        
        for i in range(1, self.TC_NO):
            coordinates = [coord for coord in coordinates if dist(coord, tc_pos[i-1]) >= self.size/self.TC_MIN_DIST_DIV]
            rand_coord = coordinates[self.rand.randint(0, len(coordinates))]
            tc_pos.append(rand_coord)
            gold_pos.append(self.map.place_tc(tuple(rand_coord)))
        
        return tc_pos, gold_pos
    
    
    def paste_icon(self, image, icon, pos):
        """Paste icon onto an image

        Args:
            image (PIL.Image): Image to paste on
            icon (PIL.Image): Icon to paste
            pos (tuple): Location to paste on the image
        """
        image.paste(icon, (int(pos[1] - icon.size[1]/2), int(pos[0] - icon.size[0]/2)), icon)
    
    
    def paste_compass(self, image):
        """

        Args:
            image (PIL.Image): Map image

        Returns:
            PIL.Image: Image including the compass border
        """
        compass = self.icons.get_compass(self.size)
        offset = (compass.size[0] - image.size[0]) // 2, (compass.size[1] - image.size[1]) // 2
        compass.paste(image, offset, image)
        return compass
        
    
        
        