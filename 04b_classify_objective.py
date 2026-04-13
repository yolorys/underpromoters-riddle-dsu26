#!/usr/bin/env python

import csv
from collections import Counter
from pathlib import Path
from utils import add_arguments, add_input_output_args

# --- MATH & LOGIC ---

def classify_superiority(k_prob_str, q_prob_str):
    """
    Classifies the mathematical relationship between the two pieces.
    Requires a 5% (0.05) active-player probability difference to declare strict superiority.
    """
    if k_prob_str == "N/A" or q_prob_str == "N/A":
        return "None_Legal"
    
    try:
        k_prob = float(k_prob_str)
        q_prob = float(q_prob_str)
    except ValueError:
        return "Data_Error"
        
    diff = k_prob - q_prob
    
    if diff >= 0.05:
        return "Knight_Strictly_Superior"
    elif diff <= -0.05:
        return "Queen_Strictly_Superior"
    else:
        return "Equivalent"

# --- MAIN SCRIPT ---

def process_classifications(input_path, output_path):
    classifications = []
    
    with open(input_path, 'r', newline='') as f_in, open(output_path, 'w', newline='') as f_out:
        reader = csv.DictReader(f_in)
        
        # Add our final analytical column
        fieldnames = reader.fieldnames + ["Objective_Class"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for count, row in enumerate(reader, start=1):
            
            # Extract the probabilities
            k_prob = row["Knight_Win_Prob"]
            q_prob = row["Queen_Win_Prob"]
            
            # Classify based on the 5% threshold
            classification = classify_superiority(k_prob, q_prob)
            classifications.append(classification)
            
            # Write data
            row["Objective_Class"] = classification
            writer.writerow(row)
            
            # Real-time telemetry
            if count % 10000 == 0:
                print(f"Classification: Processed {count} positions...", flush=True)
                
    # --- PRINT SUMMARY STATISTICS ---
    print("\n" + "="*70, flush=True)
    print("OBJECTIVE GROUND TRUTH RESULTS", flush=True)
    print("="*70, flush=True)
    
    summary = Counter(classifications)
    total = len(classifications)
    
    print(f"Total Theoretical Positions Analyzed: {total}\n", flush=True)
    
    for tier, count in summary.most_common():
        percentage = (count / total) * 100
        print(f"{tier:<26}: {count:>6} ({percentage:>5.1f}%)", flush=True)

# === ENTRY POINT ===
if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Classify objective superiority of promotions")
    add_arguments(parser)
    
    add_input_output_args(parser, Path("objective_with_prob.csv"), Path("objective_final_classifications.csv"))

    args = parser.parse_args()

    print("="*70)
    print(f"Starting Objective Classification on '{args.input}'...")
    print("="*70, flush=True)

    process_classifications(args.input, args.output)