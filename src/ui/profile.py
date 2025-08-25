import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox

import math

from core import update_base_config_file
from ui.settings import Settings


class LogIn(ctk.CTkFrame):
  def __init__(self, root, cursor, conn):
    ctk.CTkFrame.__init__(self, root)
    self.root = root
    self.cursor = cursor
    self.conn = conn
    
    self.pack(fill="both", expand=True)

    self.run()

  def run(self):
    for widgets in self.winfo_children():
      widgets.destroy()

    self.cursor.execute("SELECT id, name FROM users")
    rows = self.cursor.fetchall()

    frame_content = ctk.CTkFrame(self)
    frame_content.pack(side="top", anchor="center", pady=30)
    ctk.CTkLabel(frame_content, text="StudyArc", font=("TkDefaultFont", 35, "bold")).pack(anchor="center", pady=30, padx=30)
    
    frame_list_users_text = ctk.CTkFrame(frame_content, fg_color="transparent")
    frame_list_users_text.pack(side="top", fill="x", pady=(0,5), padx=10)
    ctk.CTkLabel(frame_list_users_text, text="List Users").pack(side="left")
    ctk.CTkButton(frame_list_users_text, text="Add User", command=lambda: self.add_user(), width=90, state="disabled" if len(rows) == 4 else "active").pack(side="right", padx=(30,0))

    ttk.Separator(frame_content, orient="horizontal").pack(side="top", fill="x", pady=(0,15))

    frame_cards = ctk.CTkFrame(frame_content, fg_color="transparent")
    frame_cards.pack(side="top", anchor="center", pady=(0,15))

    if len(rows) == 0:
      ctk.CTkLabel(frame_cards, text="No Users").pack(anchor="center")
    else:
      for row in rows:
        frame_user = ctk.CTkFrame(frame_cards, width=120, height=120)
        frame_user.pack(side="left", padx=(10,10))
        frame_user.pack_propagate(False)

        ctk.CTkLabel(frame_user, text=row[1], font=("TkDefaultFont", 16)).pack(side="top", pady=(10,0))
        ctk.CTkButton(frame_user, text="Select", command=lambda r=row: self.select(int(r[0]))).pack(side="bottom", fill="x", padx=10, pady=(0,10))

  def add_user(self):
    username_dialog = ctk.CTkInputDialog(title="New User", text="Enter username")
    username = username_dialog.get_input()

    if username:
      self.cursor.execute("INSERT INTO users (name, exp, level) VALUES (?, ?, ?)", (username, 0, 1))
      self.conn.commit()

      update_base_config_file(self.cursor.lastrowid)

      self.run()

  def select(self, user_id):
    self.root.user_id = user_id
    self.root.run()


class Profile(ctk.CTkFrame):
  def __init__(self, root, controller, user_id, cursor, conn):
    ctk.CTkFrame.__init__(self, root)
    self.root = root
    self.user_id = user_id
    self.controller = controller
    self.cursor = cursor
    self.conn = conn

    self.pack(side="top", fill="x", padx=10, pady=10)

    self.username = ""
    self.level = 1
    self.xp = 0
    
    self.load_stats()
    self.run()

  def run(self):
    for widgets in self.winfo_children():
      widgets.destroy()

    frame_title = ctk.CTkFrame(self, fg_color="transparent")
    frame_title.pack(side="top", fill="x", padx=15, pady=(15, 10))
    ctk.CTkLabel(frame_title, text=self.username, font=("TkDefaultFont", 25, "bold")).pack(side="left")
    ctk.CTkButton(frame_title, text="Settings", command=lambda: self.open_settings()).pack(side="right")

    frame_level_xp = ctk.CTkFrame(self, fg_color="transparent")
    frame_level_xp.pack(side="top", fill="x", padx=15)
    self.label_xp = ctk.CTkLabel(frame_level_xp, text=f"XP: {self.xp}/{self.get_max_xp_level(self.level)}")
    self.label_xp.pack(side="left")
    self.label_level = ctk.CTkLabel(frame_level_xp, text=f"Level: {self.level}")
    self.label_level.pack(side="right")

    self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate", width=self.get_max_xp_level(self.level))
    self.progress_bar.pack(side="top", fill="x", padx=15, pady=(0,15))
    self.progress_bar.set(self.xp / self.get_max_xp_level(self.level))

  def set_increase_xp(self, xp_to_give):
    self.xp += xp_to_give

    if self.check_new_level_reached():
      self.xp -= self.get_max_xp_level(self.level)
      self.level += 1

      self.cursor.execute("UPDATE users SET exp = ?, level = level + 1 WHERE id = ?", (self.xp, self.user_id,))
      self.conn.commit()

      messagebox.showinfo("New Level Reached!", f"🎉 Level Up! You’ve reached Level {self.level}\n\nKeep pushing your limits!")
    else:
      self.cursor.execute("UPDATE users SET exp = ? WHERE id = ?", (self.xp, self.user_id,))
      self.conn.commit()

    self.label_xp.configure(text=f"XP: {self.xp}/{self.get_max_xp_level(self.level)}")
    self.label_level.configure(text=f"Level: {self.level}")
    self.progress_bar.set(self.xp / self.get_max_xp_level(self.level))

  def set_reward_session(self, minutes):
    return math.floor(minutes * 0.4)
  
  def set_reward_task(self):
    return 5
  
  def get_max_xp_level(self, level):
    return 60*level
  
  def get_current_level(self):
    self.cursor.execute("SELECT level FROM users WHERE id = ?", (self.user_id,))
    return self.cursor.fetchone()[0]
  
  def load_stats(self):
    self.cursor.execute("SELECT name, exp, level FROM users WHERE id = ?", (self.user_id,))
    row = self.cursor.fetchone()  

    self.username = row[0]
    self.xp = row[1]
    self.level = row[2]

  def check_new_level_reached(self):
    current_level = self.get_current_level()
    max_xp_current_level = self.get_max_xp_level(current_level)

    if self.xp >= max_xp_current_level:
      return True
    
  def open_settings(self):
    Settings(self, self.cursor, self.conn, self.user_id)