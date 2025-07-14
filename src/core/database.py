import sqlite3
from core.paths import DATABASE_PATH

class Database:
  def __init__(self) -> None:
    self.path_database = DATABASE_PATH

    self.conn = sqlite3.connect(self.path_database, timeout=10)
    self.cursor = self.conn.cursor()

    

    self.create_tables()

  def create_tables(self) -> None:
    self.cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL
)                        
                        """)
    
    # current_week table
    self.cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT,
  time INTEGER,
  description TEXT,
  user_id INTEGER NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id) on DELETE CASCADE
)
                        """)
    
    # weeks_log table
    self.cursor.execute("""
CREATE TABLE IF NOT EXISTS weeks_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  week_start TEXT,
  week_end TEXT,
  time TEXT,
  user_id INTEGER NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id) on DELETE CASCADE
)
                        """)
    
    # projects table
    self.cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  status TEXT,
  name TEXT,
  description TEXT,
  time_spent INTEGER,
  user_id INTEGER NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id) on DELETE CASCADE
)
""")
    
        # weeks_log table
    self.cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  status TEXT,
  project_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  FOREIGN KEY(project_id) REFERENCES projects(id) on DELETE CASCADE,
  FOREIGN KEY(user_id) REFERENCES users(id) on DELETE CASCADE
)
                        """)
    
    self.conn.commit()

  def close(self):
    if self.conn:
      self.conn.close()

if __name__ == "__main__":
  Database()
    