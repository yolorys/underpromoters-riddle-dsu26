#!/usr/bin/env bash
#SBATCH --partition=compute
#SBATCH --job-name=chess-analysis
#SBATCH --output=chess-analysis-%j.out
#SBATCH --error=chess-analysis-%j.err
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=2-00:00:00

echo nix develop --command python $@
nix develop --command python $@
