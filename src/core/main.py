import tkinter as tk
from tkinter import ttk

from ui.timer import Timer
from ui.projects import Projects
from ui.activity import CurrentWeek

from core.database import Database
from core.settings import COLOR_BACKGROUND_SIDEPANEL
from utils.utils import resource_path

class StudyArc(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title("StudyArc")

    self.database = Database()
    self.cursor = self.database.cursor
    self.conn = self.database.conn

    try:
      self.iconbitmap("../assets/icon.ico")
    except tk.TclError:
      self.iconbitmap(resource_path("assets/icon.ico"))

    self.user_id = 1

  def run(self):
    for widgets in self.winfo_children():
      widgets.destroy()

    frame_timer_projects = tk.Frame(self)
    frame_timer_projects.pack(side="top", fill="both", expand=True)

    frame_left = tk.Frame(frame_timer_projects, bg=COLOR_BACKGROUND_SIDEPANEL)
    frame_left.pack(side="left", fill="both", expand=True)

    tk.Label(frame_left, text="Study Dashboard", font=("TkDefaultFont", 22, "bold"), anchor="w", bg=COLOR_BACKGROUND_SIDEPANEL).pack(side="top", fill="x", pady=15, padx=25)

    self.timer_frame = Timer(frame_left, self, self.cursor, self.conn)
    self.current_week_activity = CurrentWeek(frame_left, self.cursor, self.conn, self.user_id)

    frame_right = tk.Frame(frame_timer_projects)
    frame_right.pack(side="left", fill="both", expand=True)

    self.projects_frame = Projects(frame_right, self.cursor, self.conn, self.user_id)

    self.mainloop()

if __name__ == "__main__":
  app = StudyArc()
  app.run()