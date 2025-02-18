import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import random
import os

# Set the folder containing the GIFs
GIF_FOLDER = r"C:\Path\gif"

# Automatically get all GIF files in the folder
def get_gif_files():
    return [os.path.join(GIF_FOLDER, f) for f in os.listdir(GIF_FOLDER) if f.lower().endswith(".gif")]

# Get the list of GIFs
gif_paths = get_gif_files()

if not gif_paths:
    print("No GIFs found in the folder!")
    exit()  # Exit if no GIFs are found

# Wait time before new Gif displayed, in Seconds
MIN_WAIT = 1
MAX_WAIT = 5

# Get screen size, Change to your monitor size if needed
screen_width = 1920  
screen_height = 1080

# Gif Size, Change size if needed
GIF_WIDTH = 200 
GIF_HEIGHT = 112

# For Padding from edges, Change if needed
PADDING = 100

class GIFPlayer(tk.Toplevel):
    def __init__(self, master, gif_path):
        super().__init__(master)

        self.overrideredirect(True)  # Remove window borders
        self.attributes("-topmost", True)  # 👈 Keep the GIF on top of all windows

        # Load GIF and extract frames
        self.gif = Image.open(gif_path)
        self.frames = [ImageTk.PhotoImage(frame.copy().resize((200, 112))) for frame in ImageSequence.Iterator(self.gif)]
        self.total_frames = len(self.frames)
        self.frame_idx = 0
        self.rotation_count = 0

        # For Random position on the screen
        x = random.randint(0, max(0, screen_width - 200))
        y = random.randint(0, max(0, screen_height - 112))

        # For Random position at the edge of the screen
        # random_x, random_y = get_edge_position()
        # x = random_x
        # y = random_y
        self.geometry(f"200x112+{x}+{y}")

        # Create a canvas
        self.canvas = tk.Canvas(self, width=200, height=112, highlightthickness=0)
        self.canvas.pack()
        self.img_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.frames[0])

        # Bind click event to close GIF
        self.canvas.bind("<Button-1>", self.close_gif)

        # Start animation
        self.animate()

    def animate(self):
        """animates the GIF"""
        if self.frame_idx == 0 and self.rotation_count >= 3:
            self.destroy()  # Close after 2 full loops
            return

        self.canvas.itemconfig(self.img_id, image=self.frames[self.frame_idx])
        self.frame_idx = (self.frame_idx + 1) % self.total_frames

        if self.frame_idx == 0:
            self.rotation_count += 1  # Count how many times it loops

        self.after(30, self.animate)  # Update frame every 50ms

    def close_gif(self, event=None):
        """Destroys the GIF window when clicked."""
        self.destroy()

def show_gif(root):
    """Plays a GIF before showing the next one."""

    gif_path = random.choice(gif_paths)
    gif_player = GIFPlayer(root, gif_path)  # Show new GIF

    # Wait until GIF finishes before starting the next one
    wait_time = (gif_player.total_frames * 3 * 45) + random.randint(MIN_WAIT, MAX_WAIT)  # 45ms per frame, 3 loops + random wait time
    root.after(wait_time, show_gif, root)  # Schedule next GIF only after the current one finishes


def get_edge_position():
    """ Returns a random (x, y) position near the edges of the screen. """
    edge = random.choice(["top", "bottom", "left", "right"])

    if edge == "top":
        x = random.randint(PADDING, screen_width - GIF_WIDTH - PADDING)
        y = PADDING
    elif edge == "bottom":
        x = random.randint(PADDING, screen_width - GIF_WIDTH - PADDING)
        y = screen_height - GIF_HEIGHT - PADDING
    elif edge == "left":
        x = PADDING
        y = random.randint(PADDING, screen_height - GIF_HEIGHT - PADDING)
    else:  # "right"
        x = screen_width - GIF_WIDTH - PADDING
        y = random.randint(PADDING, screen_height - GIF_HEIGHT - PADDING)

    return x, y

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    show_gif(root)  # Start GIF loop
    root.mainloop()  # Keep running


# Run the program
main()