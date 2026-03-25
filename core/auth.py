import os
import hashlib

SECRET_KEY = os.getenv("SECRET_KEY", "grupo-band-secret-2025")
ALGORITHM = "HS256"


def verify_password(plain: str, hashed: str) -> bool:
          try:
                        import bcrypt
                        if hashed.startswith("$2b$") or hashed.startswith("$2a$"):
                                          return bcrypt.checkpw(plain.encode(), hashed.encode())
          except ImportError:
                        pass
                    return hashlib.sha256(plain.encode()).hexdigest() == hashed
