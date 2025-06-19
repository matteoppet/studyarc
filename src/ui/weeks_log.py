import tkinter as tk
from tkinter import ttk
from utils.utils import seconds_to_time
from tkinter import messagebox 
from datetime import datetime, timedelta

class Week(tk.Toplevel):
  class FrameDay(ttk.Frame):
    def __init__(self, root, values=None, count=None, day=None):
      super().__init__(root)
      self.root = root
      self.values = values
      self.count = count
      self.day = day
      self.pack(side="top", fill="x", padx=10)
      self.draw()

    def draw(self):
      if self.values:
        date_object = datetime.strptime(self.values[2], "%Y-%m-%d")
        date_only_object = date_object.date()
        name_day = date_only_object.strftime('%A')
        ttk.Label(self, text=f"{name_day}, {date_only_object}", anchor="w", font=("TkDefaultFont", 9), foreground="light slate gray").pack(side="top", fill="x")
        
        frame_time = ttk.Frame(self)
        frame_time.pack(side="top", fill="x", pady=3)
        ttk.Label(frame_time, text="Total Studied:", font=("TkDeafultFont", 8, "bold"), width=15).pack(side="left")
        time = seconds_to_time(self.values[3])
        time_formatted = f"{time[0]:02d}:{time[1]:02d}:{time[2]:02d}"
        ttk.Label(frame_time, text=time_formatted, font=("TkDeafultFont", 8)).pack(side="left")

        ttk.Label(self, text=f"Description: {self.values[4]}", anchor="w", font=("TkDeafultFont", 8)).pack(side="top", fill="x")
      else:
        name_day = self.day.strftime('%A')
        ttk.Label(self, text=f"{name_day}, {self.day}", anchor="w", font=("TkDefaultFont", 9), foreground="light slate gray").pack(side="top", fill="x")
        ttk.Label(self, text="No study sessions on this day.").pack(side="top", fill="x", pady=5)

      if self.count != 6:
        ttk.Separator(self, orient="horizontal").pack(side="top", fill="x", pady=5)

  def __init__(self, root, user_id, week_id, cursor, conn):
    super().__init__(root)
    self.root = root
    self.user_id = user_id
    self.week_id = week_id
    self.cursor = cursor
    self.conn = conn
    self.minsize(400, 200)

    self.start_week = None
    self.end_week = None 
    self.cursor.execute("SELECT week_start, week_end FROM weeks_log WHERE id = ?", (self.week_id,))
    for row in self.cursor.fetchall():
      self.start_week = row[0]
      self.end_week = row[1]

    self.draw()

  def draw(self):
    ttk.Label(self, text=f"Overview Week of {self.start_week}", font=("TkDefaultFont", 13, "bold"), anchor="w").pack(side="top", fill="x", padx=10, pady=10)
    ttk.Separator(self, orient="horizontal").pack(side="top", fill="x", pady=(0, 10))

    self.cursor.execute("SELECT * FROM sessions WHERE date >= ? AND date <= ? AND user_id = ?", (self.start_week, self.end_week, self.user_id,))
    days = [row for row in self.cursor.fetchall()]

    date_object = datetime.strptime(self.start_week, "%Y-%m-%d")
    date_only_object = date_object.date()
    for count in range(0,7):
      current_day = date_only_object + timedelta(days=count)
      found = False
      
      for row in days:
        if row[2] == str(current_day):
          self.FrameDay(self, row, count)
          found = True
          break
          
      if not found:
        self.FrameDay(self, count=count, day=current_day)

    ttk.Separator(self, orient="horizontal").pack(side="top", fill="x", pady=10)

    frame_button = ttk.Frame(self)
    frame_button.pack(side="top", fill="x", pady=(0, 10), padx=10)
    ttk.Button(frame_button, text="Close", command=lambda: self.destroy()).pack(side="right")

class WeeksLog(ttk.Frame):
  def __init__(self, root, controller, user_id, cursor, conn):
    super().__init__(root)
    self.root = root
    self.controller = controller
    self.user_id = user_id
    self.cursor = cursor
    self.conn = conn
    self.pack(side="right", anchor="n", padx=15, pady=15, expand=True, fill="both")
    self.pack_propagate(False)
    self.configure(width=self.winfo_width()/2)
    
  def draw(self):
    title_frame = ttk.Frame(self)
    title_frame.pack(fill="x")
    ttk.Label(title_frame, text="Weeks Log", font=("TkDefaultFont", 15, "bold")).pack(side="left")

    total_time_studied_frame = ttk.Frame(self)
    total_time_studied_frame.pack(fill="x", pady=10)
    total_time = 0
    self.cursor.execute("SELECT time FROM weeks_log WHERE user_id = ?", (self.user_id,))
    for row in self.cursor.fetchall():
      total_time += int(row[0])
    time = seconds_to_time(total_time)
    time_formatted = f"{time[0]:02d}:{time[1]:02d}:{time[2]:02d}"
    ttk.Label(total_time_studied_frame, text="Time studied in total:").pack(side="left")
    ttk.Label(total_time_studied_frame, text=time_formatted, font=("TkDefaultFont", 9, "bold")).pack(side="left")

    self.cursor.execute("PRAGMA table_info(weeks_log)")
    headers_name = [row[1] for row in self.cursor.fetchall()][0:4]
    self.treeview = ttk.Treeview(
      self,
      columns=headers_name,
      show="headings"
    )

    for heading in headers_name: 
      if heading.lower() == "id":
        self.treeview.heading(heading, text=heading.upper())
      else:
        self.treeview.heading(heading, text=heading.title().replace("_", " "))

      if heading.lower() in ["time", "id"]:
        self.treeview.column(heading, width=int((self.winfo_width()/2)/4), anchor="center")
      else:
        self.treeview.column(heading, width=int((self.winfo_width()/2)/4), anchor="w")  

    self.cursor.execute("SELECT * FROM weeks_log WHERE user_id = ?", (self.user_id, ))
    for row in self.cursor.fetchall():
      values = list(row[0:4])


      time = seconds_to_time(int(values[3]))
      values[3] = f"{time[0]:02d}:{time[1]:02d}:{time[2]:02d}"

      self.treeview.insert(
        "",
        tk.END,
        values=values
      )

    v_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.treeview.yview)
    self.treeview.configure(yscrollcommand=v_scrollbar.set)
    self.treeview.pack(side="left", fill="both", expand=True)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    self.collapse_menu = tk.Menu(self, tearoff=0)
    self.collapse_menu.add_command(label="Open", command=lambda: self.open_week()) 
    self.collapse_menu.add_command(label="Delete", command=lambda: self.delete_week())

    self.treeview.bind("<Button-3>", self.open_collapse_menu)

  def open_collapse_menu(self, event):
    item_id = self.treeview.identify_row(event.y)
    if item_id:
      self.treeview.selection_set(item_id)
      self.collapse_menu.post(event.x_root, event.y_root)

  def open_week(self):
    selected = self.treeview.selection()
    ID = int(self.treeview.item(selected[0], "values")[0])
    Week(self, self.user_id, ID, self.cursor, self.conn)

  def delete_week(self):
    if messagebox.askyesno("Delete Week Record", "Are you sure to delete this week record?\n\nThis action is irreversible."):
      selected = self.treeview.selection()
      ID = int(self.treeview.item(selected[0], "values")[0])
      self.treeview.delete(selected[0])
      self.cursor.execute("DELETE FROM weeks_log WHERE id = ?", (ID,))
      messagebox.showinfo("Delete Week Record", "The record has been successfully deleted.")
