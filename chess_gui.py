#!/usr/bin/env python3
"""
Chess Game - Pygame GUI Version
Two-player local chess with basic rules (no castling, en passant, or pawn promotion).
Click to select a piece, then click a highlighted square to move.
"""

import pygame
import sys

# Constants
TILE_SIZE = 80
HEADER_HEIGHT = 80
BOARD_SIZE = 8
FPS = 60

# Colors
COLOR_LIGHT_SQUARE = (240, 217, 181)    # Tan #F0D9B5
COLOR_DARK_SQUARE = (181, 136, 99)      # Brown #B58863
COLOR_SELECTED = (127, 255, 127)        # Green highlight
COLOR_VALID_MOVE = (255, 255, 127)      # Yellow highlight
COLOR_CHECK = (255, 102, 102)           # Red highlight
COLOR_WHITE_PIECE = (255, 255, 255)     # White
COLOR_BLACK_PIECE = (0, 0, 0)           # Black
COLOR_TEXT = (0, 0, 0)                  # Black text
COLOR_OVERLAY = (0, 0, 0, 180)          # Semi-transparent black

# Unicode chess pieces
PIECES = {
    ('white', 'king'): '\u2654',    # ♔
    ('white', 'queen'): '\u2655',   # ♕
    ('white', 'rook'): '\u2656',    # ♖
    ('white', 'bishop'): '\u2657',  # ♗
    ('white', 'knight'): '\u2658',  # ♘
    ('white', 'pawn'): '\u2659',    # ♙
    ('black', 'king'): '\u265A',    # ♚
    ('black', 'queen'): '\u265B',   # ♛
    ('black', 'rook'): '\u265C',    # ♜
    ('black', 'bishop'): '\u265D',  # ♝
    ('black', 'knight'): '\u265E',  # ♞
    ('black', 'pawn'): '\u265F',    # ♟
}


