import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.simpledialog import askstring
from core.paths import ICON_PATH, USER_PATH
from PIL import Image, ImageTk

class Login(tk.Toplevel):
  def __init__(self, root, cursor, conn):
    super().__init__(root)
    self.root = root
    self.title("Login")
    self.minsize(300,390)
    self.geometry(f"+{int(self.winfo_screenmmwidth()/2)}+{int(self.winfo_screenmmheight()/2)}")
    self.transient(self.root)

    try: 
      self.iconbitmap(ICON_PATH)
    except tk.TclError:
      self.iconbitmap("../assets/logo.ico")
    
    self.cursor = cursor
    self.conn = conn

    self.selected_user = tk.StringVar()
    self.user_id = None

    self.run()

  def run(self):
    for widgets in self.winfo_children():
      widgets.destroy()

    frame_content = ttk.Frame(self)
    frame_content.pack(side="top", fill="both", expand=True)

    ttk.Label(frame_content, text="StudyArc", font=("TkDefaultFont", 20, "bold")).pack(side="top", pady=(25, 15))

    image = Image.open(USER_PATH)
    resized_image = image.resize((130, 130))  # specify dimensions
    self.image = ImageTk.PhotoImage(resized_image)  # keep reference
    image_label = ttk.Label(frame_content, image=self.image)
    image_label.pack(side="top", anchor="center", pady=(0,15))

    frame_login = ttk.Frame(frame_content)
    frame_login.pack(side="top", anchor="center")

    ttk.Label(frame_login, text="Select user:").pack(side="top")
    self.cursor.execute("SELECT name FROM users")
    list_users = [row for row in self.cursor.fetchall()]
    if len(list_users) == 0:
      ttk.Label(frame_login, text="No user available").pack(side="top", pady=5)
      ttk.Button(frame_login, text="Enter", command=lambda: self.enter_app(), state="disabled").pack(side="top", fill="x")  
    else:
      combobox = ttk.Combobox(frame_login, textvariable=self.selected_user, values=list_users)
      combobox.pack(side="top", pady=5)
      ttk.Button(frame_login, text="Enter", command=lambda: self.enter_app()).pack(side="top", fill="x")  

    ttk.Separator(frame_login, orient="horizontal").pack(side="top", fill="x", pady=10)
    ttk.Button(frame_login, text="Create user", command=lambda: self.create_new_user()).pack(side="top", fill="x")

  def enter_app(self):
    self.cursor.execute("SELECT id FROM users WHERE name = ?", (self.selected_user.get(),))
    id = self.cursor.fetchone()[0]
    
    self.root.user_id = int(id)
    self.destroy()
    self.root.deiconify()

  def create_new_user(self):
    name_new_user = askstring("New user", "Insert new user-name")

    if name_new_user != "":
      try:
        self.cursor.execute("INSERT INTO users (name) VALUES (?)", (name_new_user,))
        self.conn.commit()
        self.selected_user.set(name_new_user)
        self.run()
        messagebox.showinfo("New user", "New user added successfully.")
      except sqlite3.IntegrityError:
        messagebox.showerror("Create user", "An user with this name already exists.")

    self.run()