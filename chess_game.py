#!/usr/bin/env python3

import sys
import os
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colored output
init()

def clear_screen():
    """Clear the terminal screen and move cursor to top-left."""
    # Use ANSI escape codes to clear screen and move cursor
    print("\033[2J\033[H", end="")

def move_cursor_to_top():
    """Move cursor to top-left of terminal."""
    print("\033[H", end="")

class PieceColor(Enum):
    WHITE = "white"
    BLACK = "black"

class PieceType(Enum):
    KING = "K"
    QUEEN = "Q"
    ROOK = "R"
    BISHOP = "B"
    KNIGHT = "N"
    PAWN = "P"

    @property
    def value_score(self) -> int:
        """Return the relative value score of each piece type."""
        VALUES = {
            PieceType.KING: 0,  # Special case, not used in evaluation
            PieceType.QUEEN: 9,
            PieceType.ROOK: 5,
            PieceType.BISHOP: 3,
            PieceType.KNIGHT: 3,
            PieceType.PAWN: 1
        }
        return VALUES[self]

@dataclass
class Position:
    row: int
    col: int

    def is_valid(self) -> bool:
        return 0 <= self.row < 8 and 0 <= self.col < 8

    def to_algebraic(self) -> str:
        return f"{chr(self.col + 97)}{8 - self.row}"

    @staticmethod
    def from_algebraic(notation: str) -> 'Position':
        col = ord(notation[0].lower()) - 97
        row = 8 - int(notation[1])
        return Position(row, col)

