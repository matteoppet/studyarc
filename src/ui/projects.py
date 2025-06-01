import tkinter as tk
from tkinter import ttk
import csv
from tkinter import messagebox

from ui.style import StyleManager
from core.paths import PROJECTS_CSV

from tktooltip import ToolTip

class CreateNewProject(tk.Toplevel):
  def __init__(self, root):
    super().__init__()
    self.root = root
    self.title("New project")
    self.minsize(350, 150)
    self.resizable(False, False)
    self.geometry(f"+{self.winfo_pointerx()}+{self.winfo_pointery()}")

    self.project_name_stringvar = tk.StringVar()
    self.project_description_stringvar = tk.StringVar()
    self.project_link_stringvar = tk.StringVar()

    self.draw()

  def draw(self):
    frame_content = ttk.Frame(self)
    frame_content.pack(side="top", expand=True, fill="both", padx=10, pady=10)

    frame_project_name = ttk.Frame(frame_content)
    frame_project_name.pack(side="top", fill="x")
    ttk.Label(frame_project_name, text="Project name:").pack(side="left")
    ttk.Entry(frame_project_name, textvariable=self.project_name_stringvar, width=30).pack(side="right")

    frame_project_description = ttk.Frame(frame_content)
    frame_project_description.pack(side="top", fill="x", pady=5)
    ttk.Label(frame_project_description, text="Brief description:").pack(side="left")
    ttk.Entry(frame_project_description, textvariable=self.project_description_stringvar, width=30).pack(side="right")

    frame_project_link = ttk.Frame(frame_content)
    frame_project_link.pack(side="top", fill="x")
    ttk.Label(frame_project_link, text="Useful link:").pack(side="left")
    ttk.Entry(frame_project_link, textvariable=self.project_link_stringvar, width=30).pack(side="right")

    ttk.Separator(frame_content, orient="horizontal").pack(side="top", fill="x", pady=10)

    frame_buttons = ttk.Frame(frame_content)
    frame_buttons.pack(side="top", fill="x", expand=True)
    ttk.Button(frame_buttons, text="Create", command=lambda: self.create()).pack(side="right")
    ttk.Button(frame_buttons, text="Cancel", command=lambda: self.destroy()).pack(side="left")

  def create(self):
    status = "Not started"
    name = self.project_name_stringvar.get()
    description = self.project_description_stringvar.get()
    link = self.project_link_stringvar.get()

    if name == "":
      messagebox.showerror("Missing values", "A name for the project must exists.")

    else:
      rows_to_write = []
      with open(PROJECTS_CSV, "r") as readf:
        reader = csv.DictReader(readf)

        rows_to_write.append({"Status": status, "Name": name, "Description": description, "Useful link": link})
        for row in reader:
          rows_to_write.append(row)

      with open(PROJECTS_CSV, "w", newline="") as writef:
        writer = csv.DictWriter(writef, fieldnames=rows_to_write[0].keys())
        writer.writeheader()
        writer.writerows(rows_to_write)

      self.root.treeview.insert("", 0, values=[status,name,description,link])

      messagebox.showinfo("New project created", "The new project has been created successfully.")

class Projects(ttk.Frame):
  def __init__(self, root, controller):
    super().__init__(root)
    self.controller = controller
    self.pack(side="top", anchor="n", expand=True, fill="both")
    self.pack_propagate(False)
    self.configure(width=(self.winfo_width()/2)+100)

  def draw(self):
    title_frame = ttk.Frame(self)
    title_frame.pack(fill="x", pady=20)

    ttk.Label(title_frame, text="Projects Management", font=(StyleManager.get_current_font(), 15, "bold")).pack(side="left")
    ttk.Button(title_frame, text="New", command=lambda: self.new_project()).pack(side="right")
    button_help = ttk.Button(title_frame, text="?", width=5)
    button_help.pack(side="right", padx=5)
    ToolTip(button_help, msg="Double left-click a row to mark the project as 'done'")

    self.headers_name = ["Status", "Name", "Description", "Useful link"]
    self.treeview = ttk.Treeview(
      self,
      columns=self.headers_name,
      show="headings",
      selectmode='browse',
    )

    for heading in self.headers_name:
      self.treeview.heading(heading, text=heading)

      if heading.lower() == "status":
        self.treeview.column(heading, width=100)
      else:
        self.treeview.column(heading, width=140)

    with open(PROJECTS_CSV, "r") as readf:
      reader = csv.DictReader(readf)

      for row in reader:
        self.treeview.insert("", tk.END, values=list(row.values()), tags=row["Status"])

    self.treeview.bind("<Double-1>", lambda x: self.mark_project_as_done(x))
    self.treeview.tag_configure('Done', foreground='gray', font=("TkDefaultFont", 8, 'italic'))
    self.treeview.pack(side="top", fill="both", expand=True)

  def mark_project_as_done(self, event):
    item = self.treeview.selection()[0]
    values = list(self.treeview.item(item, "values"))

    if self.treeview.tag_has("Done", item) == 0:
      values[0] = "Done"

      self.treeview.move(item, "", tk.END)
      self.treeview.item(item, tags="Done", values=values)
    else:
      values[0] = "Not started"

      self.treeview.move(item, "", 0)
      self.treeview.item(item, tags="Not started", values=values)

    self.save_data()

  def save_data(self):
    all_values = []
    for child in self.treeview.get_children(""):
      values_current_item = self.treeview.item(child, "values")
      all_values.append(list(values_current_item))

    with open(PROJECTS_CSV, "w", newline="") as writef:
      writer = csv.writer(writef)
      writer.writerow(["Status","Name","Description","Useful link"])

      writer.writerows(all_values)

  def new_project(self):
    CreateNewProject(self)