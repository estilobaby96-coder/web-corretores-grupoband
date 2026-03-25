import os
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

NEON_URL = os.getenv("NEON_URL", "")

def get_connection():
            return psycopg2.connect(NEON_URL, cursor_factory=psycopg2.extras.RealDictCursor)

class DatabaseSession:
            def __init__(self):
                            self.conn = None
                            self.cur = None

            def __enter__(self):
                            self.conn = get_connection()
                            self.cur = self.conn.cursor()
                            return self.cur

            def __exit__(self, exc_type, exc_val, exc_tb):
                            if exc_type:
                                                self.conn.rollback()
            else:
                    self.conn.commit()
                    self.cur.close()
            self.conn.close()
