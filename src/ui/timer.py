import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

from datetime import timedelta, date
import json

from core.settings import COLOR_BACKGROUND
from utils.utils import get_time_from_seconds, format_time
from core.__init__ import CONFIG_FILE


class Timer(ctk.CTkFrame):
  def __init__(self, root, controller, cursor, conn, user_id):
    ctk.CTkFrame.__init__(self, root)
    self.root = root
    self.controller = controller
    self.cursor = cursor
    self.conn = conn
    self.user_id = user_id

    self.pack(side="top", anchor="nw", padx=25, pady=5, expand=True, fill="both")

    self.category_selected = tk.StringVar(value="Custom")
    self.description = tk.StringVar()
    self.categories_available = ["Custom", "Projects", "Subjects"]

    self.font_size_timer_label = 45
    self.timer_started = False
    self.pause_timer = False
    self.timer_minutes = 25
    self.timer_seconds = 0

    self.tasks = {}

    self.run()

  def run(self):
    for widgets in self.winfo_children():
      widgets.destroy()

    ctk.CTkLabel(self, text="Timer", font=("TkDefaultFont", 24, "bold"), anchor="w").pack(side="top", fill="x", pady=10, padx=10)

    ttk.Separator(self, orient="horizontal").pack(side="top", fill="x", pady=(0,10))

    frame_content = ctk.CTkFrame(self)
    frame_content.pack(side="top")

    frame_timer_label = ctk.CTkFrame(frame_content, fg_color="transparent")
    frame_timer_label.pack(side="top", anchor="center", pady=10, fill="x")
    self.timer_label = ctk.CTkLabel(frame_timer_label, text=f"{self.timer_minutes:02d}:{self.timer_seconds:02d}", font=("TKDefaultFOnt", self.font_size_timer_label, "bold"))
    self.timer_label.pack(side="top", anchor="center", pady=20, padx=20)

    frame_buttons = ctk.CTkFrame(frame_timer_label, fg_color="transparent")
    frame_buttons.pack(side="top", pady=(0,20))
    if self.timer_started:
      self.stop_timer_button = ctk.CTkButton(frame_buttons, text="Stop", command=lambda: self.stop_timer())
      self.stop_timer_button.pack(side="left", padx=(0,5))
      self.reset_timer_button = ctk.CTkButton(frame_buttons, text="Reset", command=lambda: self.reset_timer())
      self.reset_timer_button.pack(side="left")
    else:
      self.start_timer_button = ctk.CTkButton(frame_buttons, text="Start", command=lambda: self.start_timer())
      self.start_timer_button.pack(side="left")

    self.bind("<Configure>", self.resize_timer_font)

    frame_description = ctk.CTkFrame(frame_content, fg_color="transparent")
    frame_description.pack(side="top", fill="both")
    ctk.CTkLabel(frame_description, text="Insert a Description:").pack(side="top")
    self.frame_comboboxes_description = ctk.CTkFrame(frame_description, fg_color="transparent")
    self.frame_comboboxes_description.pack(side="top", fill="x", padx=10, pady=(5,10))
    self.category_combobox = ctk.CTkComboBox(self.frame_comboboxes_description, variable=self.category_selected, values=self.categories_available, command=lambda x: self.run_description_field(self.category_selected.get()), width=150)
    self.category_combobox.pack(side="left", padx=(0,10))
    
    # TODO: FIX THIS

    if self.category_selected.get() == "Custom":
      ctk.CTkEntry(self.frame_comboboxes_description, textvariable=self.description).pack(side="right")

    elif self.category_selected.get() == "Projects":
      self.cursor.execute("SELECT name FROM projects WHERE user_id = ?", (self.user_id,))
      rows = [row[0] for row in self.cursor.fetchall()]
      ctk.CTkComboBox(self.frame_comboboxes_description, variable=self.description, values=rows).pack(side="right")

    elif self.category_selected.get() == "Subjects":
      self.cursor.execute("SELECT name FROM projects WHERE user_id = ?", (self.user_id,))
      rows = [row[0] for row in self.cursor.fetchall()]
      ctk.CTkComboBox(self.frame_comboboxes_description, variable=self.description, values=rows).pack(side="right")

    frame_title = ctk.CTkFrame(self, fg_color="transparent")
    frame_title.pack(fill="x", padx=10, pady=(20,10))
    ctk.CTkLabel(frame_title, text="Tasks", font=("TkDefaultFont", 20, "bold")).pack(side="left")
    ctk.CTkButton(frame_title, text="Add", command=lambda: self.add_task()).pack(side="right")

    ttk.Separator(self, orient="horizontal").pack(side="top", fill="x", pady=(0,10))

    frame_tasks = ctk.CTkScrollableFrame(self, fg_color="transparent")
    frame_tasks.pack(side="top", fill="both", expand=True)
    if len(self.tasks.items()) == 0:
      ctk.CTkLabel(frame_tasks, text="No Tasks").pack(side="top", anchor="center", pady=10)
    else:
      for id, name in self.tasks.items():
        current_task_frame = ctk.CTkFrame(frame_tasks, fg_color="gray")
        current_task_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(current_task_frame, text=f"{id}:", width=25).pack(side="left")
        ctk.CTkLabel(current_task_frame, text=name).pack(side="left")
        ctk.CTkButton(current_task_frame, text="Complete", width=15, command=lambda x=id: self.delete_task(x)).pack(side="right", padx=5, pady=5)

  def resize_timer_font(self, event):
    self.font_size_timer_label = int(event.width / 10)
    self.timer_label.configure(font=("TKDefaultFont", self.font_size_timer_label, "bold"))

  def add_task(self):
    dialog = ctk.CTkInputDialog(text="Insert new task:", title="New Task")
    text = dialog.get_input()

    if text:
      highest_id = 0 if len(self.tasks.keys()) == 0 else max(self.tasks.keys())
      self.tasks[highest_id+1] = text
      self.run()

  def delete_task(self, id):
    del self.tasks[id]
    self.run()

  def start_timer(self):
    if not self.pause_timer:
      if self.timer_minutes == 0 and self.timer_seconds == 0:
        total_seconds = self.timer_minutes * 60 + self.timer_seconds - 1
        self.timer_minutes, self.timer_seconds = divmod(total_seconds, 60)
        self.timer_label.configure(text=f"{self.timer_minutes:02d}:{self.timer_seconds:02d}")
        self.id_timer = self.after(1000, self.start_timer)

        if not self.timer_started:
          self.timer_started = True
          self.run()
      else:
        self.save()
        self.reset_timer()

  def stop_timer(self):
    self.pause_timer = not self.pause_timer

    self.stop_timer_button.configure(text="Continue" if self.pause_timer else "Stop")

    self.after_cancel(self.id_timer)
    self.id_timer = self.after(1000, self.start_timer)
  
  def reset_timer(self):
    self.after_cancel(self.id_timer)
    self.timer_minutes = 25
    self.timer_seconds = 0
    self.timer_started = False
    self.run()

  def save(self):
    time_in_seconds = self.timer_minutes * 60 + self.timer_seconds
    category = self.category_selected.get()
    description = self.description.get()
    today = date.today()

    self.cursor.execute("INSERT INTO sessions (date, time, description, user_id) VALUES (?, ?, ?, ?)", (today, time_in_seconds, description, self.user_id))

    if category.lower() == "projects":
      self.cursor.execute("UPDATE projects SET time = time + ? WHERE user_id = ? AND name = ?", (time_in_seconds, self.user_id, description))
    elif category.lower() == "subjects":
      self.cursor.execute("UPDATE subjects SET time = time + ? WHERE user_id = ? AND name = ?", (time_in_seconds, self.user_id, description))

    self.conn.commit()