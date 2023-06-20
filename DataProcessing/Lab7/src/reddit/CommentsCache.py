import os
import pandas as pd
from typing import List
from src.types.Comment import Comment
from src.reddit.base_cache import BaseCache
from src.types.ClassifiedComment import ClassifiedComment


class CommentsCache(BaseCache):
    cache_name = "_comments"

    def __init__(self, subreddit: str) -> None:
        super().__init__(subreddit, self.cache_name)

    @property
    def size(self) -> int:
        return len(pd.read_csv(self.file_path))

    def add_comments(self, comments: List[Comment]):
        clasified_comments = [
            ClassifiedComment(comment, self.subreddit) for comment in comments
        ]
        if not os.path.exists(self.file_path):
            self._create_new_cache(clasified_comments)
            return

        new_df = pd.DataFrame([vars(comment) for comment in clasified_comments])
        df = pd.read_csv(self.file_path)

        df_combined = df.append(new_df, ignore_index=True)

        df_combined.to_csv(self.file_path, index=False)
