import os
from dotenv import load_dotenv
from pathlib import Path


class EnvSingleton:
    def __init__(self) -> None:
        self.set_python_path()
        self.CLIENT_ID = self.get("CLIENT_ID")
        self.CLIENT_SECRET = self.get("CLIENT_SECRET")
        self.REDDIT_USERNAME = self.get("REDDIT_USERNAME")
        self.PASSWORD = self.get("PASSWORD")
        self.CACHE_FOLDER = self.get("CACHE_FOLDER")
        self.SUBMISSION_LIMIT = int(self.get("SUBMISSION_LIMIT"))

    def set_python_path(self):
        self.load_env()
        pythonpath = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        os.environ["PYTHONPATH"] = pythonpath

    def load_env(self):
        env_path = Path(".") / ".env"
        load_dotenv(dotenv_path=env_path)

    def get(self, var: str):
        value = os.getenv(var)
        if value is None:
            raise f"{var} not set in .env"
        return value


ENV = EnvSingleton()
