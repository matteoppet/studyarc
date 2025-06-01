import tkinter as tk
from tkinter import ttk, font

from core.paths import USER_CONFIG
import json

THEMES = {
  "Light": {
    "bg": "#ffffff",
    "bg-darker": "#d8d8d8",
    "fg": "#000000",
    "bg_table": "#f5f5f5"
  },
  "Dark": {
    "bg": "#131314",
    "bg-darker": "#0A0A0A",
    "fg": "#ffffff",
    "bg_table": "#1b1b1b"
  },
  "Rose": {
    "bg": "#FF90BB",
    "bg-darker": "#ff7daf",
    "fg": "#000000",
    "bg_table": "#FFC1DA"
  },
  "Retro": {
    "bg": "#bfbfbf",
    "bg-darker": "#aeadad",
    "fg": "#000000",
    "bg_table": "#8b8b8b"
  }
}

class StyleManager:
  def __init__(self, root):
    self.root = root

    self.current_theme = self.get_current_theme()
    self.current_font = self.get_current_font()
    self.current_style = self.get_current_style()

    self.style = ttk.Style()

    self.update_theme()

  def update_theme(self):
    bg = THEMES[self.current_theme]["bg"]
    fg = THEMES[self.current_theme]["fg"]
    custom_font = (self.current_font, 10)

    self.style.theme_use(self.current_style)
    
    if self.style.theme_use() == "clam":      
      self.root.configure(bg=bg)

      self.style.configure("TFrame", background=bg, foreground=fg)
      self.style.configure("TLabelframe", background=bg, foreground=fg)
      self.style.configure("TLabelframe.Label", background=bg, foreground=fg)

      # items
      self.style.configure("Red.TButton", background="red3", foreground="white")
      self.style.configure("Green.TButton", background="green4", foreground="white")
      self.style.configure("TLabel", background=bg, foreground=fg, font=custom_font)
      self.style.configure("TButton", background="#568af2", foreground="white")
      self.style.configure("Treeview", background=THEMES[self.current_theme]["bg_table"], fieldbackground=THEMES[self.current_theme]["bg_table"], foreground=fg, font=(custom_font, 9))
      self.style.configure("Treeview.Heading", font=(self.current_font, 10, "bold"), padding=(3,8))
      self.style.configure("TimerProgress.Horizontal.TProgressbar", background="#568af2", foreground="#568af2")
      self.style.configure("TNotebook", background=bg, foreground=fg, borderwidth=0)
      self.style.configure("TNotebook.Tab", background=bg, foreground=fg)

      self.style.map("TNotebook.Tab", background=[('selected', THEMES[self.current_theme]["bg_table"])])

  @staticmethod
  def change_theme(new_theme):
    with open(USER_CONFIG, "r") as readf:
      reader = json.load(readf)

    reader["theme"] = new_theme

    with open(USER_CONFIG, "w") as writef:
      json.dump(reader, writef, indent=2)

  @staticmethod
  def change_font(new_font):
    with open(USER_CONFIG, "r") as readf:
      reader = json.load(readf)

    reader["font"] = new_font

    with open(USER_CONFIG, "w") as writef:
      json.dump(reader, writef, indent=2)

  @staticmethod
  def get_item_color(item):
    if StyleManager.get_current_style() == "clam":
      return THEMES[StyleManager.get_current_theme()][item]
    else:
      return "black" if item != "bg" else None
  
  @staticmethod
  def get_current_theme():
    with open(USER_CONFIG, "r") as readf:
      reader = json.load(readf)
    return reader.get("theme", "Light")
  
  @staticmethod
  def get_current_font():
    with open(USER_CONFIG, "r") as readf:
      reader = json.load(readf)
    return reader.get("font", "@Microsoft JhengHei")
  
  @staticmethod
  def get_current_style():
    with open(USER_CONFIG, "r") as readf:
      reader = json.load(readf)
    return reader.get("style", "xpnative")

  @staticmethod
  def get_all_themes():
    return list(THEMES.keys())
  
  @staticmethod
  def get_all_fonts():
    return tk.font.families()
  
  @staticmethod
  def get_all_styles():
    return ['winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative']
  
  @staticmethod
  def change_style(new_style):
    with open(USER_CONFIG, "r") as readf:
      reader = json.load(readf)

    reader["style"] = new_style
    reader["theme"] = "Light"

    with open(USER_CONFIG, "w") as writef:
      json.dump(reader, writef, indent=2)