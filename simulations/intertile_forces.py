import numpy as np
import argparse
from dataclasses import dataclass
from oxDNA_analysis_tools.external_force_utils.force_reader import read_force_file, write_force_file
from oxDNA_analysis_tools.external_force_utils.forces import mutual_trap
from oxDNA_analysis_tools.UTILS.RyeReader import strand_describe

# p and q always refer to the position in tile 1
# diff is the tile difference between p and q
@dataclass
class heuristic:
    p : int
    q : int
    d : int

def get_diff(i, d, tpl):
    if np.floor(i/tpl) % 2:
        d = d+1
    if (np.floor((i+d) / tpl) - np.floor(i / tpl)) - 1:
        d = d - tpl

    return d

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('topology')
    parser.add_argument('example_force')
    parser.add_argument('tiles_per_layer', type=int)
    args = parser.parse_args()

    top = args.topology
    ff = args.example_force
    tpl = args.tiles_per_layer

    sy, ele = strand_describe(top)

    forces = read_force_file(ff)

    tile_len = sy.strands[0].get_length()

    init_forces = []

    for f in forces[::2]:
        t1 = int(np.floor(f['particle'] / tile_len))
        t2 = int(np.floor(f['ref_particle'] / tile_len))
        diff = np.abs(t2 - t1)

        init_forces.append(heuristic(int(f['particle']), int(f['ref_particle'] % tile_len), diff))

    output_forces = []

    for i, _ in enumerate(sy.strands):
        for h in init_forces:
            p = h.p + (i*tile_len)
            q = int(h.q + ((i+get_diff(i, h.d, tpl))*tile_len))
            #q = int(h.q + ((i + (h.d + (np.floor(i / tpl) % 2) - (tpl * ((np.floor((i+h.d +(np.floor(i / tpl) % 2)) / tpl) - np.floor(i / tpl)) - 1)))) * tile_len))

            if q > len(ele):
                continue

            f = mutual_trap(p, q, 0.09, 1.2, True)
            output_forces.append(f)
            f = mutual_trap(q, p, 0.09, 1.2, True)
            output_forces.append(f)

    write_force_file(output_forces, 'forces.txt')

if __name__ == '__main__':
    main()