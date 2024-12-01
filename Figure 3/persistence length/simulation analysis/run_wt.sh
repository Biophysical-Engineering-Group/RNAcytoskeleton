#!/bin/bash -l
# Job name
#SBATCH -J T3H

# How many resources to use
#SBATCH -N 1
#SBATCH -n 10
#SBATCH -c 1
#SBATCH --constraint="gpu"
#SBATCH --gres=gpu:a100:1
#SBATCH --mem=40000
#SBATCH --time=1-00:00:00

conda activate oxDNA

python ~/final_scripts/longfil_process.py trajectory.dat filament.top 3 --remove 0.1
