import sqlite3
from core.__init__ import DATABASE_FILE
import sys

class Database:
  def __init__(self):
    self.name_file_databse = DATABASE_FILE

    self.conn = sqlite3.connect(self.name_file_databse)
    self.cursor = self.conn.cursor()

    self.create_tables()

  def create_tables(self):
    self.cursor.execute("""CREATE TABLE IF NOT EXISTS users 
                        (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        exp INTEGER,
                        level INTEGER
                        )
                        """)
    if not self.columns_exists("users", "exp"):
      self.cursor.execute("ALTER TABLE users ADD COLUMN exp INTEGER")
    if not self.columns_exists("users", "level"):
      self.cursor.execute("ALTER TABLE users ADD COLUMN level INTEGER")

    self.cursor.execute("""CREATE TABLE IF NOT EXISTS sessions 
                        (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        time INTEGER,
                        description TEXT,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id) on DELETE CASCADE
                        )""")
    
    self.cursor.execute("""CREATE TABLE IF NOT EXISTS projects 
                        (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        status TEXT,
                        time INTEGER,
                        description TEXT,
                        folder TEXT,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id) on DELETE CASCADE
                        )""")
    
    self.cursor.execute("""CREATE TABLE IF NOT EXISTS projects_tasks
                        (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        project_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY(project_id) REFERENCES projects(id) on DELETE CASCADE
                        FOREIGN KEY(user_id) REFERENCES users(id) on DELETE CASCADE
                        )""")
    
    self.cursor.execute("""CREATE TABLE IF NOT EXISTS subjects
                        (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        time INTEGER,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id) on DELETE CASCADE
                        )""")

    self.conn.commit()


  def columns_exists(self, table, column):
    self.cursor.execute(f"PRAGMA table_info({table})")
    columns = [info[1] for info in self.cursor.fetchall()]

    return column in columns