class ChessGame:
    """Chess game logic."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset the game to initial state."""
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_turn = 'white'
        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.in_check = False
        self._setup_board()

    def _setup_board(self):
        """Set up the initial piece positions."""
        # Black pieces (top of board, rows 0-1)
        back_row = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for col, piece in enumerate(back_row):
            self.board[0][col] = ('black', piece)
            self.board[1][col] = ('black', 'pawn')

        # White pieces (bottom of board, rows 6-7)
        for col, piece in enumerate(back_row):
            self.board[7][col] = ('white', piece)
            self.board[6][col] = ('white', 'pawn')

    def get_piece(self, row, col):
        """Get the piece at the given position."""
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.board[row][col]
        return None

    def get_valid_moves(self, row, col):
        """Get all valid moves for the piece at (row, col)."""
        piece = self.get_piece(row, col)
        if piece is None:
            return []

        color, piece_type = piece
        moves = []

        if piece_type == 'pawn':
            moves = self._get_pawn_moves(row, col, color)
        elif piece_type == 'rook':
            moves = self._get_rook_moves(row, col, color)
        elif piece_type == 'knight':
            moves = self._get_knight_moves(row, col, color)
        elif piece_type == 'bishop':
            moves = self._get_bishop_moves(row, col, color)
        elif piece_type == 'queen':
            moves = self._get_queen_moves(row, col, color)
        elif piece_type == 'king':
            moves = self._get_king_moves(row, col, color)

        # Filter out moves that would leave own king in check
        valid_moves = []
        for move in moves:
            if not self._would_be_in_check(row, col, move[0], move[1], color):
                valid_moves.append(move)

        return valid_moves

    def _get_pawn_moves(self, row, col, color):
        """Get valid moves for a pawn."""
        moves = []
        direction = -1 if color == 'white' else 1
        start_row = 6 if color == 'white' else 1

        # Move forward one square
        new_row = row + direction
        if 0 <= new_row < BOARD_SIZE and self.board[new_row][col] is None:
            moves.append((new_row, col))
            # Move forward two squares from starting position
            if row == start_row:
                new_row2 = row + 2 * direction
                if self.board[new_row2][col] is None:
                    moves.append((new_row2, col))

        # Capture diagonally
        for dc in [-1, 1]:
            new_col = col + dc
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                target = self.board[new_row][new_col]
                if target is not None and target[0] != color:
                    moves.append((new_row, new_col))

        return moves

    def _get_rook_moves(self, row, col, color):
        """Get valid moves for a rook."""
        return self._get_linear_moves(row, col, color, [(0, 1), (0, -1), (1, 0), (-1, 0)])

    def _get_bishop_moves(self, row, col, color):
        """Get valid moves for a bishop."""
        return self._get_linear_moves(row, col, color, [(1, 1), (1, -1), (-1, 1), (-1, -1)])

    def _get_queen_moves(self, row, col, color):
        """Get valid moves for a queen."""
        return self._get_linear_moves(row, col, color,
                                      [(0, 1), (0, -1), (1, 0), (-1, 0),
                                       (1, 1), (1, -1), (-1, 1), (-1, -1)])

    def _get_linear_moves(self, row, col, color, directions):
        """Get moves in straight lines (for rook, bishop, queen)."""
        moves = []
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target = self.board[r][c]
                if target is None:
                    moves.append((r, c))
                elif target[0] != color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves

    def _get_knight_moves(self, row, col, color):
        """Get valid moves for a knight."""
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target = self.board[r][c]
                if target is None or target[0] != color:
                    moves.append((r, c))
        return moves

    def _get_king_moves(self, row, col, color):
        """Get valid moves for a king."""
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    target = self.board[r][c]
                    if target is None or target[0] != color:
                        moves.append((r, c))
        return moves

    def _find_king(self, color):
        """Find the position of the king of the given color."""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board[r][c]
                if piece == (color, 'king'):
                    return (r, c)
        return None

    def _is_square_attacked(self, row, col, by_color):
        """Check if a square is attacked by any piece of the given color."""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board[r][c]
                if piece is not None and piece[0] == by_color:
                    # Get raw moves without check validation to avoid infinite recursion
                    moves = self._get_raw_moves(r, c, piece)
                    if (row, col) in moves:
                        return True
        return False

    def _get_raw_moves(self, row, col, piece):
        """Get moves without check validation (to avoid recursion)."""
        color, piece_type = piece
        if piece_type == 'pawn':
            # For pawns, only check diagonal captures for attack purposes
            moves = []
            direction = -1 if color == 'white' else 1
            new_row = row + direction
            for dc in [-1, 1]:
                new_col = col + dc
                if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                    moves.append((new_row, new_col))
            return moves
        elif piece_type == 'rook':
            return self._get_linear_moves(row, col, color, [(0, 1), (0, -1), (1, 0), (-1, 0)])
        elif piece_type == 'knight':
            return self._get_knight_moves(row, col, color)
        elif piece_type == 'bishop':
            return self._get_linear_moves(row, col, color, [(1, 1), (1, -1), (-1, 1), (-1, -1)])
        elif piece_type == 'queen':
            return self._get_linear_moves(row, col, color,
                                          [(0, 1), (0, -1), (1, 0), (-1, 0),
                                           (1, 1), (1, -1), (-1, 1), (-1, -1)])
        elif piece_type == 'king':
            return self._get_king_moves(row, col, color)
        return []

    def _would_be_in_check(self, from_row, from_col, to_row, to_col, color):
        """Check if making a move would leave the king in check."""
        # Temporarily make the move
        original_piece = self.board[to_row][to_col]
        moving_piece = self.board[from_row][from_col]
        self.board[to_row][to_col] = moving_piece
        self.board[from_row][from_col] = None

        # Find king position (might have moved)
        king_pos = self._find_king(color)
        if king_pos is None:
            # King captured - this shouldn't happen in valid game
            self.board[from_row][from_col] = moving_piece
            self.board[to_row][to_col] = original_piece
            return True

        # Check if king is under attack
        opponent = 'black' if color == 'white' else 'white'
        in_check = self._is_square_attacked(king_pos[0], king_pos[1], opponent)

        # Undo the move
        self.board[from_row][from_col] = moving_piece
        self.board[to_row][to_col] = original_piece

        return in_check

    def is_in_check(self, color):
        """Check if the given color's king is in check."""
        king_pos = self._find_king(color)
        if king_pos is None:
            return False
        opponent = 'black' if color == 'white' else 'white'
        return self._is_square_attacked(king_pos[0], king_pos[1], opponent)

    def is_checkmate(self, color):
        """Check if the given color is in checkmate."""
        if not self.is_in_check(color):
            return False
        # Check if any piece can make a valid move
        return not self._has_valid_moves(color)

    def is_stalemate(self, color):
        """Check if the given color is in stalemate."""
        if self.is_in_check(color):
            return False
        return not self._has_valid_moves(color)

    def _has_valid_moves(self, color):
        """Check if the given color has any valid moves."""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board[r][c]
                if piece is not None and piece[0] == color:
                    if self.get_valid_moves(r, c):
                        return True
        return False

    def select_piece(self, row, col):
        """Select a piece at the given position."""
        piece = self.get_piece(row, col)
        if piece is not None and piece[0] == self.current_turn:
            self.selected_piece = (row, col)
            self.valid_moves = self.get_valid_moves(row, col)
            return True
        return False

    def move_piece(self, to_row, to_col):
        """Move the selected piece to the target position."""
        if self.selected_piece is None:
            return False

        from_row, from_col = self.selected_piece

        if (to_row, to_col) not in self.valid_moves:
            return False

        # Make the move
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None

        # Clear selection
        self.selected_piece = None
        self.valid_moves = []

        # Switch turns
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

        # Check for check/checkmate/stalemate
        self.in_check = self.is_in_check(self.current_turn)

        if self.is_checkmate(self.current_turn):
            self.game_over = True
            self.winner = 'white' if self.current_turn == 'black' else 'black'
        elif self.is_stalemate(self.current_turn):
            self.game_over = True
            self.winner = None  # Draw

        return True

    def handle_click(self, row, col):
        """Handle a click on the board."""
        if self.game_over:
            return

        # If clicking on a valid move destination, make the move
        if (row, col) in self.valid_moves:
            self.move_piece(row, col)
            return

        # Otherwise, try to select a piece
        piece = self.get_piece(row, col)
        if piece is not None and piece[0] == self.current_turn:
            self.select_piece(row, col)
        else:
            # Deselect
            self.selected_piece = None
            self.valid_moves = []


