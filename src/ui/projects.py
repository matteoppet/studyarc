import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from utils.utils import seconds_to_time

# insert time and tasks and title

class OverviewProject(ttk.Frame):
  def __init__(self, root, project_id = None, user_id = None, cursor = None, conn = None):
    super().__init__(root)
    self.root = root
    self.pack(side="right", fill="both", expand=True)
    self.bind("<Configure>", lambda x: self.draw())
    self.project_id = project_id
    self.user_id = user_id
    self.cursor = cursor
    self.conn = conn

    self.edit_mode = False
    self.title_stringvar = tk.StringVar()
    self.status_stringvar = tk.StringVar()
    self.new_task_stringvar = tk.StringVar()

    self.draw()

  def draw(self):
    try:
      self.clear_widgets()

      if self.project_id == None:
        ttk.Label(self, text="No project selected", anchor="center").pack(fill="both", anchor="center", expand=True)
      else:
        self.cursor.execute("SELECT name, description, time_spent, status FROM projects WHERE id = ? AND user_id = ?", (self.project_id, self.user_id,))
        name, description, time_spent, status = self.cursor.fetchone()
        self.title_stringvar.set(name)
        self.status_stringvar.set(status)

        frame_title = ttk.Frame(self)
        frame_title.pack(fill="x", side="top", padx=10, pady=10)
        if self.edit_mode:
          ttk.Entry(frame_title, textvariable=self.title_stringvar).pack(side="left", fill="x", expand=True, padx=(0,15))
        else:
          ttk.Label(frame_title, text=name, font=("TkDefaultFont", 15, "bold")).pack(side="left")

        if self.edit_mode:
          ttk.Button(frame_title, text="Save", command=lambda: self.save_edit()).pack(side="right")
        else:
          ttk.Button(frame_title, text="Edit Project", command=lambda: self.switch_to_edit_mode()).pack(side="right")
      
        ttk.Separator(self, orient="horizontal").pack(side="top", fill="x")

        frame_content = ttk.Frame(self)
        frame_content.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        ##############à

        frame_time_and_status = ttk.Frame(frame_content)
        frame_time_and_status.pack(side="top", fill="x")
        
        frame_time = ttk.Frame(frame_time_and_status)
        frame_time.pack(side="left", fill="x", expand=True)
        time = seconds_to_time(int(time_spent))
        ttk.Label(frame_time, text=f"Time spent on this project: {time[0]:02d}:{time[1]:02d}:{time[2]:02d}").pack(side="top", fill="x")
        
        ttk.Separator(frame_time_and_status, orient="vertical").pack(fill="y", side="left")

        frame_status = ttk.Frame(frame_time_and_status)
        frame_status.pack(side="right", fill="x", expand=True)
        ttk.Label(frame_status, text="Status:").pack(side="left", padx=(10, 0))
        if self.edit_mode: 
          combobox = ttk.Combobox(frame_status, textvariable=self.status_stringvar)
          combobox.pack(side="left", padx=(5,0))
          combobox["values"] = [
            "Not Started",
            "In Progress",
            "Done"
          ]
        else:
          tk.Label(frame_status, text=status, fg="red" if status == "Not Started" else "orange" if status == "In Progress" else "green").pack(side="left")

        #################

        ttk.Separator(frame_content, orient="horizontal").pack(side="top", fill="x", pady=10)

        if self.edit_mode:
          self.textarea = tk.Text(frame_content)
          self.textarea.pack(side="top", anchor="nw", fill="both")
          self.textarea.insert(tk.END, description if description is not None else "")
        else:
          ttk.Label(frame_content, text=description if description is not None and description != "" else "This project does not have a description.", wraplength=self.winfo_width()-20, justify="left").pack(side="top", anchor="nw")

        ttk.Separator(frame_content, orient="horizontal").pack(side="top", fill="x", pady=10)

        frame_insert_task = ttk.Frame(frame_content)
        frame_insert_task.pack(side="top", fill="x")
        ttk.Entry(frame_insert_task, textvariable=self.new_task_stringvar).pack(side="left", fill="x", expand=True)
        ttk.Button(frame_insert_task, text="Add Task", command=lambda: self.add_task()).pack(side="left", padx=5)
        
        self.cursor.execute("PRAGMA table_info(tasks)")
        headers_name = [row[1] for row in self.cursor.fetchall()][1:3]
        self.treeview = ttk.Treeview(
          frame_content,
          columns=headers_name,
          show="headings"
        )

        for heading in headers_name:
          self.treeview.heading(heading, text=heading.title())

          if heading.lower() == "status":
            self.treeview.column(heading, anchor='center')

        self.cursor.execute("SELECT id, name, status FROM tasks WHERE project_id = ? AND user_id = ?", (self.project_id, self.user_id,))
        for row in self.cursor.fetchall():
          self.treeview.insert("", tk.END, values=row[1:], iid=row[0])

        self.collapse_menu = tk.Menu(self, tearoff=0)
        self.collapse_menu.add_command(label="Delete", command=lambda: self.delete_task())

        menustatus = tk.Menu(self.collapse_menu, tearoff=0)
        menustatus.add_command(label="Not Started", command=lambda: self.change_status("Not Started"))
        menustatus.add_command(label="In Progress", command=lambda: self.change_status("In Progress"))
        menustatus.add_command(label="Done", command=lambda: self.change_status("Done"))

        self.collapse_menu.add_cascade(label="Status", menu=menustatus)
        self.treeview.bind("<Button-3>", self.open_collapse_menu)
        
        self.treeview.pack(side="top", fill="both", expand=True, pady=10)
    except TypeError:
      pass

  def clear_widgets(self):
    for widget in self.winfo_children():
      widget.destroy()

  def add_task(self):
    new_task = self.new_task_stringvar.get()

    if new_task != "":
      self.cursor.execute("INSERT INTO tasks (name, status, project_id, user_id) VALUES (?, ?, ?, ?)", (new_task, "Not Started", self.project_id, self.user_id))
      self.conn.commit()
      new_id = self.cursor.lastrowid
      self.treeview.insert("", 0, values=(new_task, "Not Started"), iid=new_id)
      self.new_task_stringvar.set("")

  def delete_task(self):
    id_task = self.treeview.selection()[0]
    self.cursor.execute("DELETE FROM tasks WHERE id = ? AND project_id = ? AND user_id = ?", (id_task, self.project_id, self.user_id))
    self.conn.commit()
    self.treeview.delete(id_task)

  def change_status(self, new_status):
    id_task = self.treeview.selection()[0]
    name = self.treeview.item(id_task, "values")[0]
    self.cursor.execute("UPDATE tasks SET status = ? WHERE id = ? AND project_id = ? AND user_id = ?", (new_status, id_task, self.project_id, self.user_id))
    self.conn.commit()
    self.treeview.delete(id_task)
    self.treeview.insert("", 0 if new_status == "In Progress" else tk.END, iid=id_task, values=(name, new_status))
  
  def open_collapse_menu(self, event):
    item_id = self.treeview.identify_row(event.y)
    if item_id:
      self.treeview.selection_set(item_id)
      self.collapse_menu.post(event.x_root, event.y_root)

  def save_edit(self):
    new_description = self.textarea.get("1.0", "end-1c")
    new_name = self.title_stringvar.get()
    new_status = self.status_stringvar.get()

    self.cursor.execute("UPDATE projects SET name = ?, description = ?, status = ? WHERE id = ?", (new_name, new_description, new_status, self.project_id))
    self.conn.commit()

    index = "end" if new_status == "Done" else 0
    self.root.treeview.item(self.project_id, text=new_name, tags=(new_status,))
    self.root.treeview.move(self.project_id, "", index)

    self.edit_mode = False
    self.draw()

  def switch_to_edit_mode(self):
    self.edit_mode = True
    self.draw()

