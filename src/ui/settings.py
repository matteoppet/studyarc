from tkinter import messagebox
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

from utils.utils import export_logs_to_csv, LogOldSession
from core.__init__ import CONFIG_FILE, check_for_update
from core.version import CURRENT_VERSION

import json

class Settings(ctk.CTkToplevel):
  def __init__(self, root, cursor, conn, user_id):
    ctk.CTkToplevel.__init__(self, root)
    self.root = root
    self.cursor = cursor
    self.conn = conn
    self.user_id = user_id

    self.title("Settings")
    self.geometry(f"+{self.winfo_width()/2}+{self.winfo_height()/2}")
    self.transient(self.root)
    self.minsize(500, 500)

    self.username = tk.StringVar(value="Bread Pitt")
    self.daily_goal_hours = tk.IntVar(value=0)
    self.daily_goal_minutes = tk.IntVar(value=0)

    self.themes_available = ["light", "dark"]
    self.themes_selected = tk.StringVar(value="light")
    self.themes_selected.trace_add("write", self.change_theme)

    self.load_info()

    self.run()

  def run(self):
    frame_content = ctk.CTkFrame(self, fg_color="transparent")
    frame_content.pack(fill="both", expand=True)
    
    ctk.CTkLabel(frame_content, text="Settings", font=("TkDefaultFont", 30)).pack(side="top", anchor="w", padx=10, pady=10)

    ttk.Separator(frame_content, orient="horizontal").pack(side="top", fill="x")

    tabview = ctk.CTkTabview(master=frame_content)
    tabview.pack(side="top", anchor="n", fill="both", padx=10, pady=10, expand=True)

    tabview.add("General")
    tabview.add("Appearance")
    tabview.add("Version")

    tabview.set("General")

    self.draw_general_tab(tabview.tab("General"))
    self.draw_appearance_tab(tabview.tab("Appearance"))
    self.draw_version_tab(tabview.tab("Version"))

  def draw_general_tab(self, frame):
    ######### PROFILE
    ctk.CTkLabel(frame, text="Profile", font=("TkDefaultFont", 20, "bold")).pack(side="top", anchor="w", padx=10, pady=(10,0))
    ttk.Separator(frame, orient="horizontal").pack(side="top", fill="x", padx=10, pady=5)

    username_frame = ctk.CTkFrame(frame)
    username_frame.pack(side="top", fill="x", padx=10, pady=(5,5))
    ctk.CTkLabel(username_frame, text="Username").pack(side="left")
    ctk.CTkButton(username_frame, text="Set", width=50, command=lambda: self.set_new_username()).pack(side="right", padx=(7,0))
    ctk.CTkEntry(username_frame, textvariable=self.username).pack(side="right")

    ######## ACTIVITY
    ctk.CTkLabel(frame, text="Activity", font=("TkDefaultFont", 20, "bold")).pack(side="top", anchor="w", padx=10, pady=(10,0))
    ttk.Separator(frame, orient="horizontal").pack(side="top", fill="x", padx=10, pady=5)

    daily_goal_frame = ctk.CTkFrame(frame)
    daily_goal_frame.pack(side="top", fill="x", padx=10, pady=(5,10))
    ctk.CTkLabel(daily_goal_frame, text="Daily goal").pack(side="left")

    ctk.CTkButton(daily_goal_frame, text="Set", width=50, command=lambda: self.set_new_daily_goal()).pack(side="right", padx=(7,0))

    ctk.CTkLabel(daily_goal_frame, text="min").pack(side="right", padx=(3,0))
    ctk.CTkEntry(daily_goal_frame, textvariable=self.daily_goal_minutes, width=30).pack(side="right")

    ctk.CTkLabel(daily_goal_frame, text="hour").pack(side="right", padx=(3,5))
    ctk.CTkEntry(daily_goal_frame, textvariable=self.daily_goal_hours, width=30).pack(side="right")

    log_old_session_frame = ctk.CTkFrame(frame)
    log_old_session_frame.pack(side="top", fill="x", padx=10, pady=(0,10))
    ctk.CTkLabel(log_old_session_frame, text="Log old session").pack(side="left")
    ctk.CTkButton(log_old_session_frame, text="Log", width=80, command=lambda: LogOldSession(self, self.cursor, self.conn, self.user_id)).pack(side="right")

    export_logs_to_csv_frame = ctk.CTkFrame(frame)
    export_logs_to_csv_frame.pack(side="top", fill="x", padx=10, pady=(0,10))
    ctk.CTkLabel(export_logs_to_csv_frame, text="Export logs to CSV").pack(side="left")
    ctk.CTkButton(export_logs_to_csv_frame, text="Export", width=80, command=lambda: export_logs_to_csv(self.cursor, self.user_id)).pack(side="right")

    clear_streak = ctk.CTkFrame(frame)
    clear_streak.pack(side="top", fill="x", padx=10)
    ctk.CTkLabel(clear_streak, text="Clear activity streak").pack(side="left")
    ctk.CTkButton(clear_streak, text="Clear", width=80, fg_color="red", command=lambda: self.set_clear_streak()).pack(side="right")

  def draw_appearance_tab(self, frame):
    ctk.CTkLabel(frame, text="Activity", font=("TkDefaultFont", 20, "bold")).pack(side="top", anchor="w", padx=10, pady=(10,0))
    ttk.Separator(frame, orient="horizontal").pack(side="top", fill="x", padx=10, pady=5)

    theme_frame = ctk.CTkFrame(frame)
    theme_frame.pack(side="top", fill="x", padx=10, pady=5)
    ctk.CTkLabel(theme_frame, text="Theme").pack(side="left")
    ctk.CTkOptionMenu(theme_frame, values=self.themes_available, variable=self.themes_selected).pack(side="right")

  def draw_version_tab(self, frame):
    ctk.CTkLabel(frame, text="Version", font=("TkDefaultFont", 20, "bold")).pack(side="top", anchor="w", padx=10, pady=(10,0))
    ttk.Separator(frame, orient="horizontal").pack(side="top", fill="x", padx=10, pady=5)

    current_version_frame = ctk.CTkFrame(frame)
    current_version_frame.pack(side="top", fill="x", padx=10, pady=5)
    ctk.CTkLabel(current_version_frame, text="Current version").pack(side="left")
    ctk.CTkLabel(current_version_frame, text=f"v{CURRENT_VERSION}").pack(side="right")
    
    check_for_update_frame = ctk.CTkFrame(frame)
    check_for_update_frame.pack(side="top", fill="x", padx=10, pady=5)
    ctk.CTkLabel(check_for_update_frame, text="Check for updates").pack(side="left")
    ctk.CTkButton(check_for_update_frame, text="Check", width=80, command=lambda: check_for_update(self)).pack(side="right")

  def set_new_username(self):
    self.cursor.execute("UPDATE users SET name = ? WHERE id = ?", (self.username.get(), self.user_id,))
    self.conn.commit()

  def set_new_daily_goal(self):
    with open(CONFIG_FILE, "r") as config_read:
      data = json.load(config_read)

    data["daily_session_goal"][str(self.user_id)] = [
      abs(self.daily_goal_hours.get()), abs(self.daily_goal_minutes.get())
    ]

    with open(CONFIG_FILE, "w") as config_write:
      config_write.write(json.dumps(data, indent=2))

  def set_clear_streak(self):
    with open(CONFIG_FILE, "r") as config_read:
      data = json.load(config_read)

    if messagebox.askyesno("Streak Reset", f"Are you sure to reset your current streak?\n\nDays: {data['streaks'][str(self.user_id)]['current_streak']}"):
      data["streaks"][str(self.user_id)]["current_streak"] = 0

      with open(CONFIG_FILE, "w") as config_write:
        config_write.write(json.dumps(data, indent=2))

  def change_theme(self, *args):
    ctk.set_appearance_mode(self.themes_selected.get())

    with open(CONFIG_FILE, "r") as config_read:
      data = json.load(config_read)

    data["themes"][str(self.user_id)] = self.themes_selected.get()

    with open(CONFIG_FILE, "w") as config_write:
      config_write.write(json.dumps(data, indent=2))

  def load_info(self):
    self.cursor.execute("SELECT name FROM users WHERE id = ?", (self.user_id,))
    row = self.cursor.fetchone()

    self.username.set(row[0])

    with open(CONFIG_FILE, "r") as config_read:
      data = json.load(config_read)

    self.daily_goal_hours.set(data["daily_session_goal"][str(self.user_id)][0])
    self.daily_goal_minutes.set(data["daily_session_goal"][str(self.user_id)][1])
    self.themes_selected.set(data["themes"][str(self.user_id)])