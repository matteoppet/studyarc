import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.simpledialog import askstring

from core.settings import COLOR_BACKGROUND, COLOR_FOREGROUND
from core.__init__ import CONFIG_FILE
from utils.utils import get_time_from_seconds, format_time, resource_path

import json

class ProjectOVerview(tk.Toplevel):
  def __init__(self, root, id_project, cursor, conn, user_id, treeview_projects):
    super().__init__(root)
    self.id_project = id_project
    self.root = root
    self.cursor = cursor
    self.conn = conn
    self.user_id = user_id
    self.treeview_projects = treeview_projects
    
    self.cursor.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (self.id_project, self.user_id))
    self.data_project = self.cursor.fetchall()[0]

    self.title = self.data_project[1]
    self.geometry(f"600x500+{self.winfo_pointerx()}+{self.winfo_pointery()}")
    try:
      self.iconbitmap("../assets/icon.ico")
    except tk.TclError:
      self.iconbitmap(resource_path("assets/icon.ico"))

    self.container = tk.Frame(self)
    self.container.pack(fill="both", expand=True, padx=10, pady=10)

    self.new_task_name = tk.StringVar()
    self.status_edit = tk.StringVar(value=self.data_project[2])
    self.title_edit = tk.StringVar(value=self.title)

    self.edit_var = False

    self.run()

  def run(self):
    for widgets in self.container.winfo_children():
      widgets.destroy()

    WIDTH_LABELS = 15

    frame_head = tk.Frame(self.container)
    frame_head.pack(side="top", fill="x")
    if self.edit_var:
      tk.Entry(frame_head, textvariable=self.title_edit).pack(side="left", fill="x", expand=True, padx=(0,20))
    else:
      tk.Label(frame_head, textvariable=self.title_edit, font=("TkDefaultFont", 16, "bold"), anchor="w", bg=COLOR_BACKGROUND, fg=COLOR_FOREGROUND).pack(side="left", fill="x")
    self.edit_button = tk.Button(frame_head, text="Save" if self.edit_var else "Edit", width=10, command=lambda: self.edit())
    self.edit_button.pack(side="right")

    ttk.Separator(self.container, orient="horizontal").pack(fill="x", pady=10)

    frame_status = tk.Frame(self.container)
    frame_status.pack(side="top", fill="x")
    tk.Label(frame_status, text="Status:", width=WIDTH_LABELS, font=("TkDefaultFont", 10, "bold"), anchor="w").pack(side="left")
    if self.edit_var:
      ttk.Combobox(frame_status, textvariable=self.status_edit, values=["Not Started", "In Progress", "Done"]).pack(side="left")
    else:
      tk.Label(frame_status, text=f"{self.status_edit.get()}", anchor="w").pack(side="left", fill="x", pady=(2,0))

    frame_time_studied = tk.Frame(self.container)
    frame_time_studied.pack(side="top", fill="x", pady=(5,0))
    tk.Label(frame_time_studied, text="Total Time:", width=WIDTH_LABELS, font=("TkDefaultFont", 10, "bold"), anchor="w").pack(side="left")
    hours, minutes, seconds = get_time_from_seconds(self.data_project[3])
    tk.Label(frame_time_studied, text=f"{hours}h {minutes}m {seconds}s", anchor="w").pack(side="left", fill="x", pady=(2,0))

    ttk.Separator(self.container, orient="horizontal").pack(fill="x", pady=10)

    notebook = ttk.Notebook(self.container)
    notebook.pack(side="top", fill="both", expand=True)

    frame_tasks = tk.Frame(notebook)
    frame_logs = tk.Frame(notebook)

    frame_tasks.pack(fill="both", expand=True)
    frame_logs.pack(fill="both", expand=True)

    notebook.add(frame_tasks, text="Tasks")
    notebook.add(frame_logs, text="Time Logs")

    self.run_tasks(frame_tasks)
    self.run_logs(frame_logs)

    ttk.Separator(self.container, orient="horizontal").pack(fill="x", pady=10)

    frame_foot_buttons = tk.Frame(self.container)
    frame_foot_buttons.pack(side="top", fill="x")
    tk.Button(frame_foot_buttons, text="Close", command=lambda: self.destroy()).pack(side="right")

  def run_tasks(self, frame):
    tk.Label(frame, text="Tasks", font=("TkDefaultFont", 13, "bold"), anchor="w").pack(side="top", fill="x", pady=10, padx=10)

    add_task_frame = tk.Frame(frame)
    add_task_frame.pack(side="top", fill="x", padx=10, pady=(0,10))
    tk.Entry(add_task_frame, textvariable=self.new_task_name).pack(side="left", expand=True, fill="x", pady=(2,0))
    tk.Button(add_task_frame, text="Add", command=lambda: self.add_tasks()).pack(side="left", padx=(10,0))

    self.treeview_tasks = ttk.Treeview(frame, height=8, columns=("Status",))
    self.treeview_tasks.pack(side="top", fill="both", expand=True, padx=10, pady=(0,10))

    self.treeview_tasks.heading("#0", text="Name")
    self.treeview_tasks.heading("Status", text="Status")

    self.cursor.execute("SELECT id, name, status FROM projects_tasks WHERE project_id = ? AND user_id = ?", (self.id_project, self.user_id))
    for row in self.cursor.fetchall():
      self.treeview_tasks.insert(
        "",
        index = 0 if row[2].lower() == "in progress" else tk.END,
        text=row[1],
        values=[row[2]],
        iid=int(row[0])
      )

    self.collapse_menu = tk.Menu(self, tearoff=0)
    self.collapse_menu.add_command(label="Delete", command=lambda: self.delete_task())

    menustatus = tk.Menu(self.collapse_menu, tearoff=0)
    menustatus.add_command(label="Not Started", command=lambda: self.change_tasks_status("Not Started"))
    menustatus.add_command(label="In Progress", command=lambda: self.change_tasks_status("In Progress"))
    menustatus.add_command(label="Done", command=lambda: self.change_tasks_status("Done"))

    self.collapse_menu.add_cascade(label="Status", menu=menustatus)
    self.treeview_tasks.bind("<Button-3>", self.open_collapse_menu_tasks)

  def run_logs(self, frame):
    tk.Label(frame, text="Logs", font=("TkDefaultFont", 13, "bold"), anchor="w").pack(side="top", fill="x", pady=10, padx=10)

    self.cursor.execute("SELECT date, time FROM sessions WHERE user_id = ? AND description = ?", (self.user_id, self.title))
    sessions = self.cursor.fetchall()

    if len(sessions) == 0:
      tk.Label(frame, text="No Logs Available").pack(expand=True, anchor="center", fill="both")
    else:
      treeview_logs = ttk.Treeview(frame, height=8, columns=("Time",))
      treeview_logs.pack(side="top", padx=10, pady=10, expand=True, fill="both")

      treeview_logs.heading("#0", text="Date")
      treeview_logs.heading("Time", text="Time")
      treeview_logs.column("Time", anchor="center")
      treeview_logs.column("#0", anchor="center")

      self.cursor.execute("SELECT date, time FROM sessions WHERE user_id = ? AND description = ?", (self.user_id, self.title))
      for row in self.cursor.fetchall():
        treeview_logs.insert("", 0, text=row[0], values=[row[1]])

  def add_tasks(self):
    new_task_name = self.new_task_name.get()

    self.cursor.execute("INSERT INTO projects_tasks (name, status, project_id, user_id) VALUES (?, ?, ?, ?)", (new_task_name, "Not Started", self.id_project, self.user_id))
    self.conn.commit()

    new_task_id = self.cursor.lastrowid

    self.cursor.execute("SELECT id FROM projects_tasks WHERE status = ? AND project_id = ? AND user_id = ?", ("In Progress", self.id_project, self.user_id))
    rows = self.cursor.fetchall()

    self.treeview_tasks.insert(
      "",
      len(rows),
      text=new_task_name,
      values=["Not Started"],
      iid = new_task_id
    )
    self.new_task_name.set(value="")

  def change_tasks_status(self, new_status):
    id_task = self.treeview_tasks.selection()[0]

    self.cursor.execute("UPDATE projects_tasks SET status = ? WHERE id = ? AND project_id = ? AND user_id = ?", (new_status, id_task, self.id_project, self.user_id))
    self.conn.commit()

    self.treeview_tasks.delete(id_task)
    self.cursor.execute("SELECT id, name, status FROM projects_tasks WHERE user_id = ? AND id = ? AND project_id = ?", (self.user_id, id_task, self.id_project))
    task_values = self.cursor.fetchall()[0]
    self.treeview_tasks.insert(
      "",
      index=0 if task_values[2].lower() == "in progress" else tk.END,
      text=task_values[1],
      values=[task_values[2]],
      iid=int(task_values[0])
    )

  def delete_task(self):
    selected_item = self.treeview_tasks.selection()
    if selected_item:
      id_task = selected_item[0]

      self.cursor.execute("DELETE FROM projects_tasks WHERE id = ? AND user_id = ? AND project_id = ?", (id_task, self.user_id, self.id_project))
      self.conn.commit()

      self.treeview_tasks.delete(id_task)

  def open_collapse_menu_tasks(self, event):
    item_id = self.treeview_tasks.identify_row(event.y)
    if item_id:
      self.treeview_tasks.selection_set(item_id)
      self.collapse_menu.post(event.x_root, event.y_root)

  def edit(self):
    if self.edit_var:
      new_title = self.title_edit.get()
      new_status = self.status_edit.get()

      self.cursor.execute("UPDATE projects SET name = ?, status = ? WHERE id = ? AND user_id = ?", (new_title, new_status, self.id_project, self.user_id))
      self.conn.commit()
      hours, minutes, seconds = get_time_from_seconds(int(self.data_project[3]))
      self.treeview_projects.item(self.id_project, text=new_title, values=[new_status,f"{hours}h {minutes:02d}m {seconds:02d}s"])

      if new_status.lower() == "done":
        self.treeview_projects.move(self.id_project, self.treeview_projects.parent(self.id_project) if self.data_project[5] else "", tk.END)

      self.edit_button.config(text="Edit")
      self.edit_var = False
      self.run()
    else:
      self.edit_button.config(text="Save")
      self.edit_var = True
      self.run()

