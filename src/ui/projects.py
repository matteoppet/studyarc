import tkinter as tk
from tkinter import ttk
import csv
from tkinter import messagebox
from tkinter.simpledialog import askstring
import ast

from ui.style import StyleManager
from core.paths import PROJECTS_CSV

import webbrowser

from tktooltip import ToolTip

class OverviewProject(tk.Toplevel):
  def __init__(self, root, action):
    super().__init__()
    self.root = root

    self.action = action

    self.title("Create Project" if self.action == "create" else "Overview project")
    self.minsize(400, 200)
    self.resizable(True, False)
    self.geometry(f"+{self.winfo_pointerx()}+{self.winfo_pointery()}")

    self.project_name_stringvar = tk.StringVar()
    self.project_description_stringvar = tk.StringVar()
    self.project_list_of_links = []
    self.project_status = tk.StringVar(value="Not Started")

    if self.action == "open":
      item = self.root.treeview.selection()[0]
      values = self.root.treeview.item(item, "values")

      self.project_status.set(values[0])
      self.project_name_stringvar.set(values[1])
      self.project_description_stringvar.set(values[2])

      for link in ast.literal_eval(values[3]):
        self.project_list_of_links.append(link)

    self.draw()

  def draw(self):
    WIDTH_LABELS_LEFT = 20

    frame_content = ttk.Frame(self)
    frame_content.pack(side="top", expand=True, fill="both", padx=10, pady=10)

    frame_project_name = ttk.Frame(frame_content)
    frame_project_name.pack(side="top", fill="x")
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
    frame_buttons.pack(side="top", fill="x", expand=True)
    if self.action == "open":
      ttk.Button(frame_buttons, text="Close", command=lambda: self.destroy()).pack(side="right")
    else:
      ttk.Button(frame_buttons, text="Create", command=lambda: self.create()).pack(side="right")
      ttk.Button(frame_buttons, text="Cancel", command=lambda: self.destroy()).pack(side="left")

  def create(self):
    status = self.project_status.get()
    name = self.project_name_stringvar.get()
    description = self.project_description_stringvar.get()
    links = str(self.project_list_of_links)

    if name == "":
      messagebox.showerror("Missing values", "A name for the project must exists.")

    else:
      rows_to_write = []
      with open(PROJECTS_CSV, "r") as readf:
        reader = csv.DictReader(readf)

        rows_to_write.append({"Status": status, "Name": name, "Description": description, "Useful link": links})
        for row in reader:
          rows_to_write.append(row)

      with open(PROJECTS_CSV, "w", newline="") as writef:
        writer = csv.DictWriter(writef, fieldnames=rows_to_write[0].keys())
        writer.writeheader()
        writer.writerows(rows_to_write)

      self.root.treeview.insert("", 0, values=[status,name,description,links])

      messagebox.showinfo("New project created", "The new project has been created successfully.")

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

    if messagebox.askyesno("Delete project", f"Are you sure to delete this project?\n\nTitle project: {title}\n\nThis action will not be reversible."):
      self.treeview.delete(item)
      self.save_data()
      messagebox.showinfo("Project deletion", "Project deleted successfully!")