import tkinter as tk
from tkinter import ttk
import csv
from datetime import datetime, date
from tkinter import messagebox
import json

PATH_DATA_CURRENT_WEEK_CSV = "data_current_week.csv"
PATH_DATA_WEEKS_LOG_CSV = "data_weeks_log.csv"

class TimerWindow(tk.Toplevel):
  def __init__(self, master, root):
    super().__init__()
    self.root = root
    self.master = master

    self.title("Study time")
    self.minsize(200, 200)
    self.topmost = False
    self.attributes("-topmost", self.topmost)

    self.protocol("WM_DELETE_WINDOW", lambda: self.end_timer())

    self.count_seconds = 0
    self.count_minutes = 0
    self.count_hours = 0

    self.week_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    self.current_week_day = self.week_days[datetime.weekday(datetime.today())].capitalize()

    self.goal_study_time_selected = self.master.goal_study_time_selected.get()
    self.goal_description = self.master.goal_study_description.get()
    self.goal_formatted_time = self.goal_study_time_selected.replace("h", "").replace("m", "").replace("s", "")

    self.id_timer = self.after(1000, self.update_timer)
    
    self.display_timer()

  def display_timer(self):
    # TITLE
    tk.Label(self, text="Study Timer", font=("Arial 18 bold")).pack(side="top", anchor="center", pady=15, padx=15)

    # TIMER
    self.timer_label = tk.Label(self, text=f"{(self.count_hours):02d}:{(self.count_minutes):02d}:{(self.count_seconds):02d}", font=("Arial 16"))
    self.timer_label.pack(side="top", anchor="center")

    # GOAL LABEL
    tk.Label(self, text=f"Goal: {self.goal_study_time_selected}", foreground="gray").pack(side="top", pady=3, anchor="center")

    ttk.Separator(self, orient="horizontal").pack(side="top", fill="x", pady=10)

    frame_buttons = tk.Frame(self)
    frame_buttons.pack(side="top", padx=10, fil="x")

    button_end_timer = tk.Button(frame_buttons, text="End timer", foreground="dark blue", command=lambda: self.end_timer())
    button_end_timer.pack(side="right")

    self.button_pin_window_on_top = tk.Button(frame_buttons, text="Pin window", command=lambda: self.pin_window())
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
    with open(PATH_DATA_CURRENT_WEEK_CSV, "r") as temp_data:
      reader = csv.DictReader(temp_data)

      for row in reader:
        if str(row["Day"]) == str(current_day):
          already_inside = row
          break

    with open(PATH_DATA_CURRENT_WEEK_CSV, "r") as f:
        reader = csv.reader(f)
        data = list(reader)

    if already_inside:
      time_to_add = row["Time"]
      formatted_hours = int(time_to_add.replace("h", "").split(" ")[0])
      formatted_minutes = int(time_to_add.replace("m", "").split(" ")[1])
      formatted_seconds = int(time_to_add.replace("s", "").split(" ")[2])

      total_seconds_1 = formatted_hours * 3600 + formatted_minutes * 60 + formatted_seconds
      total_seconds_2 = self.count_hours * 3600 + self.count_minutes * 60 + self.count_seconds
      total_seconds = total_seconds_1 + total_seconds_2

      result_hours = total_seconds // 3600
      result_minutes = (total_seconds % 3600) // 60
      result_seconds = total_seconds % 60
      text_to_write = f"{(result_hours):02d}h {(result_minutes):02d}m {(result_seconds):02d}s"
      row_to_write = [current_day, text_to_write, f"{row["Description"]}, {description}"]

      data.pop(1)
      data.insert(1, row_to_write)
    else:
      row_to_write = [current_day, time_studied, description]
      data.insert(1, row_to_write)

    with open(PATH_DATA_CURRENT_WEEK_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

  def check_new_week(self):
    with open("data.json", "r") as file:
      data = json.load(file)

    last_day_recorded = data["last_day"]
    
    today = date.today()
    today_string = f"{today.year} {today.month} {today.day}"

    if last_day_recorded == "":
      dict_to_write = {
        "last_day": today_string
      }
      json_object = json.dumps(dict_to_write, indent=2)

      with open("data.json", "w") as outfile:
        outfile.write(json_object)
      return False

    else:
      today = date.today()
      today_string = f"{today.year} {today.month} {today.day}"
      date1 = datetime(int(last_day_recorded.split(" ")[0]),int(last_day_recorded.split(" ")[1]), int(last_day_recorded.split(" ")[2]))
      date2 = datetime(int(today.year), (today.month), int(today.day))

      week1 = date1.isocalendar()[:2]
      week2 = date2.isocalendar()[:2]

      dict_to_write = {
        "last_day": today_string
      }
      json_object = json.dumps(dict_to_write, indent=2)

      with open("data.json", "w") as outfile:
        outfile.write(json_object)

      return week1 != week2

  def create_new_week_log(self):
    week_days = []
    total_time_studied = 0

    with open(PATH_DATA_CURRENT_WEEK_CSV, "r") as reading_file:
      reader = csv.DictReader(reading_file)

      for row in reader:
        week_days.append(row)

        formatted_hours = int(row["Time"].replace("h", "").split(" ")[0])
        formatted_minutes = int(row["Time"].replace("m", "").split(" ")[1])
        formatted_seconds = int(row["Time"].replace("s", "").split(" ")[2])
        total_seconds = formatted_hours * 3600 + formatted_minutes * 60 + formatted_seconds
        total_time_studied += total_seconds
    
    with open(PATH_DATA_WEEKS_LOG_CSV, "r") as data_weeks_log_read:
      reader = csv.reader(data_weeks_log_read)
      temp_data = list(reader)

    result_hours = total_time_studied // 3600
    result_minutes = (total_time_studied % 3600) // 60
    result_seconds = total_time_studied % 60
    text_to_write = f"{(result_hours):02d}h {(result_minutes):02d}m {(result_seconds):02d}s"
    temp_data.insert(1, [len(temp_data), text_to_write, week_days])

    with open(PATH_DATA_WEEKS_LOG_CSV, "w", newline="") as data_to_write:
      writer = csv.writer(data_to_write)
      writer.writerows(temp_data)

  def clear_last_week(self):
    fieldnames = []
    with open(PATH_DATA_CURRENT_WEEK_CSV) as f:
      reader = csv.DictReader(f)

      fieldnames = reader.fieldnames 

    f = open(PATH_DATA_CURRENT_WEEK_CSV, "w")
    f.truncate()
    f.close()

    with open(PATH_DATA_CURRENT_WEEK_CSV, "w", newline="") as csvfile:
      spamwriter = csv.writer(csvfile)

      spamwriter.writerow(fieldnames)

class CreateNewLog(tk.Toplevel):
  def __init__(self, master):
    super().__init__(master)
    self.master = master
    self.title("Creation new log")
    self.minsize(400, 250)

    self.container = tk.Frame(self)
    self.container.pack(fill="both")

    self.goal_study_time_options = ["No goal", "0h 30m", "0h 45m", "1h 0m", "1h 30m", "2h"]
    self.goal_study_time_selected = tk.StringVar(self)
    self.goal_study_time_selected.set(self.goal_study_time_options[0])

    self.goal_study_description = tk.StringVar(self)
    self.goal_study_description.set("")

    self.run()

  def run(self):
    tk.Label(self.container, text="Create new log", font=("Arial 15 bold")).pack(side="top", pady=10)

    ######################################################################
    
    quick_info_frame = tk.LabelFrame(self.container, text="Quick Info", pady=5)
    quick_info_frame.pack(side="top", fill="x", padx=5)

    today_date_frame = tk.Frame(quick_info_frame)
    today_date_frame.pack(side="top", fill="x")
    tk.Label(today_date_frame, text="Today date: ", font=("Arial 9 bold")).pack(side="left", padx=10)
    tk.Label(today_date_frame, text=f"{datetime.today().strftime('%Y-%m-%d')}").pack(side="right", padx=10)

    current_time_frame = tk.Frame(quick_info_frame)
    current_time_frame.pack(side="top", fill="x")
    tk.Label(current_time_frame, text="Current time: ", font=("Arial 9 bold")).pack(side="left", padx=10)
    tk.Label(current_time_frame, text=f"{datetime.now().strftime('%H:%M:%S')}").pack(side="right", padx=10)

    ######################################################################

    customization_frame = tk.LabelFrame(self.container, text="Customization")
    customization_frame.pack(side="top", fill="x", padx=5, ipady=5, pady=5)

    frame_insert_goal_time = tk.Frame(customization_frame)
    frame_insert_goal_time.pack(side="top", fill="x")
    tk.Label(frame_insert_goal_time, text="Goal study time: ", font=("Arial 9 bold")).pack(side="left", padx=10)
    self.option_menu = ttk.Combobox(frame_insert_goal_time, textvariable=self.goal_study_time_selected, values=self.goal_study_time_options)
    self.option_menu.pack(side="right", padx=10)

    frame_insert_goal_description = tk.Frame(customization_frame)
    frame_insert_goal_description.pack(side="top", fill="x")
    tk.Label(frame_insert_goal_description, text="Goal description: ", font=("Arial 9 bold")).pack(side="left", padx=10, pady=2)
    entry_description = tk.Entry(frame_insert_goal_description, textvariable=self.goal_study_description, width=30)
    entry_description.pack(side="right", padx=10, pady=2)

    ########################################################################

    buttons_frame = tk.Frame(self.container)
    buttons_frame.pack(side="top", fill="x", padx=5, pady=10)

    button_start = tk.Button(buttons_frame, text="Start", foreground="green", command=lambda: self.start_timer())
    button_start.pack(side="right", padx=10)

    button_cancel = tk.Button(buttons_frame, text="Cancel", foreground="red", command=lambda: self.destroy())
    button_cancel.pack(anchor="e")

  def start_timer(self):
    self.master.controller.withdraw()
    self.destroy()
    TimerWindow(self, self.master)

class Home(tk.Frame):
  def __init__(self, root, controller):
    super().__init__(root)
    self.controller = controller
    self.pack(side="left", anchor="n", padx=15, pady=15, expand=True)

    self.headers_name = []
    self.data = []

    self.load_data()

  def draw_table(self):
    # TITLE FRAME + BUTTON CREATE NEW LOG
    title_frame = tk.Frame(self)
    title_frame.pack(fill="x")

    tk.Label(title_frame, text="Current week", font="Arial 15 bold").pack(side="left")

    create_new_log_button = tk.Button(title_frame, text="Create new log", command=lambda: self.create_new_log())
    create_new_log_button.pack(side="right")

    # CURRENT DAY FRAME
    current_day_frame = tk.Frame(self)
    current_day_frame.pack(fill="x", pady=10)
    tk.Label(current_day_frame, text=f"Today is: {datetime.today().strftime('%Y-%m-%d')}").pack(side="left")

    # DRAW TABLE
    header_row = tk.Frame(self, width=20)
    header_row.pack(fill="x", expand=True)

    for header_name in self.headers_name:
      tk.Label(header_row, text=header_name.capitalize(), borderwidth=1, relief="solid", width=20, bg="lightgray").pack(side="left", expand=True, fill="x", ipady=4)

    for row_data in self.data:
      current_row = tk.Frame(self, borderwidth=1, relief="solid", width=20)
      current_row.pack(fill="x", expand=True)
      
      for key, value in row_data.items():
        if key == "Time":
          tk.Label(current_row, text=str(value).capitalize(), width=20, anchor="center").pack(side="left", fill="x", ipady=2)
        else:
          tk.Label(current_row, text=str(value).capitalize(), width=20, anchor="w", wraplength=150, justify="left").pack(side="left", fill="x", ipady=2)

  def load_data(self):
    self.data.clear()

    with open(PATH_DATA_CURRENT_WEEK_CSV, newline="") as tempdata:
      reader = csv.DictReader(tempdata)

      self.headers_name = reader.fieldnames

      for row in reader:
        current_row = {}

        for key, value in row.items():
          current_row[key] = str(value.capitalize())

        self.data.append(current_row)

  def create_new_log(self):
    CreateNewLog(self)