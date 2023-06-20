import os
import pandas as pd
from src.stats import Stats
from src.helpers import ENV
from typing import List, Optional


class BaseCache:
    _cache_folder: str = ENV.CACHE_FOLDER
    cache_name = "_"

    def __init__(self, subreddit: str, cache_name: str) -> None:
        self.subreddit: str = subreddit
        self._base_path: str = f"{self._cache_folder}/{self.subreddit}"
        self.file_path: str = f"{self._base_path}/{self.subreddit}{cache_name}.csv"

        if not os.path.exists(self._cache_folder):
            os.mkdir(self._cache_folder)
        
        if not os.path.exists(self._base_path):
            os.mkdir(self._base_path)

    def get_data(self) -> Optional[pd.DataFrame]:
        if not self.is_cached():
            return None
        Stats.read_attempt(self.cache_name)
        df = pd.read_csv(self.file_path)
        Stats.read_successful(self.cache_name)
        return df

    def is_cached(self) -> bool:
        if not os.path.exists(self.file_path):
            return False

        return self._validate_cache()

    def _validate_cache(self) -> bool:
        Stats.read_attempt(self.cache_name)
        df = pd.read_csv(self.file_path)
        Stats.read_successful(self.cache_name)
        return bool(len(df))

    def _create_new_cache(self, data: List):
        df = pd.DataFrame([vars(x) for x in data])
        Stats.write_attempt(self.cache_name)
        df.to_csv(self.file_path, index=False)
        Stats.write_successful(self.cache_name)
