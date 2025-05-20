import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from home import Home
from weeks_log import WeeksLog
from paths import USER_CONFIG, ICON_PATH
from style import StyleManager

import webbrowser
import json

class Settings(tk.Toplevel):
  class NewSubjectWindow(tk.Toplevel):
    def __init__(self, root):
      super().__init__()
      self.root = root
      self.title("Create")
      self.resizable(False, False)

      mouse_x = self.winfo_pointerx()
      mouse_y = self.winfo_pointery()
      self.geometry(f"+{mouse_x}+{mouse_y}")

      try: self.iconbitmap(ICON_PATH)
      except tk.TclError: self.iconbitmap("../assets/logo_transparent_resized.ico")

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
    self.resizable(False, False)

    mouse_x = self.winfo_pointerx()
    mouse_y = self.winfo_pointery()
    self.geometry(f"600x600+{mouse_x}+{mouse_y}")

    try: self.iconbitmap(ICON_PATH)
    except tk.TclError: self.iconbitmap("../assets/logo_transparent_resized.ico")

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

    def change_font(new_font):
      StyleManager.change_font(new_font)
      StyleManager(self.root)

    self.clear_content_frame()

    ttk.Label(self.frame_content, text="Settings", font=(StyleManager.get_current_font(), 16)).pack(padx=15, pady=15, anchor="nw")
    ttk.Separator(self.frame_content, orient="horizontal").pack(fill="x")

    appearance_frame_content = ttk.Frame(self.frame_content)
    appearance_frame_content.pack(pady=20)
    ttk.Label(appearance_frame_content, text="Appearance", font=(StyleManager.get_current_font(), 14, "bold")).pack(side="top", anchor="nw")
    ttk.Separator(appearance_frame_content, orient="horizontal").pack(side="top", fill="x", pady=10)

    frame_themes = ttk.Frame(appearance_frame_content)
    frame_themes.pack(side="top")
    ttk.Label(frame_themes, text="Themes", anchor="w", width=20).pack(side="left")
    themes_menu = ttk.Combobox(frame_themes, textvariable=self.current_theme_stringvar, values=StyleManager.get_all_themes(), width=20)
    themes_menu.pack(side="right")
    themes_menu.bind('<<ComboboxSelected>>', lambda event: change_theme(self.current_theme_stringvar.get()))

    frame_fonts = ttk.Frame(appearance_frame_content)
    frame_fonts.pack(side="top", pady=4)
    ttk.Label(frame_fonts, text="Fonts", anchor="w", width=20).pack(side="left")
    fonts_menu = ttk.Combobox(frame_fonts, textvariable=self.current_font_stringvar, values=StyleManager.get_all_fonts(), width=20)
    fonts_menu.pack(side="right")
    fonts_menu.bind('<<ComboboxSelected>>', lambda event: change_font(self.current_font_stringvar.get()))

    study_setup_content = ttk.Frame(self.frame_content)
    study_setup_content.pack(pady=20)
    ttk.Label(study_setup_content, text="Study Setup", font=(StyleManager.get_current_font(), 14, "bold")).pack(side="top", anchor="nw")
    ttk.Separator(study_setup_content, orient="horizontal").pack(side="top", fill="x", pady=10)
    ttk.Label(study_setup_content, text="Subjects", anchor="w", width=15).pack(side="left", anchor="nw")

    frame_buttons_study_setup = ttk.Frame(study_setup_content)
    frame_buttons_study_setup.pack(side="right", anchor="nw")
    button_add_subject = ttk.Button(frame_buttons_study_setup, text="Add", width=5, command=lambda: self.add_subject())
    button_add_subject.pack(side="top")
    button_delete_subject = ttk.Button(frame_buttons_study_setup, text="Del", width=5, style="Red.TButton", command=lambda: self.delete_subject())
    button_delete_subject.pack(side="top", pady=2)

    self.listbox_subjects = tk.Listbox(study_setup_content, listvariable=self.subjects_available_stringvar, height=len(self.list_subjects_available))
    self.listbox_subjects.pack(side="right", padx=5, anchor="n")

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

  def run_preferences_frame(self):
    def apply():
      goal_time_list = [abs(int(session_goal_time_string_hours.get())), abs(int(session_goal_time_string_minutes.get()))]

      if goal_time_list[1] > 60:
        messagebox.showerror("Invalid session goal time", "Session goal time minutes must be below or equal to 60")
      else:
        with open(USER_CONFIG) as f:
          data_json = json.load(f)
        
        data_json["session_goal"] = [int(session_goal_time_string_hours.get()), int(session_goal_time_string_minutes.get())]
        json_object = json.dumps(data_json, indent=2)

        with open(USER_CONFIG, "w") as outfile:
          outfile.write(json_object)

    self.run_sidepanel_frame()
    self.clear_content_frame()

    with open(USER_CONFIG, "r") as file:
      settings_data = json.load(file)

    frame_title = ttk.Frame(self.content_frame)
    frame_title.pack(padx=15, pady=15, anchor="nw")
    ttk.Label(frame_title, text="Preferences", font=(StyleManager.get_current_font(), 18, "bold")).pack(anchor="nw")

    ttk.Separator(self.content_frame, orient="horizontal").pack(fill="x")

    ######################################

    frame_texts = ttk.Frame(self.content_frame)
    frame_texts.pack(padx=15, pady=15, anchor="nw", fill="both")

    frame_session_goal_time = ttk.Frame(frame_texts)
    frame_session_goal_time.pack(padx=5, pady=5, anchor="nw", fill="x")
    with open(USER_CONFIG) as f: temp_data = json.load(f)
    session_goal_time_string_hours = tk.StringVar()
    session_goal_time_string_hours.set(temp_data["session_goal"][0])
    session_goal_time_string_minutes = tk.StringVar()
    session_goal_time_string_minutes.set(temp_data["session_goal"][1])
    ttk.Label(frame_session_goal_time, text="Session goal time").pack(side="left")
    # MINUTES
    ttk.Label(frame_session_goal_time, text="Minutes").pack(side="right")
    tk.Entry(frame_session_goal_time, width=3, textvariable=session_goal_time_string_minutes).pack(side="right", padx=2)
    # HOURS
    ttk.Label(frame_session_goal_time, text="Hours").pack(side="right", padx=2)
    tk.Entry(frame_session_goal_time, width=3, textvariable=session_goal_time_string_hours).pack(side="right")

    frame_button_apply = ttk.Frame(self.content_frame)
    frame_button_apply.pack(padx=15, pady=15, side="bottom", fill="both")
    tk.Button(frame_button_apply, text="Apply", width=10, command=lambda: apply()).pack(side="right")

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

