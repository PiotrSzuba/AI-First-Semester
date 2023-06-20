import os
import time
import fnmatch
import pandas as pd
from src.stats import Stats
from typing import List, Optional
from src.reddit import RedditClient, CommentsCache, SubmissionCache


class ContextSingleton:
    _cache_folder: str = "src/cache"

    def __init__(self) -> None:
        self.cache_items: List[CommentsCache] = []
        self.update_cache()
    

    def get_subreddit(self, subreddit_name: str) -> Optional[pd.DataFrame]:
        start_time = time.time()
        
        item = self._get_cache_item(subreddit_name)
        if item is not None:
            df = item.get_data()
            Stats.write_context_get_time(time.time() - start_time)
            return df

        result = RedditClient.get_subreddit_comments(subreddit_name)
        
        item = CommentsCache(subreddit_name)
        if item.is_cached():
            self.cache_items.append(item)
        
        Stats.write_context_get_time(time.time() - start_time)
        return result

    def update_cache(self):
        self.cache_items = []
        for file_name in self._get_files():  
            item = self._get_comments_cache(file_name)
            if not item.is_cached():
                continue

            self.cache_items.append(item)

    def get_cached_subreddits(self) -> List[str]:
        self.update_cache()
        
        return [item.subreddit for item in self.cache_items if item.is_cached()]

    def get_average_data(self, data: pd.DataFrame, average_from_n_hours: int, emotions: List[str]) -> pd.DataFrame:
        df_melted = self._melt_data_frame(data, emotions)
        df_melted.set_index('date', inplace=True)
        return df_melted.groupby('emotion').resample(f'{average_from_n_hours}H').mean(numeric_only=True).reset_index()#.mean().reset_index()
        
    def get_overall_average_data(self, data: pd.DataFrame, emotions: List[str]) -> pd.DataFrame:
        return self._melt_data_frame(data, emotions).groupby('emotion').mean(numeric_only=True).reset_index()#.mean().reset_index()

    def get_top_users_by_emotion(self, subreddit_name: str, emotion: str, n_top: int = 5, min_comments: int = 2) -> pd.DataFrame:
        self.update_cache()
        item = self._get_cache_item(subreddit_name)
        if item is None:
            return None
        
        df = item.get_data()
        
        if item is None:
            return None
        filtered_users = df.groupby("username").filter(lambda x: len(x) >= min_comments)
        grouped_users = filtered_users.groupby("username").mean(numeric_only=True)
        sorted_users= grouped_users.sort_values(by=emotion, ascending=False)
        top_users = sorted_users.head(n_top)[[emotion]]
        top_users.reset_index(inplace=True)
        
        return top_users.sort_index()

    def get_progress(self, subreddit_name: str) -> float:
        comments = CommentsCache(subreddit_name)
        submissions = SubmissionCache(subreddit_name)
        
        if not comments.is_cached():
            return 0
        
        if not submissions.is_cached():
            return 0
        
        progress = comments.size / submissions.comments_count
        return progress if progress <= 1 else 1.0

    def _remove_first_and_last_days(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        data.loc[:, 'date'] = pd.to_datetime(data['date'])
        data.loc[:, 'date_only'] = data['date'].dt.date
        
        num_days = (data['date_only'].max() - data['date_only'].min()).days + 1
        if num_days > 7:
            min_date = data['date_only'].min()
            max_date = data['date_only'].max()
            return data[(data['date_only'] > min_date) & (data['date_only'] < max_date)].drop(columns=['date_only'])
        else:
            return data.drop(columns=['date_only'])
    
    def _melt_data_frame(self, data: pd.DataFrame, emotions: List[str]):
        data = self._remove_first_and_last_days(data)
        data["date"] = pd.to_datetime(data["date"]).dt.normalize()
        return data.melt(id_vars=['date'], value_vars=emotions, var_name='emotion', value_name='value')

    def _get_comments_cache(self, file_name: str) -> CommentsCache:
        cleaned_file_name = file_name.replace(
            f"{CommentsCache.cache_name}", ""
        ).replace(".csv", "")
        return CommentsCache(cleaned_file_name)
    
    def _get_files(self) -> List[str]:
        directories = [
            self._cache_folder + "/" + dir for dir in os.listdir(self._cache_folder)
        ]
        
        files = [
            file
            for sublist in [os.listdir(dir) for dir in directories]
            for file in sublist
        ]
        
        return [file for file in files if fnmatch.fnmatch(file, "*.csv") and CommentsCache.cache_name in file]

    def _get_cache_item(self, subreddit_name: str):
        return next(
            (item for item in self.cache_items if item.subreddit == subreddit_name),
            None,
        )


Context = ContextSingleton()
