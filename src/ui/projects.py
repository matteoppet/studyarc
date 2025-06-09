import tkinter as tk
from tkinter import ttk
import csv
from tkinter import messagebox
from tkinter.simpledialog import askstring
import ast

from ui.style import StyleManager
from core.paths import PROJECTS_CSV
from utils.utils import seconds_to_time

import webbrowser
from tktooltip import ToolTip

class Tasks(tk.Frame):
  def __init__(self, root: tk.Toplevel, data_item: dict, frame: tk.Frame):
    self.root = root
    self.data_item = data_item
    self.frame = frame

    self.root.protocol("WM_DELETE_WINDOW", lambda: self.save_tasks())

    self.changes = False
    self.tasks = {}
    self.capped_ID = 0

    self.draw()
    self.load_tasks()

  def draw(self):
    frame_title = ttk.Frame(self.frame)
    frame_title.pack(side="top", fill="x")
    tk.Label(frame_title, text="Tasks Manager", anchor="w", font=(StyleManager.get_current_font(), 13, "bold")).pack(side="top", fill="x", anchor="w", pady=5)

    ttk.Separator(self.frame, orient="horizontal").pack(side="top", fill="x", pady=(0,5))

    frame_content = ttk.Frame(self.frame)
    frame_content.pack(side="top", fill="both", expand=True)

    frame_list_tasks = ttk.Frame(frame_content)
    frame_list_tasks.pack(side="left", padx=5, pady=5, expand=True, fill="both")

    self.list_tasks_todo = tk.Listbox(frame_list_tasks)
    self.list_tasks_todo.pack(side="top", fill="both", expand=True)

    frame_buttons = ttk.Frame(frame_content)
    frame_buttons.pack(side="right", padx=5, pady=5, fill="both")
    
    ttk.Button(frame_buttons, text="Done/Undone", command=lambda: self.task_status_change()).pack(side="top")

    ttk.Separator(frame_buttons, orient="horizontal").pack(side="top", fill="x", pady=10)

    ttk.Button(frame_buttons, text="New", command=lambda: self.create_task()).pack(side="top")
    ttk.Button(frame_buttons, text="Edit", command=lambda: self.edit_task()).pack(side="top", pady=5)
    ttk.Button(frame_buttons, text="Delete", command=lambda: self.delete_task()).pack(side="top")

    ttk.Separator(frame_buttons, orient="horizontal").pack(side="top", fill="x", pady=10)

    ttk.Button(frame_buttons, text="Move up", command=lambda: self.move_task(-1)).pack(side="top")
    ttk.Button(frame_buttons, text="Move down", command=lambda: self.move_task(1)).pack(side="top", pady=5)

  def create_task(self):
    self.changes = True
    name_new_task = askstring("New task", "What will be your new task?")

    if name_new_task == "":
      messagebox.showerror("Error new task", "The name of a task cannot be empty.")
      self.root.tkraise()
      return
    
    self.capped_ID += 1
    self.tasks[self.capped_ID] = {"status": False, "name": name_new_task}
    self.list_tasks_todo.insert(self.list_tasks_todo.size()-1, f"{self.capped_ID}: {name_new_task}")

  def load_tasks(self):
    data = ast.literal_eval(str(self.data_item[-1]))
    id_tasks_completed = []
    id_tasks_todo = []

    for ID, task in data.items():
      if task["status"]:
        id_tasks_completed.append(ID)
      else:
        id_tasks_todo.append(ID)

    for id_task in id_tasks_todo:
      self.list_tasks_todo.insert(tk.END, f"{id_task}: {data[id_task]['name']}")
      self.tasks[int(id_task)] = data[id_task]

    self.list_tasks_todo.insert(tk.END, "----------")

    for id_task in id_tasks_completed:
      self.list_tasks_todo.insert(tk.END, f"{id_task}: {data[id_task]['name']}")
      self.list_tasks_todo.itemconfig(tk.END, {"fg": "green"})
      self.tasks[int(id_task)] = data[id_task]

  def task_status_change(self):
    try:
      if len(self.list_tasks_todo.curselection()) != 0:
        self.changes = True
        item = self.list_tasks_todo.curselection()[0]
        ID, name = self.list_tasks_todo.get(item).split(": ")
        ID = int(ID)

        self.tasks[ID]["status"] = not bool(self.tasks[ID]["status"])

        self.list_tasks_todo.delete(item)

        if self.tasks[ID]["status"]:
          self.list_tasks_todo.insert(tk.END, f"{ID}: {name}")
          self.list_tasks_todo.itemconfig(self.list_tasks_todo.size()-1, {"fg": "green"})
        else:
          self.list_tasks_todo.insert(0, f"{ID}: {name}")
          self.list_tasks_todo.itemconfig(0, {"fg": "black"})
    except ValueError:
      pass

  def delete_task(self):
    try:
      if len(self.list_tasks_todo.curselection()) != 0:
        self.changes = True
        item = self.list_tasks_todo.curselection()[0]
        ID, name = self.list_tasks_todo.get(item).split(": ")

        self.tasks.pop(int(ID))
        self.list_tasks_todo.delete(item)
        messagebox.showinfo("Task deleted", "The task has deleted successfully.")
    except ValueError:
      pass

  def edit_task(self):
    try:
      if len(self.list_tasks_todo.curselection()) != 0:
        self.changes = True
        item = self.list_tasks_todo.curselection()[0]
        ID, name = self.list_tasks_todo.get(item).split(": ")

        new_name = askstring("Edit task", "Change name of the task:", initialvalue=name)
        self.tasks[int(ID)]["name"] = new_name
        
        self.list_tasks_todo.delete(item)
        self.list_tasks_todo.insert(item, f"{ID}: {new_name}")
        self.list_tasks_todo.itemconfig(item, {"fg": "green" if self.tasks[int(ID)]["status"] else "black"})

    except ValueError:
      pass

  def move_task(self, direction):
    try:
      if len(self.list_tasks_todo.curselection()) != 0:
        self.changes = True
        item = self.list_tasks_todo.curselection()[0]
        ID, name = self.list_tasks_todo.get(item).split(": ")

        self.list_tasks_todo.delete(item)
        self.list_tasks_todo.insert(item+direction, f"{ID}: {name}")
        self.list_tasks_todo.itemconfig(item+direction, {"fg": "green" if self.tasks[int(ID)]["status"] else "black"})

        id_keys = list(self.tasks.keys())

        index = id_keys.index(int(ID))
        id_keys.remove(int(ID))
        id_keys.insert(index+direction, int(ID))
        self.tasks = {key: self.tasks[key] for key in id_keys}

    except ValueError:
      pass

  def save_tasks(self):
    if self.changes:
      ID_item = self.data_item[0]
      self.root.root.data[int(ID_item)][-1] = self.tasks
      self.root.root.save_data()

    self.root.destroy()

