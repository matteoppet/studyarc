from pydoc import text
from tkinter import messagebox
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

from utils.utils import format_time, get_time_from_seconds

class ProjectOverview(ctk.CTkToplevel):
  def __init__(self, root, cursor, conn, id_project, user_id, profile_class):
    super().__init__(root)
    self.root = root
    self.cursor = cursor
    self.id_project = id_project
    self.conn = conn
    self.user_id = user_id
    self.profile_class = profile_class

    self.cursor.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (self.id_project, self.user_id[0]))
    self.data_project = self.cursor.fetchone()

    self.title(self.data_project[1])
    self.geometry(f"700x600+{self.winfo_pointerx()}+{self.winfo_pointery()}")
    self.protocol("WM_DELETE_WINDOW", lambda: self.close_window())

    self.status = tk.StringVar(value=self.data_project[2])
    self.status_available = ["Not Started", "In Progress", "Done"]
    self.reset_time = False

    self.edit_mode = False

    self.run()

  def run(self):
    for widgets in self.winfo_children():
      widgets.destroy()
    
    self.cursor.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (self.id_project, self.user_id[0]))
    self.data_project = self.cursor.fetchone()

    frame_title = ctk.CTkFrame(self, fg_color="transparent")
    frame_title.pack(side="top", fill="x", padx=15, pady=10)
    ctk.CTkLabel(frame_title, text=self.data_project[1], font=("TkDefaultFont", 30, "bold")).pack(side="left")
    self.button_edit = ctk.CTkButton(frame_title, text="Save" if self.edit_mode else "Edit", width=60, command=lambda: self.change_edit_mode(), fg_color="green" if self.edit_mode else None)
    self.button_edit.pack(side="right")

    ttk.Separator(self, orient="horizontal").pack(side="top", fill="x")

    frame_content = ctk.CTkFrame(self, fg_color="transparent")
    frame_content.pack(side="top", fill="both", padx=10, pady=(15,10), expand=True)

    frame_left = ctk.CTkFrame(frame_content, fg_color="transparent")
    frame_left.pack(side="left", fill="both", expand=True)
    self.run_frame_left(frame_left)

    self.frame_right = ctk.CTkFrame(frame_content, fg_color="transparent")
    self.frame_right.pack(side="right", fill="y", padx=(10,0))
    self.run_frame_right(self.frame_right)

  def run_frame_left(self, frame):
    for widgets in frame.winfo_children():
      widgets.destroy()

    COLOR_TEXT = "white" if ctk.get_appearance_mode() == "black" else "black"

    ############ FRAME STATUS
    frame_label_status = ctk.CTkFrame(frame, fg_color="transparent")
    frame_label_status.pack(side="top", anchor="nw", padx=10)
    ctk.CTkLabel(frame_label_status, text="Status:", width=85, anchor="w").pack(side="left")

    color_background_status = "lightgray"
    if self.data_project[2] == "In Progress":
      color_background_status = "orange"
    elif self.data_project[2] == "Done":
      color_background_status = "lightgreen"

    if self.edit_mode:
      optionmenu = ctk.CTkOptionMenu(frame_label_status, variable=self.status, values=self.status_available)
      optionmenu.pack(side="left")

    else:
      frame_status = ctk.CTkFrame(frame_label_status, fg_color=color_background_status, width=100, height=26)
      frame_status.pack(side="left")
      ctk.CTkLabel(frame_status, text=self.data_project[2], text_color=COLOR_TEXT).pack(anchor="center", padx=10)
      frame_status.pack_propagate(False)

    ########### FRAME TIME
    frame_label_time = ctk.CTkFrame(frame, fg_color="transparent")
    frame_label_time.pack(side="top", anchor="nw", pady=10, padx=10)
    ctk.CTkLabel(frame_label_time, text="Time Spent:", width=85, anchor="w").pack(side="left")
    frame_time = ctk.CTkFrame(frame_label_time, fg_color="lightgray", width=100, height=26)
    frame_time.pack(side="left")

    hours, minutes, seconds = get_time_from_seconds(self.data_project[3])
    formatted_time = format_time(hours, minutes, seconds)

    self.time_label = ctk.CTkLabel(frame_time, text=formatted_time, text_color=COLOR_TEXT)
    self.time_label.pack(anchor="center", padx=10)
    frame_time.pack_propagate(False)

    if self.edit_mode:
      ctk.CTkButton(frame_label_time, text="Reset", command=lambda: self.reset_time_func(), fg_color="red", width=50).pack(side="left", padx=10)

    ########## FRAME TEXTBOX
    ctk.CTkLabel(frame, text="Notes", font=("TkDefaultFont", 22, "bold"), anchor="w", fg_color="transparent").pack(side="top", fill="x", padx=10, pady=(15, 10))
    ctk.CTkTextbox(frame).pack(fill="both", padx=10, expand=True)

  def run_frame_right(self, frame):
    for widgets in frame.winfo_children():
      widgets.destroy()

    ctk.CTkLabel(frame, text="Tasks", font=("TkDefaultFont", 22, "bold"), anchor="w", fg_color="transparent").pack(side="top", fill="x", padx=10, pady=(15, 10))

    button_add_task = ctk.CTkButton(frame, text="Add Task", command=lambda: self.add_task())
    button_add_task.pack(side="top", fill="x", pady=10, padx=10)

    frame_tasks = ctk.CTkScrollableFrame(frame, width=300)
    frame_tasks.pack(side="top", fill="both", expand=True,  padx=10, pady=10)

    self.cursor.execute("SELECT id, name FROM projects_tasks WHERE user_id = ? AND project_id = ?", (self.user_id[0], self.data_project[0]))
    rows = self.cursor.fetchall()

    if len(rows) == 0:
      ctk.CTkLabel(frame_tasks, text="No Tasks").pack(side="top", anchor="center", pady=10)
    else:
      for row in reversed(rows):
        frame_current_task = ctk.CTkFrame(frame_tasks)
        frame_current_task.pack(side="top", fill="x", padx=5, pady=5)

        ctk.CTkButton(frame_current_task, text="✔", width=30, command=lambda r=row: self.mark_task_done(r[0])).pack(side="right", padx=(5,5), pady=5)
        ctk.CTkLabel(frame_current_task, text=row[1], wraplength=200, justify="left").pack(side="left", padx=5, pady=5)
    
  def add_task(self):
    task_dialog = ctk.CTkInputDialog(title="New Task", text="Enter new task:")
    text = task_dialog.get_input()

    if text:
      self.cursor.execute("INSERT INTO projects_tasks (name, project_id, user_id) VALUES (?, ?, ?)", (text, self.user_id[0], self.data_project[0]))
      self.conn.commit()
    
      self.run_frame_right(self.frame_right)

  def mark_task_done(self, id_task):
    self.cursor.execute("DELETE FROM projects_tasks WHERE id = ? AND user_id = ? AND project_id = ?", (id_task, self.user_id[0], self.data_project[0]))
    self.conn.commit()

    xp_given = self.profile_class.set_reward_task()
    self.profile_class.set_increase_xp(xp_given)

    messagebox.showinfo("Task Completed",  f"✅ Task completed! You earned +{xp_given} XP. Keep it up!")

    self.run_frame_right(self.frame_right)

  def change_edit_mode(self):
    if self.edit_mode:
      new_status = self.status.get()

      if self.reset_time:
        self.cursor.execute("UPDATE projects SET status = ?, time = ? WHERE id = ? AND user_id = ?", (new_status, 0, self.data_project[0], self.user_id[0]))
        self.conn.commit()
      else:
        self.cursor.execute("UPDATE projects SET status = ? WHERE id = ? AND user_id = ?", (new_status, self.data_project[0], self.user_id[0]))
        self.conn.commit()

    self.edit_mode = not self.edit_mode
    self.run()
    self.root.treeview

  def reset_time_func(self):
    if not self.reset_time and messagebox.askyesno("Reset Time", "Are you sure to reset the time spent on this project?\n\nAction not reversible."):
      self.time_label.configure(text="0:00:00")
      self.reset_time = True

  def close_window(self):
    self.root.create_widgets()
    self.destroy()

