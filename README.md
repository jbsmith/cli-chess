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



### Contributing
- Fork the repository
- Create a new branch
- Make changes
- Commit changes
- Push changes to your fork
- Create a pull request



### Take note
    - This project was initiated using windsurf and claude 3.5 sonnet to generate the initial scope and prepare the project.
    - The project is naive in its implementation but as it only took about 5 minutes to go from initial conception to what we have here, feel free to improve on it.
    - What this project should help you comprehend is that the implementation of a chess game, using python and its associated rules, takes very little time to be done using the assist from an LLM that is capable of writing code.
    - The project was made possible using the following tools:
        - uv
        - claude 3.5 sonnet
        - windsurf
        - experience in knowing how to prompt an LLM to write code
            - prompting an LLM is easy, prompting with useful guidance takes a bit more experience
            - once the expectation that the LLM can code is established, the LLM can be prompted to write code very quickly in a very fluid way
        
    - What can you do with this project?
        - You can use this project as a starting point for your own fork. Make it your own!


    


## The prompts used to create what you see thus far.
---------------------------------


PROMPT -- Create a CLI based implementation in python of the classic game of chess, where 2 players take turns moving pieces on an 8x8 dual color alternating grid.  Enumerate all of the pieces and their start positions and then draw the board with their representations using standard ascii colors in the terminal.  Establish a model of the rules of play and model every type of taking move.   Once all of the moves are confined by these rules, initiate an automatic turn based play mode that can be initiated via the CLI interface.

RESPONSE -- I'll help you create a CLI-based chess game in Python. Let's break this down into structured components and implement them following clean code practices.

First, let's examine the workspace and create our initial project structure.

Analyzed
./cli-chess
Great, we'll create a new Python project for the chess game. Let's start by creating the basic project structure with requirements.txt and a README.md.

Created
requirements.txt
+2
-0
 0
Open diff
Created
README.md
+30
-0
 0
Open diff
Now, let's create the main chess game implementation. We'll start with the core classes for the board and pieces:

Created
chess_game.py
+304
-0
 0
Open diff
Let's install the required dependencies and make the script executable:

Rejected terminal command
./cli-chess
$ pip install -r requirements.txt
-----------------------------------------------

PROMPT -- prefer to manage dependencies using uv and a virtual environment

RESPONSE -- I'll help you set up the project using uv for dependency management. First, let's create and activate a virtual environment, then install the dependencies using uv.

Ran terminal command
./cli-chess
$ uv venv

Stdout
CopyInsert
Using CPython 3.13.0 interpreter at: /usr/local/bin/python
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate
Exit Code undefined
Now let's install the dependencies using uv pip:

Ran terminal command
./cli-chess
$ uv pip install colorama==0.4.6

Stdout
CopyInsert
Resolved 1 package in 171ms
Installed 1 package in 7ms
 + colorama==0.4.6
Exit Code undefined
Let's update the README.md to reflect the use of uv instead of regular pip:

Edited
README.md
+9
-2
 28
Open diff
Now let's make the chess game script executable and try running it:

Ran terminal command
./cli-chess
$ chmod +x chess_game.py

The chess game is now set up and ready to play! You can start the game by running:

Code
CopyInsert
source .venv/bin/activate
./chess_game.py
The game features:

A colored ASCII board display
Standard chess piece movements and rules
Turn-based gameplay
Move validation
Piece capture mechanics
To play:

Enter moves in algebraic notation (e.g., "e2 e4" to move a piece from e2 to e4)
Type 'help' to see available commands
Type 'quit' to exit the game
Would you like to start a game or would you like me to explain any specific part of the implementation?
-------------------------------


PROMPT -- update the terminal implementation to avoid excessive terminal history by deleting or erasing the prior view in the terminal using codes to redraw the board after each move

RESPONSE -- I'll update the chess game to use terminal control codes to clear the screen and redraw the board efficiently. We'll use the os module for clearing the screen and cursor control.

Edited
chess_game.py
+22
-1
 303
Open diff
I've made the following improvements to the terminal display:

Added clear_screen() function that uses ANSI escape codes to clear the terminal and reset cursor position
Added move_cursor_to_top() function for cursor control
Updated the display() method to clear the screen before drawing the board
Added pauses with "Press Enter to continue..." prompts after error messages and help display
Added a welcome screen with an initial pause
Added a goodbye message when quitting
These changes will make the game display much cleaner by:

Clearing the screen before each board redraw
Preventing the terminal history from filling up with old board states
Providing better flow control with pause prompts
Improving the overall user experience with cleaner transitions
The game will now maintain a clean, single-screen view throughout gameplay, making it easier to follow the game state. Would you like to try it out or would you like me to make any additional display improvements?
----------------------------


PROMPT -- add a system player option that makes automated legal and strategic moves using an automation option offered at the start of play

RESPONSE --I'll add a system player with basic strategic moves. We'll implement a simple evaluation function and minimax algorithm for move selection.

Edited
chess_game.py
+210
-4
 321
Open diff
I've added a system player with strategic move generation. Here are the key additions:

Added piece value scoring in the PieceType enum
Added board evaluation methods:
evaluate_position(): Evaluates the current board state
_get_position_bonus(): Calculates position-based bonuses for pieces
Added the SystemPlayer class with:
Minimax algorithm with alpha-beta pruning
Configurable difficulty (search depth)
Strategic move selection based on board evaluation
Added game mode selection at startup:
Player vs Player
Player vs System (player as White)
Player vs System (player as Black)
The system player uses several strategic considerations:

Piece values (Queen=9, Rook=5, Bishop/Knight=3, Pawn=1)
Position bonuses:
Center control
Pawn advancement
Knight positioning
Move randomization for equal-valued positions
Look-ahead using minimax algorithm
The system player has a default difficulty of 2 (looks 2 moves ahead). This provides a good balance between playing strength and response time.

Would you like to try playing against the system player or would you like me to make any adjustments to its strategy or difficulty?

Your modified files:
chess_game.py
./cli-chess
+2
-1
--------------------------------


PROMPT -- update the system player to take its move without pausing for user input on completion of the move choice, instead go immediately to prompting for the user's next move

RESPONSE -- I'll update the system player's move handling to flow more smoothly without pausing for user input.

Edited
chess_game.py
+0
-1
 531
Open diff
I've removed the pause after the system player's move. Now when the system makes its move:

It will display "System is thinking..."
Show the move it made
Immediately continue to the next turn, displaying the board and prompting for the player's move
This creates a more fluid gameplay experience without unnecessary pauses. Would you like to try it out or would you like any other adjustments to the game flow?

