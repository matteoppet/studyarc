import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

from datetime import timedelta, date
import json

from utils.utils import get_seconds_from_time, get_time_from_seconds, format_time
from core.__init__ import CONFIG_FILE

class CurrentWeek(ctk.CTkFrame):
  def __init__(self, root, cursor, conn, user_id):
    ctk.CTkFrame.__init__(self, root)
    self.pack(side="top", fill="both", anchor="n", padx=25, pady=(30,15))

    self.cursor = cursor
    self.conn = conn
    self.user_id = user_id

    self.run()

  def run(self):
    for widgets in self.winfo_children():
      widgets.destroy()

    TODAY = date.today()
    MONDAY = TODAY - timedelta(days=TODAY.weekday())

    header_frame = ctk.CTkFrame(self, fg_color="transparent")
    header_frame.pack(side="top", fill="x", pady=10, padx=10)
    ctk.CTkLabel(header_frame, text="Activity", font=("TkDefaultFont", 24, "bold"), anchor="w").pack(side="left", anchor="n", fill="x")

    ttk.Separator(self, orient="horizontal").pack(side="top", fill="x", pady=(0,10))

    activity_frame = ctk.CTkFrame(self, fg_color="transparent")
    activity_frame.pack(side="top", fill="x", padx=10)

    self.cursor.execute("SELECT time FROM sessions WHERE date = ? AND user_id = ?", (TODAY, self.user_id))
    row = self.cursor.fetchone()
    if row is None:
      today_hours = 0
      today_minutes = 0
    else:
      today_hours, today_minutes, _ = get_time_from_seconds(row[0])

    with open(CONFIG_FILE, "r") as config_file:
      data = json.load(config_file)

    goal_hours, goal_minutes = data["daily_session_goal"][str(self.user_id)]
    formatted_today_progress_string = f"{today_hours}:{today_minutes:02d}/{goal_hours}:{goal_minutes:02d}"

    ctk.CTkLabel(activity_frame, text=f"⏰ Today's progress: {formatted_today_progress_string}").pack(side="left")
    ctk.CTkLabel(activity_frame, text=f"⚡ Current Streak: {data['streaks'][str(self.user_id)]['current_streak']}").pack(side="right")

    self.treeview_week = ttk.Treeview(self, columns=("Time", "Description"), height=7)
    self.treeview_week.pack(side="top", fill="both", padx=10, pady=10)

    self.treeview_week.heading("#0", text="Day")
    self.treeview_week.heading("Time", text="Time")
    self.treeview_week.heading("Description", text="Description")

    self.treeview_week.column("#0", stretch=True)
    self.treeview_week.column("Time", stretch=True, anchor="center")
    self.treeview_week.column("Description", stretch=True)

    goal_time_in_seconds = get_seconds_from_time(data["daily_session_goal"][str(self.user_id)][0], data["daily_session_goal"][str(self.user_id)][1], 0)
    name_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for count in range(0, 7):
      current_date = MONDAY + timedelta(days=count)
      current_day_formatted = f"{name_days[count]}, {current_date.day:02d}"

      self.cursor.execute("SELECT time, description FROM sessions WHERE user_id = ? AND date = ?", (self.user_id, current_date))
      rows = self.cursor.fetchall()
      descriptions = []
      total_time_seconds = 0
      for row in rows:
        total_time_seconds += row[0]
        descriptions.append(row[1])

      goal_reached = False
      if total_time_seconds >= goal_time_in_seconds:
        goal_reached = True

      hours_current_date, minutes_current_date, seconds_current_date = get_time_from_seconds(total_time_seconds)
      current_day_time_formatted = format_time(hours_current_date, minutes_current_date, seconds_current_date)

      tags = []
      if goal_reached:
        tags.append("goal_reached")
      else:
        tags.append("goal_not_reached")

      if TODAY == current_date:
        tags.append("current_day")

      self.treeview_week.insert(
        "", tk.END,
        text=current_day_formatted,
        values=[current_day_time_formatted, descriptions],
        tags=tags
      )

    self.treeview_week.tag_configure("goal_reached", background="lightgreen")
    self.treeview_week.tag_configure("current_day", foreground="blue")

    self._set_appearance_mode(ctk.get_appearance_mode())

  def _set_appearance_mode(self, mode_string):
    super()._set_appearance_mode(mode_string)
    
    style = ttk.Style()
    style.theme_use("clam")

    if mode_string.lower() == "dark":
      style.configure(
        "Dark.Treeview",
        background="#1e1e1e",
        foreground="white",
        rowheight=25,
        relief="flat"
      )

      style.map ("Dark.Treeview",
                 background=[("selected", "#0078d4")],
                 foreground=[("selected", "white")]
      )
      
      style.configure("Dark.Treeview.Heading",
            background="#2d2d2d",
            foreground="white",
      )

      style.configure("TSeparator", background="#2b2b2b")
      self.treeview_week.config(style="Dark.Treeview")

    elif mode_string.lower() == "light":
      style.configure("Light.Treeview",
          background="white",
          foreground="black",
          rowheight=25,
      )

      style.map("Light.Treeview",
          background=[("selected", "#cce7ff")],
          foreground=[("selected", "black")]
      )

      style.configure("Light.Treeview.Heading",
          background="#f0f0f0",
          foreground="black",
      )

      self.treeview_week.config(style="Light.Treeview")