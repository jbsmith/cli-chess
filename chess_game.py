#!/usr/bin/env python3

import sys
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colored output
init()

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
        piece = self.get_piece(from_pos)
        if not piece:
            return False

        if to_pos not in piece.get_valid_moves(self):
            return False

        # Move the piece
        self.squares[to_pos.row][to_pos.col] = piece
        self.squares[from_pos.row][from_pos.col] = None
        piece.position = to_pos
        piece.has_moved = True
        return True

    def display(self):
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

class ChessGame:
    def __init__(self):
        self.board = Board()
        self.current_player = PieceColor.WHITE
        self.game_over = False

    def play(self):
        print("Welcome to CLI Chess!")
        print("Enter moves in the format: 'e2 e4' or type 'quit' to exit")
        
        while not self.game_over:
            self.board.display()
            print(f"\n{self.current_player.value}'s turn")
            
            move = input("Enter your move: ").strip().lower()
            
            if move == 'quit':
                break
            elif move == 'help':
                self._show_help()
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
            except ValueError as e:
                print(f"Error: {e}")

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
            
        return self.board.move_piece(from_pos, to_pos)

    def _show_help(self):
        print("\nGame Controls:")
        print("- Enter moves in algebraic notation (e.g., 'e2 e4')")
        print("- Type 'quit' to exit the game")
        print("- Type 'help' to see this message again")

if __name__ == "__main__":
    game = ChessGame()
    game.play()
