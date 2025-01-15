import argparse
from copy import deepcopy
from oxDNA_analysis_tools.external_force_utils.force_reader import write_force_file, read_force_file
from oxDNA_analysis_tools.UTILS.RyeReader import strand_describe

def cli_parser(prog="extrapolate_force.py"):
    parser = argparse.ArgumentParser(prog=prog, description="Given forces on one tile, generate the same forces for n tiles")
    parser.add_argument('topology', type=str, help="Topology file of the filament")
    parser.add_argument('forces', type=str, help="Forces for a single tile")
    parser.add_argument('-o', '--output', type=str, help="Output file name")
    return parser

def main():
    parser = cli_parser()
    args = parser.parse_args()

    top = args.topology
    if args.output:
        output_file = args.output
    else:
        output_file = 'filament_forces.txt'

    sys, _ = strand_describe(top)

    # Get the length of a single tile
    tile_len = len(sys[0])
    n_tiles = len(sys)
    
    # Read the example forces
    forces = read_force_file(args.forces)

    new_forces = []

    # Copy the force to all the other tiles
    for i in range(1, n_tiles):
        for f in forces:
            new_f = deepcopy(f)
            new_f["particle"] = int(f["particle"] + (i*tile_len))
            new_f["ref_particle"] = int(f["ref_particle"] + (i*tile_len))
            new_forces.append(new_f)

    forces = forces+new_forces

    write_force_file(forces, output_file)

if __name__ == "__main__":
    main()