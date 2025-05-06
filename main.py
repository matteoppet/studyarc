import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from PIL import Image, ImageTk
import sys
import os

from home import Home
from weeks_log import WeeksLog

# class Settings(tk.Toplevel):
#   def __init__(self, root):
#     super().__init__()
#     self.title("Settings")
#     self.minsize(500,500)

#     self.languages_available = ["English"]
#     self.start_week_available = ["Monday", "Sunday"]

#     self.sidepanel_frame = None
#     self.main_container = tk.Frame(self)
#     self.main_container.pack(fill="both", expand=True)
#     self.content_frame = tk.Frame(self.main_container)
#     self.content_frame.pack(side="right", fill="both", expand=True)

#     self.run_appearance_frame()
  
#   def run_sidepanel_frame(self):
#     if self.sidepanel_frame:
#       self.sidepanel_frame.destroy()

#     self.color_sidepanel_frame_background = "light gray"
#     self.sidepanel_frame = tk.Frame(self.main_container, width=150, background=self.color_sidepanel_frame_background)
#     self.sidepanel_frame.pack(side="left", fill="y")

#     tk.Label(self.sidepanel_frame, text="Settings", font=("Arial 16 bold"), background=self.color_sidepanel_frame_background).pack(side="top", anchor="center", pady=15, padx=15)

#     tk.Button(self.sidepanel_frame, text="Appearance", command=lambda: self.run_appearance_frame()).pack(side="top", anchor="center", fill="x")
#     tk.Button(self.sidepanel_frame, text="Preferences", command=lambda: self.run_preferences_frame()).pack(side="top", anchor="center", fill="x", pady=5)
#     tk.Button(self.sidepanel_frame, text="Little help", command=lambda: self.run_donation_frame()).pack(side="top", anchor="center", fill="x")

#   def clear_content_frame(self):
#     for widget in self.content_frame.winfo_children():
#       widget.destroy()

#   def run_appearance_frame(self):
#     self.run_sidepanel_frame()
#     self.clear_content_frame()

#     tk.Label(self.content_frame, text="Working on it...").pack(padx=15, pady=15)

#   def run_preferences_frame(self):
#     self.run_sidepanel_frame()
#     self.clear_content_frame()

#     with open('settings.json', "r") as file:
#       settings_data = json.load(file)

#     tk.Label(self.content_frame, text="Preferences", font=("Arial 18 bold")).pack(padx=15, pady=15, anchor="nw")
#     ttk.Separator(self.content_frame, orient="horizontal").pack(fill="x")

#     for setting_name, value in settings_data["preferences"].items():
#       frame_setting = tk.Frame(self.content_frame)
#       frame_setting.pack(side="top", fill="x", pady=10, padx=15, ipady=5)

#       tk.Label(frame_setting, text=setting_name.capitalize()).pack(side="left", padx=10)

#   def run_donation_frame(self):
#     self.run_sidepanel_frame()
#     self.clear_content_frame()

#     tk.Label(self.content_frame, text="hola").pack(padx=15, pady=15)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Main(tk.Tk):
  def __init__(self):
    super().__init__()
    self.minsize(1000, 500)
    self.title("Study tracker")

    logo_path = resource_path("assets/logo_transparent_resized.png")
    ico = Image.open(logo_path)
    photo = ImageTk.PhotoImage(ico)
    self.wm_iconphoto(False, photo)

  def run(self):
    for widget in self.winfo_children():
      widget.destroy()

    menubar = tk.Menu(self)
    self.config(menu=menubar)

    more_menu = tk.Menu(menubar, tearoff=0)
    more_menu.add_command(label="Settings", command=lambda: self.open_settings())
    more_menu.add_command(label="Help", command=lambda: self.open_help())

    menubar.add_cascade(label="More", menu=more_menu)

    self.container = tk.Frame(self)
    self.container.pack(fill="both", expand=True)

    tk.Label(self.container, text="Study Tracker", font=("Arial 18 bold")).pack(anchor="center", padx=15, pady=15)

    self.home_frame = Home(self.container, self)
    self.home_frame.draw_table()

    self.weeks_log_frame = WeeksLog(self.container, self)
    self.weeks_log_frame.draw_table()

    self.mainloop()

  def open_settings(self):
    print("settings")

  def open_help(self):
    print("TODO help")

if __name__ == "__main__":
  main = Main()
  main.run()
