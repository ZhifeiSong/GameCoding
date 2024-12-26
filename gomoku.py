import tkinter as tk
from tkinter import messagebox

BOARD_SIZE = 15
CELL_SIZE = 40  # Pixels for each cell on the canvas

class GomokuGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Gomoku v0.0.1")

        # Score variables
        self.black_score = 0
        self.white_score = 0

        # Game state variables
        self.current_player = 1  # 1 = Black, 2 = White
        self.board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]  # 0 = empty

        # History of moves for undo functionality
        # Each entry: (row, col, player, stone_canvas_id)
        self.move_history = []

        # Setup frames
        self.setup_score_frame()
        self.setup_board_canvas()

    def setup_score_frame(self):
        """Create a frame at the top to display scores and whose turn it is."""
        self.score_frame = tk.Frame(self.root, bg="lightgray")
        self.score_frame.pack(side=tk.TOP, fill=tk.X)

        self.black_score_label = tk.Label(
            self.score_frame, text=f"Black Score: {self.black_score}", 
            font=("Helvetica", 14), bg="lightgray"
        )
        self.black_score_label.pack(side=tk.LEFT, padx=20, pady=10)

        self.white_score_label = tk.Label(
            self.score_frame, text=f"White Score: {self.white_score}", 
            font=("Helvetica", 14), bg="lightgray"
        )
        self.white_score_label.pack(side=tk.LEFT, padx=20, pady=10)

        self.turn_label = tk.Label(
            self.score_frame, text="Current Turn: Black", 
            font=("Helvetica", 14, "bold"), bg="lightgray"
        )
        self.turn_label.pack(side=tk.LEFT, padx=20, pady=10)
        # Add an Undo button
        self.undo_button = tk.Button(
            self.score_frame,
            text="Undo Move",
            font=("Helvetica", 12),
            command=self.undo_move
        )
        self.undo_button.pack(side=tk.RIGHT, padx=10, pady=10)


    def setup_board_canvas(self):
        """Create a canvas for the Gomoku board."""
        self.canvas = tk.Canvas(
            self.root, width=BOARD_SIZE*CELL_SIZE, height=BOARD_SIZE*CELL_SIZE, bg="#F9DDA4"
        )
        self.canvas.pack()

        # Draw grid lines
        for i in range(BOARD_SIZE):
            # Horizontal lines
            self.canvas.create_line(0, i*CELL_SIZE, BOARD_SIZE*CELL_SIZE, i*CELL_SIZE, fill="black", width=2)
            # Vertical lines
            self.canvas.create_line(i*CELL_SIZE, 0, i*CELL_SIZE, BOARD_SIZE*CELL_SIZE, fill="black", width=2)

        # Bind left-click event
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def on_canvas_click(self, event):
        """Handle clicks on the canvas, convert pixel coords to board coords."""
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        # Check boundaries
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            if self.board[row][col] == 0:
                # Place a stone
                self.board[row][col] = self.current_player
                stone_id = self.draw_stone(row, col, self.current_player)

                # Record the move in history (for undo)
                self.move_history.append((row, col, self.current_player, stone_id))

                # Check for win
                if self.check_win(row, col, self.current_player):
                    # Force UI to draw that final stone before showing the message
                    self.canvas.update_idletasks()
                    self.handle_win(self.current_player)
                else:
                    # Switch player
                    self.current_player = 2 if self.current_player == 1 else 1
                    self.turn_label.config(
                        text="Current Turn: " + ("Black" if self.current_player == 1 else "White")
                    )

    def draw_stone(self, row, col, player):
        """Draw a stone on the board (black or white)."""
        x1 = col * CELL_SIZE + 2
        y1 = row * CELL_SIZE + 2
        x2 = (col+1) * CELL_SIZE - 2
        y2 = (row+1) * CELL_SIZE - 2

        color = "black" if player == 1 else "white"
        stone_id = self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="black")
        return stone_id

    def check_win(self, row, col, player):
        """
        Check if placing a stone at (row, col) caused player to win.
        We'll check in 4 directions (horizontal, vertical, and two diagonals).
        """
        # Directions as (delta_row, delta_col)
        directions = [(1,0), (0,1), (1,1), (1,-1)]

        for d_row, d_col in directions:
            count = 1  # start with current stone
            # check in the positive direction
            count += self.count_stones(row, col, d_row, d_col, player)
            # check in the negative direction
            count += self.count_stones(row, col, -d_row, -d_col, player)

            if count >= 5:
                return True
        return False

    def count_stones(self, row, col, d_row, d_col, player):
        """Count consecutive stones of `player` in one direction (d_row, d_col)."""
        count = 0
        r, c = row + d_row, col + d_col
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
            count += 1
            r += d_row
            c += d_col
        return count

    def handle_win(self, player):
        """When a player wins, show a message, update score, and reset the board."""
        winner_text = "Black" if player == 1 else "White"
        messagebox.showinfo("Game Over", f"{winner_text} wins!")
        
        # Update score
        if player == 1:
            self.black_score += 1
            self.black_score_label.config(text=f"Black Score: {self.black_score}")
        else:
            self.white_score += 1
            self.white_score_label.config(text=f"White Score: {self.white_score}")

        self.reset_board()

    def reset_board(self):
        """Clear the board and start a new round."""
        self.board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.canvas.delete("all")
        self.move_history = []  # Clear the move history

        # Redraw the board lines
        for i in range(BOARD_SIZE):
            # Horizontal lines
            self.canvas.create_line(0, i*CELL_SIZE, BOARD_SIZE*CELL_SIZE, i*CELL_SIZE, fill="black")
            # Vertical lines
            self.canvas.create_line(i*CELL_SIZE, 0, i*CELL_SIZE, BOARD_SIZE*CELL_SIZE, fill="black")

        # Reset the player turn to black (or keep to whomever we wish to start next)
        self.current_player = 1
        self.turn_label.config(text="Current Turn: Black")
    
    def undo_move(self):
        """Undo the last move if available."""
        if not self.move_history:
            return  # No moves to undo

        # Pop the last move
        row, col, player, stone_id = self.move_history.pop()

        # Remove stone from board
        self.board[row][col] = 0

        # Remove stone from the canvas
        self.canvas.delete(stone_id)

        # Revert current player to the player who made the undone move
        self.current_player = player
        self.turn_label.config(
            text="Current Turn: " + ("Black" if self.current_player == 1 else "White")
        )


def main():
    root = tk.Tk()
    game = GomokuGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()