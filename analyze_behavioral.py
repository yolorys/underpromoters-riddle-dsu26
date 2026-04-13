#!/usr/bin/env python

import csv
import chess
import chess.engine

from utils import add_arguments, add_input_output_args, STOCKFISH_PATH, ANALYSIS_TIME_LIMIT
from pathlib import Path

# --- SCRIPT ---

def evaluate_move_score(engine, board, move):
    """Evaluates a specific move and returns White's centipawn score."""
    if move not in board.legal_moves:
        return None # Move is illegal in this position
    
    temp_board = board.copy()
    temp_board.push(move)
    info = engine.analyse(temp_board, chess.engine.Limit(time=ANALYSIS_TIME_LIMIT))
    return info["score"].white().score(mate_score=10000)

# --- Main Loop Logic ---
# This assumes input is now a CSV with: FEN, White, Black, Move

def process_behavioral_data(input_path, output_path):
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    
    with open(input_path, 'r') as f_in, open(output_path, 'w', newline='') as f_out:
        # Using DictReader/Writer to handle new columns more easily (metadata like usernames / moves)
        reader = csv.DictReader(f_in)
        fieldnames = ["FEN", "White", "Black", "Move", "Knight_Promo_Score", "Queen_Promo_Score"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            board = chess.Board(row["FEN"])
            actual_move = chess.Move.from_uci(row["Move"])

            # 1. Evaluate the ACTUAL HUMAN MOVE
            actual_score = evaluate_move_score(engine, board, actual_move)

            # 2. Evaluate the "HYPOTHETICAL" choice (Q/N) on the SAME square
            if actual_move.promotion == chess.KNIGHT:
                hypo_promotion = chess.QUEEN
            else:
                hypo_promotion = chess.KNIGHT

            # Create a brand new move object to avoid mutating the original move (which is needed for the actual move evaluation)
            hypo_move = chess.Move(actual_move.from_square, actual_move.to_square, promotion=hypo_promotion)

            hypo_score = evaluate_move_score(engine, board, hypo_move)

            # 3. Correctly assign scores to the columns for probability script
            if actual_move.promotion == chess.KNIGHT:
                k_score, q_score = actual_score, hypo_score
            else:
                k_score, q_score = hypo_score, actual_score

            writer.writerow({
                "FEN": row["FEN"],
                "White": row["White"],
                "Black": row["Black"],
                "Move": row["Move"],
                "Knight_Promo_Score": k_score if k_score is not None else "N/A",
                "Queen_Promo_Score": q_score if q_score is not None else "N/A"
            })
        engine.quit()

# === ENTRY POINT ===
if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    add_arguments(parser)

    add_input_output_args(parser, Path("promotions_with_moves.csv"), Path("behavioral_analysis_results.csv"))

    args = parser.parse_args()

    print("="*70)
    print(f"Starting Behavioral Analysis on {args.input}...")
    print("="*70, flush=True)

    # Call the encapsulated loop function
    process_behavioral_data(args.input, args.output)

    print(f"\n{'='*70}")
    print(f"Analysis Complete! Results saved to: {args.output}")
    print(f"{'='*70}", flush=True)
