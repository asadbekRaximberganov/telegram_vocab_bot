import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "").lstrip("@")
DATABASE_PATH: str = "data/database.db"
BOOKS_DIR: str = "books"
