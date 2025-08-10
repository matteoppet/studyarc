import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

from utils.utils import format_time, get_time_from_seconds

class ProjectOverview(ctk.CTkToplevel):
  def __init__(self):
    ...

class SectionFrame(ctk.CTkFrame):
  def __init__(
    self, root, cursor, conn, user_id, title):
    ctk.CTkFrame.__init__(self, root)
    self.root = root
    self.cursor = cursor
    self.conn = conn
    self.user_id = user_id,
    self.title = title

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
      self.cursor.execute("SELECT id FROM projects WHERE status = ? AND user_id = ?", ("In Progress", self.user_id))
      in_progress_projects = len(self.cursor.fetchall())

      self.cursor.execute("SELECT id FROM projects WHERE status = ? AND user_id = ?", ("Done", self.user_id))
      done_projects = len(self.cursor.fetchall())
      
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

      self.treeview.insert(
        "",
        tk.END,
        iid=row[0],
        text=row[1],
        values=values,
        tags=tags
      )

    if self.title.lower() == "projects":
      self.treeview.tag_configure("In Progress", foreground="orange")
      self.treeview.tag_configure("Done", foreground="green")

    self.treeview.pack(side="top", fill="both", expand=True)

  def add(self):
    dialog = ctk.CTkInputDialog(title=self.title, text=f"Enter name new {self.title.lower()[0:-1]}")
    text = dialog.get_input()

    if text:
      if self.title == "Projects":
        self.cursor.execute("INSERT INTO projects (name, time, status, user_id) VALUES (?,?,?,?)", (text, 0, "Not Started", self.user_id[0]))
        self.conn.commit()

        new_id = self.cursor.lastrowid

        self.treeview.insert("",
        tk.END,
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


class Projects(ctk.CTkFrame):
  def __init__(self, root, cursor, conn, user_id):
    ctk.CTkFrame.__init__(self, root)
    self.root = root
    self.cursor = cursor
    self.conn = conn
    self.user_id = user_id

    self.pack(side="top", padx=10, pady=10, anchor="nw", fill="both", expand=True)

    self.run()

  def run(self):
    for widgets in self.winfo_children():
      widgets.destroy()

    SectionFrame(
      self, self.cursor, self.conn, self.user_id, "Projects"
    )

    SectionFrame(
      self, self.cursor, self.conn, self.user_id, "Subjects"
    )