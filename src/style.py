import tkinter as tk
from tkinter import ttk, font

from paths import USER_CONFIG
import json

THEMES = {
  "Light": {
    "bg": "#ffffff",
    "fg": "#000000",
    "bg_table": "#f5f5f5"
  },
  "Dark": {
    "bg": "#131314",
    "fg": "#ffffff",
    "bg_table": "#1b1b1b"
  },
  "Rose": {
    "bg": "#FF90BB",
    "fg": "#000000",
    "bg_table": "#FFC1DA"
  }
}

class StyleManager:
  def __init__(self, root):
    self.root = root

    self.current_theme = self.get_current_theme()
    self.current_font = self.get_current_font()

    self.style = ttk.Style()
    self.update_theme()

  def update_theme(self):
    bg = THEMES[self.current_theme]["bg"]
    fg = THEMES[self.current_theme]["fg"]
    custom_font = (self.current_font, 10)

    self.root.configure(bg=bg)
    self.style.theme_use("clam")

    # frames
    self.style.configure("TFrame", background=bg, foreground=fg)
    self.style.configure("TLabelframe", background=bg, foreground=fg)
    self.style.configure("TLabelframe.Label", background=bg, foreground=fg)
    
    # items
    self.style.configure("TLabel", background=bg, foreground=fg, font=custom_font)
    self.style.configure("TButton", background="#568af2", foreground="black")
    self.style.configure("Treeview", background=THEMES[self.current_theme]["bg_table"], fieldbackground=THEMES[self.current_theme]["bg_table"], foreground=fg, font=(custom_font, 9))
    self.style.configure("Treeview.Heading", font=(self.current_font, 10, "bold"), padding=(3,8))

  @staticmethod
  def change_theme(new_theme):
    with open(USER_CONFIG, "r") as readf:
      reader = json.load(readf)
      readf.close()

    reader["theme"] = new_theme

    with open(USER_CONFIG, "w") as writef:
      json.dump(reader, writef, indent=2)

  @staticmethod
  def change_font(new_font):
    with open(USER_CONFIG, "r") as readf:
      reader = json.load(readf)
      readf.close()

    reader["font"] = new_font

    with open(USER_CONFIG, "w") as writef:
      json.dump(reader, writef, indent=2)

  @staticmethod
  def get_item_color(item):
    return THEMES[StyleManager.get_current_theme()][item]
  
  @staticmethod
  def get_current_theme():
    with open(USER_CONFIG, "r") as readf:
      reader = json.load(readf)
      readf.close()
    return reader["theme"]
  
  @staticmethod
  def get_current_font():
    with open(USER_CONFIG, "r") as readf:
      reader = json.load(readf)
      readf.close()
    return reader["font"]

  @staticmethod
  def get_all_themes():
    return list(THEMES.keys())
  
  @staticmethod
  def get_all_fonts():
    return tk.font.families()
  