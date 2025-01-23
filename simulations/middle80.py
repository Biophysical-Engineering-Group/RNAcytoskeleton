# Generate id files for each of the middle 80 tiles

import argparse
import numpy as np
import os

parser = argparse.ArgumentParser()
parser.add_argument('topology')
args = parser.parse_args()

top = args.topology

with open(top, 'r') as f:
    header = f.readline()

header = header.split()
n_nuc = int(header[0])
n_str = int(header[1])

tenpercent = int(np.floor(0.1 * n_str))

nuc_per_tile = np.round(n_nuc / n_str, 5)
assert(nuc_per_tile.is_integer())
nuc_per_tile = int(nuc_per_tile)

os.mkdir('tile_ids')

for i in range(tenpercent, n_str-tenpercent):
    with open(f'tile_ids/{i:04}.txt', 'w+') as f:
        f.write(' '.join([str((nuc_per_tile * i) + n) for n in range(nuc_per_tile)]))
