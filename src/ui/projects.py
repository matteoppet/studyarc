import tkinter as tk
from tkinter import ttk

from ui.style import StyleManager

class CreateNewProject(tk.Toplevel):
  def __init__(self, root):
    super().__init__()
    self.root = root
    self.title("New project")
    self.draw()

  def draw(self):
    ...


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

    self.treeview.pack(side="top", fill="both", expand=True)

  def new_project(self):
    CreateNewProject(self)