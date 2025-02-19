import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import random
import os
import sqlite3

# Set the folder containing the GIFs
GIF_FOLDER = r"C:\Users\Dimas\MyPythonScripts\AutoGif\gif"
DB_FILE = "gif_data.db"

PADDING = 100
HEIGHT_MAX = 240
WIDTH_MAX = 240

WAIT_MIN = 30 * 1000
WAIT_MAX = 60 * 1000

# Create database if not exists
def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gifs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE,
            width INTEGER,
            height INTEGER,
            frame_delay REAL,
            total_duration INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Get stored GIF data
def get_stored_gifs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT path, width, height, frame_delay, total_duration FROM gifs")
    data = {row[0]: {'width': row[1], 'height': row[2], 'frame_delay': row[3], 'total_duration': row[4]} for row in cursor.fetchall()}
    conn.close()
    return data

# Store new GIF data
def store_gif_data(path, width, height, frame_delay, total_duration):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO gifs (path, width, height, frame_delay, total_duration) VALUES (?, ?, ?, ?, ?)",
                   (path, width, height, frame_delay, total_duration))
    conn.commit()
    conn.close()

# Process and store new GIFs
def process_new_gifs():
    stored_gifs = get_stored_gifs()
    gif_paths = [os.path.join(GIF_FOLDER, f) for f in os.listdir(GIF_FOLDER) if f.lower().endswith(".gif")]
    
    new_gif_data = {}
    max_width, max_height = WIDTH_MAX, HEIGHT_MAX
    for path in gif_paths:
        if path in stored_gifs:
            new_gif_data[path] = stored_gifs[path]  # Load stored data
        else:
            gif = Image.open(path)
            frame_delay = gif.info.get("duration", 30)  # Convert ms to seconds
            total_duration = len(list(ImageSequence.Iterator(gif))) * frame_delay * 1000  # Total duration in ms
            
            scale_factor = min(max_width / gif.width, max_height / gif.height, 1)  # Ensure it scales down but not up
            new_width = int(gif.width * scale_factor)
            new_height = int(gif.height * scale_factor)
            
            store_gif_data(path, new_width, new_height, frame_delay, total_duration)
            new_gif_data[path] = {'width': new_width, 'height': new_height, 'frame_delay': frame_delay, 'total_duration': total_duration}
    
    return new_gif_data

# Tkinter GIF Player
class GIFPlayer(tk.Toplevel):
    def __init__(self, master, gif_path, gif_data):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        
        self.gif = Image.open(gif_path)
        self.frames = [ImageTk.PhotoImage(frame.copy().resize((gif_data['width'], gif_data['height']))) for frame in ImageSequence.Iterator(self.gif)]
        self.total_frames = len(self.frames)
        self.frame_idx = 0
        self.rotation_count = 0
        
        screen_width, screen_height = 1920, 1080  # Change if needed
        x = random.randint(0, max(0, screen_width - gif_data['width'] - PADDING))
        y = random.randint(0, max(0, screen_height - gif_data['height'] - PADDING))
        self.geometry(f"{gif_data['width']}x{gif_data['height']}+{x}+{y}")
        
        self.canvas = tk.Canvas(self, width=gif_data['width'], height=gif_data['height'], highlightthickness=0)
        self.canvas.pack()
        self.img_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.frames[0])
        self.canvas.bind("<Button-1>", self.close_gif)
        
        self.frame_delay = int(gif_data['frame_delay'] * 1000)
        self.total_duration = gif_data['total_duration']
        self.animate()

    def animate(self):
        if self.frame_idx == 0 and self.rotation_count >= 3:
            self.destroy()
            return

        self.canvas.itemconfig(self.img_id, image=self.frames[self.frame_idx])
        self.frame_idx = (self.frame_idx + 1) % self.total_frames
        
        if self.frame_idx == 0:
            self.rotation_count += 1
        
        self.after(self.frame_delay, self.animate)

    def close_gif(self, event=None):
        self.destroy()

# Show GIF
def show_gif(root, gif_data):
    gif_path = random.choice(list(gif_data.keys()))
    player = GIFPlayer(root, gif_path, gif_data[gif_path])
    root.after(int(gif_data[gif_path]['total_duration']) + random.randint(WAIT_MIN, WAIT_MAX), show_gif, root, gif_data)

# Main function
def main():
    global root
    root = tk.Tk()
    root.withdraw()
    setup_database()
    gif_data = process_new_gifs()
    root.after(100, show_gif, root, gif_data)
    root.mainloop()

# Run the program
main()
