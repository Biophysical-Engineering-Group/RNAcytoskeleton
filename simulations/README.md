# filament_simulation

## Scripts

### assemble_filament.py
Python script to take a single tile and convert it into a filament.  
* configuration - conf file (.dat) you want to assemble the tile from.
* topology - topology file (.top) for the configuration file.
* n_layers - How many tiles long do you want the filament to be?
* tile_per_layer - How many tiles are there per layer?
* filament_radius - Fudge factor to move the tiles away from the helix axis.

Produces top & dat files for the filament.  Currently hardcoded to `filament.{top,dat}`.

### db2forces.py
[DEPRECIATED: use `oat db2forces` instead] Python script to take the dot-bracket notation for a single tile and generate an oxDNA force file.  Only works with old-style topologies.
* design_file - A file with the sequence on line 0 and the dot-bracket on line 1
* -o - Output force file name (default: forces.txt)
* -s - Stiffness of the created forces (default: 3.1) 

Produces:
* force file - based on the input dot-bracket

### extract_from_trace.sh
Zsh script to extract oxDNA files from a ROAD trace file

Run in a directory containing the trace file. If there are more than one trace files in the directory, it will generate structures for each of them.

Produces:
* pdb file - RNAbuild.pl output file for the design schematic
* top & dat files - From the pdb file
* force file - From the design dot-bracket

### extrapolate_force.py
Given the forces for a single tile, generate forces for a topology file containing many copies of that tile.
* topology - An oxDNA topology file containing multiple tiles
* forces - An oxDNA force file with forces for a single tile
* -o - Output force file name (default: filament_forces.txt)

Produces:
force file - For the entire filament

### intertile_force
Python script to generate forces holding a filament together from an example for which sticky ends are complimentary on a single tile
* topology - Topology file for the filament
* example_force - Force file noting which nucleotides complimentary for one tile in the fillament (can be generated from oxView or you could add this to extract_from_trace.sh)

Produces a force file with the forces required to pull a tile together.  Currently hardcoded to `forces.txt`.

## Dependencies for shell scripts
* [ROAD](https://github.com/esa-lab/ROAD) (With Perl installed in a conda environment called `ROAD`)
* [oxDNA_analysis_tools](https://github.com/lorenzo-rovigatti/oxDNA/tree/master/analysis) (Installed in your base conda environment)
* [tacoxDNA](https://github.com/lorenzo-rovigatti/tacoxDNA) (With its dependencies installed in your base conda environemnt)

If you want to change those conda requirements, edit the conda commands in `extract_from_tract.sh`