class OverviewProject(tk.Toplevel):
  def __init__(self, root, action):
    super().__init__()
    self.root = root

    self.action = action

    self.title("Create Project" if self.action == "create" else "Overview project")
    self.minsize(400, 200)
    self.resizable(True, True)
    self.geometry(f"+{self.winfo_pointerx()}+{self.winfo_pointery()}")

    self.project_name_stringvar = tk.StringVar()
    self.project_description_stringvar = tk.StringVar()
    self.project_time_studied_stringvar = tk.StringVar()
    self.project_list_of_links = []
    self.project_status = tk.StringVar(value="Not Started")

    if self.action == "open":
      item = self.root.treeview.selection()[0]
      tags = self.root.treeview.item(item, "tags")
      ID = int(tags[0])

      self.project_status.set(self.root.data[ID][1])
      self.project_name_stringvar.set(self.root.data[ID][2])
      self.project_description_stringvar.set(self.root.data[ID][3])
      self.project_time_studied_stringvar.set(f"{seconds_to_time(int(self.root.data[ID][4]))[0]:02d}:{seconds_to_time(int(self.root.data[ID][4]))[1]:02d}:{seconds_to_time(int(self.root.data[ID][4]))[2]:02d}")

      for link in ast.literal_eval(self.root.data[ID][5]):
        self.project_list_of_links.append(link)

      self.notebook = ttk.Notebook(self)
      self.notebook.pack(expand=True, fill="both")

      frame_content = ttk.Frame(self.notebook)
      frame_content.pack(fill="both", expand=True)
      frame_tasks = ttk.Frame(self.notebook)
      frame_tasks.pack(fill="both", expand=True)

      self.notebook.add(frame_content, text="Overview")
      self.notebook.add(frame_tasks, text="Tasks")

      self.draw(frame_content)
      Tasks(self, self.root.data[ID], frame_tasks)
    else:
      frame_content = ttk.Frame(self)
      frame_content.pack(side="top", expand=True, fill="both", padx=10, pady=10)

      self.draw(frame_content)

  def draw(self, frame_content):
    WIDTH_LABELS_LEFT = 20

    frame_project_name = ttk.Frame(frame_content)
    frame_project_name.pack(side="top", fill="x", pady=(10,0))
    ttk.Label(frame_project_name, text="Project name:", width=WIDTH_LABELS_LEFT).pack(side="left")
    if self.action == "create":
      ttk.Entry(frame_project_name, textvariable=self.project_name_stringvar).pack(side="left", fill="x", expand=True)
    else:
      ttk.Label(frame_project_name, text=self.project_name_stringvar.get()).pack(side="left")

    ttk.Separator(frame_content, orient="horizontal").pack(fill="x", pady=10)

    frame_project_description = ttk.Frame(frame_content)
    frame_project_description.pack(side="top", fill="x")
    ttk.Label(frame_project_description, text="Description:", width=WIDTH_LABELS_LEFT).pack(side="left")
    if self.action == "create":
      ttk.Entry(frame_project_description, textvariable=self.project_description_stringvar).pack(side="left", fill="x", expand=True)
    else:
      ttk.Label(frame_project_description, text=self.project_description_stringvar.get(), wraplength=200).pack(side="left")

    if self.action != "create":
      frame_project_time_studied = ttk.Frame(frame_content)
      frame_project_time_studied.pack(side="top", fill="x", pady=(5,0))
      ttk.Label(frame_project_time_studied, text="Time spent:", width=WIDTH_LABELS_LEFT).pack(side="left")
      ttk.Label(frame_project_time_studied, text=self.project_time_studied_stringvar.get(), wraplength=200).pack(side="left")

    frame_project_link = ttk.Frame(frame_content)
    frame_project_link.pack(side="top", fill="x", ipady=10)
    ttk.Label(frame_project_link, text="Links:", width=WIDTH_LABELS_LEFT).pack(side="left", anchor="w")

    frame_list = ttk.Frame(frame_project_link)
    frame_list.pack(side="left", expand=True, fill="both")
    self.list_links = tk.Listbox(frame_list, height=5)
    self.list_links.pack(side="top", fill="x", expand=True)
    self.list_links.bind("<Double-1>", lambda x: self.open_link_in_browser(x))

    if self.action == "open":
      ttk.Label(frame_list, text="Double click to open a link..").pack(side="top", anchor="nw")

      for link in self.project_list_of_links:
        self.list_links.insert(tk.END, link)

    frame_buttons_list_links = ttk.Frame(frame_project_link)
    frame_buttons_list_links.pack(side="left", padx=5, pady=10, fill="y")
    ttk.Button(frame_buttons_list_links, text="New", command=lambda: self.open_insert_link(), state="normal" if self.action == "create" else "disabled").pack(side="top", anchor="n")
    ttk.Button(frame_buttons_list_links, text="Delete", state="normal" if self.action == "create" else "disabled").pack(side="top", anchor="n", pady=5)

    ttk.Separator(frame_content, orient="horizontal").pack(side="top", fill="x", pady=10, anchor="nw")

    frame_status = ttk.Frame(frame_content)
    frame_status.pack(side="top", fill="x")
    ttk.Label(frame_status, text="Status:", width=WIDTH_LABELS_LEFT).pack(side="left")
    ttk.Label(frame_status, text=self.project_status.get()).pack(side="left")

    ttk.Separator(frame_content, orient="horizontal").pack(side="top", fill="x", pady=10, anchor="nw")

    frame_buttons = ttk.Frame(frame_content)
    frame_buttons.pack(side="top", fill="x")
    if self.action == "open":
      ttk.Button(frame_buttons, text="Close", command=lambda: self.destroy()).pack(side="right", anchor="n")
    else:
      ttk.Button(frame_buttons, text="Create", command=lambda: self.create()).pack(side="right", anchor="n")
      ttk.Button(frame_buttons, text="Cancel", command=lambda: self.destroy()).pack(side="left", anchor="n")

  def create(self):
    ID = self.root.ID_TO_CONTINUE+1
    status = self.project_status.get()
    name = self.project_name_stringvar.get()
    description = self.project_description_stringvar.get()
    time = 0
    links = str(self.project_list_of_links)
    tasks = "{}"

    if name == "":
      messagebox.showerror("Missing values", "A name for the project must exists.")

    else:
      rows_to_write = []
      with open(PROJECTS_CSV, "r") as readf:
        reader = csv.DictReader(readf)

        rows_to_write.append({"ID": ID, "Status": status, "Name": name, "Description": description, "Time": 0, "Link": links, "Tasks": tasks})
        for row in reader:
          rows_to_write.append(row)

      with open(PROJECTS_CSV, "w", newline="") as writef:
        writer = csv.DictWriter(writef, fieldnames=rows_to_write[0].keys())
        writer.writeheader()
        writer.writerows(rows_to_write)

      self.root.treeview.insert("", 0, values=[ID,status,name,description], tags=(ID, status))

      self.root.data[int(ID)] = [ID,status,name,description,time,links,tasks]
      self.root.ID_TO_CONTINUE += 1

      messagebox.showinfo("New project created", "The new project has been created successfully.")
      self.root.save_data()
      self.destroy()

  def open_insert_link(self):
    new_link = askstring("Insert link", "Insert a link useful for your project!")
    self.list_links.insert(tk.END, new_link)
    self.project_list_of_links.append(new_link)

  def open_link_in_browser(self, event):
    item = self.list_links.selection_get()
    webbrowser.open_new(item)