class Piece:
    def __init__(self, piece_type: PieceType, color: PieceColor, position: Position):
        self.piece_type = piece_type
        self.color = color
        self.position = position
        self.has_moved = False

    def __str__(self) -> str:
        symbol = self.piece_type.value
        return f"{Fore.BLUE if self.color == PieceColor.WHITE else Fore.RED}{symbol}{Style.RESET_ALL}"

    def get_valid_moves(self, board: 'Board') -> List[Position]:
        moves = []
        row, col = self.position.row, self.position.col
        
        if self.piece_type == PieceType.PAWN:
            # Direction depends on color
            direction = 1 if self.color == PieceColor.BLACK else -1
            
            # Forward move
            forward = Position(row + direction, col)
            if (0 <= forward.row < 8 and 
                not board.squares[forward.row][forward.col]):  # Empty square
                moves.append(forward)
                
                # Initial two-square move
                if not self.has_moved:
                    double_forward = Position(row + 2 * direction, col)
                    if (0 <= double_forward.row < 8 and 
                        not board.squares[double_forward.row][double_forward.col]):
                        moves.append(double_forward)
            
            # Diagonal captures
            for capture_col in [col - 1, col + 1]:
                if 0 <= capture_col < 8:
                    capture_pos = Position(row + direction, capture_col)
                    if 0 <= capture_pos.row < 8:
                        # Normal capture
                        target = board.squares[capture_pos.row][capture_pos.col]
                        if target and target.color != self.color:
                            moves.append(capture_pos)
                        
                        # En passant capture
                        if board.last_pawn_move:
                            last_from, last_to = board.last_pawn_move
                            if (last_to.col == capture_col and  # Adjacent column
                                last_to.row == row and  # Same row
                                abs(last_from.row - last_to.row) == 2 and  # Double move
                                board.squares[last_to.row][last_to.col].color != self.color):  # Opponent's pawn
                                moves.append(capture_pos)
            
            # TODO: Add en passant captures later
            
        elif self.piece_type == PieceType.KNIGHT:
            # Knight moves in L-shape
            knight_moves = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            for dr, dc in knight_moves:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target_piece = board.squares[new_row][new_col]
                    if not target_piece or target_piece.color != self.color:
                        moves.append(Position(new_row, new_col))
                        
        elif self.piece_type == PieceType.BISHOP:
            # Bishop moves diagonally
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                while 0 <= new_row < 8 and 0 <= new_col < 8:
                    target_piece = board.squares[new_row][new_col]
                    if not target_piece:
                        moves.append(Position(new_row, new_col))
                    elif target_piece.color != self.color:
                        moves.append(Position(new_row, new_col))
                        break
                    else:
                        break
                    new_row, new_col = new_row + dr, new_col + dc
                    
        elif self.piece_type == PieceType.ROOK:
            # Rook moves horizontally and vertically
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                while 0 <= new_row < 8 and 0 <= new_col < 8:
                    target_piece = board.squares[new_row][new_col]
                    if not target_piece:
                        moves.append(Position(new_row, new_col))
                    elif target_piece.color != self.color:
                        moves.append(Position(new_row, new_col))
                        break
                    else:
                        break
                    new_row, new_col = new_row + dr, new_col + dc
                    
        elif self.piece_type == PieceType.QUEEN:
            # Queen moves like both bishop and rook
            directions = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1),           (0, 1),
                (1, -1),  (1, 0),  (1, 1)
            ]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                while 0 <= new_row < 8 and 0 <= new_col < 8:
                    target_piece = board.squares[new_row][new_col]
                    if not target_piece:
                        moves.append(Position(new_row, new_col))
                    elif target_piece.color != self.color:
                        moves.append(Position(new_row, new_col))
                        break
                    else:
                        break
                    new_row, new_col = new_row + dr, new_col + dc
                    
        elif self.piece_type == PieceType.KING:
            # King moves one square in any direction
            directions = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1),           (0, 1),
                (1, -1),  (1, 0),  (1, 1)
            ]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target_piece = board.squares[new_row][new_col]
                    if not target_piece or target_piece.color != self.color:
                        moves.append(Position(new_row, new_col))
            
            # TODO: Add castling moves later
        
        return moves

    def _get_pawn_moves(self, board: 'Board') -> List[Position]:
        moves = []
        direction = 1 if self.color == PieceColor.BLACK else -1
        
        # Forward move
        forward = Position(self.position.row + direction, self.position.col)
        if forward.is_valid() and not board.get_piece(forward):
            moves.append(forward)
            
            # Initial two-square move
            if not self.has_moved:
                double_forward = Position(self.position.row + 2 * direction, self.position.col)
                if double_forward.is_valid() and not board.get_piece(double_forward):
                    moves.append(double_forward)

        # Capture moves
        for col_offset in [-1, 1]:
            capture_pos = Position(self.position.row + direction, self.position.col + col_offset)
            if capture_pos.is_valid():
                piece = board.get_piece(capture_pos)
                if piece and piece.color != self.color:
                    moves.append(capture_pos)

        return moves

    def _get_rook_moves(self, board: 'Board') -> List[Position]:
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dx, dy in directions:
            for i in range(1, 8):
                new_pos = Position(self.position.row + dx * i, self.position.col + dy * i)
                if not new_pos.is_valid():
                    break
                    
                piece = board.get_piece(new_pos)
                if piece:
                    if piece.color != self.color:
                        moves.append(new_pos)
                    break
                moves.append(new_pos)
                
        return moves

    def _get_knight_moves(self, board: 'Board') -> List[Position]:
        moves = []
        offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for dx, dy in offsets:
            new_pos = Position(self.position.row + dx, self.position.col + dy)
            if new_pos.is_valid():
                piece = board.get_piece(new_pos)
                if not piece or piece.color != self.color:
                    moves.append(new_pos)
                    
        return moves

    def _get_bishop_moves(self, board: 'Board') -> List[Position]:
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dx, dy in directions:
            for i in range(1, 8):
                new_pos = Position(self.position.row + dx * i, self.position.col + dy * i)
                if not new_pos.is_valid():
                    break
                    
                piece = board.get_piece(new_pos)
                if piece:
                    if piece.color != self.color:
                        moves.append(new_pos)
                    break
                moves.append(new_pos)
                
        return moves

    def _get_queen_moves(self, board: 'Board') -> List[Position]:
        return self._get_rook_moves(board) + self._get_bishop_moves(board)

    def _get_king_moves(self, board: 'Board') -> List[Position]:
        moves = []
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        
        for dx, dy in directions:
            new_pos = Position(self.position.row + dx, self.position.col + dy)
            if new_pos.is_valid():
                piece = board.get_piece(new_pos)
                if not piece or piece.color != self.color:
                    moves.append(new_pos)
                    
        return moves

