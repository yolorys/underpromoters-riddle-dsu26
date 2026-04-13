# The Underpromoter's Riddle: A Computational Analysis of the Knight Promotion in Chess

**Author:** Yelarys Seidin  
**Institution:** Dakota State University  
**Event:** DSU Annual Research Symposium (Spring 2026)  

## Project Overview
In chess, when a pawn reaches the 8th rank, it must be promoted. Because the Queen is the most powerful piece, human players choose to promote to a Queen overwhelmingly (up to 97.3% of the time). However, in roughly 1.5% of games, a player will explicitly reject a Queen in favor of a mathematically weaker Knight—a move known as an "Underpromotion." 

This research utilizes high-performance computing to ask a fundamental question: **When elite players choose a 3-point Knight over a 9-point Queen, is it a tactical necessity, or simply a stylistic flex?**

By comparing the actual decisions of human players against the infallible mathematical "Ground Truth" of the Stockfish chess engine, this pipeline reveals the psychological "Queen Bias" that causes humans to blunder winning games, while also identifying brilliant tactical saves and unnecessary stylistic flexing.

## The Computational Pipeline
This repository contains the Python scripts used to process over 310,000 elite games from the Lichess Database. The architecture is broken into four distinct stages:

### Stage 1: Extraction
* `01a_find_knight_promotions.py`
* `01b_find_queen_promotions.py`
**Function:** Scans raw PGN files to find the exact half-move prior to a promotion occurring. It extracts the static board state (FEN string) and filters the data into datasets based on what the human eventually chose (Knight vs. Queen).

### Stage 2: Evaluation (Two Perspectives)
* `02a_analyze_behavioral.py`
* `02b_analyze_objective.py`
* `utils.py`
**Function:** Deployed on DSU's Nestor High-Performance Computing (HPC) cluster, these scripts utilize the Stockfish engine to evaluate the board states. 
* *Behavioral Track:* Evaluates the specific move the human chose.
* *Objective Track:* Evaluates all legal promotion paths to find the mathematical absolute best move.

### Stage 3: Conversion
* `03_convert_probabilities.py`
**Function:** Engine evaluations are output in "centipawns" (an unbounded, non-linear scale). This script passes those raw scores through a logistic S-Curve equation to compress them into a strict, standardized Win Probability between 0% and 100%.

### Stage 4: Classification
* `04a_classify_behavioral.py`
* `04b_classify_objective.py`
**Function:** Classifies the standardized data into human-readable buckets. It determines the mathematical "Ground Truth" (Objective) and tags human behavior (Behavioral) as *Brilliant*, a *Blunder*, or a *Style/Flex*.

## Final Datasets
The pipeline generated three final output files containing the evaluated and classified board states (~71,000 specific FEN positions):
* `05a_knight_behavioral_classification.csv`
* `05b_queen_behavioral_classification.csv`
* `05c_objective_classification.csv`

## Technologies Used
* **Python 3** (Data extraction, parsing, and pipeline architecture)
* **python-chess** (Library for PGN parsing and FEN generation)
* **Stockfish** (Open-source chess engine for board evaluation)
* **SLURM Workload Manager** (HPC cluster job scheduling via `submit.slurm`)

## Known Limitations (Version 1.0)
* **Dataset Purity:** The Stage 1 extraction scripts pulled from the Lichess Elite Database without filtering out registered bot/AI accounts. Consequently, the current Behavioral Classification datasets contain a mixture of human and machine decisions. Version 2.0 of this pipeline will implement string-matching and API checks to strictly isolate human-only accounts, ensuring the "Queen Bias" and "Style/Flex" classifications are perfectly mapped to human psychology.