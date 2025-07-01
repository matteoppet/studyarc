import tkinter as tk
from tkinter import Toplevel, ttk
from datetime import datetime, date, timedelta
from tkinter import messagebox
from tkinter.simpledialog import askstring
import json
from core.paths import USER_CONFIG, ICON_PATH
from ui.style import StyleManager
from utils.utils import time_to_seconds, seconds_to_time, get_current_week_dates
from tkcalendar import Calendar

FORMAT_TIME_STRING = "%h:%m:%s"
FORMAT_DAY_STRING = "%Y-%m-%d"

class Timer(Toplevel):
  def __init__(self, root, user_id, cursor, conn):
    super().__init__()
    self.root = root
    self.user_id = user_id
    self.cursor = cursor
    self.conn = conn

    self.title("Session Timer")
    self.minsize(220, 150)
    self.resizable(False, False)
    self.geometry(f"+{self.winfo_pointerx()}+{self.winfo_pointery()}")
    self.topmost = False
    self.attributes("-topmost", self.topmost)
    self.configure(bg=StyleManager.get_item_color("bg"))
    self.protocol("WM_DELETE_WINDOW", lambda: self.close())

    self.reset()

  def draw(self):
    self.timer_text = ttk.Label(self, text="00:00:00", font=("TkDefaultFont", 24, "bold"), anchor="center")
    self.timer_text.pack(side="top", fill="both", pady=(15, 10))

    frame_tasks = ttk.Frame(self)
    frame_tasks.pack(side="top", fill="both", padx=10)
    ttk.Label(frame_tasks, text="Task Manager", font=("TkDefaultFont", 16, "bold")).pack(side="top", anchor="nw", pady=10)

    self.listbox_tasks = tk.Listbox(frame_tasks, height=7, selectmode="single")
    self.listbox_tasks.pack(side="top", fill="both", expand=True)

    ttk.Button(frame_tasks, text="Complete Task", command=lambda: self.complete_task()).pack(side="top", fill="x", pady=(10, 5))
    ttk.Button(frame_tasks, text="Add Task", command=lambda: self.add_task()).pack(side="top", fill="x")
    ttk.Button(frame_tasks, text="Delete Task", command=lambda: self.delete_task()).pack(side="top", fill="x", pady=(5,10))

    ttk.Separator(self, orient="horizontal").pack(side="top", fill="x")

    frame_buttons = ttk.Frame(self)
    frame_buttons.pack(side="top", fill="x", padx=10, pady=10)
    ttk.Button(frame_buttons, text="Close", command=lambda: self.close()).pack(side="right")
    ttk.Button(frame_buttons, text="Reset", command=lambda: self.reset()).pack(side="right", padx=5)
    self.pin_button = ttk.Button(frame_buttons, text="Pin", command=lambda: self.pin_unpin())
    self.pin_button.pack(side="left")

  def add_task(self):
    new_task_name = askstring("New Task", "What's is your new task?")
    self.listbox_tasks.insert(0, new_task_name)

  def delete_task(self):
    selection = self.listbox_tasks.curselection()
    if selection:
      index = selection[0]
      self.listbox_tasks.delete(index)

  def complete_task(self):
    selection = self.listbox_tasks.curselection()
    if selection:
      index = selection[0]
      text = self.listbox_tasks.get(index)
      
      if str(text).find("✓") == -1:
        self.listbox_tasks.delete(index)
        self.listbox_tasks.insert(tk.END, f" ✓ {text}")

  def play_gif(self):
    self.frame_gif = (self.frame_gif + 1) % len(self.gif_frames)
    self.canvas.itemconfig(self.gif_background, image=self.gif_frames[self.frame_gif])
    self.id_timer_gif = self.after(100, self.play_gif)

  def update_timer(self):
    if not self.check_goal_reached():
      if self.timer_seconds != 59:
        self.timer_seconds += 1
      else:
        self.timer_seconds = 0
        self.timer_minutes += 1

        if self.timer_minutes == 60:
          self.timer_minutes = 0
          self.timer_hours += 1

      self.timer_text.configure(text=f"{self.timer_hours:02d}:{self.timer_minutes:02d}:{self.timer_seconds:02d}")
      self.id_timer = self.after(1000, self.update_timer)
    else:
      if not messagebox.askyesno("Session Completed", "Congratulation, you have reached your goal!\n\nDo you want to start a new timer?"):
        self.destroy()
        self.root.root.controller.deiconify()
        self.root.root.controller.run()
      else:
        self.reset()

  def check_goal_reached(self):
    if self.goal_hours != 0 or self.goal_minutes != 0:
      goal_in_seconds = time_to_seconds(self.goal_hours, self.goal_minutes)
      current_timer_in_seconds = time_to_seconds(self.timer_hours, self.timer_minutes)

      if goal_in_seconds == current_timer_in_seconds:
        self.save()
        return True
    else: return False

  def save(self):
    def check_new_week(today_date, last_day_recorded):
      with open(USER_CONFIG, "r") as readf:
        data = json.load(readf)

      if last_day_recorded == "":
        data["data"]["previous_session_date"] = today_date
        with open(USER_CONFIG, "w") as outfile:
          outfile.write(json.dumps(data, indent=2))

        return False
      else:
        date1 = "2028-02-02"
        date2 = datetime(int(today_date.split("-")[0]), int(today_date.split("-")[1]), int(today_date.split("-")[2])).isocalendar()[:2]

        data["data"]["previous_session_date"] = today_date
        with open(USER_CONFIG, "w") as outfile:
          outfile.write(json.dumps(data, indent=2))
        
        return date1 != date2
      
    def create_new_week_log(last_day_recorded):
      date_object = datetime.strptime(last_day_recorded, "%Y-%m-%d")
      date_only_object = date_object.date()
      get_monday, get_sunday = get_current_week_dates(date_only_object)

      total_time = 0
      self.cursor.execute("SELECT time FROM sessions WHERE date >= ? AND date <= ?", (get_monday, get_sunday,))
      for row in self.cursor.fetchall():
        total_time += int(row[0])

      self.cursor.execute("INSERT INTO weeks_log (week_start, week_end, time, user_id) VALUES (?, ?, ?, ?)", (get_monday, get_sunday, total_time, self.user_id,))
      self.conn.commit()

    #######################
    today = date.today().isoformat()
    timer_to_seconds = time_to_seconds(self.timer_hours, self.timer_minutes) + self.timer_seconds

    self.cursor.execute("SELECT 1 FROM sessions WHERE date = ?", (today,))
    exists = self.cursor.fetchone() is not None

    if self.root.category_selected.get().lower() == "projects":
      description = self.root.areas_selected_value.get().split(": ")[1]
    else:
      description = self.root.areas_selected_value.get()

    if exists:
      self.cursor.execute("UPDATE sessions SET time = time + ?, description = description || ', ' || ? WHERE date = ? AND user_id = ?", (timer_to_seconds, description, today, self.user_id))
      self.conn.commit()
    else:
      self.cursor.execute("INSERT INTO sessions (date, time, description, user_id) VALUES (?, ?, ?, ?)", (today, timer_to_seconds, description, self.user_id))
      self.conn.commit()

      with open(USER_CONFIG, "r") as readf:
        data = json.load(readf)
      last_day_recorded = data["data"]["previous_session_date"]

      yesterday = datetime.now() - timedelta(1)
      yesterday_formatted = datetime.strftime(yesterday, '%Y-%m-%d')

      if last_day_recorded == yesterday_formatted or last_day_recorded == "":
        preview_streak = data["data"]["streak"]
        data["data"]["streak"] = int(preview_streak) + 1
      else:
        data["data"]["streak"] = 0

      with open(USER_CONFIG, "w") as write_file:
        write_file.write(json.dumps(data, indent=2))

      if check_new_week(today, last_day_recorded):
        create_new_week_log(last_day_recorded)

    if self.root.category_selected.get().lower() == "projects":
      ID = self.root.areas_selected_value.get().split(": ")[0]

      self.cursor.execute("UPDATE projects SET time_spent = time_spent + ? WHERE ID = ? AND user_id = ?", (timer_to_seconds, ID, self.user_id))
      self.conn.commit()

  def reset(self):
    self.timer_hours = 0
    self.timer_minutes = 0
    self.timer_seconds = 0
    self.goal_hours = self.root.goal_hours.get()
    self.goal_minutes = self.root.goal_minutes.get()

    for widgets in self.winfo_children():
      widgets.destroy()

    self.draw()
    
    self.id_timer = self.after(1000, self.update_timer)

  def close(self):
    confirm_close = False

    if not self.check_goal_reached():
      if messagebox.askyesno("Closing Timer", "You have not reached your goal estabilished, are you sure you want to end the session?\n\nCurrent progress will be saved."):
        confirm_close = True

    if confirm_close or (self.goal_hours == 0 and self.goal_minutes == 0):
      self.save()
      self.destroy()
      self.root.root.deiconify()
      self.root.root.run()

  def pin_unpin(self):
    self.topmost = not self.topmost
    self.attributes("-topmost", self.topmost)

    if self.topmost:
      self.pin_button.config(text="Unpin")
    else:
      self.pin_button.config(text="Pin")