class Projects(tk.Frame):
  def __init__(self, root, cursor, conn, user_id):
    tk.Frame.__init__(self, root)
    self.config(bg=COLOR_BACKGROUND)
    self.pack(side="left", pady=(5, 28), anchor="nw", padx=(35, 25), fill="both", expand=True)

    self.cursor = cursor
    self.conn = conn
    self.user_id = user_id
    
    self.new_subject_name = tk.StringVar()
    self.new_project_name = tk.StringVar()

    self.project_folders = {}
    self.selected_project_folder = tk.StringVar(value="")
    self.load_project_folders()
    
    self.run()

  def run(self):
    for widgets in self.winfo_children():
      widgets.destroy()

    notebook = ttk.Notebook(self)
    notebook.pack(side="top", fill="both", expand=True)

    frame_subjects = tk.Frame(notebook)
    frame_projects = tk.Frame(notebook) 

    frame_subjects.pack(fill='both', expand=True)
    frame_projects.pack(fill='both', expand=True)

    notebook.add(frame_subjects, text="Subjects")
    notebook.add(frame_projects, text="Projects")

    self.run_subjects(frame_subjects)
    self.run_projects(frame_projects)

  def run_subjects(self, frame):
    tk.Label(frame, text="Subjects", font=("TkDefaultFont", 18, "bold"), anchor="w", bg=COLOR_BACKGROUND, fg=COLOR_FOREGROUND).pack(side="top", fill="x", padx=10, pady=10)

    frame_add_subject_and_treeview = tk.Frame(frame)
    frame_add_subject_and_treeview.pack(side="left", fill="both", expand=True, padx=10)

    frame_add_subject = tk.Frame(frame_add_subject_and_treeview)
    frame_add_subject.pack(side="top", anchor="n", fill="x", pady=(0,5))
    tk.Entry(frame_add_subject, textvariable=self.new_subject_name).pack(side="left", anchor="n", fill="x", expand=True)
    tk.Button(frame_add_subject, text="Add", command=lambda: self.add_subject()).pack(side="left", padx=(10,0))

    self.treeview_subjects = ttk.Treeview(frame_add_subject_and_treeview, columns=("Time",), show="tree headings")
    self.treeview_subjects.pack(side="top", fill="both", expand=True)

    self.treeview_subjects.heading("#0", text="Name")
    self.treeview_subjects.heading("Time", text="Time Studied")
    self.treeview_subjects.column("Time", anchor="center")

    # init listbox with created subjects
    with open(CONFIG_FILE, "r") as read_config_file:
      data = json.load(read_config_file)
    
    count = 0
    for subject, time in data["subjects"].items():
      hours, minutes, seconds = get_time_from_seconds(int(time))
      self.treeview_subjects.insert("", tk.END, iid=count, text=subject, values=[f"{hours:02d}h {minutes:02d}m {seconds:02d}s"])
      count += 1

    controls_frame = tk.Frame(frame)
    controls_frame.pack(side="left", fill="both", padx=10)
    WIDTH_BUTTONS = 15
    tk.Button(controls_frame, text="Delete", width=WIDTH_BUTTONS, command=lambda: self.delete_subject()).pack(side="top", pady=(31,0))
    
    ttk.Separator(controls_frame, orient="horizontal").pack(side="top", fill="x", pady=10)

    tk.Button(controls_frame, text="Move up", state="disabled", width=WIDTH_BUTTONS, command=lambda: self.move_subject(-1)).pack(side="top", pady=(0,5))
    tk.Button(controls_frame, text="Move down", state="disabled", width=WIDTH_BUTTONS, command=lambda: self.move_subject(-1)).pack(side="top", pady=(0,5))

  def run_projects(self, frame):
    tk.Label(frame, text="Projects", font=("TkDefaultFont", 18, "bold"), anchor="w", bg=COLOR_BACKGROUND, fg=COLOR_FOREGROUND).pack(side="top", fill="x", padx=10, pady=10)

    frame_add_project_and_treview = tk.Frame(frame)
    frame_add_project_and_treview.pack(side="left", fill="both", expand=True, padx=10)

    frame_add_project = tk.Frame(frame_add_project_and_treview)
    frame_add_project.pack(side="top", anchor="n", fill="x", pady=(0,5))
    tk.Entry(frame_add_project, textvariable=self.new_project_name).pack(side="left", anchor="n", fill="x", expand=True)
    tk.Button(frame_add_project, text="Add", command=lambda: self.add_project()).pack(side="left", padx=(10,0))
    self.combobox_project_folder = ttk.Combobox(frame_add_project, values=list(self.project_folders.keys()), textvariable=self.selected_project_folder)
    self.combobox_project_folder.pack(side="right", padx=(10,0))

    self.treeview_projects = ttk.Treeview(frame_add_project_and_treview, columns=("Status","Time"))
    self.treeview_projects.pack(side="top", fill="both", expand=True)

    self.collapse_menu = tk.Menu(self, tearoff=0)
    self.collapse_menu.add_command(label="Open", command=lambda: self.open_project())
    self.collapse_menu.add_command(label="Delete", command=lambda: self.delete_project())

    menustatus = tk.Menu(self.collapse_menu, tearoff=0)
    menustatus.add_command(label="Not Started", command=lambda: self.change_project_status("Not Started"))
    menustatus.add_command(label="In Progress", command=lambda: self.change_project_status("In Progress"))
    menustatus.add_command(label="Done", command=lambda: self.change_project_status("Done"))

    self.collapse_menu.add_cascade(label="Status", menu=menustatus)
    self.treeview_projects.bind("<Button-3>", self.open_collapse_menu)

    self.treeview_projects.bind("<<TreeviewOpen>>", self.on_open)
    self.treeview_projects.bind("<<TreeviewClose>>", self.on_close)

    self.treeview_projects.heading("#0", text="Name")
    self.treeview_projects.heading("Status", text="Status")
    self.treeview_projects.heading("Time", text="Time")
    self.treeview_projects.column("Time", anchor="center")
    self.treeview_projects.column("Status", anchor="center")

    try:
      self.folder_icon_open = tk.PhotoImage(file=resource_path("assets/open_folder.png"))
      self.folder_icon_close = tk.PhotoImage(file=resource_path("assets/close_folder.png"))
    except tk.TclError:
      self.folder_icon_open = tk.PhotoImage(file="../assets/open_folder.png")
      self.folder_icon_close = tk.PhotoImage(file="../assets/close_folder.png")

    for folder, open in self.project_folders.items():
      self.treeview_projects.insert("", tk.END, text=folder, open=open, image=self.folder_icon_open if open else self.folder_icon_close)

    self.cursor.execute("SELECT id, name, status, time, folder FROM projects WHERE user_id = ?", (self.user_id,))
    self.filter_by_status(self.treeview_projects, self.cursor.fetchall())

    controls_frame = tk.Frame(frame)
    controls_frame.pack(side="left", fill="both", padx=10)
    WIDTH_BUTTONS = 15
    tk.Button(controls_frame, text="Open", width=WIDTH_BUTTONS, command=lambda: self.open_project()).pack(side="top", pady=(31,0))
    
    ttk.Separator(controls_frame, orient="horizontal").pack(side="top", fill="x", pady=10)

    tk.Button(controls_frame, text="Add Folder", width=WIDTH_BUTTONS, command=lambda: self.add_folder()).pack(side="top", pady=(0,5))
    tk.Button(controls_frame, text="Delete Folder", width=WIDTH_BUTTONS, command=lambda: self.delete_folder()).pack(side="top", pady=(0,5))
    
    ttk.Separator(controls_frame, orient="horizontal").pack(side="top", fill="x", pady=10)

    tk.Button(controls_frame, text="Delete", width=WIDTH_BUTTONS, command=lambda: self.delete_project()).pack(side="top", pady=(0,5))

  def filter_by_status(self, treeview, rows):
    status_priority = {
      "In Progress": 0,
      "Not Started": 1,
      "Done": 2
    }

    sorted_data = sorted(rows, key=lambda x: status_priority.get(x[2], 99))

    for row in sorted_data:
      hours, minutes, seconds = get_time_from_seconds(int(row[3]))
      formatted_time = format_time(hours, minutes, seconds)
      folder_iid = self.find_folder_by_name(row[4])

      treeview.insert(
        "" if folder_iid is None else folder_iid,
        tk.END,
        iid=row[0],
        text=row[1],
        values=[row[2], formatted_time]
      )

  def add_subject(self):
    new_subject_name = self.new_subject_name.get()

    with open(CONFIG_FILE, "r") as read_config_file:
      data = json.load(read_config_file)

    for name_subject in data["subjects"].keys():
      if name_subject.lower() == new_subject_name.lower():
        messagebox.showerror("Error adding subject", "This subject already exists.")
        return

    data["subjects"][new_subject_name] = 0

    with open(CONFIG_FILE, "w") as updated_config_file:
      updated_config_file.write(json.dumps(data, indent=4))

    self.treeview_subjects.insert("", 0, iid=len(data["subjects"].keys())-1, text=new_subject_name, values=[f"{0}h {0}m {0}s"])
    self.new_subject_name.set(value="")

  def delete_subject(self):
    selected_item = self.treeview_subjects.selection()
    if selected_item:

      with open(CONFIG_FILE, "r") as read_config_file:
        data = json.load(read_config_file)

      key_item_to_delete = list(data["subjects"].keys())[int(selected_item[0])]

      if messagebox.askokcancel("Delete Confirmation", f"Are you sure to delete this subject?\n\n-> {key_item_to_delete}\n\nThis action is not reversible."):
        del data["subjects"][key_item_to_delete]

        with open(CONFIG_FILE, "w") as updated_config_file:
          updated_config_file.write(json.dumps(data, indent=4))

        self.treeview_subjects.delete(selected_item[0])

  def move_subject(self, direction):
    raise NotImplementedError
  
  def add_project(self):
    new_project_name = self.new_project_name.get()
    folder_selected = self.selected_project_folder.get()
    folder_iid = self.find_folder_by_name(folder_selected)

    self.cursor.execute("SELECT name FROM projects WHERE name = ? AND user_id = ?", (new_project_name, self.user_id,))
    if len(self.cursor.fetchall()) != 0:
      messagebox.showerror("Project creation failed", "This project name already exists.")
      return
    if new_project_name == "":
      messagebox.showerror("Project creation failed", "Project name cannot be empty.")
      return
    
    self.cursor.execute("SELECT name FROM projects WHERE status = ? AND user_id = ?", ("In Progress", self.user_id,))
    project_in_progress = len(self.cursor.fetchall())

    self.cursor.execute("INSERT INTO projects (name, status, time, folder, user_id) VALUES (?, ?, ?, ?, ?)", (new_project_name, "Not Started", 0, folder_selected, self.user_id,))
    self.conn.commit()
    inserted_id = self.cursor.lastrowid
    self.treeview_projects.insert("" if folder_iid is None else folder_iid, project_in_progress, iid=inserted_id, text=new_project_name, values=["Not Started", "00h 00m 00s"])
    self.new_project_name.set(value="")

  def load_project_folders(self):
    with open(CONFIG_FILE, "r") as project_folders_file:
      data = json.load(project_folders_file)

    self.project_folders = data["project_folders"]

  def add_folder(self):
    new_folder_name = askstring("Creation Folder", "Insert folder name")
    
    if new_folder_name is None or new_folder_name == "":
      return

    with open(CONFIG_FILE, "r") as project_folders_file:
      data = json.load(project_folders_file)

    if new_folder_name in list(data["project_folders"].keys()):
      messagebox.showerror("Folder creation failed", "This folder already exists.")
      return

    data["project_folders"][new_folder_name] = False

    with open(CONFIG_FILE, "w") as updated_config_file:
      updated_config_file.write(json.dumps(data, indent=4))

    self.project_folders[new_folder_name] = False
    self.combobox_project_folder["values"] = list(self.project_folders.keys())
    self.treeview_projects.insert("", tk.END, text=new_folder_name, image=self.folder_icon_close)

  def find_folder_by_name(self, name):
    for item in self.treeview_projects.get_children():
        if self.treeview_projects.item(item, 'text') == name:
            return item
    return None
    
  def on_open(self, event):
    item_id = event.widget.focus()
    text = self.treeview_projects.item(item_id, 'text')
    self.treeview_projects.item(item_id, image=self.folder_icon_open)

    with open(CONFIG_FILE, "r") as project_folders_file:
      data = json.load(project_folders_file)

    data["project_folders"][text] = True

    with open(CONFIG_FILE, "w") as updated_config_file:
      updated_config_file.write(json.dumps(data, indent=4))
  
  def on_close(self, event):
    item_id = event.widget.focus()
    text = self.treeview_projects.item(item_id, 'text')
    self.treeview_projects.item(item_id, image=self.folder_icon_close)

    with open(CONFIG_FILE, "r") as project_folders_file:
      data = json.load(project_folders_file)

    data["project_folders"][text] = False

    with open(CONFIG_FILE, "w") as updated_config_file:
      updated_config_file.write(json.dumps(data, indent=4))
  
  def delete_folder(self):
    selected_item = self.treeview_projects.selection()
    if selected_item:
      item_id = selected_item[0]
      text = self.treeview_projects.item(item_id, 'text')

      with open(CONFIG_FILE, "r") as project_folders_file:
        data = json.load(project_folders_file)
      if text not in list(data["project_folders"].keys()):
        return

      self.cursor.execute("SELECT id FROM projects WHERE folder = ? AND user_id = ?", (text, self.user_id,))
      for row in self.cursor.fetchall():
        self.cursor.execute("UPDATE projects SET folder = ? WHERE id = ? AND user_id = ?", (None, row[0], self.user_id,))
        self.treeview_projects.move(row[0], "", tk.END)
        self.conn.commit()

      self.treeview_projects.delete(item_id)

      with open(CONFIG_FILE, "r") as project_folders_file:
        data = json.load(project_folders_file)

      del data["project_folders"][text]

      with open(CONFIG_FILE, "w") as updated_config_file:
        updated_config_file.write(json.dumps(data, indent=4))

  def delete_project(self):
    selected_item = self.treeview_projects.selection()
    if selected_item:
      item_id = selected_item[0]
      text = self.treeview_projects.item(item_id, 'text')

      if messagebox.askokcancel("Project Delete", f"Are you sure to delete this project?\n\n-> {text}\n\nThis action cannot be reversible."):
        self.cursor.execute("DELETE FROM projects WHERE id = ? AND user_id = ?", (item_id, self.user_id))
        self.conn.commit()

        self.treeview_projects.delete(item_id)

        messagebox.showinfo("Project Delete", "Project successfully deleted.")

  def open_collapse_menu(self, event):
    item_id = self.treeview_projects.identify_row(event.y)
    if item_id:
      self.treeview_projects.selection_set(item_id)
      self.collapse_menu.post(event.x_root, event.y_root)

  def change_project_status(self, new_status):
    id_project = self.treeview_projects.selection()[0]

    # update on the database
    self.cursor.execute("UPDATE projects SET status = ? WHERE id = ? AND user_id = ?", (new_status, int(id_project), self.user_id,))
    self.conn.commit()

    # update on the treeview table
    self.treeview_projects.delete(id_project)
    self.cursor.execute("SELECT id, name, status, time, folder FROM projects WHERE user_id = ? AND id  = ?", (self.user_id, id_project,))
    for row in self.cursor.fetchall():
      hours, minutes, seconds = get_time_from_seconds(int(row[3]))
      folder_iid = self.find_folder_by_name(row[4])
      self.treeview_projects.insert("" if folder_iid is None else folder_iid, tk.END if row[2] == "Not Started" else 0, iid=row[0], text=row[1], values=[row[2], f"{hours:02d}h {minutes:02d}m {seconds:02d}s"])

  def open_project(self):
    selected_item = self.treeview_projects.selection()
    if selected_item:
      ProjectOVerview(self, selected_item[0], self.cursor, self.conn, self.user_id, self.treeview_projects)