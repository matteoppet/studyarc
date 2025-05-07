import tkinter as tk
from tkinter import ttk

from home import Home
from weeks_log import WeeksLog
from utils import resource_path

import webbrowser
import json
from pathlib import Path
import csv

### CREATION FILES NEEDED

base_dir = Path("C:/study_tracker")
csv_files = {
  "data_current_week.csv": [["Day", "Time", "Description"]],
  "data_weeks_log.csv": [["Week number","Total Time","Summary"]],
  "data.json": {"last_day": ""}
}

if not base_dir.exists():
  base_dir.mkdir(parents=True)

  for filename, headers in csv_files.items():
    file_path = base_dir / filename

    if filename.endswith(".csv"):
      with open(file_path, "w", newline="") as f:
        csv.writer(f).writerows(headers)

    elif filename.endswith(".json"):
      json_object = json.dumps(headers, indent=2)

      with open(file_path, "w") as f:
        f.write(json_object)

###

class Settings(tk.Toplevel):
  def __init__(self, root):
    super().__init__()
    self.title("Settings")
    self.minsize(500,500)

    self.languages_available = ["English"]
    self.start_week_available = ["Monday", "Sunday"]

    self.sidepanel_frame = None
    self.main_container = tk.Frame(self)
    self.main_container.pack(fill="both", expand=True)
    self.content_frame = tk.Frame(self.main_container)
    self.content_frame.pack(side="right", fill="both", expand=True)

    self.run_appearance_frame()
  
  def run_sidepanel_frame(self):
    if self.sidepanel_frame:
      self.sidepanel_frame.destroy()

    self.color_sidepanel_frame_background = "light gray"
    self.sidepanel_frame = tk.Frame(self.main_container, width=150, background=self.color_sidepanel_frame_background)
    self.sidepanel_frame.pack(side="left", fill="y")

    tk.Label(self.sidepanel_frame, text="Settings", font=("Arial 16 bold"), background=self.color_sidepanel_frame_background).pack(side="top", anchor="center", pady=15, padx=15)

    tk.Button(self.sidepanel_frame, text="Appearance", command=lambda: self.run_appearance_frame()).pack(side="top", anchor="center", fill="x")
    tk.Button(self.sidepanel_frame, text="Preferences", command=lambda: self.run_preferences_frame()).pack(side="top", anchor="center", fill="x", pady=5)
    tk.Button(self.sidepanel_frame, text="Little help", command=lambda: self.run_donation_frame()).pack(side="top", anchor="center", fill="x")

  def clear_content_frame(self):
    for widget in self.content_frame.winfo_children():
      widget.destroy()

  def run_appearance_frame(self):
    self.run_sidepanel_frame()
    self.clear_content_frame()

    tk.Label(self.content_frame, text="Appearance", font=("Arial 18 bold")).pack(padx=15, pady=15, anchor="nw")
    ttk.Separator(self.content_frame, orient="horizontal").pack(fill="x")

    tk.Label(self.content_frame, text="Working on it...").pack(padx=15, pady=15)

  def run_preferences_frame(self):
    self.run_sidepanel_frame()
    self.clear_content_frame()

    with open('data.json', "r") as file:
      settings_data = json.load(file)

    tk.Label(self.content_frame, text="Preferences", font=("Arial 18 bold")).pack(padx=15, pady=15, anchor="nw")
    ttk.Separator(self.content_frame, orient="horizontal").pack(fill="x")

    tk.Label(self.content_frame, text="Working on it...").pack(padx=15, pady=15)

  def run_donation_frame(self):
    self.run_sidepanel_frame()
    self.clear_content_frame()

    frame_title = tk.Frame(self.content_frame)
    frame_title.pack(padx=15, pady=15, anchor="nw")
    tk.Label(frame_title, text="Little help from you!", font=("Arial 18 bold")).pack(anchor="nw")

    ttk.Separator(self.content_frame, orient="horizontal").pack(fill="x")

    frame_texts = tk.Frame(self.content_frame)
    frame_texts.pack(padx=15, pady=15, anchor="nw")

    tk.Label(frame_texts, text="💛 Made with love (and a lot of late-night coding)!", font=("Arial 10 bold")).pack(anchor="nw")
    tk.Label(frame_texts, text=f"If this little tracker helps make your days easier, i'd be thrilled if you sent a coffe my way\nNo pressure -- One coffe = one happy coder☕", justify="left").pack(anchor="nw")
    link = tk.Label(frame_texts, text="👉 buymeacoffee.com/matteopet", fg="blue", cursor="hand2")
    link.pack(anchor="nw")
    link.bind("<Button-1>", lambda e: webbrowser.open_new("https://buymeacoffee.com/matteopet"))

    tk.Label(frame_texts, text="Thank you!").pack(anchor="center", pady=15)

class Main(tk.Tk):
  def __init__(self):
    super().__init__()
    self.minsize(1000, 500)
    self.title("Study tracker")

    icon = resource_path("assets/logo_transparent_resized.ico")
    self.iconbitmap(icon)

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
    Settings(self)

  def open_help(self):
    print("TODO help")

if __name__ == "__main__":
  main = Main()
  main.run()