class Main(tk.Tk):
  def __init__(self):
    super().__init__()
    self.minsize(1000, 500)
    self.title("Study tracker")

    StyleManager(self)

    try: self.iconbitmap(ICON_PATH)
    except tk.TclError: self.iconbitmap("../assets/logo_transparent_resized.ico")

  def run(self):
    for widget in self.winfo_children():
      widget.destroy()

    menubar = tk.Menu(self)

    more_menu = tk.Menu(menubar, tearoff=0)
    more_menu.add_command(label="Settings", command=lambda: self.open_settings())
    more_menu.add_command(label="Documentation", command=lambda: self.open_help())
    more_menu.add_command(label="About", command=lambda: self.open_help())
    more_menu.add_separator()
    more_menu.add_command(label="Exit", command=lambda: self.destroy())

    menubar.add_cascade(label="Help", menu=more_menu)

    self.config(menu=menubar)

    self.container = ttk.Frame(self)
    self.container.pack(fill="both", expand=True)

    ttk.Label(self.container, text="Study Tracker", font=(StyleManager.get_current_font(), 18, "bold")).pack(anchor="center", padx=15, pady=15)

    self.home_frame = Home(self.container, self)
    self.home_frame.draw_table()

    self.weeks_log_frame = WeeksLog(self.container, self)
    self.weeks_log_frame.draw_table()

    self.mainloop()

  def open_settings(self):
    Settings(self)

  def open_help(self):
    print("TODO help")

if __name__ == "__main__":
  main = Main()
  main.run()
