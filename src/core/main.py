import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tktooltip import ToolTip

from ui.current_week import Home
from ui.weeks_log import WeeksLog
from ui.projects import Projects
from ui.settings import Settings
from core.paths import USER_CONFIG, ICON_PATH, GIFS_PATH, SETTINGS_PATH
from ui.style import StyleManager
from core.version import install_new_version, check_new_version

import urllib.request

class Main(tk.Tk):
  def __init__(self):
    super().__init__()
    self.minsize(1200, 700)
    self.title("StudyArc")

    StyleManager(self)

    self.show_projects_var = tk.BooleanVar(value=True)
    self.show_weeks_log_var = tk.BooleanVar(value=True)
    self.show_current_week_var = tk.BooleanVar(value=True)

    try: self.iconbitmap(ICON_PATH)
    except tk.TclError: self.iconbitmap("../assets/logo.ico")

  def run(self):
    for widget in self.winfo_children():
      widget.destroy()

    menubar = tk.Menu(self)

    view_menu = tk.Menu(menubar, tearoff=0)
    view_menu.add_checkbutton(label="Show current week", command=lambda: self.run(), variable=self.show_current_week_var)
    view_menu.add_checkbutton(label="Show week log", command=lambda: self.run(), variable=self.show_weeks_log_var)
    view_menu.add_checkbutton(label="Show projects", command=lambda: self.run(), variable=self.show_projects_var)
    menubar.add_cascade(label="View", menu=view_menu)

    more_menu = tk.Menu(menubar, tearoff=0)
    more_menu.add_command(label="Settings", command=lambda: self.open_settings())
    more_menu.add_command(label="Documentation", command=lambda: self.open_help())
    more_menu.add_command(label="About", command=lambda: self.open_help())
    more_menu.add_separator()
    more_menu.add_command(label="Exit", command=lambda: self.destroy())

    menubar.add_cascade(label="Help", menu=more_menu)

    self.config(menu=menubar)

    self.container = ttk.Frame(self)
    self.container.pack(fill="both", expand=True)

    ttk.Label(self.container, text="Study Dashboard", font=(StyleManager.get_current_font(), 20, "bold")).pack(anchor="center", pady=15)

    frame_left_side = ttk.Frame(self.container)
    frame_left_side.pack(side="left", expand=True, fill="both", padx=15, pady=15)

    if self.show_current_week_var.get():
      self.current_week_frame = Home(frame_left_side, self)
      self.current_week_frame.draw_table()

    if self.show_projects_var.get():
      self.projects_frame = Projects(frame_left_side, self)
      self.projects_frame.draw()

    if self.show_weeks_log_var.get():
      self.weeks_log_frame = WeeksLog(self.container, self)
      self.weeks_log_frame.draw_table()

    if check_new_version():
      if messagebox.showinfo("Update Available", "A new version of the app is available. Close this window to make the installation will begin."):
        if install_new_version():
          messagebox.showinfo("Update Completed", "The new update has been installed, the app will shutdown and you have to reopen it to apply the new update!")

    self.mainloop()

  def open_settings(self):
    self.withdraw()
    Settings(self)

  def open_help(self):
    print("TODO help")

if __name__ == "__main__":
  main = Main()
  main.run()