import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

from ui.timer import Timer
from ui.projects import Projects
from ui.activity import CurrentWeek
from ui.profile import Profile, LogIn

from core.database import Database
from utils.utils import resource_path
from core.__init__ import check_for_update, CONFIG_FILE

import json

class StudyArc(ctk.CTk):
  def __init__(self):
    super().__init__()
    self.title("StudyArc")
    self.geometry("1480x900")

    self.database = Database()
    self.cursor = self.database.cursor
    self.conn = self.database.conn

    ctk.set_appearance_mode("light")

    try:
      self.iconbitmap("../assets/icon.ico")
    except tk.TclError:
      self.iconbitmap(resource_path("assets/icon.ico"))

    self.user_id = None

  def run(self):
    for widgets in self.winfo_children():
      widgets.destroy()

    if self.user_id is None:
      LogIn(self, self.cursor, self.conn)
    else:
      with open(CONFIG_FILE, "r") as config_read:
        data = json.load(config_read)

      ctk.set_appearance_mode(data["themes"][str(self.user_id)])

      frame_timer_projects = ctk.CTkFrame(self, fg_color="transparent")
      frame_timer_projects.pack(side="top", fill="both", expand=True)

      frame_left = ctk.CTkFrame(frame_timer_projects, fg_color="transparent")
      frame_left.pack(side="left", fill="both")

      ctk.CTkLabel(frame_left, text="Study Dashboard", font=("TkDefaultFont", 28, "bold"), anchor="w").pack(side="top", fill="x", pady=15, padx=25)

      self.timer_frame = Timer(frame_left, self, self.cursor, self.conn, self.user_id)
      self.current_week_activity = CurrentWeek(frame_left, self.cursor, self.conn, self.user_id)

      ttk.Separator(frame_timer_projects, orient="vertical").pack(side="left", fill="y", padx=10)

      frame_right = ctk.CTkFrame(frame_timer_projects, fg_color="transparent")
      frame_right.pack(side="left", fill="both", expand=True)

      self.profile_frame = Profile(frame_right, self.user_id, self.cursor, self.conn)
      self.projects_frame = Projects(frame_right, self.cursor, self.conn, self.user_id, self.profile_frame)

    self.mainloop()

if __name__ == "__main__":
  app = StudyArc()
  check_for_update(app)
  app.run()