#!/bin/bash
# Run this in the parent directory
set -e
# variable setup
firstdir=$(find . -maxdepth 1 -type d -name 'run*' -print -quit)
seq_dep_file=/u/epoppleton/software/oxDNA/rna_sequence_dependent_parameters.txt

# Align everything to the centroid of the first trajectory
cd $firstdir
oat mean -p 5 trajectory.dat
oat centroid -p 5 mean.dat trajectory.dat
cd ..

for x in run*/; do
    cd $x
    sed -i "s|/u/matran/oxDNA/rna_sequence_dependent_parameters.txt|$seq_dep_file|" input_run
    oat align -p 5 -r ../$firstdir\/centroid.dat trajectory.dat aligned.dat
    if [ -f filament.top ]; then #We're in a filament simulation
       mkdir single_tiles
       cp filament.top single_tiles/
       cp input_run single_tiles/
    fi
    if [ \( -f aligned.dat \) -a \( -f trajectory.dat \) ]; then 
        rm trajectory.dat
    fi
    cd ..
    
done

# Prepare the nucleotide id files
if [ -f $firstdir\/filament.top ]; then
    python $(dirname "$0")/middle80.py $firstdir/filament.top
fi
