import tkinter as tk
from tkinter import PhotoImage, ttk
from tkinter import simpledialog
from tkinter import messagebox

from utils.utils import resource_path

from PIL import Image, ImageTk

class LogProfile(tk.Frame):
  def __init__(self, root, cursor, conn):
    tk.Frame.__init__(self, root)
    self.root = root
    self.cursor = cursor
    self.conn = conn
  
    self.pack(fill="both", expand=True)

    self.run()

  def run(self):
    for widgets in self.winfo_children():
      widgets.destroy()
    
    frame_content = tk.Frame(self)
    frame_content.pack(side="top", anchor="center", pady=30)
    tk.Label(frame_content, text="StudyArc", font=("TkDefaultFont", 25, "bold")).pack(anchor="center", pady=30)

    frame_list_users_text = tk.Frame(frame_content)
    frame_list_users_text.pack(side="top", fill="x", pady=(0,5))
    tk.Label(frame_list_users_text, text="List users", font=("TkDefaultFont", 13)).pack(side="left")
    tk.Button(frame_list_users_text, text="Add user", command=lambda: self.create_user()).pack(side="right", padx=(10,0))

    ttk.Separator(frame_content, orient="horizontal").pack(fill="x", side="top", pady=(0,15))

    frame_cards = tk.Frame(frame_content)
    frame_cards.pack(side="top", anchor="center")

    self.cursor.execute("SELECT id, name FROM users")
    rows = self.cursor.fetchall()
    if len(rows) == 0:
      tk.Label(frame_cards, text="No users available").pack(anchor="center")
    else:
      for row in rows:
        frame_single_user = tk.Frame(frame_cards, borderwidth=1, relief="solid", width=120, height=120)
        frame_single_user.pack(side="left", padx=(10))
        frame_single_user.pack_propagate(False)

        tk.Label(frame_single_user, text=row[1], font=("TkDefaultFont", 16)).pack(side="top", pady=(10, 0))
        tk.Button(frame_single_user, text="Select", width=5, height=2, command=lambda r=row: self.select_user(int(r[0]))).pack(side="bottom", pady=(0,10))

  def select_user(self, user_id):
    self.root.user_id = user_id
    self.root.run()

  def create_user(self):
    new_username = simpledialog.askstring("New User", "Enter new username")

    self.cursor.execute("SELECT name FROM users")
    rows = self.cursor.fetchall()

    if new_username in rows:
      messagebox.showerror("New User Error", "This username already exists, try again!")
    else:
      self.cursor.execute("INSERT INTO users (name, exp, level) VALUES (?, ?, ?)", (new_username, 0, 1))
      self.conn.commit()

      self.run()


class Profile(tk.Frame):
  def __init__(self, root, user_id, cursor, conn):
    tk.Frame.__init__(self, root)
    self.root = root 
    self.user_id = user_id
    self.cursor = cursor
    self.conn = conn 

    self.config(borderwidth=1, relief="solid")
    self.pack(side="top", fill="x", padx=2)

    self.frames_gif = []
    self.frame_gif_index = 0
    self.load_gif(resource_path("../assets/profile.gif"))

    self.username = tk.StringVar(value="Username")
    self.level = 0
    self.exp = 0

    self.run()

  def run(self):
    for widgets in self.winfo_children():
      widgets.destroy()

    self.label_profile_gif = tk.Label(self)
    self.label_profile_gif.pack(side="left", fill="both")
    self.animate()

    content_right = tk.Frame(self)
    content_right.pack(side="left", fill="both", expand=True)

    frame_name_profile = tk.Frame(content_right)
    frame_name_profile.pack(side="top", fill="x", padx=10, pady=10)
    tk.Label(frame_name_profile, textvariable=self.username, font=("TkDefaultFont", 18, "bold")).pack(side="left")
    tk.Button(frame_name_profile, text="Settings", width=10, state="disabled").pack(side="right")

    frame_experience_bar = tk.Frame(content_right)
    frame_experience_bar.pack(side="top", fill="x", padx=10)
    frame_texts_experience_bar = tk.Frame(frame_experience_bar)
    frame_texts_experience_bar.pack(side="top", fill="x")
    self.experience_text = tk.Label(frame_texts_experience_bar, text=f"Exp: 1432/5000")
    self.experience_text.pack(side="left")
    self.level_user = tk.Label(frame_texts_experience_bar, text="Level: 80")
    self.level_user.pack(side="right")
    self.experience_bar = ttk.Progressbar(frame_experience_bar)
    self.experience_bar.pack(side="top", fill="x")
    self.load_stats()

  def load_gif(self, path):
    gif = Image.open(path)
    try:
      while True:
        current_frame = gif.copy()
        resized = current_frame.resize((110,110))
        converted = resized.convert("RGBA")
        tk_image = ImageTk.PhotoImage(converted)
        self.frames_gif.append(tk_image)
        gif.seek(gif.tell() + 1)
    except EOFError:
      pass

  def animate(self):
    if self.frames_gif:
      self.label_profile_gif.configure(image=self.frames_gif[self.frame_gif_index])
      self.frame_gif_index = (self.frame_gif_index + 1) % len(self.frames_gif)
      self.after(200, self.animate)

  def load_stats(self):
    self.cursor.execute("SELECT name, exp, level FROM users WHERE id = ?", (self.user_id,))
    row = self.cursor.fetchone()  
    
    experience_current_level = self.get_experience_current_level()

    self.username.set(row[0])
    self.level_user.config(text=f"Level: {row[2]}")
    self.experience_text.config(text=f"Exp: {row[1]}/{experience_current_level}")

  def get_experience_current_level(self):
    return 2000