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
        if self.piece_type == PieceType.PAWN:
            moves.extend(self._get_pawn_moves(board))
        elif self.piece_type == PieceType.ROOK:
            moves.extend(self._get_rook_moves(board))
        elif self.piece_type == PieceType.KNIGHT:
            moves.extend(self._get_knight_moves(board))
        elif self.piece_type == PieceType.BISHOP:
            moves.extend(self._get_bishop_moves(board))
        elif self.piece_type == PieceType.QUEEN:
            moves.extend(self._get_queen_moves(board))
        elif self.piece_type == PieceType.KING:
            moves.extend(self._get_king_moves(board))
        return [move for move in moves if move.is_valid()]

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

    def move_piece(self, from_pos: Position, to_pos: Position) -> bool:
        """Move a piece and return True if the move was valid."""
        piece = self.squares[from_pos.row][from_pos.col]
        if not piece:
            return False
            
        # Check if move is valid
        if to_pos not in piece.get_valid_moves(self):
            return False
            
        # Try the move
        captured_piece = self.squares[to_pos.row][to_pos.col]
        self.squares[to_pos.row][to_pos.col] = piece
        self.squares[from_pos.row][from_pos.col] = None
        
        # Check if move puts own king in check
        if self.is_king_in_check(piece.color):
            # Undo the move
            self.squares[from_pos.row][from_pos.col] = piece
            self.squares[to_pos.row][to_pos.col] = captured_piece
            return False
            
        piece.has_moved = True
        return True

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

    def get_all_valid_moves(self, color: PieceColor) -> List[Tuple[Position, Position]]:
        """Get all valid moves for a given color."""
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if piece and piece.color == color:
                    valid_moves = piece.get_valid_moves(self)
                    moves.extend([(piece.position, move) for move in valid_moves])
        return moves

    def clone(self) -> 'Board':
        """Create a deep copy of the board for move simulation."""
        new_board = Board()
        new_board.squares = [[None for _ in range(8)] for _ in range(8)]
        
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if piece:
                    new_pos = Position(row, col)
                    new_piece = Piece(piece.piece_type, piece.color, new_pos)
                    new_piece.has_moved = piece.has_moved
                    new_board.squares[row][col] = new_piece
                    
        return new_board

