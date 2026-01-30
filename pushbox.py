#!/usr/bin/env python3
"""
Push Box (Sokoban) Game
Use WASD or arrow keys to move the player.
Push all boxes onto the target locations to win!
"""

import sys
import tty
import termios

# Game symbols
WALL = '#'
FLOOR = ' '
PLAYER = '@'
PLAYER_ON_TARGET = '+'
BOX = '$'
BOX_ON_TARGET = '*'
TARGET = '.'

# Level layout
LEVEL = [
    "########",
    "#      #",
    "# $ $  #",
    "# $@$  #",
    "#  .   #",
    "# ...  #",
    "#      #",
    "########",
]


class Game:
    def __init__(self, level):
        self.walls = set()
        self.targets = set()
        self.boxes = set()
        self.player = None
        self.moves = 0
        self.parse_level(level)

    def parse_level(self, level):
        """Parse the level string into game objects."""
        for y, row in enumerate(level):
            for x, char in enumerate(row):
                pos = (x, y)
                if char == WALL:
                    self.walls.add(pos)
                elif char == TARGET:
                    self.targets.add(pos)
                elif char == BOX:
                    self.boxes.add(pos)
                elif char == BOX_ON_TARGET:
                    self.boxes.add(pos)
                    self.targets.add(pos)
                elif char == PLAYER:
                    self.player = pos
                elif char == PLAYER_ON_TARGET:
                    self.player = pos
                    self.targets.add(pos)

        self.width = max(len(row) for row in level)
        self.height = len(level)

    def render(self):
        """Render the current game state."""
        print("\033[H\033[J", end="")  # Clear screen
        print("Push Box Game")
        print("Controls: WASD or Arrow Keys | Q to Quit | R to Restart")
        print(f"Moves: {self.moves}")
        print()

        for y in range(self.height):
            row = ""
            for x in range(self.width):
                pos = (x, y)
                if pos in self.walls:
                    row += WALL
                elif pos == self.player:
                    if pos in self.targets:
                        row += PLAYER_ON_TARGET
                    else:
                        row += PLAYER
                elif pos in self.boxes:
                    if pos in self.targets:
                        row += BOX_ON_TARGET
                    else:
                        row += BOX
                elif pos in self.targets:
                    row += TARGET
                else:
                    row += FLOOR
            print(row)
        print()

    def move(self, dx, dy):
        """Try to move the player in the given direction."""
        new_x = self.player[0] + dx
        new_y = self.player[1] + dy
        new_pos = (new_x, new_y)

        # Check wall collision
        if new_pos in self.walls:
            return False

        # Check box collision
        if new_pos in self.boxes:
            # Try to push the box
            box_new_x = new_x + dx
            box_new_y = new_y + dy
            box_new_pos = (box_new_x, box_new_y)

            # Can't push if wall or another box is in the way
            if box_new_pos in self.walls or box_new_pos in self.boxes:
                return False

            # Push the box
            self.boxes.remove(new_pos)
            self.boxes.add(box_new_pos)

        # Move player
        self.player = new_pos
        self.moves += 1
        return True

    def is_won(self):
        """Check if all boxes are on targets."""
        return self.boxes == self.targets

    def reset(self):
        """Reset the level."""
        self.__init__(LEVEL)


def get_key():
    """Get a single keypress from the user."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        # Handle arrow keys (escape sequences)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def main():
    game = Game(LEVEL)

    while True:
        game.render()

        if game.is_won():
            print("Congratulations! You won!")
            print(f"Total moves: {game.moves}")
            print("Press R to restart or Q to quit.")

        key = get_key().lower()

        # Movement
        if key in ('w', '\x1b[a'):  # Up
            game.move(0, -1)
        elif key in ('s', '\x1b[b'):  # Down
            game.move(0, 1)
        elif key in ('a', '\x1b[d'):  # Left
            game.move(-1, 0)
        elif key in ('d', '\x1b[c'):  # Right
            game.move(1, 0)
        elif key == 'r':  # Restart
            game.reset()
        elif key == 'q' or key == '\x03':  # Quit (q or Ctrl+C)
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
