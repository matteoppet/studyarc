import tkinter as tk
from tkinter import ttk

from datetime import timedelta, date

from core.settings import COLOR_BACKGROUND, COLOR_FOREGROUND
from utils.utils import get_time_from_seconds, get_seconds_from_time, resource_path, format_time
from core.__init__ import CONFIG_FILE

import json

class ChangeDailyGoalTopLevel(tk.Toplevel):
  def __init__(self, root):
    super().__init__(root)

    self.title("Change Daily Goal")
    self.geometry(f"250x120+{self.winfo_pointerx()}+{self.winfo_pointery()}")
    self.resizable(False, False)
    try:
      self.iconbitmap("../assets/icon.ico")
    except tk.TclError:
      self.iconbitmap(resource_path("assets/icon.ico"))


    with open(CONFIG_FILE, "r") as config_file_read:
      self.data = json.load(config_file_read)

    self.hours_intvar = tk.IntVar(value=int(self.data["daily_session_goal"][0]))
    self.minutes_intvar = tk.IntVar(value=int(self.data["daily_session_goal"][1]))

    self.run()

  def run(self):
    tk.Label(self, text="Insert your daily session goal:").pack(fill="x", anchor="center", padx=10, pady=10)

    frame_entries = tk.Frame(self)
    frame_entries.pack(side="top", fill="x")

    frame_hours_minutes = tk.Frame(frame_entries)
    frame_hours_minutes.pack(anchor="center")

    frame_hours = tk.Frame(frame_hours_minutes)
    frame_hours.pack(side="left")
    tk.Entry(frame_hours, width=4, justify="center", textvariable=self.hours_intvar).pack(side="left")
    tk.Label(frame_hours, text="h").pack(side="left", padx=(5,0))

    frame_minutes = tk.Frame(frame_hours_minutes)
    frame_minutes.pack(side="left", padx=(10,0))
    tk.Entry(frame_minutes, width=4, justify="center", textvariable=self.minutes_intvar).pack(side="left")
    tk.Label(frame_minutes, text="m").pack(side="left", padx=(5,0))

    ttk.Separator(self, orient="horizontal").pack(side="top", fill="x", pady=10)

    frame_buttons = tk.Frame(self)
    frame_buttons.pack(side="top", fill="x", pady=(0,10), padx=10)

    tk.Button(frame_buttons, text="Save", command=lambda: self.save()).pack(side="right", padx=(10,0))
    tk.Button(frame_buttons, text="Cancel", command=lambda: self.destroy()).pack(side="right")

  def save(self):
    new_hours = abs(self.hours_intvar.get())
    new_minutes = abs(self.minutes_intvar.get())

    self.data["daily_session_goal"] = [new_hours, new_minutes]

    with open(CONFIG_FILE, "w") as updated_config_file:
      updated_config_file.write(json.dumps(self.data, indent=4))

    self.destroy()

class CurrentWeek(tk.Frame):
  def __init__(self, root, cursor, conn, user_id):
    tk.Frame.__init__(self, root)
    self.config(bg=COLOR_BACKGROUND, borderwidth=1, relief="solid")
    self.pack(side="top", fill="both", anchor="n", padx=25, pady=(30,0), expand=True)

    self.cursor = cursor
    self.conn = conn
    self.user_id = user_id

    self.run()

  def run(self):
    header_frame = tk.Frame(self)
    header_frame.pack(side="top", fill="x", pady=10, padx=10)
    tk.Label(header_frame, text="Current Week", font=("TkDefaultFont", 18, "bold"), anchor="w", bg=COLOR_BACKGROUND, fg=COLOR_FOREGROUND).pack(side="left", anchor="n", fill="x")
    tk.Button(header_frame, text="Set daily goal", command=lambda: self.open_change_daily_goal()).pack(side="right")

    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    list_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    tk.Label(self, text=f"Week dates: {monday} -- {sunday}", bg=COLOR_BACKGROUND, fg=COLOR_FOREGROUND, anchor="w").pack(side="top", anchor="n", fill="x", padx=10)

    ttk.Separator(self, orient="horizontal").pack(fill="x", side="top", padx=10, pady=10)

    week_days_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
    week_days_frame.pack(side="top", fill="x", padx=10, anchor="n")

    WIDTH_DAYS_LABEL = 13
    WIDTH_TIME_LABEL = 10

    with open(CONFIG_FILE, "r") as config_file_read:
      data = json.load(config_file_read)
    daily_session_goal_seconds = get_seconds_from_time(data["daily_session_goal"][0], data["daily_session_goal"][1], 0)
    
    current_week_dates = [monday + timedelta(days=count) for count in range(0,7)]
    for count in range(0, 7):
      current_date = current_week_dates[count]

      self.cursor.execute("SELECT date, time, description FROM sessions WHERE date = ? AND user_id = ?", (current_date, self.user_id))
      rows = self.cursor.fetchall()

      descriptions = {row[0]: [] for row in rows}
      for row in rows:
        if row[2] != '':
          try:
            name = row[2].split(". ")[1]
            descriptions[row[0]].append(name)
          except:
            descriptions[row[0]].append(row[2])

          descriptions[row[0]].append("|")

      if rows == []:
        current_day = monday + timedelta(days=count)
        frame_current_day = tk.Frame(week_days_frame, bg=COLOR_BACKGROUND)
        frame_current_day.pack(side="top", fill="x", pady=(0,5))
        tk.Label(frame_current_day, text=f"{list_days[count]} {str(current_day).split("-")[2]}:", bg=COLOR_BACKGROUND, fg=COLOR_FOREGROUND, anchor="e", width=WIDTH_DAYS_LABEL, font=("TkDefaultFont", 9, "bold")).pack(side="left")
        tk.Label(frame_current_day, text="No data", bg=COLOR_BACKGROUND, fg=COLOR_FOREGROUND, anchor="center", width=WIDTH_TIME_LABEL).pack(side="left", padx=10)

      else:
        total_time_in_seconds = sum([row[1] for row in rows])
        hours, minutes, seconds = get_time_from_seconds(total_time_in_seconds)
        formatted_time = format_time(hours, minutes, seconds)

        frame_current_day = tk.Frame(week_days_frame, bg=COLOR_BACKGROUND)
        frame_current_day.pack(side="top", fill="x", pady=(0,5))
        tk.Label(frame_current_day, text=f"{list_days[count]} {str(current_date).split("-")[2]}:", bg=COLOR_BACKGROUND, fg=COLOR_FOREGROUND, anchor="e", width=WIDTH_DAYS_LABEL, font=("TkDefaultFont", 9, "bold")).pack(side="left")
        
        if total_time_in_seconds >= daily_session_goal_seconds:
          tk.Label(frame_current_day, text=formatted_time, bg="lightgreen", fg="black", anchor="center", width=WIDTH_TIME_LABEL).pack(side="left", padx=10)
        else:
          tk.Label(frame_current_day, text=formatted_time, bg="lightgray", fg=COLOR_FOREGROUND, anchor="center", width=WIDTH_TIME_LABEL).pack(side="left", padx=10)

        tk.Label(frame_current_day, text=descriptions[str(current_date)], bg=COLOR_BACKGROUND, fg=COLOR_FOREGROUND, anchor="w").pack(side="left", fill="x")


  def open_change_daily_goal(self):
    ChangeDailyGoalTopLevel(self)