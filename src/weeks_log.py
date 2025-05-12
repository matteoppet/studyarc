import tkinter as tk
from tkinter import ttk
import csv
import ast

from paths import DATA_WEEKS_LOG

class OpenWeek(tk.Toplevel):
  def __init__(self, root, info_week):
    super().__init__()
    self.root = root
    self.info_week = ast.literal_eval(info_week)
    
    self.title("Week summary")

    self.container = tk.Frame(self)
    self.container.pack(side="top")
    
    self.run()

  def run(self):
    # Title
    tk.Label(self.container, text="Week Summary", font=("Arial 18 bold")).pack(side="top", anchor="center", pady=15, padx=15)

    # frame days
    frame_days = tk.LabelFrame(self.container, text="Days")
    frame_days.pack(side="top", padx=10)

    fieldnames = []
    with open(DATA_WEEKS_LOG, "r") as f:
      reader = csv.DictReader(f)
      fieldnames = reader.fieldnames

    header_row = tk.Frame(frame_days)
    header_row.pack(fill="x", padx=5)
    for name in fieldnames:
      tk.Label(header_row, text=name.capitalize(), width=20, borderwidth=1, relief="solid", bg="lightgray").pack(side="left")

    for day in self.info_week:
      current_row = tk.Frame(frame_days)
      current_row.pack(fill="x", anchor="w", padx=5)

      for key, value in day.items():
        tk.Label(current_row, text=str(value).capitalize(), width=20, borderwidth=1, relief="solid", anchor="w").pack(side="left")

    frame_missed_days = tk.Frame(frame_days)
    frame_missed_days.pack(fill="x", padx=5)
    count_missed_days = 7-len(self.info_week)
    tk.Label(frame_missed_days, text=f"Missed study days: {count_missed_days}/7", foreground=("green4" if count_missed_days == 0 else "coral" if count_missed_days > 0 and count_missed_days < 5 else "red")).pack(side="left", pady=10)

    # frame button
    tk.Button(self.container, text="Ok", width=10, command=lambda: self.destroy()).pack(side="bottom", anchor="se", padx=10, pady=10)

class WeeksLog(tk.Frame):
  def __init__(self, root, controller):
    super().__init__(root)
    self.controller = controller
    self.pack(side="left", anchor="n", padx=15, pady=15, expand=True)

    self.data = []
    self.total_time_studied = 0

    self.load_data()

  def draw_table(self):
    # TITLE FRAME + BUTTON CREATE NEW LOG
    title_frame = tk.Frame(self)
    title_frame.pack(fill="x")

    tk.Label(title_frame, text="Weeks log", font="Arial 15 bold").pack(side="left")

    # CURRENT DAY FRAME
    for row_data in self.data:
      current_row_time = row_data["Total Time"]

      formatted_hours = int(current_row_time.replace("h", "").split(" ")[0])
      formatted_minutes = int(current_row_time.replace("m", "").split(" ")[1])
      formatted_seconds = int(current_row_time.replace("s", "").split(" ")[2])
      self.total_time_studied += formatted_hours * 3600 + formatted_minutes * 60 + formatted_seconds

    result_hours = self.total_time_studied // 3600
    result_minutes = (self.total_time_studied % 3600) // 60
    result_seconds = self.total_time_studied % 60
    text_to_write = f"{(result_hours):02d}h {(result_minutes):02d}m {(result_seconds):02d}s"

    total_hours_studied_frame = tk.Frame(self)
    total_hours_studied_frame.pack(fill="x", pady=10)
    tk.Label(total_hours_studied_frame, text=f"Total hours studied: {text_to_write}").pack(side="left")

    # DRAW TABLE
    header_row = tk.Frame(self, width=20)
    header_row.pack(fill="x", expand=True)

    for header_name in self.headers_name:
      tk.Label(header_row, text=header_name.capitalize(), borderwidth=1, relief="solid", width=20, bg="lightgray").pack(side="left", expand=True, fill="x", ipady=4)

    # CANVAS
    self.canvas = tk.Canvas(self)
    self.vscrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
    self.scrollable_frame = tk.Frame(self.canvas)
    self.scrollable_frame.bind(
      "<Configure>",
      lambda e: self.canvas.configure(
        scrollregion=self.canvas.bbox("all")
      )
    )

    self.canvas.create_window(0, 0, window=self.scrollable_frame, anchor="nw")
    self.canvas.configure(yscrollcommand=self.vscrollbar.set)

    for row_data in self.data:
      current_row = tk.Frame(self.scrollable_frame, borderwidth=1, relief="solid", width=20)
      current_row.pack(fill="x", expand=True)
      
      for key, value in row_data.items():
        if key == "Summary":
          tk.Button(current_row, text="Open", command=lambda x=value: self.open_week_summary(x), width=20).pack(anchor="center", fill="both")
        else:
          tk.Label(current_row, text=str(value).capitalize(), width=20, anchor="center").pack(side="left", fill="x", ipady=2)

    self.canvas.pack(side="left", fill="both", expand=True)
    self.vscrollbar.pack(side="right", fill="y")

  def load_data(self):
    self.data.clear()

    with open(DATA_WEEKS_LOG, newline="") as tempdata:
      reader = csv.DictReader(tempdata)

      self.headers_name = reader.fieldnames

      for row in reader:
        current_row = {}

        for key, value in row.items():
          current_row[key] = str(value.capitalize())

        self.data.append(current_row)

  def open_week_summary(self, info_week):
    OpenWeek(self, info_week)