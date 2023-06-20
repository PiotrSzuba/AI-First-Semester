import os
import pandas as pd
from typing import List, Optional
from src.types.Submission import Submission
from src.reddit.base_cache import BaseCache
from src.reddit.CommentsCache import CommentsCache


class SubmissionCache(BaseCache):
    cache_name = "_submissions"

    def __init__(self, subreddit: str) -> None:
        super().__init__(subreddit, self.cache_name)

    @property
    def comments_count(self) -> int:
        df = pd.read_csv(self.file_path)
        return df['comment_count'].sum()

    def get_data(self) -> Optional[pd.DataFrame]:
        if not self.is_cached():
            return None

        comments_cache = CommentsCache(self.subreddit)

        if not comments_cache.is_cached():
            os.remove(self.file_path)
            return None

        submission_df = pd.read_csv(self.file_path)
        comments_df = pd.read_csv(comments_cache.file_path)

        filtered_df = self._filter_data(submission_df, comments_df)

        filtered_df.to_csv(self.file_path, index=False)

        return filtered_df

    def add_submissions(self, submissions: List[Submission]) -> Optional[pd.DataFrame]:
        if not os.path.exists(self.file_path):
            self._create_new_cache(submissions)
            return None

        if len(submissions) == 0:
            return None

        df = pd.read_csv(self.file_path)
        new_df = pd.DataFrame([vars(submission) for submission in submissions])
        df_combined = df.append(new_df, ignore_index=True)
        df_combined.to_csv(self.file_path, index=False)

        return df_combined

    def _filter_data(
        self, submission_df: pd.DataFrame, comments_df: pd.DataFrame
    ) -> pd.DataFrame:
        distinct_submission_titles = comments_df[["submission_title"]].drop_duplicates()
        filtered_submission_df = submission_df.merge(
            distinct_submission_titles,
            left_on="title",
            right_on="submission_title",
            how="inner",
        )

        return filtered_submission_df
