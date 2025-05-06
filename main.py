import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from PIL import Image, ImageTk
import sys
import os

from home import Home
from weeks_log import WeeksLog

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Main(tk.Tk):
  def __init__(self):
    super().__init__()
    self.minsize(1000, 500)
    self.title("Study tracker")

    logo_path = resource_path("assets/logo_transparent_resized.png")
    ico = Image.open(logo_path)
    photo = ImageTk.PhotoImage(ico)
    self.wm_iconphoto(False, photo)

  def run(self):
    for widget in self.winfo_children():
      widget.destroy()

    menubar = tk.Menu(self)
    self.config(menu=menubar)

    more_menu = tk.Menu(menubar, tearoff=0)
    more_menu.add_command(label="Settings", command=lambda: self.open_settings())
    more_menu.add_command(label="Help", command=lambda: self.open_help())

    menubar.add_cascade(label="More", menu=more_menu)

    self.container = tk.Frame(self)
    self.container.pack(fill="both", expand=True)

    tk.Label(self.container, text="Study Tracker", font=("Arial 18 bold")).pack(anchor="center", padx=15, pady=15)

    self.home_frame = Home(self.container, self)
    self.home_frame.draw_table()

    self.weeks_log_frame = WeeksLog(self.container, self)
    self.weeks_log_frame.draw_table()

    self.mainloop()

  def open_settings(self):
    print("settings")

  def open_help(self):
    print("TODO help")

if __name__ == "__main__":
  main = Main()
  main.run()
