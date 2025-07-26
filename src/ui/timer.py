import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from core.settings import COLOR_BACKGROUND, COLOR_FOREGROUND
from core.__init__ import CONFIG_FILE
from utils.utils import get_seconds_from_time

from datetime import date
import json

class Timer(tk.Frame):
  def __init__(self, root, controller, cursor, conn):
    tk.Frame.__init__(self, root)
    self.root = root
    self.controller = controller
    self.cursor = cursor
    self.conn = conn

    self.config(bg=COLOR_BACKGROUND, borderwidth=1, relief="solid")
    self.pack(side="top", anchor="nw", padx=25, pady=5, expand=True, fill="both")
    
    self.timer_minutes_var = 25
    self.timer_seconds_var = 0 
    self.time_minutes_var_selected = tk.IntVar(value=25)

    self.working_on_category_selected = tk.StringVar()
    self.working_on_selected = tk.StringVar()

    self.name_new_task_stringvar = tk.StringVar()
    self.num_tasks = 0
    self.tasks = []

    self.pause_timer = False

    self.run()

  def run(self):
    tk.Label(self, text="Timer", font=("TkDefaultFont", 20, "bold"), anchor="w", bg=COLOR_BACKGROUND, fg=COLOR_FOREGROUND).pack(side="top", fill="x", pady=(5,0), padx=5)

    timer_controls_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
    timer_controls_frame.pack(side="top", anchor="nw", fill="x")

    time_text_frame = tk.Frame(timer_controls_frame, bg=COLOR_BACKGROUND)
    time_text_frame.pack(side="left")
    self.time_text = tk.Label(time_text_frame, text=f"{self.timer_minutes_var:02d}:{self.timer_seconds_var:02d}", font=("TkDefaultFont", 35, "bold"), bg=COLOR_BACKGROUND, fg=COLOR_FOREGROUND)
    self.time_text.pack(side="top", anchor="n", pady=20, padx=30)

    controls_frame = tk.Frame(timer_controls_frame, bg=COLOR_BACKGROUND)
    controls_frame.pack(side="left", padx=10, fill="x", expand=True)
    self.start_button = tk.Button(controls_frame, text="Start", width=15, command=lambda: self.start())
    self.start_button.pack(side="top", pady=(0,5), fill="x", expand=True)
    tk.Button(controls_frame, text="Restart", width=15, command=lambda: self.reset()).pack(side="top", fill="x", expand=True)

    ttk.Separator(self, orient="horizontal").pack(fill="x", padx=10)

    settings_timer = tk.Frame(controls_frame, bg=COLOR_BACKGROUND)
    settings_timer.pack(side="top", anchor="nw", fill="x", expand=True)
    tk.Label(settings_timer, text="Custom time (minutes)", bg=COLOR_BACKGROUND, fg=COLOR_FOREGROUND, anchor="w").pack(side="top", fill="x", pady=(10,0))
    custom_timer_entry_button_frame = tk.Frame(settings_timer, bg=COLOR_BACKGROUND)
    custom_timer_entry_button_frame.pack(side="top", fill="x", expand=True, pady=(0,5))
    tk.Entry(custom_timer_entry_button_frame, textvariable=self.time_minutes_var_selected).pack(side="left", fill="x", expand=True, padx=(0,10))
    tk.Button(custom_timer_entry_button_frame, text="Set", width=6, command=lambda: self.set_custom_time()).pack(side="right")

    tk.Label(controls_frame, text="Working on", anchor="w").pack(side="top", fill="x")
    frame_comboboxes = tk.Frame(controls_frame)
    frame_comboboxes.pack(side="top", fill="x", pady=(0,10))

    combobox_category = ttk.Combobox(frame_comboboxes, values=["Subjects", "Projects"], textvariable=self.working_on_category_selected)
    combobox_category.pack(side="left", fill="x", padx=(0,10))
    combobox_category.bind("<<ComboboxSelected>>", lambda x: self.changed_working_on_category())
    with open(CONFIG_FILE, "r") as read_config_file:
      data = json.load(read_config_file)
    self.combobox_values = ttk.Combobox(frame_comboboxes, values=list(data["subjects"].keys()), textvariable=self.working_on_selected)
    self.combobox_values.pack(side="left", fill="x")

    self.run_tasks()
  
  def run_tasks(self):
    if hasattr(self, 'frame_tasks'):
      self.frame_tasks.destroy()

    self.frame_tasks = tk.Frame(self)
    self.frame_tasks.pack(side="top", fill="both", expand=False, pady=10, padx=10)
    
    frame_title_and_info = tk.Frame(self.frame_tasks)
    frame_title_and_info.pack(side="top", fill="x", pady=(5,10))
    tk.Label(frame_title_and_info, text="Quick Tasks", font=("TkDefaultFont", 13, "bold"), fg=COLOR_FOREGROUND, bg=COLOR_BACKGROUND, anchor="w").pack(side="left", fill="x")
    tk.Label(frame_title_and_info, text="*Double click to mark task completed", fg=COLOR_FOREGROUND, bg=COLOR_BACKGROUND, anchor="e").pack(side="right", fill="x")

    frame_add_task = tk.Frame(self.frame_tasks)
    frame_add_task.pack(side="top", anchor="n", fill="x", pady=(0,5))
    tk.Entry(frame_add_task, textvariable=self.name_new_task_stringvar).pack(side="left", anchor="n", fill="x", expand=True, pady=(3,0))
    tk.Button(frame_add_task, text="Add", command=lambda: self.add_task()).pack(side="left", padx=(10,0))

    if self.num_tasks == 0:
      tk.Label(self.frame_tasks, text="No tasks added", fg=COLOR_FOREGROUND, bg=COLOR_BACKGROUND).pack(expand=True, pady=(30,0))
    else:
      self.listbox_tasks = tk.Listbox(self)
      self.listbox_tasks.pack(side="top", fill="both", expand=True, padx=10, anchor="n")
      self.listbox_tasks.bind("<Double-1>", lambda x: self.complete_task())

  def set_custom_time(self):
    if self.time_minutes_var_selected.get() > 60:
      messagebox.showerror("Custom Time Error", "Custom time invalid, it can't be over 60 minutes.")
    else:
      self.timer_minutes_var = abs(self.time_minutes_var_selected.get())
      self.time_text.config(text=f"{self.timer_minutes_var:02d}:{self.timer_seconds_var:02d}")
    
  def reset(self):
    self.timer_minutes_var = abs(self.time_minutes_var_selected.get())
    self.timer_seconds_var = 0
    self.time_text.config(text=f"{self.timer_minutes_var:02d}:{self.timer_seconds_var:02d}")
  
  def start(self):
    if self.start_button["text"].lower() == "start":

      self.pause_timer = False
      self.id_timer = self.after(1000, self.update_timer)

      self.start_button.config(text="Pause")
    elif self.start_button["text"].lower() == "pause":

      self.pause_timer = True
      self.id_timer = self.after(1000, self.update_timer)

      self.start_button.config(text="Start")

  def update_timer(self):
    if not self.pause_timer:
      if (self.timer_minutes_var > 0 or self.timer_seconds_var > 0):
        total_seconds = self.timer_minutes_var * 60 + self.timer_seconds_var - 1
        self.timer_minutes_var, self.timer_seconds_var = divmod(total_seconds, 60)
        self.time_text.config(text=f"{self.timer_minutes_var:02d}:{self.timer_seconds_var:02d}")
        self.id_timer = self.after(1000, self.update_timer)

      else:
        self.save()
        messagebox.showinfo("Study Session Ended", "Study session completed. Take a break before the next session.")
        self.after_cancel(self.id_timer)
        self.id_timer = None
        self.reset()
        self.controller.run()

  def changed_working_on_category(self):
    category = self.working_on_category_selected.get()

    if category.lower() == "subjects":
      with open(CONFIG_FILE, "r") as read_config_file:
        data = json.load(read_config_file)
      self.combobox_values["values"] = list(data["subjects"].keys())
      self.working_on_selected.set(value="")
    else:
      test = ["StudyArc", "Pacman"]      
      self.combobox_values["values"] = test
      self.working_on_selected.set(value="")

  def save(self):
    time_studied = self.time_minutes_var_selected.get()
    total_seconds_time_studied = time_studied * 60
    working_on_category_selected = self.working_on_category_selected.get()
    working_on_selected = self.working_on_selected.get()
    today_date = date.today()
    user_id = 1

    if working_on_category_selected != "" and working_on_selected != "":
      if working_on_category_selected.lower() == "subjects":
        with open(CONFIG_FILE, "r") as read_config_file:
          data = json.load(read_config_file)

        data["subjects"][working_on_selected] = total_seconds_time_studied

        with open(CONFIG_FILE, "w") as updated_config_file:
          updated_config_file.write(json.dumps(data, indent=4))

    self.cursor.execute("INSERT INTO sessions (date, time, description, user_id) VALUES (?, ?, ?, ?)", (today_date, total_seconds_time_studied, working_on_selected, user_id))
    self.conn.commit()

  def add_task(self):
    name_new_task = self.name_new_task_stringvar.get()

    if (name_new_task != "" or len(name_new_task) != 0):
      self.num_tasks += 1

      if self.num_tasks == 1:
        self.run_tasks()

      self.tasks.append(name_new_task.lower())
      self.listbox_tasks.insert(tk.END, f"{self.num_tasks-1}. {name_new_task.capitalize()}")
      self.name_new_task_stringvar.set("")
    else:
      messagebox.showerror("Empty task", "Tasks cannot be empty.")

  def complete_task(self):
    selected_index = self.listbox_tasks.curselection()
    if selected_index:
        selected_item = self.listbox_tasks.get(selected_index[0])
        id, name = selected_item.split(". ")
        del self.tasks[int(id)]
        self.listbox_tasks.delete(int(id))