class CreateNewLog(Toplevel):
  class ToplevelCalendar(Toplevel):
    def __init__(self, root):
      super().__init__(root)
      self.root = root
      self.title("Pick a date")
      self.geometry(f"+{self.winfo_pointerx()}+{self.winfo_pointery()}")
      self.resizable(False, False)
      self.transient(self.root)

      self.draw()

    def draw(self):
      container = tk.Frame(self)
      container.pack(fill="both", expand=True, padx=10, pady=10)
      
      today_date = str(date.today()).split("-")
      self.cal = Calendar(container, selectmode = 'day',
          year = int(today_date[0]), month = int(today_date[1]),
          day = int(today_date[2]))
      self.cal.pack(side="top", anchor="center")

      tk.Button(container, text="Select", command=lambda: self.select_date()).pack(side="top", anchor="center", pady=(15, 10))
  
    def select_date(self):
      self.root.selected_date.set(self.cal.get_date())
      self.root.select_date_button.config(text=self.cal.get_date())
      self.destroy()

  def __init__(self, root, user_id, cursor, conn):
    super().__init__(root)
    self.root = root
    self.user_id = user_id
    self.cursor = cursor
    self.conn = conn

    self.title("New log")
    self.geometry(f"+{self.winfo_pointerx()-200}+{self.winfo_pointery()}")
    self.resizable(False, False)
    self.transient(self.root)

    try: 
      self.iconbitmap(ICON_PATH)
    except tk.TclError: 
      self.iconbitmap("../assets/logo.ico")

    self.goal_hours = tk.IntVar(value=0)
    self.goal_minutes = tk.IntVar(value=0)
    self.category_selected = tk.StringVar(value="Subjects")

    self.areas_values = []
    self.areas_values_old_log = []
    with open(USER_CONFIG, "r") as readf:
        data = json.load(readf)
        readf.close()
    self.areas_values = data["data"]["subjects"]
    self.areas_values_old_log = data["data"]["subjects"]
    self.areas_selected_value = tk.StringVar(value=self.areas_values[0])
    self.areas_selected_value_old_log = tk.StringVar(value=self.areas_values_old_log[0])

    self.selected_date = tk.StringVar()
    self.old_log_hours = tk.IntVar()
    self.old_log_minutes = tk.IntVar()

    self.vcmd = (self.register(self.limit_characters), '%P')

    self.draw()

  def draw(self):
    container = ttk.Frame(self)
    container.pack(fill="both", expand=True)
    notebook = ttk.Notebook(container)
    notebook.pack(fill="both", expand=True)

    frame_new_log = ttk.Frame(notebook)
    frame_new_log.pack(fill="both", expand=True)
    frame_old_log = ttk.Frame(notebook)
    frame_old_log.pack(fill="both", expand=True)

    notebook.add(frame_new_log, text="Start Session")
    notebook.add(frame_old_log, text="Add Session")

    self.draw_new_log(frame_new_log)
    self.draw_old_log(frame_old_log)
  
  def draw_new_log(self, frame):
    def update_areas_frame():
      self.areas_values.clear()

      if self.category_selected.get() == "Projects":
        self.cursor.execute("SELECT id, name FROM projects WHERE user_id = ?", (self.user_id,))
        self.areas_values = [f"{row[0]}: {row[1]}" for row in self.cursor.fetchall()]
        if len(self.areas_values) == 0:
          with open(USER_CONFIG, "r") as readf:
            data = json.load(readf)
            readf.close()
          self.areas_values = data["data"]["subjects"]
          self.category_selected.set("Subjects")

      else:
        with open(USER_CONFIG, "r") as readf:
            data = json.load(readf)
            readf.close()
        self.areas_values = data["data"]["subjects"]

      self.combobox_areas_new.config(values=self.areas_values)
      self.areas_selected_value.set(self.areas_values[0])
      self.label_areas.config(text=self.category_selected.get())

    WIDTH_LABELS = 20

    frame_goal_time = ttk.Frame(frame)
    frame_goal_time.pack(side="top", fill="x", padx=10, pady=(10,0))
    ttk.Label(frame_goal_time, text="Duration::", width=WIDTH_LABELS).pack(side="left")
    ttk.Entry(frame_goal_time, textvariable=self.goal_minutes, width=5, justify="center", validate="key", validatecommand=self.vcmd).pack(side="right")
    ttk.Label(frame_goal_time, text="mm").pack(side="right", padx=5)
    ttk.Entry(frame_goal_time, textvariable=self.goal_hours, width=5, justify="center", validate="key", validatecommand=self.vcmd).pack(side="right")
    ttk.Label(frame_goal_time, text="hh").pack(side="right", padx=5)

    ttk.Separator(frame, orient="horizontal").pack(side="top", fill="x", pady=10)

    frame_category = ttk.Frame(frame)
    frame_category.pack(side="top", fill="x", padx=10)
    ttk.Label(frame_category, text="Work on:", width=WIDTH_LABELS).pack(side="left")
    category_combo = ttk.Combobox(frame_category, textvariable=self.category_selected, values=("Subjects", "Projects"))
    category_combo.pack(side="right")
    category_combo.bind("<<ComboboxSelected>>", lambda x: update_areas_frame())

    frame_areas = ttk.Frame(frame)
    frame_areas.pack(side="top", fill="x", padx=10, pady=(10,0))
    self.label_areas = ttk.Label(frame_areas, text=self.category_selected.get(), width=WIDTH_LABELS)
    self.label_areas.pack(side="left")
    self.combobox_areas_new = ttk.Combobox(frame_areas, textvariable=self.areas_selected_value, values=self.areas_values)
    self.combobox_areas_new.pack(side="right")

    frame_buttons = ttk.Frame(frame)
    frame_buttons.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
    ttk.Button(frame_buttons, text="Start Timer", command=lambda: self.start_timer()).pack(side="right")
    ttk.Button(frame_buttons, text="Cancel", command=lambda: self.destroy()).pack(side="right", padx=5)

  def draw_old_log(self, frame):
    def update_areas_frame():
      self.areas_values_old_log.clear()

      if self.category_selected.get() == "Projects":
        self.cursor.execute("SELECT id, name FROM projects WHERE user_id = ?", (self.user_id,))
        self.areas_values_old_log = [row for row in self.cursor.fetchall()]
        if len(self.areas_values) == 0:
          with open(USER_CONFIG, "r") as readf:
            data = json.load(readf)
            readf.close()
          self.areas_values = data["data"]["subjects"]
          self.category_selected.set("Subjects")
      else:
        with open(USER_CONFIG, "r") as readf:
            data = json.load(readf)
            readf.close()
        self.areas_values_old_log = data["data"]["subjects"]

      self.combobox_areas_old.config(values=self.areas_values_old_log)
      self.areas_selected_value_old_log.set(self.areas_values_old_log[0])
      self.label_areas.config(text=self.category_selected.get())

    WIDTH_LABELS = 20
    
    frame_day = ttk.Frame(frame)
    frame_day.pack(side="top", fill="x", padx=10, pady=(10,0))
    ttk.Label(frame_day, text="Date:", width=WIDTH_LABELS).pack(side="left")
    self.select_date_button = ttk.Button(frame_day, text="Select date", command=lambda: self.ToplevelCalendar(self))
    self.select_date_button.pack(side="right")

    frame_time = ttk.Frame(frame)
    frame_time.pack(side="top", fill="x", padx=10, pady=(10,0))
    ttk.Label(frame_time, text="Duration:", width=WIDTH_LABELS).pack(side="left")
    ttk.Entry(frame_time, textvariable=self.old_log_minutes, width=5, justify="center", validate="key", validatecommand=self.vcmd).pack(side="right")
    ttk.Label(frame_time, text="mm").pack(side="right", padx=5)
    ttk.Entry(frame_time, textvariable=self.old_log_hours, width=5, justify="center", validate="key", validatecommand=self.vcmd).pack(side="right")
    ttk.Label(frame_time, text="hh").pack(side="right", padx=5)

    ttk.Separator(frame, orient="horizontal").pack(side="top", fill="x", pady=10)

    frame_category = ttk.Frame(frame)
    frame_category.pack(side="top", fill="x", padx=10)
    ttk.Label(frame_category, text="Work on:", width=WIDTH_LABELS).pack(side="left")
    category_combo = ttk.Combobox(frame_category, textvariable=self.category_selected, values=("Subjects", "Projects"))
    category_combo.pack(side="right")
    category_combo.bind("<<ComboboxSelected>>", lambda x: update_areas_frame())

    frame_areas = ttk.Frame(frame)
    frame_areas.pack(side="top", fill="x", padx=10, pady=(10,0))
    self.label_areas = ttk.Label(frame_areas, text=self.category_selected.get(), width=WIDTH_LABELS)
    self.label_areas.pack(side="left")
    self.combobox_areas_old = ttk.Combobox(frame_areas, textvariable=self.areas_selected_value_old_log, values=self.areas_values_old_log)
    self.combobox_areas_old.pack(side="right")

    frame_buttons = ttk.Frame(frame)
    frame_buttons.pack(side="bottom", fill="x", padx=10, pady=10)
    ttk.Button(frame_buttons, text="Add session", command=lambda: self.confirm_old_log()).pack(side="right")
    ttk.Button(frame_buttons, text="Cancel", command=lambda: self.destroy()).pack(side="right", padx=5)

  def limit_characters(self, new_value):
    if len(new_value) <= 2:
      return True
    else: 
      return False

  def confirm_old_log(self):
    day = self.selected_date.get()
    area = self.areas_selected_value_old_log.get()
    hours, minutes = self.old_log_hours.get(), self.old_log_minutes.get()
    user_id = self.user_id

    day = datetime.strptime(day, "%m/%d/%y").strftime("%Y-%m-%d")

    self.cursor.execute("INSERT INTO sessions (date, time, description, user_id) VALUES (?, ?, ?, ?)", (day, time_to_seconds(hours, minutes), area, user_id))
    self.conn.commit()

    if self.category_selected.get().lower() == "projects":
      ID, name = area.split(" ")
      self.cursor.execute("UPDATE projects SET time = time + ? WHERE ID = ? AND user_id = ?", (time_to_seconds(hours, minutes), ID, user_id))
      self.conn.commit()

    self.root.clear_widgets()
    self.root.draw_table()

    messagebox.showinfo("Log recorded", "The log inserted has been recorded successfully")
    self.destroy()

  def start_timer(self):
    self.root.withdraw()
    self.destroy()
    Timer(self, self.user_id, self.cursor, self.conn)

