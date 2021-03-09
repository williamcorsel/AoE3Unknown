"""
generate.py: Main file used to generate the maps.
"""
from datetime import datetime
from time import time

from PIL import Image

from map_generator import MapGenerator
import numpy as np
import os
import argparse

# Parse arguments
parser = argparse.ArgumentParser(description='Generate random AOE3 style minimaps')
parser.add_argument("--size", type=int, default=600,
                    help='Specify map size')
parser.add_argument("--type", type=str, default='random', choices=['random', 'island', 'land'],
                    help='Specify map type')
parser.add_argument("--biome", type=str, default='random', choices=['random', 'snow', 'plains', 'andes', 'decan'],
                    help='Specify map biome')
parser.add_argument("--seed", type=int, default=None,
                    help='Specify map generation seed')
parser.add_argument("--no", type=int, default=1,
                    help="Specify number of maps to be generated")
parser.add_argument("--compass", action="store_true", 
                    help="Place compass icon around generated maps")
args = parser.parse_args()

if not os.path.isdir("out"):
    os.mkdir("out")
    
    
start_time = time()
for _ in range(args.no):
    map_generator = MapGenerator(args.size, args.seed)
    random_map = map_generator.generate(args.type, args.biome, args.compass)
    random_map.save(os.path.join('out', 'map_{}.png'.format(map_generator.seed)))

total_time = time() - start_time

print("Generating took {}s".format(total_time))

if args.no <= 1:
    random_map.show()