def draw_board(screen, game):
    """Draw the chess board."""
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # Determine square color
            is_light = (row + col) % 2 == 0
            color = COLOR_LIGHT_SQUARE if is_light else COLOR_DARK_SQUARE

            rect = pygame.Rect(
                col * TILE_SIZE,
                HEADER_HEIGHT + row * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
            pygame.draw.rect(screen, color, rect)


def draw_highlights(screen, game):
    """Draw highlights for selected piece, valid moves, and check."""
    # Highlight king in check
    if game.in_check:
        king_pos = game._find_king(game.current_turn)
        if king_pos:
            rect = pygame.Rect(
                king_pos[1] * TILE_SIZE,
                HEADER_HEIGHT + king_pos[0] * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
            pygame.draw.rect(screen, COLOR_CHECK, rect)

    # Highlight selected piece
    if game.selected_piece:
        row, col = game.selected_piece
        rect = pygame.Rect(
            col * TILE_SIZE,
            HEADER_HEIGHT + row * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )
        pygame.draw.rect(screen, COLOR_SELECTED, rect)

    # Highlight valid moves
    for row, col in game.valid_moves:
        rect = pygame.Rect(
            col * TILE_SIZE,
            HEADER_HEIGHT + row * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )
        pygame.draw.rect(screen, COLOR_VALID_MOVE, rect)


def draw_pieces(screen, game, font):
    """Draw the chess pieces."""
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = game.get_piece(row, col)
            if piece:
                symbol = PIECES.get(piece, '?')
                # Render with outline for visibility
                text = font.render(symbol, True, COLOR_BLACK_PIECE)
                text_rect = text.get_rect(center=(
                    col * TILE_SIZE + TILE_SIZE // 2,
                    HEADER_HEIGHT + row * TILE_SIZE + TILE_SIZE // 2
                ))
                screen.blit(text, text_rect)


def draw_ui(screen, game, font):
    """Draw the header UI."""
    # Draw header background
    header_rect = pygame.Rect(0, 0, screen.get_width(), HEADER_HEIGHT)
    pygame.draw.rect(screen, (240, 240, 240), header_rect)
    pygame.draw.line(screen, (180, 180, 180), (0, HEADER_HEIGHT), (screen.get_width(), HEADER_HEIGHT), 2)

    # Draw turn indicator
    turn_text = f"{game.current_turn.capitalize()}'s Turn"
    if game.in_check:
        turn_text += " - CHECK!"
    text = font.render(turn_text, True, COLOR_TEXT)
    screen.blit(text, (20, 15))

    # Draw controls hint
    controls_text = font.render("Click: Select/Move | R: Reset | Q: Quit", True, (100, 100, 100))
    screen.blit(controls_text, (20, HEADER_HEIGHT - controls_text.get_height() - 10))


def draw_game_over(screen, game, font, large_font):
    """Draw the game over overlay."""
    # Semi-transparent overlay
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill(COLOR_OVERLAY)
    screen.blit(overlay, (0, 0))

    # Game over message
    if game.winner:
        text = f"Checkmate! {game.winner.capitalize()} wins!"
    else:
        text = "Stalemate! It's a draw!"

    win_text = large_font.render(text, True, (255, 255, 255))
    hint_text = font.render("Press R to play again", True, (200, 200, 200))

    # Center the text
    screen.blit(win_text, ((screen.get_width() - win_text.get_width()) // 2,
                           screen.get_height() // 2 - 40))
    screen.blit(hint_text, ((screen.get_width() - hint_text.get_width()) // 2,
                            screen.get_height() // 2 + 20))


def main():
    pygame.init()

    # Window size
    window_width = BOARD_SIZE * TILE_SIZE
    window_height = BOARD_SIZE * TILE_SIZE + HEADER_HEIGHT

    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Chess")

    clock = pygame.time.Clock()

    # Fonts
    font = pygame.font.Font(None, 28)
    large_font = pygame.font.Font(None, 48)

    # Use a system font that supports Unicode chess symbols
    piece_font = None
    for font_name in ['Apple Symbols', 'Segoe UI Symbol', 'DejaVu Sans', 'Arial Unicode MS', 'Noto Sans Symbols']:
        try:
            piece_font = pygame.font.SysFont(font_name, 60)
            # Test if it can render a chess piece
            test_surface = piece_font.render('\u2654', True, (0, 0, 0))
            if test_surface.get_width() > 10:  # Valid render
                break
        except:
            continue
    if piece_font is None:
        piece_font = pygame.font.Font(None, 72)

    # Create game
    game = ChessGame()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x, y = event.pos
                    # Check if click is on the board
                    if y >= HEADER_HEIGHT:
                        col = x // TILE_SIZE
                        row = (y - HEADER_HEIGHT) // TILE_SIZE
                        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                            game.handle_click(row, col)

        # Draw everything
        screen.fill(COLOR_LIGHT_SQUARE)
        draw_board(screen, game)
        draw_highlights(screen, game)
        draw_pieces(screen, game, piece_font)
        draw_ui(screen, game, font)

        if game.game_over:
            draw_game_over(screen, game, font, large_font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
