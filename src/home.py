import tkinter as tk
from tkinter import ttk
import csv
from datetime import datetime, date, timedelta
from tkinter import messagebox
import json
from paths import DATA_CURRENT_WEEK, DATA_WEEKS_LOG, USER_CONFIG, ICON_PATH
from style import StyleManager
from tkcalendar import *
from utils import time_to_seconds, seconds_to_time

class TimerWindow(tk.Toplevel):
  def __init__(self, master, root):
    super().__init__()
    self.root = root
    self.master = master

    try: self.iconbitmap(ICON_PATH)
    except tk.TclError: self.iconbitmap("../assets/logo_transparent_resized.ico")

    self.title("Study time")
    self.minsize(300, 200)
    mouse_x = self.winfo_pointerx()
    mouse_y = self.winfo_pointery()
    self.geometry(f"+{mouse_x}+{mouse_y}")
    self.topmost = False
    self.attributes("-topmost", self.topmost)
    self.configure(bg=StyleManager.get_item_color("bg"))

    self.protocol("WM_DELETE_WINDOW", lambda: self.end_timer())

    self.count_seconds = 0
    self.count_minutes = 0
    self.count_hours = 0

    self.week_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    self.current_week_day = self.week_days[datetime.weekday(datetime.today())].capitalize()

    self.goal_study_time_selected = self.master.goal_study_time_selected.get()
    self.goal_description = self.master.study_subject.get()
    self.goal_formatted_time = self.goal_study_time_selected.replace("h", "").replace("m", "").replace("s", "")

    self.id_timer = self.after(1000, self.update_timer)
    
    self.display_timer()

  def display_timer(self):
    # TITLE
    ttk.Label(self, text="Study Timer", font=(StyleManager.get_current_font(), 18, "bold")).pack(side="top", anchor="center", pady=15, padx=15)

    # TIMER
    self.timer_label = ttk.Label(self, text=f"{(self.count_hours):02d}:{(self.count_minutes):02d}:{(self.count_seconds):02d}", font=(StyleManager.get_current_font(), 16))
    self.timer_label.pack(side="top", anchor="center")

    # GOAL LABEL
    ttk.Label(self, text=f"Goal: {self.goal_study_time_selected}", foreground="gray").pack(side="top", pady=3, anchor="center")

    ttk.Separator(self, orient="horizontal").pack(side="top", fill="x", pady=10)

    frame_buttons = ttk.Frame(self)
    frame_buttons.pack(side="top", padx=10, fil="x")

    button_end_timer = ttk.Button(frame_buttons, text="End timer", command=lambda: self.end_timer())
    button_end_timer.pack(side="right")

    self.button_pin_window_on_top = ttk.Button(frame_buttons, text="Pin window", command=lambda: self.pin_window())
    self.button_pin_window_on_top.pack(side="left")

    self.mainloop()

  def update_timer(self):
    if self.count_seconds != 60:
      self.count_seconds += 1
    else:
      self.count_seconds = 0
      self.count_minutes += 1

      if self.count_minutes == 60:
        self.count_minutes = 0
        self.count_hours += 1

    if self.goal_study_time_selected != "No goal":
      formatted_goal_hours = self.goal_formatted_time.split(" ")[0]
      formatted_goal_minutes = self.goal_formatted_time.split(" ")[1]
      if f"{(self.count_hours):02d}" == f"{int(formatted_goal_hours):02d}" and f"{(self.count_minutes):02d}" == f"{int(formatted_goal_minutes):02d}":
        self.goal_timer_reached()

    self.timer_label.config(text=f"{(self.count_hours):02d}:{(self.count_minutes):02d}:{(self.count_seconds):02d}")
    self.id_timer = self.after(1000, self.update_timer)

  def end_timer(self):
    self.after_cancel(self.id_timer)  

    self.save_data()

    self.destroy()
    self.root.controller.deiconify()
    self.root.controller.run()

  def goal_timer_reached(self):
    messagebox.showinfo(title="Goal study time reached", message=f"Congratulation, you have reached your study time goal!\n{self.goal_study_time_selected}")
    
    self.save_data()

    self.destroy()
    self.root.controller.deiconify()
    self.root.controller.run()

  def pin_window(self):
    self.topmost = not self.topmost
    self.attributes("-topmost", self.topmost)

    if self.topmost:
      self.button_pin_window_on_top.config(text="Unpin window")
    else:
      self.button_pin_window_on_top.config(text="Pin window")

  def save_data(self):
    current_day = f"{self.current_week_day}, {datetime.today().strftime('%m-%d')}"
    time_studied = f"{(self.count_hours):02d}h {(self.count_minutes):02d}m {(self.count_seconds):02d}s"
    description = self.goal_description

    if self.check_new_week():
      self.create_new_week_log()
      self.clear_last_week()

    already_inside = False
    with open(DATA_CURRENT_WEEK, "r") as temp_data:
      reader = csv.DictReader(temp_data)

      for row in reader:
        if str(row["Day"]) == str(current_day):
          already_inside = row
          break

    with open(DATA_CURRENT_WEEK, "r") as f:
        reader = csv.reader(f)
        data = list(reader)

    if already_inside:
      time_to_add = row["Time"]
      formatted_hours = int(time_to_add.replace("h", "").split(" ")[0])
      formatted_minutes = int(time_to_add.replace("m", "").split(" ")[1])
      formatted_seconds = int(time_to_add.replace("s", "").split(" ")[2])

      total_seconds_1 = time_to_seconds(formatted_hours, formatted_minutes) + formatted_seconds
      total_seconds_2 = time_to_seconds(self.count_hours, self.count_minutes) + self.count_seconds
      total_seconds = total_seconds_1 + total_seconds_2

      time = seconds_to_time(total_seconds)
      text_to_write = f"{(time[0]):02d}h {(time[1]):02d}m {(time[2]):02d}s"
      row_to_write = [current_day, text_to_write, f"{row["Description"]}, {description}"]

      data.pop(1)
      data.insert(1, row_to_write)
    else:
      row_to_write = [current_day, time_studied, description]
      data.insert(1, row_to_write)

    with open(DATA_CURRENT_WEEK, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

  def check_new_week(self):
    with open(USER_CONFIG, "r") as file:
      data = json.load(file)

    last_day_recorded = data["last_day"]
    
    today = date.today()
    today_string = f"{today.year} {today.month} {today.day}"

    with open(USER_CONFIG) as f:
      data_json = json.load(f)

    if last_day_recorded == "":  
      data_json["last_day"] = today_string
      json_object = json.dumps(data_json, indent=2)

      with open(USER_CONFIG, "w") as outfile:
        outfile.write(json_object)

      return False

    else:
      today = date.today()
      today_string = f"{today.year} {today.month} {today.day}"
      date1 = datetime(int(last_day_recorded.split(" ")[0]),int(last_day_recorded.split(" ")[1]), int(last_day_recorded.split(" ")[2]))
      date2 = datetime(int(today.year), (today.month), int(today.day))

      week1 = date1.isocalendar()[:2]
      week2 = date2.isocalendar()[:2]

      data_json["last_day"] = today_string
      json_object = json.dumps(data_json, indent=2)

      with open(USER_CONFIG, "w") as outfile:
        outfile.write(json_object)

      return week1 != week2

  def create_new_week_log(self):
    week_days = []
    total_time_studied = 0

    with open(DATA_CURRENT_WEEK, "r") as reading_file:
      reader = csv.DictReader(reading_file)

      for row in reader:
        week_days.append(row)

        formatted_hours = int(row["Time"].replace("h", "").split(" ")[0])
        formatted_minutes = int(row["Time"].replace("m", "").split(" ")[1])
        formatted_seconds = int(row["Time"].replace("s", "").split(" ")[2])
        total_seconds = formatted_hours * 3600 + formatted_minutes * 60 + formatted_seconds
        total_time_studied += total_seconds
    
    with open(DATA_WEEKS_LOG, "r") as data_weeks_log_read:
      reader = csv.reader(data_weeks_log_read)
      temp_data = list(reader)

    result_hours = total_time_studied // 3600
    result_minutes = (total_time_studied % 3600) // 60
    result_seconds = total_time_studied % 60
    text_to_write = f"{(result_hours):02d}h {(result_minutes):02d}m {(result_seconds):02d}s"
    temp_data.insert(1, [len(temp_data), text_to_write, week_days])

    with open(DATA_WEEKS_LOG, "w", newline="") as data_to_write:
      writer = csv.writer(data_to_write)
      writer.writerows(temp_data)

  def clear_last_week(self):
    fieldnames = []
    with open(DATA_CURRENT_WEEK) as f:
      reader = csv.DictReader(f)

      fieldnames = reader.fieldnames 

    f = open(DATA_CURRENT_WEEK, "w")
    f.truncate()
    f.close()

    with open(DATA_CURRENT_WEEK, "w", newline="") as csvfile:
      spamwriter = csv.writer(csvfile)

      spamwriter.writerow(fieldnames)

class CreateNewLog(tk.Toplevel):
  def __init__(self, master):
    super().__init__(master)
    self.master = master
    self.title("Creation")
    self.minsize(400, 200)
    mouse_x = self.winfo_pointerx()
    mouse_y = self.winfo_pointery()
    self.geometry(f"+{mouse_x}+{mouse_y}")
    self.resizable(False, False)

    try: self.iconbitmap(ICON_PATH)
    except tk.TclError: self.iconbitmap("../assets/logo_transparent_resized.ico")

    self.container = ttk.Frame(self)
    self.container.pack(fill="both")

    self.goal_study_time_options = ["No goal", "0h 30m", "0h 45m", "1h 0m", "1h 30m", "2h"]
    self.goal_study_time_selected = tk.StringVar(self)
    self.goal_study_time_selected.set(self.goal_study_time_options[0])

    self.selected_day = tk.StringVar(self)

    self.study_subject = tk.StringVar(self)
    with open(USER_CONFIG, "r") as readf:
      data = json.load(readf)
      readf.close()
    self.study_subject_options = data["subjects"]
    self.study_subject.set(data["subjects"][0])

    self.run()

  def run(self):
    notebook = ttk.Notebook(self.container)
    notebook.pack(expand=True, fill="both")

    frame_current_log = ttk.Frame(notebook)
    frame_old_log = ttk.Frame(notebook)

    frame_current_log.pack(fill="both", expand=True)
    frame_old_log.pack(fill="both", expand=True)

    notebook.add(frame_current_log, text="Create new log")
    notebook.add(frame_old_log, text="Add log")

    self.draw_current_log(frame_current_log)
    self.draw_old_log(frame_old_log)

  def draw_current_log(self, frame):
    ttk.Label(frame, text="Study time!", font=(StyleManager.get_current_font(), 15, "bold")).pack(side="top", anchor="w", padx=10, pady=10)

    frame_current_day = ttk.Frame(frame)
    frame_current_day.pack(side="top", fill="x", padx=10)
    ttk.Label(frame_current_day, text="Current day:").pack(side="left")
    ttk.Label(frame_current_day, text=datetime.today().strftime('%Y-%m-%d')).pack(side="right")

    ttk.Separator(frame, orient="horizontal").pack(side="top", fill="x", padx=10, pady=10)

    frame_study_time_goal = ttk.Frame(frame)
    frame_study_time_goal.pack(side="top", fill="x", padx=10)
    ttk.Label(frame_study_time_goal, text="Study time goal:").pack(side="left")
    study_time_goal_menu = ttk.Combobox(frame_study_time_goal, textvariable=self.goal_study_time_selected, values=self.goal_study_time_options)
    study_time_goal_menu.pack(side="right")

    frame_subjet = ttk.Frame(frame)
    frame_subjet.pack(side="top", fill="x", padx=10, pady=3)
    ttk.Label(frame_subjet, text="Subject:").pack(side="left")
    study_subject_menu = ttk.Combobox(frame_subjet, textvariable=self.study_subject, values=self.study_subject_options)
    study_subject_menu.pack(side="right")

    ttk.Separator(frame, orient="horizontal").pack(fill="x", side="top", padx=10, pady=10)

    frame_buttons = ttk.Frame(frame)
    frame_buttons.pack(side="top", fill="x", padx=10, pady=5)
    button_start_timer = ttk.Button(frame_buttons, text="Start", command=lambda: self.start_timer())
    button_start_timer.pack(side="right")
    button_cancel = ttk.Button(frame_buttons, text="Cancel", command=lambda: self.destroy())
    button_cancel.pack(side="right")

  def draw_old_log(self, frame):
    ttk.Label(frame, text="Forgot to log your session?", font=(StyleManager.get_current_font(), 15, "bold")).pack(side="top", anchor="w", padx=10, pady=10)

    frame_select_day = ttk.Frame(frame)
    frame_select_day.pack(side="top", fill="x", padx=10)
    ttk.Label(frame_select_day, text="Select week-day:").pack(side="left")

    week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    week_dates = [(start_of_week + timedelta(days=i)).day for i in range(7)]
    options_days = [f"{week_days[i]}, {week_dates[i]}"for i in range(0,7)]
    self.selected_day.set(options_days[week_dates.index(today.day)])
    days_current_week = ttk.Combobox(frame_select_day, textvariable=self.selected_day, values=options_days)
    days_current_week.pack(side="right")

    ttk.Separator(frame, orient="horizontal").pack(fill="x", side="top", padx=10, pady=10)

    frame_select_time = ttk.Frame(frame)
    frame_select_time.pack(side="top", fill="x", padx=10)
    ttk.Label(frame_select_time, text="Insert time:").pack(side="left")

    self.hours_inserted_stringvar = tk.StringVar()
    self.minutes_inserted_stringvar = tk.StringVar()

    ttk.Label(frame_select_time, text="minutes").pack(side="right", padx=5)
    ttk.Entry(frame_select_time, textvariable=self.minutes_inserted_stringvar, width=4).pack(side="right")

    ttk.Label(frame_select_time, text="hours").pack(side="right", padx=5)
    ttk.Entry(frame_select_time, textvariable=self.hours_inserted_stringvar, width=4).pack(side="right")

    frame_select_subject = ttk.Frame(frame)
    frame_select_subject.pack(side="top", fill="x", padx=10, pady=3)
    ttk.Label(frame_select_subject, text="Subject:").pack(side="left")
    study_subject_menu = ttk.Combobox(frame_select_subject, textvariable=self.study_subject, values=self.study_subject_options)
    study_subject_menu.pack(side="right")

    ttk.Separator(frame, orient="horizontal").pack(fill="x", side="top", padx=10, pady=10)

    frame_buttons = ttk.Frame(frame)
    frame_buttons.pack(side="top", fill="x", padx=10, pady=5)
    button_start_timer = ttk.Button(frame_buttons, text="Insert", command=lambda: self.insert_old_log())
    button_start_timer.pack(side="right")
    button_cancel = ttk.Button(frame_buttons, text="Cancel", command=lambda: self.destroy())
    button_cancel.pack(side="right")

  def insert_old_log(self):
    hours = self.hours_inserted_stringvar.get()
    minutes = self.minutes_inserted_stringvar.get()

    if hours == "" or minutes == "":
      messagebox.showerror("Empty values", "Values of hours or minutes cannot be empty")

    else:
      hours = int(hours)
      minutes = int(minutes)

      day_log = self.selected_day.get()
      time_to_seconds_new_log = time_to_seconds(hours, minutes)
      subject_to_log = self.study_subject.get()

      new_time_logged = False

      # find if already exists, add to that row
      # if not, add to the row next to the day before
      rows_to_write = []
      count = 0
      with open(DATA_CURRENT_WEEK, "r") as readf:
        reader = csv.DictReader(readf)

        day_to_log = int(day_log.split(", ")[1])
        for row in reader:
          day_current_row = int(row["Day"].split(", ")[1].split("-")[1])

          if day_current_row == day_to_log:
            seconds_current_day = time_to_seconds(
              int(row["Time"].split(" ")[0].replace("h", "")),
              int(row["Time"].split(" ")[1].replace("m", "")),
            ) + int(row["Time"].split(" ")[2].replace("s", ""))

            new_time_in_seconds = time_to_seconds_new_log + seconds_current_day
            new_time_list = seconds_to_time(new_time_in_seconds)
            new_time_formatted = f"{new_time_list[0]:02d}h {new_time_list[1]:02d}m {new_time_list[2]:02d}s"

            current_row_to_write = {key: 0 for key in row.keys()}
            for key, value in row.items():
              if key == "Time":
                current_row_to_write[key] = new_time_formatted
              elif key == "Description":
                current_row_to_write[key] = f"{value}" + ", " + subject_to_log
              else:
                current_row_to_write[key] = value

            rows_to_write.append(current_row_to_write)
            new_time_logged = True

          else:
            rows_to_write.append(row)

          count += 1

        if not new_time_logged:
          count = 0
          for row in rows_to_write:
            day_current_row = int(row["Day"].split(", ")[1].split("-")[1])

            if day_current_row <= day_to_log-1 or day_current_row >= day_to_log+1:
              new_time_in_seconds = time_to_seconds_new_log
              new_time_list = seconds_to_time(new_time_in_seconds)
              new_time_formatted = f"{new_time_list[0]:02d}h {new_time_list[1]:02d}m {new_time_list[2]:02d}s"

              formatted_day = str(day_log.split(", ")[0]) + ", " + str(f"{datetime.today().month:02d}") + "-" + str(day_log.split(", ")[1])

              current_row_to_write = {"Day": 0, "Time": 0, "Description": 0}
              current_row_to_write["Day"] = formatted_day
              current_row_to_write["Time"] = new_time_formatted
              current_row_to_write["Description"] = subject_to_log

              if day_to_log < day_current_row:
                count += 1

              rows_to_write.insert(count, current_row_to_write)
              break

            count += 1
        readf.close()

      print(rows_to_write)

      with open(DATA_CURRENT_WEEK, "w", newline="") as writef:
        writer = csv.DictWriter(writef, fieldnames=rows_to_write[0].keys())
        writer.writeheader()
        writer.writerows(rows_to_write)

      self.master.clear_widgets()
      self.master.load_data()
      self.master.draw_table()
      self.destroy()


  def start_timer(self):
    self.master.controller.withdraw()
    self.destroy()
    TimerWindow(self, self.master)

class Home(ttk.Frame):
  def __init__(self, root, controller):
    super().__init__(root)
    self.controller = controller
    self.pack(side="left", anchor="n", padx=15, pady=15, expand=True)

    self.headers_name = []
    self.data = []

    self.load_data()

  def draw_table(self):
    style = ttk.Style()
    
    # TITLE FRAME + BUTTON CREATE NEW LOG
    title_frame = ttk.Frame(self)
    title_frame.pack(fill="x")

    ttk.Label(title_frame, text="Current week", font=(StyleManager.get_current_font(), 15, "bold")).pack(side="left")

    create_new_log_button = ttk.Button(title_frame, text="Create new log", command=lambda: self.create_new_log())
    create_new_log_button.pack(side="right")

    # CURRENT DAY FRAME
    current_day_frame = ttk.Frame(self)
    current_day_frame.pack(fill="x", pady=10)
    ttk.Label(current_day_frame, text=f"Today is:").pack(side="left")
    ttk.Label(current_day_frame, text=datetime.today().strftime('%Y-%m-%d'), font=(StyleManager.get_current_font(), 9, "bold")).pack(side="left")

    self.headers_name.insert(0, "Goal")
    self.treeview = ttk.Treeview(
      self,
      columns=self.headers_name,
      show="headings",
      height=7
    )

    # insert data to the treeview
    for heading in self.headers_name:
      self.treeview.heading(heading, text=heading)

      if heading == "Time":
        self.treeview.column(heading, width=140, anchor='center')
      elif heading == "Goal":
        self.treeview.column(heading, width=50, anchor='center')
      else:
        self.treeview.column(heading, width=140, anchor='w')
    for row_data in self.data:
      values_to_insert = []

      for key, value in row_data.items():
        if key == "Time":
          formatted_hours = int(value.replace("h", "").split(" ")[0])
          formatted_minutes = int(value.replace("m", "").split(" ")[1])
          formatted_seconds = int(value.replace("s", "").split(" ")[2])
          total_time_studied = time_to_seconds(formatted_hours, formatted_minutes) + formatted_seconds

          with open(USER_CONFIG, "r") as readf:
            reader = json.load(readf)
            readf.close()

          goal = reader["session_goal"]
          goal_to_seconds = goal[0] * 3600 + goal[1] * 60

          if total_time_studied >= goal_to_seconds:
            values_to_insert.insert(0, "👍")
          else:
            values_to_insert.insert(0, "👎")

          values_to_insert.append(value)
          
        else:
          values_to_insert.append(value)

      self.treeview.insert(
        "",
        tk.END,
        values=values_to_insert,
      )

    for item_id in self.treeview.get_children():
      values = self.treeview.item(item_id, "values")
      item_day = values[1].split(", ")

      if item_day[1] == datetime.today().strftime('%m-%d'):
        self.treeview.item(item_id, tags="current_day")

    # style the treeview
    style.configure("Treeview", rowheight=25) 
    self.treeview.tag_configure("current_day", background="#cce5ff", foreground="black" if StyleManager.get_current_theme().lower() == "light" else StyleManager.get_item_color("bg"))
    
    self.treeview.pack(side="left", fill="both", expand=True)

  def clear_widgets(self):
    for widgets in self.winfo_children():
      widgets.destroy()

  def load_data(self):
    self.data.clear()

    with open(DATA_CURRENT_WEEK, newline="") as tempdata:
      reader = csv.DictReader(tempdata)

      self.headers_name = reader.fieldnames

      for row in reader:
        current_row = {}

        for key, value in row.items():
          current_row[key] = str(value.capitalize())

        self.data.append(current_row)

  def create_new_log(self):
    CreateNewLog(self)