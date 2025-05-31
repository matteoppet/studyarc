import tkinter as tk
from tkinter import ttk
import csv
import ast

from style import StyleManager
from paths import DATA_WEEKS_LOG, DATA_CURRENT_WEEK

class OpenWeek(tk.Toplevel):
  def __init__(self, root, info_week):
    super().__init__()
    self.root = root
    self.resizable(False, False)
    self.info_week = ast.literal_eval(info_week)
    
    self.title("Week summary")

    self.container = ttk.Frame(self)
    self.container.pack(side="top")
    
    self.run()

  def run(self):
    # Title
    ttk.Label(self.container, text="Week Summary", font=(StyleManager.get_current_font(), 18, "bold")).pack(side="top", anchor="center", pady=15, padx=15)

    # frame days
    frame_days = ttk.LabelFrame(self.container, text="Summary Days")
    frame_days.pack(side="top", padx=10)

    fieldnames = []
    with open(DATA_CURRENT_WEEK, "r") as f:
      reader = csv.DictReader(f)
      fieldnames = reader.fieldnames

    self.treeview = ttk.Treeview(
      frame_days,
      columns=fieldnames,
      show="headings",
      height=7
    )

    for heading in fieldnames:
      self.treeview.heading(heading, text=heading)
      
      if heading in ["Total Time", "Week number"]:
        self.treeview.column(heading, width=140, anchor='center')
      else:
        self.treeview.column(heading, width=140, anchor='w')

    for row_data in self.info_week:
      self.treeview.insert(
        "",
        tk.END,
        values=list(row_data.values())
      )

    self.treeview.pack(padx=10, pady=10)

    frame_missed_days = ttk.Frame(frame_days)
    frame_missed_days.pack(fill="x", padx=5)
    count_missed_days = 7-len(self.info_week)
    ttk.Label(frame_missed_days, text=f"Missed study days: {count_missed_days}/7", foreground=("green4" if count_missed_days == 0 else "coral" if count_missed_days > 0 and count_missed_days < 5 else "red")).pack(side="left", pady=10)

    # frame button
    ttk.Button(self.container, text="Ok", width=10, command=lambda: self.destroy()).pack(side="bottom", anchor="se", padx=10, pady=10)

class WeeksLog(ttk.Frame):
  def __init__(self, root, controller):
    super().__init__(root)
    self.controller = controller
    self.pack(side="right", anchor="n", padx=15, pady=15, expand=True, fill="both")
    self.pack_propagate(False)
    self.configure(width=self.winfo_width()/2)

    self.data = []
    self.total_time_studied = 0

    self.load_data()

  def draw_table(self):
    # TITLE FRAME + BUTTON CREATE NEW LOG
    title_frame = ttk.Frame(self)
    title_frame.pack(fill="x")

    ttk.Label(title_frame, text="Weeks log", font=(StyleManager.get_current_font(), 15, "bold")).pack(side="left")

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

    total_hours_studied_frame = ttk.Frame(self)
    total_hours_studied_frame.pack(fill="x", pady=10)
    ttk.Label(total_hours_studied_frame, text=f"Total hours studied:").pack(side="left")
    ttk.Label(total_hours_studied_frame, text=text_to_write, font=(StyleManager.get_current_font(), 9, "bold")).pack(side="left")

    style = ttk.Style()

    self.treeview = ttk.Treeview(
      self,
      columns=self.headers_name,
      show="headings",
      height=7
    )

    for heading in self.headers_name:
      self.treeview.heading(heading, text=heading)
      
      if heading in ["Total Time", "Week number"]:
        self.treeview.column(heading, width=140, anchor='center')
      else:
        self.treeview.column(heading, width=140, anchor='w')

    for row_data in self.data:
      values_to_insert = []
      for key, value in row_data.items():
        if key.lower() == "summary":
          values_to_insert.append("Double click to open..")
        else:
          values_to_insert.append(value)

      self.treeview.insert(
        "",
        tk.END,
        values=values_to_insert
      )

    v_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.treeview.yview)
    self.treeview.configure(yscrollcommand=v_scrollbar.set)
    self.treeview.bind("<Double-1>", lambda x: self.open_week_summary(x))

    self.treeview.pack(side="left", fill="both", expand=True)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    style.configure("Treeview", rowheight=25) 
    
  def load_data(self):
    self.data.clear()

    with open(DATA_WEEKS_LOG, newline="") as tempdata:
      reader = csv.DictReader(tempdata)

      self.headers_name = reader.fieldnames

      for row in reader:
        current_row = {}

        for key, value in row.items(): current_row[key] = str(value.capitalize())

        self.data.append(current_row)

  def open_week_summary(self, event):
    item = self.treeview.selection()[0]
    values_item = self.treeview.item(item, "values")
    info_week = self.data[int(values_item[0])-1]["Summary"]

    OpenWeek(self, info_week)