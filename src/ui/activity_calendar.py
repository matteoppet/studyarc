import tkinter as tk
from tkinter import ttk
from calendar import monthrange
from datetime import date

class ActivityCalendar(ttk.Frame):
  def __init__(self, root, user_id, cursor, conn):
    super().__init__(root)
    self.root = root
    self.user_id = user_id
    self.cursor = cursor
    self.conn = conn
    self.pack(side="top", anchor="n", fill="both", expand=True)

    self.today = date.today()
    self.months = []
    self.name_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for month in range(1, 13):
      self.months.append(monthrange(self.today.year, month)[1])

  def draw(self):
    for widget in self.winfo_children():
      widget.destroy()
    
    ttk.Label(self, text=f"Study Activity - {self.today.year}", anchor="w", font=("TkDefaultFont", 15, "bold")).pack(side="top", fill="x", pady=(0,10))

    scrollable_area_frame = ttk.Frame(self)
    scrollable_area_frame.pack(anchor="center", fill="x", expand=True)

    self.canvas = tk.Canvas(
            scrollable_area_frame, height=170, borderwidth=1, relief="solid")
    self.h_scrollbar = ttk.Scrollbar(scrollable_area_frame, orient="horizontal", command=self.canvas.xview)
    self.canvas.configure(xscrollcommand=self.h_scrollbar.set)

    self.canvas.pack(anchor="center", fill="x")
    self.h_scrollbar.pack(side="bottom", fill="x")

    self.canvas.create_text(20, 35, text="Mon")
    self.canvas.create_text(20, 65, text="Wed")
    self.canvas.create_text(20, 95, text="Fri", anchor="w")

    start_x = 45
    count_name_month = 0
    count_weeks = 1
    total_content_width = 40
    total_content_height = 15
    for days_month in self.months:
      self.cursor.execute("SELECT date FROM sessions WHERE date >= ? AND date <= ? AND user_id = ?", (f"{self.today.year}-{count_name_month:02d}-01", f"{self.today.year}-{count_name_month:02d}-{self.months[count_name_month]}", self.user_id))
      session_in_month = []
      for row in self.cursor.fetchall():
        for day in row:
          day = day.split("-")[2]
          session_in_month.append(int(day))

      start_y = 15
      self.canvas.create_text(start_x+10, start_y, text=self.name_months[count_name_month])
      start_y += 15
      
      for day in range(1, days_month+1):
        self.canvas.create_rectangle(start_x, start_y, start_x+10, start_y+10, fill="blue" if day in session_in_month else None)
        start_y += 15

        if day == 7*count_weeks:
          start_x += 15
          start_y = 30
          count_weeks += 1
          total_content_width += 15

        total_content_height = start_y

      count_weeks = 1
      count_name_month += 1

    self.canvas.create_text(200, total_content_height+75, text="Each column represent a week, and each row represent a day.")

    self.canvas.config(scrollregion=(0, 0, total_content_width+20, total_content_height))