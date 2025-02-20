import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import random
import os
import sqlite3
import json

# Set the folder containing the GIFs
GIF_FOLDER = r"C:\Users\Dimas\MyPythonScripts\AutoGif\gif"
DB_FILE = "gif_data.db"

PADDING = 100
HEIGHT_MAX = 240
WIDTH_MAX = 240

WAIT_MIN = 30 * 1000
WAIT_MAX = 60 * 1000

IS_ACTIVE = False

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
            frame_durations TEXT,  -- Store list of frame durations as JSON
            total_duration INTEGER,
            total_frames INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Get stored GIF data
# Get stored GIF data
def get_stored_gifs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT path, width, height, frame_durations, total_duration, total_frames FROM gifs")
    
    data = {}
    for row in cursor.fetchall():
        path, width, height, frame_durations_json, total_duration, total_frames = row
        frame_durations = json.loads(frame_durations_json)  # Convert JSON back to list
        data[path] = {
            'width': width,
            'height': height,
            'frame_durations': frame_durations,
            'total_duration': total_duration,
            'total_frames': total_frames
        }

    conn.close()
    return data


# Store new GIF data
def store_gif_data(path, width, height, frame_durations, total_duration, total_frames):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Convert frame durations list to JSON string
    frame_durations_json = json.dumps(frame_durations)
    
    cursor.execute("""
        INSERT OR REPLACE INTO gifs (path, width, height, frame_durations, total_duration, total_frames)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (path, width, height, frame_durations_json, total_duration, total_frames))
    
    conn.commit()
    conn.close()


# Process and store new GIFs
def process_new_gifs():
    stored_gifs = get_stored_gifs()
    gif_paths = {os.path.join(GIF_FOLDER, f) for f in os.listdir(GIF_FOLDER) if f.lower().endswith(".gif")}
    
    # Remove GIFs from DB that no longer exist in the folder
    stored_paths = set(stored_gifs.keys())
    missing_gifs = stored_paths - gif_paths  # GIFs in DB but not in folder
    
    if missing_gifs:
        delete_gifs_from_db(missing_gifs)

    new_gif_data = {}
    max_width, max_height = WIDTH_MAX, HEIGHT_MAX
    
    for path in gif_paths:
        if path in stored_gifs:
            new_gif_data[path] = stored_gifs[path]  # Load stored data
        else:
            gif = Image.open(path)
            frame_durations = []  # Store all frame durations
            
            # Collect durations for each frame
            for frame in ImageSequence.Iterator(gif):
                frame_durations.append(frame.info.get("duration", 30))  # Default to 30ms if missing

            total_frames = len(frame_durations)
            total_duration = sum(frame_durations)  # Total duration in ms
            
            # Compute scaling factor (only scales down, not up)
            scale_factor = min(max_width / gif.width, max_height / gif.height, 1)
            new_width = int(gif.width * scale_factor)
            new_height = int(gif.height * scale_factor)

            # Store GIF data with all frame durations
            store_gif_data(path, new_width, new_height, frame_durations, total_duration, total_frames)
            new_gif_data[path] = {
                'width': new_width, 
                'height': new_height, 
                'frame_durations': frame_durations, 
                'total_duration': total_duration, 
                'total_frames': total_frames
            }
    
    return new_gif_data


def delete_gifs_from_db(missing_gifs):
    """Delete GIFs from the database that no longer exist in the folder."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.executemany("DELETE FROM gifs WHERE path = ?", [(path,) for path in missing_gifs])
    conn.commit()
    conn.close()

recent_gifs = []
HISTORY_LIMIT = 8

def get_next_gif(gif_data):
    global recent_gifs
    available_gifs = list(set(gif_data.keys()) - set(recent_gifs))
    if not available_gifs:
        recent_gifs.clear()
        available_gifs = list(gif_data.keys())
    gif_path = random.choice(available_gifs)
    recent_gifs.append(gif_path)
    if len(recent_gifs) > HISTORY_LIMIT:
        recent_gifs.pop(0)
    return gif_path

import tkinter as tk
import random
from PIL import Image, ImageTk, ImageSequence

PADDING = 10  # Adjustable padding for positioning
IS_ACTIVE = False  # Global flag for active GIF state

# Tkinter GIF Player
class GIFPlayer(tk.Toplevel):
    def __init__(self, master, gif_path, gif_data):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        global IS_ACTIVE
        IS_ACTIVE = True

        # Load pre-stored frame durations
        self.frame_delays = gif_data['frame_durations']  # Load stored durations from DB
        self.total_frames = len(self.frame_delays)

        # Load GIF and resize frames
        self.gif = Image.open(gif_path)
        self.frames = [
            ImageTk.PhotoImage(frame.copy().resize((gif_data['width'], gif_data['height'])))
            for frame in ImageSequence.Iterator(self.gif)
        ]
        
        self.frame_idx = 0
        self.rotation_count = 0
        
        # Get screen dimensions
        screen_width, screen_height = 1920, 1080
        restricted_width = screen_width * 3 // 4  # 3/4 of the width (bottom-right area)
        restricted_height = screen_height // 2  # 1/2 of the height

        # Random position within bottom-right area
        x = random.randint(restricted_width, max(0, screen_width - gif_data['width'] - PADDING))
        y = random.randint(restricted_height, max(0, screen_height - gif_data['height'] - PADDING))

        self.geometry(f"{gif_data['width']}x{gif_data['height']}+{x}+{y}")

        # Random position over whole screen (optional)
        # x = random.randint(0, max(0, screen_width - gif_data['width'] - PADDING))
        # y = random.randint(0, max(0, screen_height - gif_data['height'] - PADDING))
        # self.geometry(f"{gif_data['width']}x{gif_data['height']}+{x}+{y}")
        
        self.canvas = tk.Canvas(self, width=gif_data['width'], height=gif_data['height'], highlightthickness=0)
        self.canvas.pack()
        self.img_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.frames[0])
        self.canvas.bind("<Button-1>", self.close_gif)
        
        self.animate()

    def animate(self):
        """Animates the GIF based on stored frame durations."""
        if self.frame_idx == 0 and self.rotation_count >= 3:
            self.close_gif()
            return

        self.canvas.itemconfig(self.img_id, image=self.frames[self.frame_idx])
        
        # Ensure frame delay is within range
        delay = self.frame_delays[self.frame_idx] if self.frame_idx < self.total_frames else 30
        
        self.frame_idx = (self.frame_idx + 1) % self.total_frames

        # Track how many times the GIF has looped
        if self.frame_idx == 0:
            self.rotation_count += 1
        
        self.after(delay, self.animate)

    def close_gif(self, event=None):
        """Destroy the GIF window and set flag to False."""
        global IS_ACTIVE
        IS_ACTIVE = False  # Mark GIF as finished
        self.destroy()

# Show GIF
def show_gif(root, gif_data):
    global IS_ACTIVE
    if not IS_ACTIVE:
        gif_path = get_next_gif(gif_data)
        player = GIFPlayer(root, gif_path, gif_data[gif_path])
        root.after(random.randint(WAIT_MIN, WAIT_MAX), show_gif, root, gif_data)
    else:
        root.after(1000, show_gif, root, gif_data)
    

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
