import os


os.environ.setdefault("ENV", "test")
os.environ.setdefault("API_HOST", "127.0.0.1")
os.environ.setdefault("API_PORT", "8000")
os.environ.setdefault("TOURAPI_DB_PATH", "unused-test.db")
os.environ.setdefault("CORS_ORIGINS", '["http://testserver"]')
