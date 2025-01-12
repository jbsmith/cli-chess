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
    # Using simple ASCII characters
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
        color = Fore.BLUE if self.color == PieceColor.WHITE else Fore.RED
        # Compact piece display
        return f"{color}{symbol}"

    def get_valid_moves(self, board: 'Board') -> List[Position]:
        moves = []
        if self.piece_type == PieceType.PAWN:
            # Forward moves
            direction = -1 if self.color == PieceColor.WHITE else 1
            forward = Position(self.position.row + direction, self.position.col)
            if forward.is_valid() and not board.get_piece(forward):
                moves.append(forward)
                # Initial two-square move
                if not self.has_moved:
                    double_forward = Position(self.position.row + 2 * direction, self.position.col)
                    if double_forward.is_valid() and not board.get_piece(double_forward):
                        moves.append(double_forward)
            
            # Diagonal captures
            for col_offset in [-1, 1]:
                capture_pos = Position(self.position.row + direction, self.position.col + col_offset)
                if capture_pos.is_valid():
                    piece = board.get_piece(capture_pos)
                    if piece and piece.color != self.color:
                        moves.append(capture_pos)
                    
                    # En passant
                    if board.last_pawn_move:
                        last_from, last_to = board.last_pawn_move
                        if (last_to.row == self.position.row and  # Same rank
                            abs(last_to.col - self.position.col) == 1 and  # Adjacent file
                            abs(last_from.row - last_to.row) == 2):  # Was a double move
                            # The capture square for en passant
                            en_passant_pos = Position(last_to.row + direction, last_to.col)
                            moves.append(en_passant_pos)
        
        elif self.piece_type == PieceType.KNIGHT:
            # Knight moves in L-shape
            knight_moves = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            for dr, dc in knight_moves:
                new_row, new_col = self.position.row + dr, self.position.col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target_piece = board.squares[new_row][new_col]
                    if not target_piece or target_piece.color != self.color:
                        moves.append(Position(new_row, new_col))
                        
        elif self.piece_type == PieceType.BISHOP:
            # Bishop moves diagonally
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                new_row, new_col = self.position.row + dr, self.position.col + dc
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
                new_row, new_col = self.position.row + dr, self.position.col + dc
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
                new_row, new_col = self.position.row + dr, self.position.col + dc
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
                new_row, new_col = self.position.row + dr, self.position.col + dc
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
        self.move_history = []  # List of tuples (from_pos, to_pos, piece_type, color, san_move)
        
    def _can_promote_pawn(self, piece: Piece, to_pos: Position) -> bool:
        """Check if a pawn can be promoted."""
        if piece.piece_type != PieceType.PAWN:
            return False
        return ((piece.color == PieceColor.WHITE and to_pos.row == 0) or
                (piece.color == PieceColor.BLACK and to_pos.row == 7))

    def _promote_pawn(self, piece: Piece, promotion_type: PieceType) -> None:
        """Promote a pawn to the specified piece type."""
        allowed_promotions = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]
        if promotion_type not in allowed_promotions:
            promotion_type = PieceType.QUEEN  # Default to queen if invalid
        piece.piece_type = promotion_type

    def get_piece(self, position: Position) -> Optional[Piece]:
        if position.is_valid():
            return self.squares[position.row][position.col]
        return None

    def _get_san_move(self, from_pos: Position, to_pos: Position, piece: Piece, captured_piece: Optional[Piece] = None) -> str:
        """Generate Standard Algebraic Notation (SAN) for a move."""
        # Basic move
        piece_letter = "" if piece.piece_type == PieceType.PAWN else piece.piece_type.value
        move_str = ""
        
        # Handle pawn captures
        if piece.piece_type == PieceType.PAWN and from_pos.col != to_pos.col:
            move_str = f"{chr(97 + from_pos.col)}x"
        # Handle other captures
        elif captured_piece:
            move_str = f"{piece_letter}x"
        else:
            move_str = piece_letter
            
        # Add disambiguation if needed
        if piece.piece_type != PieceType.PAWN:
            similar_pieces = []
            for row in range(8):
                for col in range(8):
                    other_piece = self.squares[row][col]
                    if (other_piece and other_piece != piece and 
                        other_piece.piece_type == piece.piece_type and
                        other_piece.color == piece.color):
                        other_moves = other_piece.get_valid_moves(self)
                        if to_pos in other_moves:
                            similar_pieces.append(Position(row, col))
            
            if similar_pieces:
                # First try just file
                if all(p.col != from_pos.col for p in similar_pieces):
                    move_str += chr(97 + from_pos.col)
                # Then try just rank
                elif all(p.row != from_pos.row for p in similar_pieces):
                    move_str += str(8 - from_pos.row)
                # Finally use both
                else:
                    move_str += f"{chr(97 + from_pos.col)}{8 - from_pos.row}"
        
        # Add destination square
        move_str += f"{chr(97 + to_pos.col)}{8 - to_pos.row}"
        
        # Test the move for check/checkmate
        self.squares[to_pos.row][to_pos.col] = piece
        self.squares[from_pos.row][from_pos.col] = None
        
        opponent_color = PieceColor.BLACK if piece.color == PieceColor.WHITE else PieceColor.WHITE
        if self.is_checkmate(opponent_color):
            move_str += "#"
        elif self.is_king_in_check(opponent_color):
            move_str += "+"
            
        # Undo the test move
        self.squares[from_pos.row][from_pos.col] = piece
        self.squares[to_pos.row][to_pos.col] = captured_piece
        
        return move_str

    def move_piece(self, from_pos: Position, to_pos: Position, promotion_type: Optional[PieceType] = None) -> Tuple[bool, Optional[str]]:
        """Move a piece and return (success, error_message)."""
        piece = self.squares[from_pos.row][from_pos.col]
        if not piece:
            return False, "No piece at starting position"
            
        # Check if move is in piece's valid moves
        valid_moves = piece.get_valid_moves(self)
        if to_pos not in valid_moves:
            return False, "Invalid move for this piece"
            
        # Handle en passant capture
        captured_piece = self.squares[to_pos.row][to_pos.col]
        if (piece.piece_type == PieceType.PAWN and 
            self.last_pawn_move and 
            to_pos.col != from_pos.col and 
            not captured_piece):
            # This is an en passant capture
            if self.last_pawn_move:  # Check if last_pawn_move exists
                last_from, last_to = self.last_pawn_move
                if last_to.col == to_pos.col:
                    captured_piece = self.squares[last_to.row][last_to.col]
                    self.squares[last_to.row][last_to.col] = None
            
        # Generate SAN before making the move
        san_move = self._get_san_move(from_pos, to_pos, piece, captured_piece)
        
        # Make the move
        self.squares[to_pos.row][to_pos.col] = piece
        self.squares[from_pos.row][from_pos.col] = None
        
        # Check if the move puts own king in check
        if self.is_king_in_check(piece.color):
            # Undo the move
            self.squares[from_pos.row][from_pos.col] = piece
            self.squares[to_pos.row][to_pos.col] = captured_piece
            if captured_piece and piece.piece_type == PieceType.PAWN and self.last_pawn_move:  # Restore en passant captured piece
                last_from, last_to = self.last_pawn_move
                self.squares[last_to.row][last_to.col] = captured_piece
            return False, "Move would leave your king in check"
            
        # Handle pawn promotion
        if self._can_promote_pawn(piece, to_pos):
            self._promote_pawn(piece, promotion_type)
            # Update SAN with promotion piece
            if promotion_type:
                san_move += f"={promotion_type.value}"
            
        # Update piece's internal position and move history
        piece.position = to_pos
        piece.has_moved = True
        
        # Update last pawn move for en passant
        if piece.piece_type == PieceType.PAWN and abs(from_pos.row - to_pos.row) == 2:
            self.last_pawn_move = (from_pos, to_pos)
        else:
            self.last_pawn_move = None
            
        # Record the move in history
        self.move_history.append((from_pos, to_pos, piece.piece_type, piece.color, san_move))
        
        return True, None

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
                        old_pos = piece.position
                        
                        # Make the move
                        self.squares[to_pos.row][to_pos.col] = piece
                        self.squares[from_pos.row][from_pos.col] = None
                        piece.position = to_pos  # Update piece's internal position
                        
                        # Check if still in check
                        still_in_check = self.is_king_in_check(color)
                        
                        # Undo the move
                        self.squares[from_pos.row][from_pos.col] = piece
                        self.squares[to_pos.row][to_pos.col] = captured_piece
                        piece.position = old_pos  # Restore piece's original position
                        
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
        move_index = len(self.move_history) - 1  # Start from the last move
        moves_displayed = 0
        max_moves_to_show = 72
        
        # Board border and coordinate styling
        border_color = Style.BRIGHT + Fore.YELLOW
        coord_color = Style.BRIGHT + Fore.CYAN
        
        # Define custom backgrounds for squares
        light_square = "\033[48;5;238m"  # Darker gray for "white" squares
        dark_square = Back.BLACK
        
        # Calculate the width needed for the move history
        move_history_width = 20
        
        print("\n")  # Extra spacing at top
        
        # Column coordinates at top with space for move history
        print("        ", end="")
        for col in range(8):
            print(f"{coord_color}{chr(97 + col)}   {Style.RESET_ALL}", end="  ")
        print(" " * 4 + "Move History")
        
        # Top border with space for move history
        print("     ", end="")
        print(f"{border_color}+-----+-----+-----+-----+-----+-----+-----+-----+{Style.RESET_ALL}", end="")
        
        # Display move history entry
        if move_index >= 0 and moves_displayed < max_moves_to_show:
            _, _, _, color, san_move = self.move_history[move_index]
            move_number = (move_index + 2) // 2
            if color == PieceColor.WHITE:
                move_str = f"{move_number}. {san_move}"
            else:
                move_str = f"{move_number}... {san_move}"
            print(f"    {move_str:<14}", end="")
            move_index -= 1
            moves_displayed += 1
        print()
        
        # Board squares
        for row in range(8):
            # First line of square (empty)
            print("     ", end="")
            print(f"{border_color}|{Style.RESET_ALL}", end="")
            for col in range(8):
                # In chess, a1 (bottom-left) is dark, so we flip the pattern
                bg_color = dark_square if (row + col) % 2 == 0 else light_square
                print(f"{bg_color}     {Style.RESET_ALL}{border_color}|{Style.RESET_ALL}", end="")
            
            # Display move history entry
            if move_index >= 0 and moves_displayed < max_moves_to_show:
                _, _, _, color, san_move = self.move_history[move_index]
                move_number = (move_index + 2) // 2
                if color == PieceColor.WHITE:
                    move_str = f"{move_number}. {san_move}"
                else:
                    move_str = f"{move_number}... {san_move}"
                print(f"    {move_str:<14}", end="")
                move_index -= 1
                moves_displayed += 1
            print()
            
            # Middle line of square (with piece)
            print(f" {coord_color}{8 - row}   {Style.RESET_ALL}", end="")
            print(f"{border_color}|{Style.RESET_ALL}", end="")
            
            for col in range(8):
                piece = self.squares[row][col]
                # In chess, a1 (bottom-left) is dark, so we flip the pattern
                bg_color = dark_square if (row + col) % 2 == 0 else light_square
                if piece:
                    # Keep background color consistent across the entire square
                    print(f"{bg_color}  {piece}  {Style.RESET_ALL}{border_color}|{Style.RESET_ALL}", end="")
                else:
                    print(f"{bg_color}     {Style.RESET_ALL}{border_color}|{Style.RESET_ALL}", end="")
            
            # Display move history entry
            if move_index >= 0 and moves_displayed < max_moves_to_show:
                _, _, _, color, san_move = self.move_history[move_index]
                move_number = (move_index + 2) // 2
                if color == PieceColor.WHITE:
                    move_str = f"{move_number}. {san_move}"
                else:
                    move_str = f"{move_number}... {san_move}"
                print(f"    {move_str:<14}", end="")
                move_index -= 1
                moves_displayed += 1
            print()
            
            # Bottom line of square (empty)
            print("     ", end="")
            print(f"{border_color}|{Style.RESET_ALL}", end="")
            for col in range(8):
                # In chess, a1 (bottom-left) is dark, so we flip the pattern
                bg_color = dark_square if (row + col) % 2 == 0 else light_square
                print(f"{bg_color}     {Style.RESET_ALL}{border_color}|{Style.RESET_ALL}", end="")
            
            # Display move history entry
            if move_index >= 0 and moves_displayed < max_moves_to_show:
                _, _, _, color, san_move = self.move_history[move_index]
                move_number = (move_index + 2) // 2
                if color == PieceColor.WHITE:
                    move_str = f"{move_number}. {san_move}"
                else:
                    move_str = f"{move_number}... {san_move}"
                print(f"    {move_str:<14}", end="")
                move_index -= 1
                moves_displayed += 1
            print()
            
            # Horizontal line between rows
            print("     ", end="")
            print(f"{border_color}+-----+-----+-----+-----+-----+-----+-----+-----+{Style.RESET_ALL}", end="")
            
            # Display move history entry on separator line
            if move_index >= 0 and moves_displayed < max_moves_to_show:
                _, _, _, color, san_move = self.move_history[move_index]
                move_number = (move_index + 2) // 2
                if color == PieceColor.WHITE:
                    move_str = f"{move_number}. {san_move}"
                else:
                    move_str = f"{move_number}... {san_move}"
                print(f"    {move_str:<14}", end="")
                move_index -= 1
                moves_displayed += 1
            print()
        
        # Column coordinates at bottom
        print("        ", end="")
        for col in range(8):
            print(f"{coord_color}{chr(97 + col)}   {Style.RESET_ALL}", end="  ")
        print("\n")

    def evaluate_position(self) -> float:
        """Evaluate the current board position from white's perspective."""
        score = 0.0
        
        # Track queens for both sides
        white_has_queen = False
        black_has_queen = False
        
        # Piece values and positions
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if not piece:
                    continue
                    
                # Track queens
                if piece.piece_type == PieceType.QUEEN:
                    if piece.color == PieceColor.WHITE:
                        white_has_queen = True
                    else:
                        black_has_queen = True
                
                piece_value = piece.piece_type.value_score
                position_bonus = self._get_position_bonus(piece, row, col)
                
                if piece.color == PieceColor.WHITE:
                    score += piece_value + position_bonus
                else:
                    score -= piece_value + position_bonus
        
        # Apply queen retention bonus
        queen_retention_bonus = 3.0  # Additional bonus for keeping the queen
        if white_has_queen:
            score += queen_retention_bonus
        if black_has_queen:
            score -= queen_retention_bonus
                    
        return score

    def _get_position_bonus(self, piece: Piece, row: int, col: int) -> float:
        """Calculate position bonus based on piece type and position."""
        bonus = 0.0
        
        # Pawns are more valuable as they advance
        if piece.piece_type == PieceType.PAWN:
            if piece.color == PieceColor.WHITE:
                bonus = (7 - row) * 0.1  # Bonus for advancing
                # Extra bonus for being close to promotion
                if row <= 2:  # Within 3 rows of promotion
                    bonus += (2 - row) * 0.2
            else:
                bonus = row * 0.1
                # Extra bonus for being close to promotion
                if row >= 5:  # Within 3 rows of promotion
                    bonus += (row - 5) * 0.2
        
        # Control of center squares
        if 2 <= row <= 5 and 2 <= col <= 5:
            bonus += 0.2
            # Extra bonus for queens in the center
            if piece.piece_type == PieceType.QUEEN:
                bonus += 0.3
            
        # Knights are better near the center
        if piece.piece_type == PieceType.KNIGHT:
            distance_from_center = abs(3.5 - row) + abs(3.5 - col)
            bonus += (8 - distance_from_center) * 0.1
            
        # Queen positioning
        if piece.piece_type == PieceType.QUEEN:
            # Penalize early queen development slightly
            if (piece.color == PieceColor.WHITE and row == 7) or \
               (piece.color == PieceColor.BLACK and row == 0):
                bonus -= 0.4
            
            # Bonus for queen mobility (more squares to move to)
            mobility_bonus = len(piece.get_valid_moves(self)) * 0.05
            bonus += mobility_bonus
            
            # Penalize exposed queen positions
            if row == 0 or row == 7 or col == 0 or col == 7:
                bonus -= 0.2
            
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

    def _setup_board(self):
        # Setup white pieces
        # Back row
        self.squares[7][0] = Piece(PieceType.ROOK, PieceColor.WHITE, Position(7, 0))
        self.squares[7][1] = Piece(PieceType.KNIGHT, PieceColor.WHITE, Position(7, 1))
        self.squares[7][2] = Piece(PieceType.BISHOP, PieceColor.WHITE, Position(7, 2))
        self.squares[7][3] = Piece(PieceType.QUEEN, PieceColor.WHITE, Position(7, 3))  # d1
        self.squares[7][4] = Piece(PieceType.KING, PieceColor.WHITE, Position(7, 4))   # e1
        self.squares[7][5] = Piece(PieceType.BISHOP, PieceColor.WHITE, Position(7, 5))
        self.squares[7][6] = Piece(PieceType.KNIGHT, PieceColor.WHITE, Position(7, 6))
        self.squares[7][7] = Piece(PieceType.ROOK, PieceColor.WHITE, Position(7, 7))
        # Pawns
        for col in range(8):
            self.squares[6][col] = Piece(PieceType.PAWN, PieceColor.WHITE, Position(6, col))

        # Setup black pieces
        # Back row
        self.squares[0][0] = Piece(PieceType.ROOK, PieceColor.BLACK, Position(0, 0))
        self.squares[0][1] = Piece(PieceType.KNIGHT, PieceColor.BLACK, Position(0, 1))
        self.squares[0][2] = Piece(PieceType.BISHOP, PieceColor.BLACK, Position(0, 2))
        self.squares[0][3] = Piece(PieceType.QUEEN, PieceColor.BLACK, Position(0, 3))  # d8
        self.squares[0][4] = Piece(PieceType.KING, PieceColor.BLACK, Position(0, 4))   # e8
        self.squares[0][5] = Piece(PieceType.BISHOP, PieceColor.BLACK, Position(0, 5))
        self.squares[0][6] = Piece(PieceType.KNIGHT, PieceColor.BLACK, Position(0, 6))
        self.squares[0][7] = Piece(PieceType.ROOK, PieceColor.BLACK, Position(0, 7))
        # Pawns
        for col in range(8):
            self.squares[1][col] = Piece(PieceType.PAWN, PieceColor.BLACK, Position(1, col))

