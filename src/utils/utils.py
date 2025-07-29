import tkinter as tk
from tkinter import ttk

from datetime import datetime
import json
from tkinter import messagebox

from core.settings import COLOR_BACKGROUND, COLOR_FOREGROUND
from core.__init__ import CONFIG_FILE

class LogOldSession(tk.Toplevel):
  def __init__(self, root, cursor, conn, user_id):
    super().__init__(root)
    self.root = root
    self.cursor = cursor
    self.conn = conn
    self.user_id = user_id

    self.title("Log Session")
    self.geometry(f"+{self.winfo_pointerx()}+{self.winfo_pointery()-300}")
    self.resizable(False, False)
    try:
      self.iconbitmap("../assets/icon.ico")
    except tk.TclError:
      self.iconbitmap(resource_path("assets/icon.ico"))

    self.container = tk.Frame(self, bg=COLOR_BACKGROUND)
    self.container.pack(fill="both", expand=True, padx=10, pady=10)

    current_day = datetime.now().day
    current_month = datetime.now().month
    current_year = datetime.now().year

    self.day_intvar = tk.IntVar(value=current_day)
    self.month_intvar = tk.IntVar(value=current_month)
    self.year_intvar = tk.IntVar(value=current_year)
    self.minutes_duration_session = tk.IntVar(value=0)
    self.working_on_category = tk.StringVar()
    self.working_on = tk.StringVar()

    self.run()

  def run(self):
    WIDTH_LABELS = 20

    tk.Label(self.container, text="Log Session", bg=COLOR_BACKGROUND, fg=COLOR_FOREGROUND, font=("TkDefaultFont", 16, "bold"), anchor="w").pack(side="top", fill="x")
    ttk.Separator(self.container, orient="horizontal").pack(fill="x", side="top", pady=10)

    date_frame = tk.Frame(self.container, bg=COLOR_BACKGROUND)
    date_frame.pack(side="top", fill="x")
    tk.Label(date_frame, text="Insert date session:", width=WIDTH_LABELS, fg=COLOR_FOREGROUND, anchor="w").pack(side="left")
    # DAY
    tk.Entry(date_frame, textvariable=self.day_intvar, width=5, justify="center").pack(side="left")
    tk.Label(date_frame, text="dd", fg=COLOR_FOREGROUND).pack(side="left", padx=(3,8))
    # MONTH
    tk.Entry(date_frame, textvariable=self.month_intvar, width=5, justify="center").pack(side="left")
    tk.Label(date_frame, text="mm", fg=COLOR_FOREGROUND).pack(side="left", padx=(3,8))
    # YEAR
    tk.Entry(date_frame, textvariable=self.year_intvar, width=5, justify="center").pack(side="left")
    tk.Label(date_frame, text="yyyy", fg=COLOR_FOREGROUND).pack(side="left", padx=(3,0))

    time_frame = tk.Frame(self.container, bg=COLOR_BACKGROUND)
    time_frame.pack(side="top", fill="x", pady=(10,0))
    tk.Label(time_frame, text="Session duration:", width=WIDTH_LABELS, fg=COLOR_FOREGROUND, anchor="w").pack(side="left")
    tk.Entry(time_frame, textvariable=self.minutes_duration_session, width=6, justify="center").pack(side="left")
    tk.Label(time_frame, text="minutes", fg=COLOR_FOREGROUND).pack(side="left", padx=3)

    description_frame = tk.Frame(self.container, bg=COLOR_BACKGROUND)
    description_frame.pack(side="top", fill="x", pady=(10,0))
    tk.Label(description_frame, text="Worked on:", width=WIDTH_LABELS, fg=COLOR_FOREGROUND, anchor="w").pack(side="left")
    self.combobox_subjects = ttk.Combobox(description_frame, textvariable=self.working_on, width=15)
    self.combobox_subjects.pack(side="right", padx=10)
    self.combobox_category = ttk.Combobox(description_frame, textvariable=self.working_on_category, values=["Subjects", "Projects"], width=15)
    self.combobox_category.pack(side="right")

    self.combobox_category.bind("<<ComboboxSelected>>", lambda x: self.change_working_on_category())

    ttk.Separator(self.container, orient="horizontal").pack(side="top", fill="x", pady=10)

    buttons_frame = tk.Frame(self.container, bg=COLOR_BACKGROUND)
    buttons_frame.pack(side="top", fill="x")
    tk.Button(buttons_frame, text="Save", width=8, command=lambda: self.save()).pack(side="right")
    tk.Button(buttons_frame, text="Cancel", command=lambda: self.destroy(), width=8).pack(side="right", padx=10)

  def save(self):
    year = abs(self.year_intvar.get())
    month = abs(self.month_intvar.get())
    day = abs(self.day_intvar.get())
    time = abs(self.minutes_duration_session.get())
    category = self.working_on_category.get()
    description = self.working_on.get()

    format_date = f"{year}-{month:02d}-{day:02d}"
    time_in_seconds = get_seconds_from_time(0, time, 0)
    
    self.cursor.execute("INSERT INTO sessions (date, time, description, user_id) VALUES (?, ?, ?, ?)", (format_date, time_in_seconds, description, self.user_id))
    self.conn.commit()

    if category.lower() == "subjects":
      with open(CONFIG_FILE, "r") as read_config_file:
        data = json.load(read_config_file)

      data["subjects"][description] += time_in_seconds

      with open(CONFIG_FILE, "w") as updated_config_file:
        updated_config_file.write(json.dumps(data, indent=4))

    elif category.lower() == "projects":
      id_project = description.split(". ")[0]

      self.cursor.execute("UPDATE projects SET time = time + ? WHERE id = ? AND user_id = ?", (time_in_seconds, int(id_project), self.user_id))
      self.conn.commit()

    messagebox.showinfo("Log Session", "Session successfully logged!")
    self.destroy()
    self.root.run()

  def change_working_on_category(self):
    category_selected = self.working_on_category.get()

    if category_selected.lower() == "subjects":
      with open(CONFIG_FILE, "r") as read_config_file:
        data = json.load(read_config_file)
      self.combobox_subjects["values"] = list(data["subjects"].keys())
      self.working_on.set(value="")
    elif category_selected.lower() == "projects":
      self.cursor.execute("SELECT id, name FROM projects WHERE user_id = ?", (self.user_id,))
      rows = self.cursor.fetchall()
      self.combobox_subjects["values"] = [f"{row[0]}. {row[1]}" for row in rows]
      self.working_on.set(value="")


def get_time_from_seconds(seconds: int) -> tuple[int, int, int]:
  seconds = int(seconds)
  hours, remainder = divmod(int(seconds), 3600)
  minutes, seconds = divmod(remainder, 60)

  return hours, minutes, seconds

def get_seconds_from_time(hours: int, minutes: int, seconds: int) -> int:
  return hours * 3600 + minutes * 60 + seconds

def format_time(hours: int, minutes: int, seconds: int) -> str:
  return f"{hours}h {minutes}m {seconds}s"

def resource_path(relative_path: str) -> str:
    import sys
    import os

    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
