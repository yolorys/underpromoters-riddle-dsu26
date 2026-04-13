# Import the necessary library for handling chess games
import csv
import chess.pgn

# --- Configuration ---
# Set the name of your large PGN file here
pgn_file_name = "lichess_elite_2025-05.pgn" 
# Set the name of the file where you want to save the results
output_file_name = "knight_promotions.csv"

# --- Main Script ---
print(f"Starting to process {pgn_file_name}...")

# Open the files and store their actual file objects in variables
pgn_file = open(pgn_file_name, encoding="utf-8-sig")
raw_output_file = open(output_file_name, 'w', newline='')

# Pass the raw file object into the DictWriter
output_writer = csv.DictWriter(raw_output_file, fieldnames=["FEN", "White", "Black", "Move"])
output_writer.writeheader()

found_count = 0
game_count = 0

# Loop through the PGN file, reading one game at a time
# This is memory-efficient and can handle very large files
while True:
    try:
        # Read a single game from the file
        game = chess.pgn.read_game(pgn_file)
        
        # If no more games are found, break the loop
        if game is None:
            break
            
        game_count += 1
        
        # Create a board object to play through the moves
        board = game.board()
        
        # Iterate through all the main moves of the game
        for move in game.mainline_moves():
            # Before we make the move, we get the board state (FEN string)
            # This represents the position right BEFORE the promotion
            fen_before_move = board.fen()
            
            # Check if the current move is a promotion to a knight
            # The 'promotion' attribute of a move is not None if it's a promotion
            # We then check if the promotion piece is a knight
            if move.promotion is not None and move.promotion == chess.KNIGHT:
                # We found one!
                found_count += 1
                # Write metadata to our output file
                output_writer.writerow({
                    "FEN": fen_before_move,
                    "White": game.headers.get("White", "Unknown"),
                    "Black": game.headers.get("Black", "Unknown"),
                    "Move": move.uci() # the actual move in UCI format (e.g., e7e8n for knight promotion)
                })
            
            # Make the move on the board to advance to the next position
            board.push(move)

        # Print a progress update every 10,000 games
        if game_count % 10000 == 0:
            print(f"Scanned {game_count} games, found {found_count} knight promotions...")

    except Exception as e:
        # This helps to skip any games that might have errors in the PGN file
        print(f"Skipping a game due to an error: {e}")
        continue

# Close the files once we're done
pgn_file.close()
raw_output_file.close()

print("\n--- Process Complete ---")
print(f"Total games scanned: {game_count}")
print(f"Total knight promotions found: {found_count}")
print(f"Results saved to: {output_file_name}")