class Home(ttk.Frame):
  def __init__(self, root: tk.Frame, controller: tk.Tk, user_id: int, cursor, conn):
    super().__init__(root)
    self.controller = controller
    self.root = root
    self.user_id = user_id
    self.pack(side="left", anchor="n", padx=(15, 7.5), pady=15, fill="both", expand=True)

    self.cursor = cursor
    self.conn = conn

  def draw_table(self):
    title_frame = ttk.Frame(self)
    title_frame.pack(fill="x")
    ttk.Label(title_frame, text="This Week", font=("TkDefaultFont", 15, "bold")).pack(side="left")

    current_day_frame = ttk.Frame(self)
    current_day_frame.pack(fill="x", pady=10)
    ttk.Label(current_day_frame, text="Today is:").pack(side="left")
    ttk.Label(current_day_frame, text=datetime.today().strftime(FORMAT_DAY_STRING), font=("TkDefaultFont", 9, "bold")).pack(side="left")

    self.cursor.execute("PRAGMA table_info(sessions)")
    headers_name = [row[1] for row in self.cursor.fetchall()][1:4]
    self.treeview = ttk.Treeview(
      self,
      columns=headers_name,
      show="headings",
      height=7,
    )

    # load and configure headers for table
    for heading in headers_name:
      self.treeview.heading(heading, text=heading.capitalize())

      if heading.lower() in ["time", "date"]:
        self.treeview.column(heading, width=140, anchor='center')
      else:
        self.treeview.column(heading, width=140, anchor='w')

    # inserting data in the table
    with open(USER_CONFIG, "r") as readf:
      reader = json.load(readf)
      readf.close()
    goal_time = reader["goals"]["daily_session_goal"]
    goal_in_seconds = time_to_seconds(int(goal_time[0]), int(goal_time[1]))

    self.cursor.execute("SELECT * FROM sessions WHERE user_id = ? AND date >= ?", (self.user_id, get_current_week_dates()[0], ))
    for row in reversed(self.cursor.fetchall()):
      values = list(row[1:4])

      seconds_current_row = values[1]
      time_formatted = seconds_to_time(int(values[1]))
      values[1] = FORMAT_TIME_STRING.replace("%h", f"{time_formatted[0]:02d}").replace("%m", f"{time_formatted[1]:02d}").replace("%s", f"{time_formatted[2]:02d}")

      self.treeview.insert(
        "",
        tk.END,
        values=values,
        iid=row[0],
        tags=(True if int(seconds_current_row) >= int(goal_in_seconds) else False))
      
    self.treeview.tag_configure(True, foreground="green")
    self.treeview.pack(side="left", fill="both", expand=True)

  def clear_widgets(self):
    for widgets in self.winfo_children():
      widgets.destroy()
      
  def create_new_log(self):
    CreateNewLog(self, self.user_id, self.cursor, self.conn)