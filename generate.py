"""
generate.py: Main file used to generate the maps.
"""
import argparse
import os
from time import time

from map_generator import MapGenerator

try:
    import gooey
    from gooey import local_resource_path
except ImportError as e:
    gooey = e


def get_argparse_args():
    parser = argparse.ArgumentParser(description='Generate random AOE3 style minimaps')
    parser.add_argument("--out", type=str, default='out', 
                        help='Specify output directory')
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
    return parser.parse_args()

if not isinstance(gooey, ImportError):
    @gooey.Gooey(
        image_dir=local_resource_path("icons"),
        menu=[{
            'name': 'About',
            'items':[{
                'type': 'AboutDialog',
                'menuTitle': 'About',
                'name': 'AOE3 Map Generator',
                'description': 'Generate random AOE3 style minimaps',
                'version': '1.0',
                'copyright': '2022',
                'developer': 'William Corsel',
                'website': 'https://github.com/williamcorsel/AoE3Unknown',
            }],
            
        }]
    )
    def get_gooey_args():
        parser = gooey.GooeyParser(description='Generate random AOE3 style minimaps')
        parser.add_argument("--out", type=str, default='out', widget='DirChooser', 
                            help='Specify output directory')
        parser.add_argument("--size", type=int, default=600, widget='IntegerField', gooey_options={'min': 100, 'max': 1000},
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
        return parser.parse_args()

    get_args = get_gooey_args
else:
    get_args = get_argparse_args


# Parse arguments
def main():
    args = get_args()

    os.makedirs(args.out, exist_ok=True)
        
    start_time = time()
    for _ in range(args.no):
        map_generator = MapGenerator(args.size, args.seed)
        random_map = map_generator.generate(args.type, args.biome, args.compass)
        map_path = os.path.join(args.out, 'map_{}.png'.format(map_generator.seed))
        print("Saving map to {}".format(map_path))
        random_map.save(map_path)

    total_time = time() - start_time

    print("Generating took {}s".format(total_time))

    if args.no <= 1:
        random_map.show()

main()