class Board:
    def __init__(self):
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        self._setup_board()
        self.last_pawn_move = None  # Tuple of (from_pos, to_pos) for en passant
        self.move_history = []  # List of tuples (from_pos, to_pos, piece_type, color)
        self.current_player = PieceColor.WHITE

    def _setup_board(self):
        # Setup white pieces
        self._place_piece(PieceType.ROOK, PieceColor.WHITE, Position(7, 0))
        self._place_piece(PieceType.KNIGHT, PieceColor.WHITE, Position(7, 1))
        self._place_piece(PieceType.BISHOP, PieceColor.WHITE, Position(7, 2))
        self._place_piece(PieceType.QUEEN, PieceColor.WHITE, Position(7, 3))
        self._place_piece(PieceType.KING, PieceColor.WHITE, Position(7, 4))
        self._place_piece(PieceType.BISHOP, PieceColor.WHITE, Position(7, 5))
        self._place_piece(PieceType.KNIGHT, PieceColor.WHITE, Position(7, 6))
        self._place_piece(PieceType.ROOK, PieceColor.WHITE, Position(7, 7))

        # Setup black pieces
        self._place_piece(PieceType.ROOK, PieceColor.BLACK, Position(0, 0))
        self._place_piece(PieceType.KNIGHT, PieceColor.BLACK, Position(0, 1))
        self._place_piece(PieceType.BISHOP, PieceColor.BLACK, Position(0, 2))
        self._place_piece(PieceType.QUEEN, PieceColor.BLACK, Position(0, 3))
        self._place_piece(PieceType.KING, PieceColor.BLACK, Position(0, 4))
        self._place_piece(PieceType.BISHOP, PieceColor.BLACK, Position(0, 5))
        self._place_piece(PieceType.KNIGHT, PieceColor.BLACK, Position(0, 6))
        self._place_piece(PieceType.ROOK, PieceColor.BLACK, Position(0, 7))

        # Setup pawns
        for col in range(8):
            self._place_piece(PieceType.PAWN, PieceColor.BLACK, Position(1, col))
            self._place_piece(PieceType.PAWN, PieceColor.WHITE, Position(6, col))

    def _place_piece(self, piece_type: PieceType, color: PieceColor, position: Position):
        self.squares[position.row][position.col] = Piece(piece_type, color, position)

    def get_piece(self, position: Position) -> Optional[Piece]:
        if position.is_valid():
            return self.squares[position.row][position.col]
        return None

    def move_piece(self, from_pos: Position, to_pos: Position) -> Tuple[bool, Optional[str]]:
        """Move a piece and return (success, error_message)."""
        piece = self.squares[from_pos.row][from_pos.col]
        if not piece:
            return False, "No piece at starting position"
            
        if piece.color != self.current_player:
            return False, "Not your turn"

        # Check if move is in piece's valid moves
        valid_moves = piece.get_valid_moves(self)
        if to_pos not in valid_moves:
            piece_type = piece.piece_type.value
            return False, f"Invalid move for {piece_type} - not in its movement pattern"
            
        # Track last pawn move for en passant
        if piece.piece_type == PieceType.PAWN:
            self.last_pawn_move = (from_pos, to_pos)
            
            # Handle en passant capture
            if abs(from_pos.col - to_pos.col) == 1 and not self.squares[to_pos.row][to_pos.col]:
                # Remove captured pawn
                capture_row = from_pos.row
                self.squares[capture_row][to_pos.col] = None
        else:
            self.last_pawn_move = None
            
        # Try the move
        captured_piece = self.squares[to_pos.row][to_pos.col]
        self.squares[to_pos.row][to_pos.col] = piece
        self.squares[from_pos.row][from_pos.col] = None
        
        # Check if move puts own king in check
        if self.is_king_in_check(piece.color):
            # Undo the move
            self.squares[from_pos.row][from_pos.col] = piece
            self.squares[to_pos.row][to_pos.col] = captured_piece
            return False, "Move would leave your king in check"

        # Record move in history
        self.move_history.append((from_pos, to_pos, piece.piece_type, piece.color))
        
        # Update piece's internal position and switch players
        piece.position = to_pos
        piece.has_moved = True
        self.current_player = PieceColor.BLACK if self.current_player == PieceColor.WHITE else PieceColor.WHITE
        return True, None

    def get_all_valid_moves(self, color: PieceColor) -> List[Tuple[Position, Position]]:
        """Get all valid moves for a given color."""
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if piece and piece.color == color:
                    valid_moves = piece.get_valid_moves(self)
                    moves.extend([(Position(row, col), move) for move in valid_moves])
        return moves

    def make_computer_move(self, color: PieceColor, depth: int = 3) -> bool:
        """Make a move for the computer using minimax with alpha-beta pruning."""
        best_score = float('-inf') if color == PieceColor.WHITE else float('inf')
        best_move = None
        
        valid_moves = self.get_all_valid_moves(color)
        if not valid_moves:
            return False
            
        for from_pos, to_pos in valid_moves:
            # Try move
            piece = self.squares[from_pos.row][from_pos.col]
            captured = self.squares[to_pos.row][to_pos.col]
            self.squares[to_pos.row][to_pos.col] = piece
            self.squares[from_pos.row][from_pos.col] = None
            
            # Evaluate position
            score = self.minimax(depth - 1, float('-inf'), float('inf'), color != PieceColor.WHITE)
            
            # Undo move
            self.squares[from_pos.row][from_pos.col] = piece
            self.squares[to_pos.row][to_pos.col] = captured
            
            # Update best move
            if color == PieceColor.WHITE and score > best_score:
                best_score = score
                best_move = (from_pos, to_pos)
            elif color == PieceColor.BLACK and score < best_score:
                best_score = score
                best_move = (from_pos, to_pos)
        
        if best_move:
            success, _ = self.move_piece(best_move[0], best_move[1])
            return success
        return False

    def minimax(self, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """Minimax algorithm with alpha-beta pruning."""
        if depth == 0:
            return self.evaluate_position()
            
        if maximizing:
            max_eval = float('-inf')
            for from_pos, to_pos in self.get_all_valid_moves(PieceColor.WHITE):
                piece = self.squares[from_pos.row][from_pos.col]
                captured = self.squares[to_pos.row][to_pos.col]
                self.squares[to_pos.row][to_pos.col] = piece
                self.squares[from_pos.row][from_pos.col] = None
                
                eval = self.minimax(depth - 1, alpha, beta, False)
                
                self.squares[from_pos.row][from_pos.col] = piece
                self.squares[to_pos.row][to_pos.col] = captured
                
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for from_pos, to_pos in self.get_all_valid_moves(PieceColor.BLACK):
                piece = self.squares[from_pos.row][from_pos.col]
                captured = self.squares[to_pos.row][to_pos.col]
                self.squares[to_pos.row][to_pos.col] = piece
                self.squares[from_pos.row][from_pos.col] = None
                
                eval = self.minimax(depth - 1, alpha, beta, True)
                
                self.squares[from_pos.row][from_pos.col] = piece
                self.squares[to_pos.row][to_pos.col] = captured
                
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def is_king_in_check(self, color: PieceColor) -> bool:
        """Check if the king of given color is in check."""
        # Find king position
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if (piece and piece.piece_type == PieceType.KING 
                    and piece.color == color):
                    king_pos = Position(row, col)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False  # Should never happen in a valid game
        
        # Check if any opponent piece can capture the king
        opponent_color = (PieceColor.BLACK if color == PieceColor.WHITE 
                         else PieceColor.WHITE)
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if piece and piece.color == opponent_color:
                    if king_pos in piece.get_valid_moves(self):
                        return True
        return False

    def is_checkmate(self, color: PieceColor) -> bool:
        """Check if the given color is in checkmate."""
        if not self.is_king_in_check(color):
            return False
            
        # Try all possible moves for all pieces
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if piece and piece.color == color:
                    from_pos = Position(row, col)
                    for to_pos in piece.get_valid_moves(self):
                        # Try the move
                        captured_piece = self.squares[to_pos.row][to_pos.col]
                        self.squares[to_pos.row][to_pos.col] = piece
                        self.squares[from_pos.row][from_pos.col] = None
                        
                        # Check if still in check
                        still_in_check = self.is_king_in_check(color)
                        
                        # Undo the move
                        self.squares[from_pos.row][from_pos.col] = piece
                        self.squares[to_pos.row][to_pos.col] = captured_piece
                        
                        if not still_in_check:
                            return False  # Found a legal move
        
        return True  # No legal moves found

    def is_stalemate(self, color: PieceColor) -> bool:
        """Check if the given color is in stalemate."""
        if self.is_king_in_check(color):
            return False
            
        # Check if any piece has valid moves
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if piece and piece.color == color:
                    from_pos = Position(row, col)
                    for to_pos in piece.get_valid_moves(self):
                        # Try the move
                        captured_piece = self.squares[to_pos.row][to_pos.col]
                        self.squares[to_pos.row][to_pos.col] = piece
                        self.squares[from_pos.row][from_pos.col] = None
                        
                        # Check if move puts king in check
                        in_check = self.is_king_in_check(color)
                        
                        # Undo the move
                        self.squares[from_pos.row][from_pos.col] = piece
                        self.squares[to_pos.row][to_pos.col] = captured_piece
                        
                        if not in_check:
                            return False  # Found a legal move
        
        return True  # No legal moves found

    def display(self):
        # Clear screen before drawing
        clear_screen()
        
        print("\n   a b c d e f g h")
        print("   ---------------")
        for row in range(8):
            print(f"{8 - row} |", end=" ")
            for col in range(8):
                piece = self.squares[row][col]
                bg_color = Back.WHITE if (row + col) % 2 == 0 else Back.BLACK
                if piece:
                    print(f"{bg_color}{piece}{Style.RESET_ALL}", end=" ")
                else:
                    print(f"{bg_color} {Style.RESET_ALL}", end=" ")
            print(f"| {8 - row}")
        print("   ---------------")
        print("   a b c d e f g h")

    def evaluate_position(self) -> float:
        """Evaluate the current board position from white's perspective."""
        score = 0.0
        
        # Piece values and positions
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if not piece:
                    continue
                    
                piece_value = piece.piece_type.value_score
                position_bonus = self._get_position_bonus(piece, row, col)
                
                if piece.color == PieceColor.WHITE:
                    score += piece_value + position_bonus
                else:
                    score -= piece_value + position_bonus
                    
        return score

    def _get_position_bonus(self, piece: Piece, row: int, col: int) -> float:
        """Calculate position bonus based on piece type and position."""
        bonus = 0.0
        
        # Pawns are more valuable as they advance
        if piece.piece_type == PieceType.PAWN:
            if piece.color == PieceColor.WHITE:
                bonus = (7 - row) * 0.1  # Bonus for advancing
            else:
                bonus = row * 0.1
        
        # Control of center squares
        if 2 <= row <= 5 and 2 <= col <= 5:
            bonus += 0.2
            
        # Knights are better near the center
        if piece.piece_type == PieceType.KNIGHT:
            distance_from_center = abs(3.5 - row) + abs(3.5 - col)
            bonus += (8 - distance_from_center) * 0.1
            
        return bonus

    def play_computer_vs_computer(self, max_moves: int = 50, delay: float = 1.0):
        """Simulate a game between two computer players."""
        import time
        
        move_count = 0
        while move_count < max_moves:
            self.display()
            time.sleep(delay)
            
            # Check for game end conditions
            if self.is_checkmate(self.current_player):
                winner = "Black" if self.current_player == PieceColor.WHITE else "White"
                print(f"\nCheckmate! {winner} wins!")
                break
            elif self.is_stalemate(self.current_player):
                print("\nStalemate! Game is a draw.")
                break
                
            # Make computer move
            if not self.make_computer_move(self.current_player):
                print(f"\nNo valid moves for {self.current_player.value}. Game over!")
                break
                
            move_count += 1
            
        if move_count >= max_moves:
            print("\nGame ended due to move limit.")
            
        self.display()  # Show final position

class Game:
    def __init__(self):
        self.board = Board()

    def show_menu(self) -> str:
        """Display game mode menu and return selected mode."""
        clear_screen()
        print("\nWelcome to CLI Chess!")
        print("\nSelect game mode:")
        print("1. Player vs Player")
        print("2. Player vs Computer (play as White)")
        print("3. Player vs Computer (play as Black)")
        print("4. Computer vs Computer")
        print("5. Quit")

        while True:
            try:
                choice = input("\nEnter your choice (1-5): ").strip()
                if choice == "1":
                    return "human"
                elif choice == "2":
                    return "white"
                elif choice == "3":
                    return "black"
                elif choice == "4":
                    return "computer"
                elif choice == "5":
                    return "quit"
                else:
                    print("Invalid choice. Please enter 1-5.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def play(self):
        """Main game loop with menu selection."""
        while True:
            mode = self.show_menu()
            
            if mode == "quit":
                clear_screen()
                print("Thanks for playing!")
                break
                
            clear_screen()
            if mode == "computer":
                print("\nComputer vs Computer match")
                print("Press Ctrl+C to stop the game")
                input("Press Enter to start...")
                self.board = Board()  # Reset board
                self.board.play_computer_vs_computer()
            elif mode in ["white", "black"]:
                computer_color = PieceColor.BLACK if mode == "white" else PieceColor.WHITE
                print(f"\nPlaying as {'White' if mode == 'white' else 'Black'}")
                print("Enter moves in algebraic notation (e.g., 'e2 e4')")
                print("Type 'quit' to return to menu")
                input("Press Enter to start...")
                self.board = Board()  # Reset board
                self.play_vs_computer(computer_color)
            else:  # human vs human
                print("\nPlayer vs Player match")
                print("Enter moves in algebraic notation (e.g., 'e2 e4')")
                print("Type 'quit' to return to menu")
                input("Press Enter to start...")
                self.board = Board()  # Reset board
                self.play_human()

    def play_human(self):
        """Human vs Human game mode."""
        while True:
            self.board.display()
            
            try:
                move = input(f"\n{self.board.current_player.value}'s move (e.g., e2 e4): ").strip().lower()
                if move == "quit":
                    break
                    
                from_sq, to_sq = move.split()
                from_pos = Position(8 - int(from_sq[1]), ord(from_sq[0]) - ord('a'))
                to_pos = Position(8 - int(to_sq[1]), ord(to_sq[0]) - ord('a'))
                
                success, error = self.board.move_piece(from_pos, to_pos)
                if not success:
                    print(f"Invalid move: {error}")
                    input("Press Enter to continue...")
                    continue
                    
                if self.board.is_checkmate(self.board.current_player):
                    self.board.display()
                    winner = "Black" if self.board.current_player == PieceColor.WHITE else "White"
                    print(f"\nCheckmate! {winner} wins!")
                    input("\nPress Enter to return to menu...")
                    break
                elif self.board.is_stalemate(self.board.current_player):
                    self.board.display()
                    print("\nStalemate! Game is a draw.")
                    input("\nPress Enter to return to menu...")
                    break
                    
            except (ValueError, IndexError):
                print("Invalid input format. Use 'e2 e4' format or 'quit' to return to menu.")
                input("Press Enter to continue...")

    def play_vs_computer(self, computer_color: PieceColor):
        """Human vs Computer game mode."""
        while True:
            self.board.display()
            
            if self.board.current_player == computer_color:
                print("\nComputer is thinking...")
                if not self.board.make_computer_move(computer_color):
                    print("\nNo valid moves for computer. Game over!")
                    input("\nPress Enter to return to menu...")
                    break
            else:
                try:
                    move = input(f"\nYour move (e.g., e2 e4): ").strip().lower()
                    if move == "quit":
                        break
                        
                    from_sq, to_sq = move.split()
                    from_pos = Position(8 - int(from_sq[1]), ord(from_sq[0]) - ord('a'))
                    to_pos = Position(8 - int(to_sq[1]), ord(to_sq[0]) - ord('a'))
                    
                    success, error = self.board.move_piece(from_pos, to_pos)
                    if not success:
                        print(f"Invalid move: {error}")
                        input("Press Enter to continue...")
                        continue
                        
                except (ValueError, IndexError):
                    print("Invalid input format. Use 'e2 e4' format or 'quit' to return to menu.")
                    input("Press Enter to continue...")
                    continue
                    
            if self.board.is_checkmate(self.board.current_player):
                self.board.display()
                winner = "Black" if self.board.current_player == PieceColor.WHITE else "White"
                print(f"\nCheckmate! {winner} wins!")
                input("\nPress Enter to return to menu...")
                break
            elif self.board.is_stalemate(self.board.current_player):
                self.board.display()
                print("\nStalemate! Game is a draw.")
                input("\nPress Enter to return to menu...")
                break

if __name__ == "__main__":
    game = Game()
    game.play()
