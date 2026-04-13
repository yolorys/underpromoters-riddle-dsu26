#!/usr/bin/env python

import csv
from collections import Counter
from pathlib import Path

def classify_behavioral_move(p_knight, p_queen):
    """
    Applies the 5-tier classification system with fixes for 
    Style (Flex) and Defensive Saves.
    NOTE: Input probabilities must already be from the Active Player's perspective.
    """
    if p_knight == "N/A" or p_queen == "N/A" or p_knight is None or p_queen is None:
        return "Invalid Data"

    # 1. DEFINE BUCKETS (0=Loss, 1=Draw, 2=Win)
    def get_bucket(prob):
        if prob < 0.35: return 0 # Loss
        if prob > 0.65: return 2 # Win
        return 1 # Draw

    q_bucket = get_bucket(p_queen)
    n_bucket = get_bucket(p_knight)

    # 2. BRILLIANT: Knight improves the RESULT bucket (e.g. Loss->Draw, Draw->Win)
    if n_bucket > q_bucket:
        return "Brilliant"

    # 3. BLUNDER: Knight worsens the RESULT bucket (e.g. Win->Draw, Draw->Loss)
    if n_bucket < q_bucket:
        return "Blunder"

    # 4. CHECK FOR STYLE (Both are Wins, but Knight is worse)
    # If both are Winning (Bucket 2), but Knight drops probability significantly
    if n_bucket == 2 and q_bucket == 2:
        if (p_queen - p_knight) > 0.05: # Knight is worse by >5%
            return "Style / Flex" # <--- YOUR RESEARCH GOLD MINE
    
    # 5. REMAINING TIERS (Optimal, Equivalent, Suboptimal)
    # If buckets are same (likely Draw/Draw or Loss/Loss), check efficiency
    diff = p_knight - p_queen

    if diff > 0.05:
        return "Optimal" # Knight is clearly better (e.g. within same bucket)
    elif diff < -0.05:
        return "Suboptimal" # Knight is clearly worse (but same result bucket)
    else:
        return "Equivalent"

# --- MAIN SCRIPT ---

if __name__ == "__main__":
    from argparse import ArgumentParser
    from utils import add_input_output_args

    parser = ArgumentParser(description="Classify behavioral promotion decisions")
    add_input_output_args(parser,
                          Path("behavioral_with_prob.csv"),
                          Path("behavioral_final_classifications.csv"))
    
    args = parser.parse_args()
    
    print("="*70)
    print(f"Classifying promotions from '{args.input}'...", flush=True)
    print("="*70, flush=True)

    classifications = []
    
    with open(args.input, 'r', newline='') as f_in, open(args.output, 'w', newline='') as f_out:
        reader = csv.DictReader(f_in)
        
        # Add classification column
        fieldnames = reader.fieldnames + ["Classification"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            try:
                # We simply read the floats directly! No dividing by 100 needed.
                knight_prob = float(row["Knight_Win_Prob"]) if row["Knight_Win_Prob"] != "N/A" else "N/A"
                queen_prob = float(row["Queen_Win_Prob"]) if row["Queen_Win_Prob"] != "N/A" else "N/A"
            except ValueError:
                knight_prob, queen_prob = "N/A", "N/A"
            
            # Classify the move
            tier = classify_behavioral_move(knight_prob, queen_prob)
            classifications.append(tier)
            
            row["Classification"] = tier
            writer.writerow(row)
    
    # Print summary statistics
    print(f"\nClassification complete!", flush=True)
    print(f"Results saved to: {args.output}", flush=True)
    print("\n" + "="*70, flush=True)
    print("FINAL RESULTS", flush=True)
    print("="*70, flush=True)
    
    summary = Counter(classifications)
    total = len(classifications)
    
    print(f"Total Positions Analyzed: {total}\n", flush=True)
    
    for tier, count in summary.most_common():
        percentage = (count / total) * 100
        print(f"{tier:<18}: {count:>4} ({percentage:>5.1f}%)", flush=True)