class Projects(ttk.Frame):
  def __init__(self, root, controller):
    super().__init__(root)
    self.controller = controller
    self.pack(side="top", anchor="n", expand=True, fill="both")
    self.pack_propagate(False)
    self.configure(width=(self.winfo_width()/2)+100)

    self.ID_TO_CONTINUE = 0

    self.headers = None
    self.data = {}
    self.load_data()

  def load_data(self):
    with open(PROJECTS_CSV, "r") as readf:
      reader = csv.DictReader(readf)
      self.headers = reader.fieldnames

      for row in reader:
        current_row_data = []

        for key, value in row.items():
          if key == "ID":
            if int(value) > self.ID_TO_CONTINUE: 
              self.ID_TO_CONTINUE = int(value)

          if key != ["Links", "Tasks"]:
            current_row_data.append(value)

        self.data[self.ID_TO_CONTINUE] = current_row_data

  def draw(self):
    title_frame = ttk.Frame(self)
    title_frame.pack(fill="x", pady=20)

    ttk.Label(title_frame, text="Projects Management", font=(StyleManager.get_current_font(), 15, "bold")).pack(side="left")
    ttk.Button(title_frame, text="New", command=lambda: self.new_project()).pack(side="right")
    button_help = ttk.Button(title_frame, text="?", width=5)
    button_help.pack(side="right", padx=5)
    ToolTip(button_help, msg="Double left-click a row to mark the project as 'done'")

    self.treeview = ttk.Treeview(
      self,
      columns=self.headers[0:4],
      show="headings",
      selectmode='browse',
    )

    for heading in self.headers[0:4]:

      self.treeview.heading(heading, text=heading)

      if heading.lower() == "status":
        self.treeview.column(heading, width=100)
      elif heading.lower() == "id":
        self.treeview.column(heading, width=5)
      else:
        self.treeview.column(heading, width=140)

    for key in self.data.keys():
      self.treeview.insert("", tk.END, values=self.data[key], tags=[self.data[key][0], self.data[key][1]])

    self.collapse_menu = tk.Menu(self, tearoff=0)
    self.collapse_menu.add_command(label="Open", command=lambda: OverviewProject(self, "open"))
    self.collapse_menu.add_command(label="Delete", command=lambda: self.delete_project())

    self.treeview.bind("<Double-1>", lambda x: self.mark_project_as_done(x))
    self.treeview.bind("<Button-3>", lambda x: self.pop_collapse_menu(x))
    self.treeview.tag_configure('Done', foreground='gray', font=("TkDefaultFont", 8, 'italic'))
    self.treeview.pack(side="top", fill="both", expand=True)

  def mark_project_as_done(self, event):
    item = self.treeview.selection()[0]
    values = list(self.treeview.item(item, "values"))
    tags = self.treeview.item(item, "tags")

    if self.treeview.tag_has("Done", item) == 0:
      values[0] = "Done"

      self.treeview.move(item, "", tk.END)
      self.treeview.item(item, tags=[tags[0], "Done"], values=values)
    else:
      values[0] = "Not started"

      self.treeview.move(item, "", 0)
      self.treeview.item(item, tags=[tags[0], "Not started"], values=values)

    self.save_data()

  def save_data(self):
    all_values = []
    for child in self.treeview.get_children(""):
      values_current_item = self.treeview.item(child, "values")
      all_values.append(list(values_current_item))

    with open(PROJECTS_CSV, "w", newline="") as writef:
      writer = csv.writer(writef)
      writer.writerow(self.headers)

      writer.writerows(self.data.values())

  def new_project(self):
    OverviewProject(self, "create")

  def pop_collapse_menu(self, event):
    try:
      item = self.treeview.identify_row(event.y)

      if item:
        self.treeview.selection_set(item)
        self.collapse_menu.tk_popup(event.x_root, event.y_root)
    finally:
      self.collapse_menu.grab_release()

  def delete_project(self):
    item = self.treeview.selection()[0]
    title = self.treeview.item(item, "values")[1]
    ID = self.treeview.item(item, "tags")[0]

    if messagebox.askyesno("Delete project", f"Are you sure to delete this project?\n\nTitle project: {title}\n\nThis action will not be reversible."):
      self.treeview.delete(item)
      self.data.pop(int(ID))
      self.save_data()
      messagebox.showinfo("Project deletion", "Project deleted successfully!")