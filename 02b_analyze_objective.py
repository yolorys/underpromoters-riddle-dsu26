#!/usr/bin/env python

import csv
import chess
import chess.engine

from utils import add_arguments, add_input_output_args, STOCKFISH_PATH, ANALYSIS_TIME_LIMIT
from pathlib import Path

# --- SCRIPT ---

def find_best_promotion_score(engine, board, piece_type):
    """
    Finds all legal promotions to a given piece type ANYWHERE on the board, 
    analyzes each, and returns the absolute best score.
    """
    promotion_moves = [move for move in board.legal_moves if move.promotion == piece_type]

    if not promotion_moves:
        return None # No promotions of this type are possible

    best_score = None
    is_white_turn = board.turn == chess.WHITE

    for move in promotion_moves:
        temp_board = board.copy()
        temp_board.push(move)
        info = engine.analyse(temp_board, chess.engine.Limit(time=ANALYSIS_TIME_LIMIT))
        score = info["score"].white().score(mate_score=10000)

        if best_score is None:
            best_score = score
        elif is_white_turn:
            if score > best_score: # White wants to maximize the score
                best_score = score
        else: # Black's turn
            if score < best_score: # Black wants to minimize the score
                best_score = score

    return best_score

# --- Main Loop Logic ---

def process_objective_data(input_path, output_path):
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    
    with open(input_path, 'r') as f_in, open(output_path, 'w', newline='') as f_out:
        reader = csv.DictReader(f_in)
        
        # We are keeping the "Move" column in the output! 
        # Even though Stockfish ignores it here, we need it later for Perspective 3.
        fieldnames = ["FEN", "White", "Black", "Move", "Best_Knight_Score", "Best_Queen_Score"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        # Use enumerate to keep a running count, starting at 1
        for count, row in enumerate(reader, start=1):
            board = chess.Board(row["FEN"])

            # 1. Evaluate the absolute ceiling for a Knight on this board
            best_knight_score = find_best_promotion_score(engine, board, chess.KNIGHT)
            
            # 2. Evaluate the absolute ceiling for a Queen on this board
            best_queen_score = find_best_promotion_score(engine, board, chess.QUEEN)

            writer.writerow({
                "FEN": row["FEN"],
                "White": row["White"],
                "Black": row["Black"],
                "Move": row["Move"], 
                "Best_Knight_Score": best_knight_score if best_knight_score is not None else "N/A",
                "Best_Queen_Score": best_queen_score if best_queen_score is not None else "N/A"
            })
            
            # --- REAL-TIME TELEMETRY ---
            # Print an update every 100 positions and force it to the SLURM .out log
            if count % 100 == 0:
                print(f"Objective Analysis: Processed {count} positions...", flush=True)
            
    engine.quit()


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    add_arguments(parser)

    add_input_output_args(parser, Path("promotions_with_moves.csv"), Path("objective_analysis_results.csv"))

    args = parser.parse_args()

    print("="*70)
    print(f"Starting Objective Analysis on {args.input}...")
    print("="*70, flush=True)

    process_objective_data(args.input, args.output)

    print(f"\n{'='*70}")
    print(f"Analysis Complete! Results saved to: {args.output}")
    print(f"{'='*70}", flush=True)
