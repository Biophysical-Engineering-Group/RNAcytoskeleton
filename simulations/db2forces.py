import argparse
from re import sub
from oxDNA_analysis_tools.db_to_force import db_to_forcelist
from oxDNA_analysis_tools.external_force_utils.force_reader import write_force_file

def cli_parser(prog="assemble_filament.py"):
    parser = argparse.ArgumentParser(prog=prog, description="Assemble tiles into a tube")
    parser.add_argument('design', type=str, help="ROAD design output file")
    parser.add_argument('-o', '--output', type=str, help="Output file name")
    parser.add_argument('-s', '--stiffness', type=float, help="Stiffness of the mutual trap to create" )
    return parser

def main():
    parser = cli_parser()
    args = parser.parse_args()

    design_file = args.design
    if args.output:
        output_file = args.output
    else:
        output_file = 'forces.txt'
    if args.stiffness:
        stiff = args.stiffness
    else:
        stiff = 3.1

    with open(design_file, 'r') as f:
        lines = f.readlines()
        db = lines[1]

    # Remove all loop annotations from the db
    db = sub('[a-zA-Z0-9]', '.', db)

    # unfortunatley, there are a lot of other utilities I need to update before I can use the new top format
    # so it'll still be backwards.
    # create a force file for all normal base pairs
    forcelist = db_to_forcelist(db, stiff, True)
 
    # Write out to file
    write_force_file(forcelist, output_file)

if __name__ == "__main__":
    main()