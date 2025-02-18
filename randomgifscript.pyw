import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import random
import os

# Set the folder containing the GIFs
GIF_FOLDER = r"C:\Users\Dimas\MyPythonScripts\AutoGif\gif"

# Wait time before new Gif displayed
MIN_WAIT = 1000
MAX_WAIT = 5000

# Screen size (adjust if needed)
screen_width = 1920
screen_height = 1080

# Gif Size
GIF_WIDTH = 200
GIF_HEIGHT = 112

# Padding from edges
PADDING = 100

# Preload all GIF frames
def preload_gifs():
    gif_data = {}
    gif_paths = [os.path.join(GIF_FOLDER, f) for f in os.listdir(GIF_FOLDER) if f.lower().endswith(".gif")]

    if not gif_paths:
        print("No GIFs found in the folder!")
        exit()

    for gif_path in gif_paths:
        try:
            gif = Image.open(gif_path)
            frames = [ImageTk.PhotoImage(frame.copy().resize((GIF_WIDTH, GIF_HEIGHT))) for frame in ImageSequence.Iterator(gif)]
            gif_data[gif_path] = frames
        except Exception as e:
            print(f"Error loading GIF {gif_path}: {e}")
    
    return gif_data

# Preloaded GIFs
preloaded_gifs = preload_gifs()

class GIFPlayer(tk.Toplevel):
    def __init__(self, master, gif_path, frames):
        super().__init__(master)
        
        self.overrideredirect(True)  # Remove window borders
        self.attributes("-topmost", True)  # Keep GIF on top

        # Use preloaded frames
        self.frames = frames
        self.total_frames = len(self.frames)
        self.frame_idx = 0
        self.rotation_count = 0

        # Random position
        x = random.randint(0, max(0, screen_width - GIF_WIDTH))
        y = random.randint(0, max(0, screen_height - GIF_HEIGHT))
        self.geometry(f"{GIF_WIDTH}x{GIF_HEIGHT}+{x}+{y}")

        # Create a canvas
        self.canvas = tk.Canvas(self, width=GIF_WIDTH, height=GIF_HEIGHT, highlightthickness=0)
        self.canvas.pack()
        self.img_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.frames[0])

        # Bind click event to close GIF
        self.canvas.bind("<Button-1>", self.close_gif)

        # Start animation
        self.animate()

    def animate(self):
        """Animate the GIF."""
        if self.frame_idx == 0 and self.rotation_count >= 3:
            self.destroy()
            return

        self.canvas.itemconfig(self.img_id, image=self.frames[self.frame_idx])
        self.frame_idx = (self.frame_idx + 1) % self.total_frames

        if self.frame_idx == 0:
            self.rotation_count += 1

        self.after(30, self.animate)

    def close_gif(self, event=None):
        """Destroy the GIF window when clicked."""
        self.destroy()

def show_gif(root):
    """Plays a random GIF and schedules the next one."""
    gif_path, frames = random.choice(list(preloaded_gifs.items()))
    gif_player = GIFPlayer(root, gif_path, frames)

    # Schedule the next GIF
    wait_time = (len(frames) * 3 * 30) + random.randint(MIN_WAIT, MAX_WAIT)
    root.after(wait_time, show_gif, root)

def main():
    root = tk.Tk()
    root.withdraw()
    show_gif(root)
    root.mainloop()

# Run the program
main()