class SystemPlayer:
    def __init__(self, color: PieceColor, difficulty: int = 2):
        self.color = color
        self.difficulty = difficulty  # Search depth

    def _choose_promotion_piece(self, board: Board) -> PieceType:
        """Choose a piece type for pawn promotion. System always chooses queen."""
        return PieceType.QUEEN

    def get_move(self, board: Board) -> Tuple[Position, Position, Optional[PieceType]]:
        """Get the best move for the system player."""
        valid_moves = board.get_all_valid_moves(self.color)
        if not valid_moves:
            return None
            
        # First, look for pawn promotion opportunities
        promotion_moves = []
        for from_pos, to_pos in valid_moves:
            piece = board.get_piece(from_pos)
            if piece and piece.piece_type == PieceType.PAWN:
                # Check if move leads to promotion
                if (self.color == PieceColor.WHITE and to_pos.row == 0) or \
                   (self.color == PieceColor.BLACK and to_pos.row == 7):
                    promotion_moves.append((from_pos, to_pos))
        
        if promotion_moves:
            # Prioritize pawn promotion
            from_pos, to_pos = random.choice(promotion_moves)
            return from_pos, to_pos, self._choose_promotion_piece(board)
            
        # Evaluate moves with minimax if difficulty > 0
        if self.difficulty > 0:
            best_score = float('-inf') if self.color == PieceColor.WHITE else float('inf')
            best_moves = []  # Keep track of all moves with the same best score
            
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
                
                # Update best moves
                if self.color == PieceColor.WHITE:
                    if score > best_score:
                        best_score = score
                        best_moves = [(from_pos, to_pos)]
                    elif score == best_score:
                        best_moves.append((from_pos, to_pos))
                else:
                    if score < best_score:
                        best_score = score
                        best_moves = [(from_pos, to_pos)]
                    elif score == best_score:
                        best_moves.append((from_pos, to_pos))
            
            # If we found good moves, randomly choose one of them
            if best_moves:
                return random.choice(best_moves)
        
        # If no good moves found or difficulty is 0, make a random valid move
        return random.choice(valid_moves)

    def _minimax(self, board: Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """Minimax algorithm with alpha-beta pruning."""
        if depth == 0:
            return self._evaluate_position(board)
            
        valid_moves = board.get_all_valid_moves(
            PieceColor.BLACK if maximizing else PieceColor.WHITE
        )
        
        if not valid_moves:
            # If no valid moves, it's either checkmate or stalemate
            if board.is_king_in_check(PieceColor.BLACK if maximizing else PieceColor.WHITE):
                return float('-inf') if maximizing else float('inf')  # Checkmate
            return 0.0  # Stalemate
            
        if maximizing:
            max_eval = float('-inf')
            for from_pos, to_pos in valid_moves:
                # Create a copy of the board for simulation
                temp_board = board.clone()
                piece = temp_board.get_piece(from_pos)
                
                # Check if this is a pawn promotion move
                promotion_type = None
                if (piece.piece_type == PieceType.PAWN and 
                    ((piece.color == PieceColor.WHITE and to_pos.row == 0) or
                     (piece.color == PieceColor.BLACK and to_pos.row == 7))):
                    promotion_type = PieceType.QUEEN  # Always promote to queen in minimax
                
                # Make the move on the temporary board
                temp_board.move_piece(from_pos, to_pos, promotion_type)
                
                # Recursive evaluation
                eval = self._minimax(temp_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for from_pos, to_pos in valid_moves:
                # Create a copy of the board for simulation
                temp_board = board.clone()
                piece = temp_board.get_piece(from_pos)
                
                # Check if this is a pawn promotion move
                promotion_type = None
                if (piece.piece_type == PieceType.PAWN and 
                    ((piece.color == PieceColor.WHITE and to_pos.row == 0) or
                     (piece.color == PieceColor.BLACK and to_pos.row == 7))):
                    promotion_type = PieceType.QUEEN  # Always promote to queen in minimax
                
                # Make the move on the temporary board
                temp_board.move_piece(from_pos, to_pos, promotion_type)
                
                # Recursive evaluation
                eval = self._minimax(temp_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def _evaluate_position(self, board: Board) -> float:
        """Evaluate the current board position from white's perspective."""
        score = 0.0
        
        # Track queens for both sides
        white_has_queen = False
        black_has_queen = False
        
        # Piece values and positions
        for row in range(8):
            for col in range(8):
                piece = board.squares[row][col]
                if not piece:
                    continue
                    
                # Track queens
                if piece.piece_type == PieceType.QUEEN:
                    if piece.color == PieceColor.WHITE:
                        white_has_queen = True
                    else:
                        black_has_queen = True
                
                piece_value = piece.piece_type.value_score
                position_bonus = self._get_position_bonus(piece, row, col, board)
                
                if piece.color == PieceColor.WHITE:
                    score += piece_value + position_bonus
                else:
                    score -= piece_value + position_bonus
        
        # Apply queen retention bonus
        queen_retention_bonus = 3.0  # Additional bonus for keeping the queen
        if white_has_queen:
            score += queen_retention_bonus
        if black_has_queen:
            score -= queen_retention_bonus
                    
        return score

    def _get_position_bonus(self, piece: Piece, row: int, col: int, board: Board) -> float:
        """Calculate position bonus based on piece type and position."""
        bonus = 0.0
        
        # Pawns are more valuable as they advance
        if piece.piece_type == PieceType.PAWN:
            if piece.color == PieceColor.WHITE:
                bonus = (7 - row) * 0.1  # Bonus for advancing
                # Extra bonus for being close to promotion
                if row <= 2:  # Within 3 rows of promotion
                    bonus += (2 - row) * 0.2
            else:
                bonus = row * 0.1
                # Extra bonus for being close to promotion
                if row >= 5:  # Within 3 rows of promotion
                    bonus += (row - 5) * 0.2
        
        # Control of center squares
        if 2 <= row <= 5 and 2 <= col <= 5:
            bonus += 0.2
            # Extra bonus for queens in the center
            if piece.piece_type == PieceType.QUEEN:
                bonus += 0.3
            
        # Knights are better near the center
        if piece.piece_type == PieceType.KNIGHT:
            distance_from_center = abs(3.5 - row) + abs(3.5 - col)
            bonus += (8 - distance_from_center) * 0.1
            
        # Queen positioning
        if piece.piece_type == PieceType.QUEEN:
            # Penalize early queen development slightly
            if (piece.color == PieceColor.WHITE and row == 7) or \
               (piece.color == PieceColor.BLACK and row == 0):
                bonus -= 0.4
            
            # Bonus for queen mobility (more squares to move to)
            mobility_bonus = len(piece.get_valid_moves(board)) * 0.05
            bonus += mobility_bonus
            
            # Penalize exposed queen positions
            if row == 0 or row == 7 or col == 0 or col == 7:
                bonus -= 0.2
            
        return bonus

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
        print("4. System vs System")
        print("5. Quit")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-5): ").strip()
                if choice == "1":
                    return None
                elif choice == "2":
                    return PieceColor.BLACK
                elif choice == "3":
                    return PieceColor.WHITE
                elif choice == "4":
                    return "system_vs_system"
                elif choice == "5":
                    self.game_over = True
                    return None
                else:
                    print("Invalid choice. Please enter 1-5.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def play(self):
        # Get game mode
        system_color = self._get_game_mode()
        if self.game_over:
            clear_screen()
            print("Thanks for playing!")
            return
            
        if system_color == "system_vs_system":
            self._play_system_vs_system()
            return
        elif system_color:
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
                from_pos, to_pos, promotion_type = self.system_player.get_move(self.board)
                self.board.move_piece(from_pos, to_pos, promotion_type)
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
                from_pos, to_pos, promotion_type = self._parse_move(move)
                success, error_msg = self._make_move(from_pos, to_pos, promotion_type)
                if not success:
                    print(f"Invalid move: {error_msg}")
                    input("\nPress Enter to continue...")
            except ValueError as e:
                print(f"Error: {e}")
                input("\nPress Enter to continue...")
                
    def _parse_move(self, move: str) -> Tuple[Position, Position, Optional[PieceType]]:
        """Parse a move string into positions and optional promotion piece."""
        parts = move.strip().lower().split()
        if len(parts) not in [2, 3]:
            raise ValueError("Invalid move format. Use 'e2 e4' or 'e7 e8 q' for promotion")
            
        try:
            from_pos = Position.from_algebraic(parts[0])
            to_pos = Position.from_algebraic(parts[1])
            
            # Check for promotion piece
            promotion_type = None
            if len(parts) == 3:
                promotion_map = {
                    'q': PieceType.QUEEN,
                    'r': PieceType.ROOK,
                    'b': PieceType.BISHOP,
                    'n': PieceType.KNIGHT
                }
                if parts[2] not in promotion_map:
                    raise ValueError("Invalid promotion piece. Use q/r/b/n")
                promotion_type = promotion_map[parts[2]]
                
            return from_pos, to_pos, promotion_type
            
        except (IndexError, ValueError):
            raise ValueError("Invalid position notation.")

    def _make_move(self, from_pos: Position, to_pos: Position, promotion_type: Optional[PieceType] = None) -> Tuple[bool, Optional[str]]:
        """Make a move and handle game state changes."""
        piece = self.board.get_piece(from_pos)
        if not piece:
            return False, "No piece at starting position"
            
        if piece.color != self.current_player:
            return False, f"That's not your piece (it's {piece.color.value}'s)"
            
        # Check if this is a pawn promotion move
        needs_promotion = (piece.piece_type == PieceType.PAWN and 
                         ((piece.color == PieceColor.WHITE and to_pos.row == 0) or
                          (piece.color == PieceColor.BLACK and to_pos.row == 7)))
        
        if needs_promotion and not promotion_type:
            return False, "Pawn promotion requires a piece type (q/r/b/n)"
            
        # Check if move is valid and doesn't leave/put king in check
        success, error_msg = self.board.move_piece(from_pos, to_pos, promotion_type)
        if not success:
            if self.board.is_king_in_check(self.current_player):
                return False, f"{error_msg} (Your king is in check)"
            else:
                return False, error_msg
            
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
            
        self.current_player = opponent_color
        return True, None

    def _show_help(self):
        print("\nGame Controls:")
        print("- Enter moves in algebraic notation (e.g., 'e2 e4')")
        print("- For pawn promotion, add the piece type (e.g., 'e7 e8 q')")
        print("  q = queen, r = rook, b = bishop, n = knight")
        print("- Type 'quit' to exit the game")
        print("- Type 'help' to see this message again")

    def _play_system_vs_system(self, max_moves: int = 1000, delay: float = 0.02):
        """Simulate a game between two system players."""
        import time
        
        white_player = SystemPlayer(PieceColor.WHITE)
        black_player = SystemPlayer(PieceColor.BLACK)
        move_count = 0
        terminal_condition = None
        winner = None
        last_capture_move = 0
        
        print("\nSystem vs System match")
        print(f"Max moves: {max_moves}")
        print("Press Ctrl+C to stop the game")
        input("Press Enter to start...")
        
        try:
            while move_count < max_moves and not self.game_over:
                self.board.display()
                current_player = white_player if self.current_player == PieceColor.WHITE else black_player
                
                print(f"\n{self.current_player.value}'s turn")
                print("System is thinking...")
                time.sleep(delay)
                
                # Get and make the move
                move = current_player.get_move(self.board)
                if not move:
                    terminal_condition = "CHECKMATE" if self.board.is_king_in_check(self.current_player) else "STALEMATE"
                    if terminal_condition == "CHECKMATE":
                        winner = PieceColor.BLACK if self.current_player == PieceColor.WHITE else PieceColor.WHITE
                    break
                
                from_pos, to_pos, promotion_type = move if len(move) == 3 else (*move, None)
                captured_piece = self.board.get_piece(to_pos)
                success, _ = self.board.move_piece(from_pos, to_pos, promotion_type)
                
                # Update last capture move if a piece was captured
                if captured_piece:
                    last_capture_move = move_count
                
                # Check for draw by lack of progress (50 moves without capture)
                if move_count - last_capture_move >= 100:  # 50 moves = 100 half-moves
                    terminal_condition = "DRAW_NO_PROGRESS"
                    break
                
                # Switch players
                opponent_color = PieceColor.BLACK if self.current_player == PieceColor.WHITE else PieceColor.WHITE
                self.current_player = opponent_color
                
                # Check if the opponent is in checkmate or stalemate
                if self.board.is_checkmate(opponent_color):
                    terminal_condition = "CHECKMATE"
                    winner = PieceColor.WHITE if opponent_color == PieceColor.BLACK else PieceColor.BLACK
                    break
                elif self.board.is_king_in_check(opponent_color):
                    print(f"\n{opponent_color.value} is in check!")
                elif self.board.is_stalemate(opponent_color):
                    terminal_condition = "STALEMATE"
                    break
                
                move_count += 1
                
        except KeyboardInterrupt:
            terminal_condition = "USER_INTERRUPT"
        
        # Display final position and game summary
        self.board.display()
        print("\nGame Over!")
        print(f"Total moves: {move_count}")
        
        if terminal_condition == "CHECKMATE":
            print(f"Terminal condition: Checkmate - {winner.value} wins!")
        elif terminal_condition == "STALEMATE":
            print("Terminal condition: Stalemate - Game is a draw!")
        elif terminal_condition == "DRAW_NO_PROGRESS":
            print("Terminal condition: Draw - No captures in last 50 moves")
        elif terminal_condition == "USER_INTERRUPT":
            print("Terminal condition: Game stopped by user")
        elif move_count >= max_moves:
            print(f"Terminal condition: Move limit reached ({max_moves} moves)")
            
        input("\nPress Enter to return to menu...")
        self.game_over = True


if __name__ == "__main__":
    game = ChessGame()
    game.play()
