# CLI Chess Game

A command-line implementation of chess where two players can play against each other or the system.

## Features
- ASCII color representation of the chess board
- Standard chess piece movements and rules
- Turn-based gameplay
- Move validation
- Piece capture mechanics

## Requirements
- Python 3.7+
- uv (for dependency management)

## Installation
```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

## Usage
```bash
python chess_game.py
```

## Game Controls
- Moves are entered in algebraic notation (e.g., "e2 e4" to move a piece from e2 to e4)
- Type 'quit' to exit the game
- Type 'help' to see available commands
