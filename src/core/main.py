import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from core.database import Database
from ui.current_week import Home, CreateNewLog
from ui.weeks_log import WeeksLog
from ui.projects import Projects
from ui.settings import Settings
from ui.activity_calendar import ActivityCalendar
from core.paths import ICON_PATH, USER_CONFIG
from ui.style import StyleManager
from core.version import install_new_version, check_new_version, REMOTE_URL, CURRENT_VERSION, get_remote_version
from ui.login import Login
from datetime import datetime
from utils.utils import get_current_week_dates

import webbrowser
import sys

from utils.utils import seconds_to_time

class Main(tk.Tk):
  def __init__(self):
    super().__init__()
    self.geometry("1200x700")
    self.title("StudyArc")
    self.protocol("WM_DELETE_WINDOW", lambda: self.on_closing())

    StyleManager(self)

    with open(USER_CONFIG, "r") as user_config_file:
      data = json.load(user_config_file)
    self.show_metrics_frame = tk.BooleanVar(value=data["display_options"]["show_metrics_frame"])
    self.show_tables_frame = tk.BooleanVar(value=data["display_options"]["show_tables_frame"])
    self.show_charts_frame = tk.BooleanVar(value=data["display_options"]["show_charts_frame"])

    try: 
      self.iconbitmap(ICON_PATH)
    except tk.TclError:
      self.iconbitmap("../assets/logo.ico")

    self.database = Database()

    self.user_id = None
    self.withdraw()
    self.login_class = Login(self, self.database.cursor, self.database.conn)
    self.wait_window(self.login_class)

    if self.user_id is not None:
      self.run()
    else:
      self.destroy()

  def run(self):
    for widget in self.winfo_children():
      widget.destroy()

    with open(USER_CONFIG, "r") as user_config_file:
      self.data = json.load(user_config_file)

    # MENUBAR
    menubar = tk.Menu(self)
    view_menu = tk.Menu(menubar, tearoff=0)
    view_menu.add_checkbutton(label="Show Metrics Frame", command=lambda: self.change_display_options("metrics"), variable=self.show_metrics_frame)
    view_menu.add_checkbutton(label="Show Tables Frame", command=lambda: self.change_display_options("tables"), variable=self.show_tables_frame)
    view_menu.add_checkbutton(label="Show Charts Frame", command=lambda: self.change_display_options("charts"), variable=self.show_charts_frame)
    menubar.add_cascade(label="View", menu=view_menu)
    more_menu = tk.Menu(menubar, tearoff=0)
    more_menu.add_command(label="Settings", command=lambda: self.open_settings())
    more_menu.add_command(label="About", command=lambda: self.open_help())
    more_menu.add_command(label="Report bug", command=lambda: self.open_report_bug())
    more_menu.add_separator()
    more_menu.add_command(label="Exit", command=lambda: self.destroy())
    menubar.add_cascade(label="Help", menu=more_menu)
    menubar.add_command(label="Projects", command=lambda: Projects(self, self.database.cursor, self.database.conn, self.user_id))
    self.config(menu=menubar)

    PADDING = 15

    # HEADER FRAME
    header_frame = ttk.Frame(self)
    header_frame.pack(side="top", fill="x", padx=PADDING, pady=PADDING)
    ttk.Label(header_frame, text="Study Dashboard", font=("TkDefaultFont", 18, "bold")).pack(side="left", anchor="nw")
    header_right_frame = ttk.Frame(header_frame)
    header_right_frame.pack(side="right")
    current_date = datetime.now().strftime("%A, %Y-%m-%d")
    ttk.Label(header_right_frame, text=f"Today is: {current_date}", font=("TkDefaultFont", 13)).pack(side="top", pady=(5,0))
    ttk.Button(header_right_frame, text="+ New Study Log", command=lambda: CreateNewLog(self, self.user_id, self.database.cursor, self.database.conn)).pack(side="top", pady=10, fill="x")

    # METRICS FRAME
    if self.show_metrics_frame.get():
      metrics_frame = ttk.Frame(self)
      metrics_frame.pack(side="top", fill="x", pady=PADDING, padx=PADDING)
      
      ## time studied today frame
      time_studied_today_frame = ttk.Frame(metrics_frame, borderwidth=1, relief="solid")
      time_studied_today_frame.pack(side="left", fill="x", expand=True)
      ttk.Label(time_studied_today_frame, text="Time Studied Today", anchor="w", font=("TkDefaultFont", 12, "bold")).pack(side="top", fill="x", pady=(10,0), padx=10)
      self.database.cursor.execute("SELECT time FROM sessions WHERE date = ? AND user_id = ?", (datetime.now().strftime("%Y-%m-%d"), self.user_id))
      total_time = 0
      for row in self.database.cursor.fetchall():
        total_time += int(row[0])
      time_list = seconds_to_time(total_time)
      ttk.Label(time_studied_today_frame, text=f"⏱︎ {time_list[0]:02d}:{time_list[1]:02d}:{time_list[2]:02d}", anchor="w", font=("TkDefaultFont", 9)).pack(fill="x", side="top", pady=(2,10), padx=10)
      
      ## time studied this week frame
      time_studied_this_week_frame= ttk.Frame(metrics_frame, borderwidth=1, relief="solid")
      time_studied_this_week_frame.pack(side="left", fill="x", expand=True, padx=10)
      ttk.Label(time_studied_this_week_frame, text="Time Studied This Week", anchor="w", font=("TkDefaultFont", 12, "bold")).pack(side="top", fill="x", pady=(10,0), padx=10)
      monday_date, sunday_date = get_current_week_dates()
      self.database.cursor.execute("SELECT time FROM sessions WHERE date >= ? AND date <= ? AND user_id = ?", (monday_date, sunday_date, self.user_id))
      total_time = 0
      for row in self.database.cursor.fetchall(): 
        total_time += int(row[0])
      time_list = seconds_to_time(total_time)
      ttk.Label(time_studied_this_week_frame, text=f"🗓 {time_list[0]:02d}:{time_list[1]:02d}:{time_list[2]:02d}", anchor="w", font=("TkDefaultFont", 9)).pack(fill="x", side="top", pady=(2,10), padx=10)

      ## current streak frame
      current_streak_frame = ttk.Frame(metrics_frame, borderwidth=1, relief="solid")
      current_streak_frame.pack(side="right", fill="x", expand=True)
      ttk.Label(current_streak_frame, text="Current Streak", anchor="w", font=("TkDefaultFont", 12, "bold")).pack(side="top", fill="x", pady=(10,0), padx=10)
      ttk.Label(current_streak_frame, text=f"⚡︎ {self.data['data']['streak']}", anchor="w", font=("TkDefaultFont", 9)).pack(side="top", fill="x", pady=(2,10), padx=10)

    # TABLES FRAME
    if self.show_tables_frame.get():
      paned_frame = tk.PanedWindow(self, orient="horizontal")
      paned_frame.pack(side="top", fill="both", expand=True, padx=15, pady=15)

      self.current_week_frame = Home(paned_frame, self, self.user_id, self.database.cursor, self.database.conn)
      self.current_week_frame.draw_table()
      paned_frame.add(self.current_week_frame, stretch="always")
      self.weeks_log_frame = WeeksLog(paned_frame, self, self.user_id, self.database.cursor, self.database.conn)
      self.weeks_log_frame.draw()
      paned_frame.add(self.weeks_log_frame)

    # CHARTS FRAME
    if self.show_charts_frame.get(): # TODO: CHARTS NEEDS TO BE AT THE CENTER, create texts that says "each column is a week etc..."
      charts_frame = ttk.Frame(self)
      charts_frame.pack(side="top", fill="x", pady=PADDING, padx=PADDING)
      self.activity_calendar = ActivityCalendar(charts_frame, self.user_id, self.database.cursor, self.database.conn)
      self.activity_calendar.draw()

    if self.data["version_info"]["auto_update"]:
      if check_new_version():
        if messagebox.showinfo("Update Available", f"A new version of this app is available!\n\nv{CURRENT_VERSION} -> v{get_remote_version(REMOTE_URL)}\n\nPlease click ok for the installation to begin. The app will close and reopen automatically after the update."):
          install_new_version(self)

    self.mainloop()

  def open_settings(self):
    self.withdraw()
    Settings(self)

  def open_help(self):
    print("TODO help")

  def open_report_bug(self):
    webbrowser.open_new_tab("https://docs.google.com/forms/d/e/1FAIpQLSdgcSgDJqZkh0PHvuEgpQuhq07JhnfQNFKfcyhdwx-WRJWm0g/viewform?usp=sharing&ouid=107040900145910921050")

  def on_closing(self):
    self.database.close()
    self.destroy()
    sys.exit()

  def change_display_options(self, frame_changed):
    if frame_changed == "metrics":
      with open(USER_CONFIG, "r") as user_config_file:
        data = json.load(user_config_file)
      data["display_options"]["show_metrics_frame"] = self.show_metrics_frame.get()

      with open(USER_CONFIG, "w") as user_config_file_write:
        user_config_file_write.write(json.dumps(data, indent=2))

    elif frame_changed == "tables":
      with open(USER_CONFIG, "r") as user_config_file:
        data = json.load(user_config_file)
      data["display_options"]["show_tables_frame"] = self.show_metrics_frame.get()

      with open(USER_CONFIG, "w") as user_config_file_write:
        user_config_file_write.write(json.dumps(data, indent=2))

    elif frame_changed == "charts":
      with open(USER_CONFIG, "r") as user_config_file:
        data = json.load(user_config_file)
      data["display_options"]["show_charts_frame"] = self.show_metrics_frame.get()

      with open(USER_CONFIG, "w") as user_config_file_write:
        user_config_file_write.write(json.dumps(data, indent=2))


    self.run()

if __name__ == "__main__":
  main = Main()