class SystemPlayer:
    def __init__(self, color: PieceColor, difficulty: int = 2):
        self.color = color
        self.difficulty = difficulty  # Search depth

    def get_move(self, board: Board) -> Tuple[Position, Position]:
        """Get the best move for the system player."""
        best_score = float('-inf') if self.color == PieceColor.WHITE else float('inf')
        best_move = None
        
        valid_moves = board.get_all_valid_moves(self.color)
        random.shuffle(valid_moves)  # Add some randomization to equal-valued moves
        
        for from_pos, to_pos in valid_moves:
            # Create a copy of the board to simulate the move
            temp_board = board.clone()
            temp_board.move_piece(from_pos, to_pos)
            
            # Evaluate the move
            if self.difficulty <= 1:
                score = temp_board.evaluate_position()
            else:
                score = self._minimax(temp_board, self.difficulty - 1, 
                                   float('-inf'), float('inf'),
                                   self.color != PieceColor.WHITE)
            
            # Update best move
            if self.color == PieceColor.WHITE:
                if score > best_score:
                    best_score = score
                    best_move = (from_pos, to_pos)
            else:
                if score < best_score:
                    best_score = score
                    best_move = (from_pos, to_pos)
        
        return best_move

    def _minimax(self, board: Board, depth: int, alpha: float, beta: float, 
                is_maximizing: bool) -> float:
        """Minimax algorithm with alpha-beta pruning."""
        if depth == 0:
            return board.evaluate_position()
            
        color = PieceColor.WHITE if is_maximizing else PieceColor.BLACK
        valid_moves = board.get_all_valid_moves(color)
        
        if not valid_moves:  # No valid moves available
            return float('-inf') if is_maximizing else float('inf')
            
        if is_maximizing:
            max_eval = float('-inf')
            for from_pos, to_pos in valid_moves:
                temp_board = board.clone()
                temp_board.move_piece(from_pos, to_pos)
                eval = self._minimax(temp_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for from_pos, to_pos in valid_moves:
                temp_board = board.clone()
                temp_board.move_piece(from_pos, to_pos)
                eval = self._minimax(temp_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

class ChessGame:
    def __init__(self):
        self.board = Board()
        self.current_player = PieceColor.WHITE
        self.game_over = False
        self.system_player = None

    def _get_game_mode(self) -> Optional[PieceColor]:
        """Get the game mode from user input."""
        clear_screen()
        print("Welcome to CLI Chess!")
        print("\nSelect game mode:")
        print("1. Player vs Player")
        print("2. Player vs System (you play White)")
        print("3. Player vs System (you play Black)")
        print("4. Quit")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-4): ").strip()
                if choice == "1":
                    return None
                elif choice == "2":
                    return PieceColor.BLACK
                elif choice == "3":
                    return PieceColor.WHITE
                elif choice == "4":
                    self.game_over = True
                    return None
                else:
                    print("Invalid choice. Please enter 1-4.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def play(self):
        # Get game mode
        system_color = self._get_game_mode()
        if self.game_over:
            clear_screen()
            print("Thanks for playing!")
            return
            
        if system_color:
            self.system_player = SystemPlayer(system_color)
            print(f"\nPlaying against system (Difficulty: {self.system_player.difficulty})")
        
        print("\nPress Enter to start...")
        input()
        
        while not self.game_over:
            self.board.display()
            print(f"\n{self.current_player.value}'s turn")
            
            # System player's turn
            if self.system_player and self.system_player.color == self.current_player:
                print("System is thinking...")
                from_pos, to_pos = self.system_player.get_move(self.board)
                self.board.move_piece(from_pos, to_pos)
                print(f"System moved: {from_pos.to_algebraic()} {to_pos.to_algebraic()}")
                self.current_player = (
                    PieceColor.BLACK if self.current_player == PieceColor.WHITE 
                    else PieceColor.WHITE
                )
                continue
            
            # Human player's turn
            move = input("Enter your move: ").strip().lower()
            
            if move == 'quit':
                clear_screen()
                print("Thanks for playing!")
                break
            elif move == 'help':
                self._show_help()
                input("\nPress Enter to continue...")
                continue
                
            try:
                from_pos, to_pos = self._parse_move(move)
                if self._make_move(from_pos, to_pos):
                    self.current_player = (
                        PieceColor.BLACK if self.current_player == PieceColor.WHITE 
                        else PieceColor.WHITE
                    )
                else:
                    print("Invalid move! Try again.")
                    input("\nPress Enter to continue...")
            except ValueError as e:
                print(f"Error: {e}")
                input("\nPress Enter to continue...")
                
    def _parse_move(self, move: str) -> Tuple[Position, Position]:
        parts = move.split()
        if len(parts) != 2:
            raise ValueError("Invalid move format. Use 'e2 e4' format.")
            
        try:
            from_pos = Position.from_algebraic(parts[0])
            to_pos = Position.from_algebraic(parts[1])
            return from_pos, to_pos
        except (IndexError, ValueError):
            raise ValueError("Invalid position notation.")

    def _make_move(self, from_pos: Position, to_pos: Position) -> bool:
        piece = self.board.get_piece(from_pos)
        if not piece:
            print("No piece at starting position!")
            return False
            
        if piece.color != self.current_player:
            print("That's not your piece!")
            return False
            
        # Check if move is valid and doesn't leave/put king in check
        if not self.board.move_piece(from_pos, to_pos):
            if self.board.is_king_in_check(self.current_player):
                print("Invalid move! Your king is in check.")
            else:
                print("Invalid move!")
            return False
            
        # Check if move puts opponent in check/checkmate
        opponent_color = (PieceColor.BLACK if self.current_player == PieceColor.WHITE 
                         else PieceColor.WHITE)
        
        if self.board.is_checkmate(opponent_color):
            self.board.display()
            print(f"\nCheckmate! {self.current_player.value} wins!")
            self.game_over = True
        elif self.board.is_king_in_check(opponent_color):
            print(f"\n{opponent_color.value} is in check!")
        elif self.board.is_stalemate(opponent_color):
            self.board.display()
            print("\nStalemate! Game is a draw.")
            self.game_over = True
            
        return True

    def _show_help(self):
        print("\nGame Controls:")
        print("- Enter moves in algebraic notation (e.g., 'e2 e4')")
        print("- Type 'quit' to exit the game")
        print("- Type 'help' to see this message again")

if __name__ == "__main__":
    game = ChessGame()
    game.play()