class SectionFrame(ctk.CTkFrame):
  def __init__(
    self, root, cursor, conn, user_id, title, profile_class):
    ctk.CTkFrame.__init__(self, root)
    self.root = root
    self.cursor = cursor
    self.conn = conn
    self.user_id = user_id,
    self.title = title
    self.profile_class = profile_class

    self.pack(side="top", fill="both", padx=10, pady=20, expand=True)
    self.configure(fg_color="transparent")

    self.create_widgets()

  def create_widgets(self):
    for widgets in self.winfo_children():
      widgets.destroy()

    frame_title = ctk.CTkFrame(self, fg_color="transparent")
    frame_title.pack(side="top", fill="x")
    ctk.CTkLabel(frame_title, text=self.title, font=("TkDefaultFont", 24, "bold"), anchor="w").pack(side="left")
    ctk.CTkButton(frame_title, text=f"Add {self.title}", command=lambda: self.add()).pack(side="right")
 
    ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

    columns = []
    if self.title == "Projects":
      columns = ["id", "name", "time", "status"]
    elif self.title == "Subjects":
      columns = ["id", "name", "time"]

    self.treeview = ttk.Treeview(
      self, columns=columns[2:]
    )

    for column in columns[1:]:
      self.treeview.heading(
        "#0" if column == "name" else column, 
        text=column.capitalize(),
        anchor="w"
      )

    columns_str = ", ".join(columns)
    self.cursor.execute(f"SELECT {columns_str} FROM {self.title.lower()} WHERE user_id = ?", (self.user_id))
    rows = self.cursor.fetchall()

    if self.title == "Projects":
      self.cursor.execute("SELECT id FROM projects WHERE status = ? AND user_id = ?", ("In Progress", self.user_id[0]))
      in_progress_projects = len(self.cursor.fetchall())
      
    for row in rows:
      tags = ""
      if self.title == "Projects":
        tags = [row[-1],]

      hours_current_project, minutes_current_project, seconds_current_project = get_time_from_seconds(row[2])
      formatted_time_string = format_time(hours_current_project, minutes_current_project, seconds_current_project)
      try:
        values = [formatted_time_string, row[3]]
      except IndexError:
        values = [formatted_time_string]

      position = tk.END
      if self.title == "Projects":
        if row[3] == "In Progress":
          position = 0
        elif row[3] == "Not Started":
          position = in_progress_projects
      

      self.treeview.insert(
        "",
        position,
        iid=row[0],
        text=row[1],
        values=values,
        tags=tags
      )

    if self.title.lower() == "projects":
      self.treeview.tag_configure("In Progress", foreground="orange")
      self.treeview.tag_configure("Done", foreground="green")

    if self.title == "Projects":
      self.treeview.bind("<Double-1>", self.open_project)
    self.treeview.pack(side="top", fill="both", expand=True)

    self._set_appearance_mode(ctk.get_appearance_mode())

  def add(self):
    dialog = ctk.CTkInputDialog(title=self.title, text=f"Enter name new {self.title.lower()[0:-1]}")
    text = dialog.get_input()

    if text:
      if self.title == "Projects":
        self.cursor.execute("INSERT INTO projects (name, time, status, user_id) VALUES (?,?,?,?)", (text, 0, "Not Started", self.user_id[0]))
        self.conn.commit()

        new_id = self.cursor.lastrowid

        self.cursor.execute("SELECT id FROM projects WHERE status = ? AND user_id = ?", ("In Progress", self.user_id[0]))
        in_progress_projects = len(self.cursor.fetchall())
        position = in_progress_projects

        self.treeview.insert("",
        position,
        iid=new_id,
        text=text,
        values=[format_time(0,0,0), "Not Started"])
      elif self.title == "Subjects":
        self.cursor.execute("INSERT INTO subjects (name, time, user_id) VALUES (?,?,?)", (text, 0, self.user_id[0]))
        self.conn.commit()

        new_id = self.cursor.lastrowid

        self.treeview.insert("",
        tk.END,
        iid=new_id,
        text=text,
        values=[format_time(0,0,0)])

  def open_project(self, event):
    project_selected = self.treeview.selection()
    if project_selected:
      id_project = project_selected[0]
      ProjectOverview(self, self.cursor, self.conn, id_project, self.user_id, self.profile_class)

  def _set_appearance_mode(self, mode_string):
    super()._set_appearance_mode(mode_string)

    style = ttk.Style()
    style.theme_use("clam")

    if mode_string.lower() == "dark":
      style.configure(
        "Dark.Treeview",
        background="#1e1e1e",
        foreground="white",
        fieldbackground="#1e1e1e",
        rowheight=25,
        relief="flat"
      )

      style.map ("Dark.Treeview",
                 background=[("selected", "#0078d4")],
                 foreground=[("selected", "white")]
      )
      
      style.configure("Dark.Treeview.Heading",
            background="#2d2d2d",
            foreground="white",
      )

      style.configure("TSeparator", background="#2b2b2b")
      self.treeview.config(style="Dark.Treeview")

    elif mode_string.lower() == "light":
      style.configure("Light.Treeview",
          background="white",
          foreground="black",
          fieldbackground="white",
          rowheight=25,
      )

      style.map("Light.Treeview",
          background=[("selected", "#cce7ff")],
          foreground=[("selected", "black")]
      )

      style.configure("Light.Treeview.Heading",
          background="#f0f0f0",
          foreground="black",
      )

      style.configure("TSeparator", background="#cccccc")
      self.treeview.config(style="Light.Treeview")

class Projects(ctk.CTkFrame):
  def __init__(self, root, cursor, conn, user_id, profile_class):
    ctk.CTkFrame.__init__(self, root)
    self.root = root
    self.cursor = cursor
    self.conn = conn
    self.user_id = user_id
    self.profile_class = profile_class

    self.pack(side="top", padx=10, pady=10, anchor="nw", fill="both", expand=True)

    self.run()

  def run(self):
    for widgets in self.winfo_children():
      widgets.destroy()

    SectionFrame(
      self, self.cursor, self.conn, self.user_id, "Projects", self.profile_class
    )

    SectionFrame(
      self, self.cursor, self.conn, self.user_id, "Subjects", self.profile_class
    )