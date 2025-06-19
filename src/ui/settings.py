import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tktooltip import ToolTip

from core.paths import USER_CONFIG, ICON_PATH
from ui.style import StyleManager

import webbrowser
import json
import shutil
import os

class Settings(tk.Toplevel):
  class NewSubjectWindow(tk.Toplevel):
    def __init__(self, root):
      super().__init__()
      self.root = root
      self.title("Create")
      self.resizable(False, False)
      self.geometry(f"+{self.winfo_pointerx()}+{self.winfo_pointery()}")

      try: self.iconbitmap(ICON_PATH)
      except tk.TclError: self.iconbitmap("../assets/logo.ico")

      self.new_subject_stringvar = tk.StringVar()
      
      self.draw()

    def draw(self):
      main_container = ttk.Frame(self)
      main_container.pack(fill="both", expand=True)

      ttk.Label(main_container, text="Enter new subject name:").pack(side="top", pady=10, padx=30)

      entry_new_subject = ttk.Entry(main_container, textvariable=self.new_subject_stringvar, width=30)
      entry_new_subject.pack(side="top")

      button_create = ttk.Button(main_container, text="Create", command=lambda: self.create_new_subject())
      button_create.pack(side="top", pady=15)

    def create_new_subject(self): 
      new_subject = self.new_subject_stringvar.get()

      if new_subject != "":
        self.root.list_subjects_available.append(new_subject)
        self.root.subjects_available_stringvar.set(self.root.list_subjects_available)
        self.root.listbox_subjects.configure(height=len(self.root.list_subjects_available))

        with open(USER_CONFIG, "r") as readf:
          data = json.load(readf)
          readf.close()

        data["subjects"] = self.root.list_subjects_available

        with open(USER_CONFIG, "w") as writef:
          writef.write(json.dumps(data, indent=2))

        self.destroy()
      else:
        messagebox.showerror("Empty text field", "Impossible to create a new empty subject.")

  def __init__(self, root):
    super().__init__()
    self.root = root
    self.title("Settings")
    self.protocol("WM_DELETE_WINDOW", lambda: self.close())

    mouse_x = self.winfo_pointerx()
    mouse_y = self.winfo_pointery()
    self.geometry(f"600x600+{mouse_x}+{mouse_y}")
    self.minsize(600, 600)

    try: self.iconbitmap(ICON_PATH)
    except tk.TclError: self.iconbitmap("../assets/logo.ico")

    self.languages_available = ["English"]
    self.start_week_available = ["Monday", "Sunday"]

    self.sidepanel_frame = None
    self.main_container = ttk.Frame(self)
    self.main_container.pack(fill="both", expand=True)

    self.current_theme_stringvar = tk.StringVar()
    self.current_theme_stringvar.set(StyleManager.get_current_theme())
    self.current_font_stringvar = tk.StringVar()
    self.current_font_stringvar.set(StyleManager.get_current_font())
    self.subjects_available_stringvar = tk.StringVar()
    self.current_style_stringvar = tk.StringVar()
    self.current_style_stringvar.set(StyleManager.get_current_style())

    with open(USER_CONFIG, "r") as readf:
      data = json.load(readf)
      readf.close()
    self.list_subjects_available = data["subjects"]
    self.subjects_available_stringvar.set(self.list_subjects_available)

    self.draw()

  def draw(self):
    frame_sidepanel_title = ttk.Frame(self.main_container)
    frame_sidepanel_title.pack(side="left", anchor="nw")
    ttk.Label(frame_sidepanel_title, text="Settings", font=(StyleManager.get_current_font(), 16, "bold")).pack(side="top", pady=15, padx=15)
    ttk.Separator(frame_sidepanel_title, orient="horizontal").pack(fill="x")
    ttk.Button(frame_sidepanel_title, text="Settings", command=lambda: self.run_settings_frame()).pack(side="top", anchor="nw", pady=15, fill="x")
    ttk.Button(frame_sidepanel_title, text="Little help", command=lambda: self.run_donation_frame()).pack(side="top", anchor="nw", fill="x")

    self.frame_content = ttk.Frame(self.main_container)
    self.frame_content.pack(side="right", anchor="nw", expand=True, fill="both")

    self.run_settings_frame()

  def clear_content_frame(self):
    for widget in self.frame_content.winfo_children():
      widget.destroy()

  def run_settings_frame(self):
    def change_theme(new_theme):
      StyleManager.change_theme(new_theme)
      StyleManager(self.root)

      self.clear_content_frame()
      self.run_settings_frame()

    def change_font(new_font):
      StyleManager.change_font(new_font)
      StyleManager(self.root)

    def change_style(new_style):
      StyleManager.change_style(new_style)
      StyleManager(self.root)

    self.clear_content_frame()

    ttk.Label(self.frame_content, text="Settings", font=(StyleManager.get_current_font(), 16)).pack(padx=15, pady=15, anchor="nw")
    ttk.Separator(self.frame_content, orient="horizontal").pack(fill="x")

    frame_for_canvas_and_scrollbar = ttk.Frame(self.frame_content)
    frame_for_canvas_and_scrollbar.pack(side="top", fill="both", expand=True)

    canvas = tk.Canvas(frame_for_canvas_and_scrollbar, bg=StyleManager.get_item_color("bg"))
    scrollbar = ttk.Scrollbar(frame_for_canvas_and_scrollbar, orient="vertical", command=canvas.yview)

    frame_current_page = ttk.Frame(canvas)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.create_window((0, 0), window=frame_current_page, anchor="n")
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * int(e.delta / 120), "units"))
    frame_current_page.bind(
      "<Configure>",
      lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
      )
    )

    center_wrapper = ttk.Frame(frame_current_page)
    center_wrapper.pack(anchor="n", padx=20)

    ############### APPEARANCE SECTION
    appearance_frame_content = ttk.Frame(center_wrapper)
    appearance_frame_content.pack(side="top", fill="x")
    ttk.Label(appearance_frame_content, text="Appearance", font=(StyleManager.get_current_font(), 14, "bold")).pack(side="top", anchor="nw")
    ttk.Separator(appearance_frame_content, orient="horizontal").pack(side="top", fill="x", pady=10)

    frame_styles = ttk.Frame(appearance_frame_content)
    frame_styles.pack(side="top", fill="x", pady=5)
    ttk.Label(frame_styles, text="Styles", anchor="w", width=26).pack(side="left")
    styles_menu = ttk.Combobox(frame_styles, textvariable=self.current_style_stringvar, values=StyleManager.get_all_styles(), width=20)
    styles_menu.pack(side="right")
    styles_menu.bind('<<ComboboxSelected>>', lambda event: change_style(self.current_style_stringvar.get()))
    button_tooltip = ttk.Button(frame_styles, text="?", width=2)
    button_tooltip.pack(side="right", padx=5)
    ToolTip(button_tooltip, msg="Only 'clam' style supports custom theme.\nIf you change it you will not be able to change the theme.")

    frame_themes = ttk.Frame(appearance_frame_content)
    frame_themes.pack(side="top", fill="x")
    ttk.Label(frame_themes, text="Themes", anchor="w", width=26).pack(side="left")
    themes_menu = ttk.Combobox(frame_themes, textvariable=self.current_theme_stringvar, values=StyleManager.get_all_themes(), width=20, state="disabled")
    themes_menu.pack(side="right")
    themes_menu.bind('<<ComboboxSelected>>', lambda event: change_theme(self.current_theme_stringvar.get()))

    frame_fonts = ttk.Frame(appearance_frame_content)
    frame_fonts.pack(side="top", pady=5, fill="x")
    ttk.Label(frame_fonts, text="Fonts", anchor="w", width=26).pack(side="left")
    fonts_menu = ttk.Combobox(frame_fonts, textvariable=self.current_font_stringvar, values=StyleManager.get_all_fonts(), width=20, state="disabled")
    fonts_menu.pack(side="right")
    fonts_menu.bind('<<ComboboxSelected>>', lambda event: change_font(self.current_font_stringvar.get()))

    ############### STUDY SETUP SECTION
    study_setup_content = ttk.Frame(center_wrapper)
    study_setup_content.pack(side="top", pady=20, fill="x")
    ttk.Label(study_setup_content, text="Study Setup", font=(StyleManager.get_current_font(), 14, "bold")).pack(side="top", anchor="nw")
    ttk.Separator(study_setup_content, orient="horizontal").pack(side="top", fill="x", pady=10)

    frame_subjects = ttk.Frame(study_setup_content)
    frame_subjects.pack(side="top", anchor="nw", pady=5, fill="x")
    ttk.Label(frame_subjects, text="Subjects", anchor="w", width=20).pack(side="left", anchor="nw")

    frame_buttons_study_setup = ttk.Frame(frame_subjects)
    frame_buttons_study_setup.pack(side="right", anchor="nw")
    button_add_subject = ttk.Button(frame_buttons_study_setup, text="Add", width=6, command=lambda: self.add_subject())
    button_add_subject.pack(side="top", anchor="nw")
    button_delete_subject = ttk.Button(frame_buttons_study_setup, text="Del", width=6, style="Red.TButton", command=lambda: self.delete_subject())
    button_delete_subject.pack(side="top", pady=2)

    self.listbox_subjects = tk.Listbox(frame_subjects, listvariable=self.subjects_available_stringvar, height=len(self.list_subjects_available))
    self.listbox_subjects.pack(side="right", padx=6, anchor="n")

    frame_daily_goal = ttk.Frame(study_setup_content)
    frame_daily_goal.pack(side="top", pady=5, fill="x")
    ttk.Label(frame_daily_goal, text="Daily goal", width=15).pack(side="left")

    self.hours_inserted_stringvar = tk.StringVar()
    self.minutes_inserted_stringvar = tk.StringVar()

    with open(USER_CONFIG, "r") as readf:
      data = json.load(readf)

      self.hours_inserted_stringvar.set(data["session_goal"][0])
      self.minutes_inserted_stringvar.set(data["session_goal"][1]) 

      readf.close()

    ttk.Button(frame_daily_goal, text="Apply", width=6, command=lambda: self.change_session_goal_time()).pack(side="right", anchor="nw")

    ttk.Label(frame_daily_goal, text="minutes").pack(side="right", padx=5)
    ttk.Entry(frame_daily_goal, textvariable=self.minutes_inserted_stringvar, width=4).pack(side="right")

    ttk.Label(frame_daily_goal, text="hours").pack(side="right", padx=5)
    ttk.Entry(frame_daily_goal, textvariable=self.hours_inserted_stringvar, width=4).pack(side="right")

    # frame_current_page.pack(side="top", anchor="center")
    canvas.pack(side="left", expand=True, fill="both")
    scrollbar.pack(side="right", fill="y")

    self.mainloop()

  def change_session_goal_time(self):
    new_hours = self.hours_inserted_stringvar.get()
    new_minutes = self.minutes_inserted_stringvar.get()

    try:
      new_hours = abs(int(new_hours))
      new_minutes = abs(int(new_minutes))

      with open(USER_CONFIG, "r") as readf:
        data = json.load(readf)
        readf.close()

      data["session_goal"] = [new_hours, new_minutes]

      with open(USER_CONFIG, "w") as writef:
        writef.write(json.dumps(data, indent=2))
        writef.close()

    except ValueError:
      messagebox.showerror("Value error", "The values must be numeric to be valid.")

  def add_subject(self):
    self.NewSubjectWindow(self)

  def delete_subject(self):
    item_selected = self.listbox_subjects.curselection()[0]
    self.listbox_subjects.delete(item_selected)
    self.list_subjects_available.remove(self.list_subjects_available[item_selected])

    # update json
    with open(USER_CONFIG, "r") as readf:
      data = json.load(readf)
      readf.close()

    data["subjects"] = self.list_subjects_available

    with open(USER_CONFIG, "w") as writef:
      writef.write(json.dumps(data, indent=2))

  def run_donation_frame(self):
    self.clear_content_frame()

    frame_title = ttk.Frame(self.frame_content)
    frame_title.pack(padx=15, pady=15, anchor="nw")
    ttk.Label(frame_title, text="Little help from you!", font=(StyleManager.get_current_font(), 16)).pack(anchor="nw")

    ttk.Separator(self.frame_content, orient="horizontal").pack(fill="x")

    frame_texts = ttk.Frame(self.frame_content)
    frame_texts.pack(padx=15, pady=15, anchor="nw")

    ttk.Label(frame_texts, text="💛 Made with love (and a lot of late-night coding)!", font=("Arial 10 bold")).pack(anchor="nw")
    ttk.Label(frame_texts, text=f"If this little tracker helps make your days easier, i'd be thrilled if you sent a coffe my way\nNo pressure -- One coffe = one happy coder☕", justify="left").pack(anchor="nw")
    link = ttk.Label(frame_texts, text="👉 buymeacoffee.com/matteopet", cursor="hand2")
    link.pack(anchor="nw")
    link.bind("<Button-1>", lambda e: webbrowser.open_new("https://buymeacoffee.com/matteopet"))

    ttk.Label(frame_texts, text="Thank you!").pack(anchor="center", pady=15)

  def close(self):
    self.destroy()
    self.root.deiconify()
    self.root.run()