class Projects(tk.Toplevel):
  def __init__(self, root, controller, cursor, conn, user_id):
    super().__init__(root)
    self.root = root
    self.controller = controller
    self.cursor = cursor
    self.conn = conn
    self.user_id = user_id
    self.title("Projects")
    self.minsize(500, 400)
    self.transient(self.root)
    self.geometry(f"+{self.winfo_pointerx()}+{self.winfo_pointery()}")

    self.frame_projects = ttk.Frame(self, width=170)
    self.frame_projects.pack(side="left", fill="y")
    self.overview_project = OverviewProject(self, cursor=self.cursor, conn=self.conn)

    self.name_new_project_stringvar = tk.StringVar()
    
    self.draw()
    
  def draw(self):
    frame_create_projects = ttk.Frame(self.frame_projects)
    frame_create_projects.pack(side="top", fill="x", padx=5, pady=5)

    ttk.Entry(frame_create_projects, textvariable=self.name_new_project_stringvar).pack(side="left", fill="x", expand=True, padx=(0,5))
    ttk.Button(frame_create_projects, text="Add project", command=lambda: self.create_project()).pack(side="left", fill="x")

    frame_treeview = ttk.Frame(self.frame_projects)
    frame_treeview.pack(side="top", padx=(5, 10), fill="both", expand=True)

    self.treeview = ttk.Treeview(frame_treeview, show="tree")
    scrollbar = ttk.Scrollbar(frame_treeview, orient="vertical", command=self.treeview.yview)
    self.treeview.configure(yscrollcommand=scrollbar.set)
    
    self.treeview.bind("<<TreeviewSelect>>", self.open_project)

    self.treeview.pack(side="left", fill="both", expand=True, pady=(0, 5))
    # scrollbar.pack(side="right", fill="y")

    self.cursor.execute("SELECT id, name, status FROM projects WHERE user_id = ?", (self.user_id,))
    for row in self.cursor.fetchall():
      self.treeview.insert("", "end" if row[2] == "Done" else 0, text=row[1], iid=row[0], tags=(row[2],))

    self.collapse_menu = tk.Menu(self, tearoff=0)
    self.collapse_menu.add_command(label="Delete", command=lambda: self.delete_project())
    self.treeview.bind("<Button-3>", self.open_collapse_menu)

    self.treeview.tag_configure("Done", foreground="green")
    self.treeview.tag_configure("In Progress", foreground="orange")
    self.treeview.tag_configure("Not Started", foreground="black")

    ttk.Separator(self, orient="vertical").pack(side="left", fill="y")

  def create_project(self):
    name = self.name_new_project_stringvar.get()
    if name != "":
      self.cursor.execute("INSERT INTO projects (name, time_spent, status, user_id) VALUES (?, ?, ?, ?)", (name, 0, "Not Started", self.user_id,))
      self.conn.commit()
      new_id = self.cursor.lastrowid
      self.treeview.insert("", index=0, text=name, iid=new_id, tags=("Not Started",))
      self.name_new_project_stringvar.set("")

      messagebox.showinfo("New project", "New project has been successfully created")

  def open_project(self, event):
    selected_item = self.treeview.focus()
    self.overview_project.project_id = selected_item
    self.overview_project.user_id = self.user_id
    self.overview_project.draw()

  def delete_project(self):
    if messagebox.askyesno("Delete Project", "Are you sure to delete this project?\n\nThis action is irreversible."):
      ID = int(self.treeview.selection()[0])
      self.treeview.delete(ID)
      self.cursor.execute("DELETE FROM projects WHERE id = ?", (ID,))
      self.conn.commit()
      self.overview_project.project_id = None
      self.overview_project.draw()
      messagebox.showinfo("Deleted Project", "The project has been successfully deleted")

  def open_collapse_menu(self, event):
    item_id = self.treeview.identify_row(event.y)
    if item_id:
      self.treeview.selection_set(item_id)
      self.collapse_menu.post(event.x_root, event.y_root)