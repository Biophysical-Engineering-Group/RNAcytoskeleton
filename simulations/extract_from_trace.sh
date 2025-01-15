#! /bin/zsh

source ~/.zshrc

for fname in $(ls | grep -Ei '\-[0-9]+_trace.txt'); do
    echo $fname
    basename=${fname%"_trace.txt"}
    start=$(cat $fname | grep -n "2D diagram" | cut -d":" -f1)
    end=$(($(cat $fname | grep -n "Strand Path" | cut -d":" -f1)-1))
    newname=$basename\_pattern.txt
    echo ">$basename" > $newname
    head -n $end $fname | tail -n $(($end-$start)) >> $newname

    conda activate ROAD

    #Make PDB file from diagram
    cp ~/software/ROAD/bin/{RNAbuild.pl,RNA_lib.pdb} .
    perl RNAbuild.pl $newname
    rm RNAbuild.pl RNA_lib.pdb

    #RNAbuild leaves some sort of protein after the TER
    #oxView doesn't seem to notice, but taco does.
    sed '/TER/q' $basename\.pdb > tmp.txt
    mv tmp.txt $basename\.pdb

    conda activate base

    #convert pdb to oxDNA
    python ~/software/tacoxDNA/src/PDB_oxDNA.py $basename\.pdb 53
    mv *.oxdna $basename\.dat
    mv *.top $basename\.top

    #Make force file from dot-bracket
    python ~/software/filament_simulation/db2forces.py $basename\_design.txt -o $basename\_forces.txt -s 0.9

done

    
