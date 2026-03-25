import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
NEON_URL = os.getenv("NEON_URL")

def get_connection():
    return psycopg2.connect(NEON_URL, cursor_factory=psycopg2.extras.RealDictCursor)

class DatabaseSession:
    def __init__(self):
          self.conn = None
          self.cur = None

  def __enter__(self):
        self.conn = get_connection()
        self.cur = self.conn.cursor()
        return self

  def __exit__(self, et, ev, tb):
        if self.cur: self.cur.close()
              if self.conn: self.conn.close()
                
