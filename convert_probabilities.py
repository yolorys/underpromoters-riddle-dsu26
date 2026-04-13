#!/usr/bin/env python

import csv
import math
from pathlib import Path

def centipawns_to_win_probability(cp_score, is_white_turn):
    """
    Converts a centipawn score to a win probability.
    Returns the probability from the perspective of the player making the move.
    """
    if cp_score == "N/A" or cp_score is None:
        return None
        
    try:
        cp = float(cp_score)
        # Cap extreme scores to prevent math.exp overflow
        cp = max(-10000, min(10000, cp)) 
        
        # Calculate White's win probability
        white_prob = 1.0 / (1.0 + math.exp(-0.0035 * cp))
        
        # Return the probability for whoever is actually playing the move
        if is_white_turn:
            return white_prob
        else:
            return 1.0 - white_prob
            
    except (ValueError, TypeError):
        return None

if __name__ == "__main__":
    from argparse import ArgumentParser
    from utils import add_input_output_args

    parser = ArgumentParser(description="Convert centipawn scores to win probabilities")
    add_input_output_args(parser,
                          Path("behavioral_analysis_results.csv"),
                          Path("analysis_with_probabilities.csv"))
    
    args = parser.parse_args()
    
    print("="*70)
    print(f"Starting Probability Conversion on '{args.input}'...")
    print("="*70, flush=True)

    with open(args.input, 'r', newline='') as f_in, open(args.output, 'w', newline='') as f_out:
        reader = csv.DictReader(f_in)
        
        # Detect whether we are processing Behavioral or Objective data based on column headers
        k_col = "Knight_Promo_Score" if "Knight_Promo_Score" in reader.fieldnames else "Best_Knight_Score"
        q_col = "Queen_Promo_Score" if "Queen_Promo_Score" in reader.fieldnames else "Best_Queen_Score"
        
        # Add new columns to the output
        fieldnames = reader.fieldnames + ["Knight_Win_Prob", "Queen_Win_Prob"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        
        for count, row in enumerate(reader, start=1):
            fen = row["FEN"]
            # FEN part 1 (index 1) tells us whose turn it is: 'w' or 'b'
            is_white_turn = fen.split()[1] == 'w'
            
            knight_score = row[k_col]
            queen_score = row[q_col]
            
            # Calculate win probabilities based on WHOSE turn it is
            knight_prob = centipawns_to_win_probability(knight_score, is_white_turn)
            queen_prob = centipawns_to_win_probability(queen_score, is_white_turn)
            
            # Format as standard floats for easier math in the classification script
            row["Knight_Win_Prob"] = round(knight_prob, 4) if knight_prob is not None else "N/A"
            row["Queen_Win_Prob"] = round(queen_prob, 4) if queen_prob is not None else "N/A"
            
            writer.writerow(row)
            
            if count % 10000 == 0:
                print(f"Conversion: Processed {count} positions...", flush=True)
    
    print(f"\n{'='*70}")
    print(f"Conversion Complete! Results saved to: {args.output}")
    print(f"{'='*70}", flush=True)