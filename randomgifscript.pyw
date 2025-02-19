import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import random
import os

# Set the folder containing the GIFs
GIF_FOLDER = r"C:\Users\Dimas\MyPythonScripts\AutoGif\gif"

# Wait time before new Gif displayed
MIN_WAIT = 1 * 1000
MAX_WAIT = 5 * 1000

# Screen size (adjust if needed)
screen_width = 1920
screen_height = 1080

# Padding from edges
PADDING = 100

root = tk.Tk()
root.withdraw()  # Hide the root window

# Preload all GIF frames
def preload_gifs():
    """Preloads all GIF frames into memory after Tkinter is initialized."""
    gif_data = {}
    gif_sizes = {}  # Store each GIF's resized width and height
    gif_delays = {} # Store each GIF's frame delay
    gif_paths = [os.path.join(GIF_FOLDER, f) for f in os.listdir(GIF_FOLDER) if f.lower().endswith(".gif")]

    if not gif_paths:
        print("No GIFs found in the folder!")
        exit()

    for gif_path in gif_paths:
        try:
            gif = Image.open(gif_path)

            # Calculate 75% scaled dimensions
            new_width = int(gif.width * 0.25)
            new_height = int(gif.height * 0.25)

            frames = [ImageTk.PhotoImage(frame.copy().resize((new_width, new_height))) for frame in ImageSequence.Iterator(gif)]
            frame_delay = gif.info.get("duration", 30)

            gif_data[gif_path] = frames
            gif_sizes[gif_path] = (new_width, new_height)  # Store resized dimensions
            gif_delays[gif_path] = frame_delay

        except Exception as e:
            print(f"Error loading GIF {gif_path}: {e}")
    
    return gif_data, gif_sizes, gif_delays

# Preloaded GIFs
preloaded_gifs = preload_gifs()

class GIFPlayer(tk.Toplevel):
    def __init__(self, master, gif_path, frames, size, frame_delay):
        super().__init__(master)
        
        self.overrideredirect(True)  # Remove window borders
        self.attributes("-topmost", True)  # Keep GIF on top

        # Use preloaded frames
        self.frames = frames
        self.total_frames = len(self.frames)
        self.frame_idx = 0
        self.rotation_count = 0
        self.frame_delay = frame_delay

        self.gif_width, self.gif_height = size

        # Random position
        x = random.randint(0, max(0, screen_width - self.gif_width))
        y = random.randint(0, max(0, screen_height - self.gif_height))
        self.geometry(f"{self.gif_width}x{self.gif_height}+{x}+{y}")

        # Create a canvas
        self.canvas = tk.Canvas(self, width=self.gif_width, height=self.gif_height, highlightthickness=0)
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

        self.after(self.frame_delay, self.animate)

    def close_gif(self, event=None):
        """Destroy the GIF window when clicked."""
        self.destroy()

def show_gif(root):
    """Plays a random GIF and schedules the next one."""
    gif_path, frames = random.choice(list(preloaded_gifs.items()))
    size = preloaded_sizes[gif_path]
    frame_delay = preloaded_delays[gif_path]
    gif_player = GIFPlayer(root, gif_path, frames, size, frame_delay)

    # Schedule the next GIF
    wait_time = (len(frames) * 3 * frame_delay) + random.randint(MIN_WAIT, MAX_WAIT)
    root.after(wait_time, show_gif, root)

def main():
    

    global preloaded_gifs, preloaded_sizes, preloaded_delays
    preloaded_gifs, preloaded_sizes, preloaded_delays = preload_gifs()  # Load GIFs, delays and sizes

    show_gif(root)
    root.mainloop()


# Run the program
main()
