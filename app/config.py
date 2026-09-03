import os

API_TOKEN = os.getenv("API_TOKEN", "secret-token-123")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leads.db")