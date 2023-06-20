import re
import praw
import pandas as pd
from src.helpers import ENV
from datetime import datetime
from typing import Optional, List
from src.types.Comment import Comment
from src.types.Submission import Submission
from src.reddit.SubmissionCache import SubmissionCache, CommentsCache
from praw.models import Subreddit, Submission as RSubmission, Comment as RComment


class RedditClientSingleton:
    def __init__(self) -> None:
        self._client = praw.Reddit(
            client_id=ENV.CLIENT_ID,
            client_secret=ENV.CLIENT_SECRET,
            username=ENV.REDDIT_USERNAME,
            password=ENV.PASSWORD,
            user_agent=f"{ENV.CLIENT_ID} by u/{ENV.REDDIT_USERNAME}",
        )

    def get_subreddit_comments(self, subreddit_name: str) -> Optional[pd.DataFrame]:
        subreddit = self._get_subreddit(subreddit_name)

        if subreddit is None:
            return None

        comments_cache = CommentsCache(subreddit_name)

        for submission in self._filter_submissions(subreddit):
            submission_comments = self._get_comments_from_submission(submission)
            comments_cache.add_comments(submission_comments)

        return comments_cache.get_data()

    def _fetch_submissions(self, subreddit: Subreddit) -> List[RSubmission]:
        return [
            submission
            for submission in subreddit.new(limit=20) #ENV.SUBMISSION_LIMIT
            if len(submission.comments) != 0
        ]

    def _handle_new_submissions(
        self,
        cache: SubmissionCache,
        cached_data: pd.DataFrame,
        submissions: List[RSubmission],
    ) -> List[RSubmission]:
        cached_ids = list(cached_data["id"])
        new_submissions = [
            submission for submission in submissions if submission.id not in cached_ids
        ]
        cache.add_submissions(self._convert_submissions(new_submissions))

        return new_submissions

    def _filter_submissions(self, subreddit: Subreddit) -> List[RSubmission]:
        cache = SubmissionCache(subreddit)
        submissions = self._fetch_submissions(subreddit)

        cached_data = cache.get_data()

        if cached_data is None:
            cache.add_submissions(self._convert_submissions(submissions))
            return submissions

        return self._handle_new_submissions(cache, cached_data, submissions)

    def _convert_submissions(self, submissions: List[RSubmission]) -> List[Submission]:
        return [Submission(submission) for submission in submissions]

    def _get_comments_from_submission(self, submission: RSubmission) -> List[Comment]:
        comments = [
            self._create_comment(comment, submission.title)
            for comment in submission.comments.list()
        ]

        return [comment for comment in comments if comment is not None]

    def _is_comment_valid(self, comment: RComment) -> bool:
        if not hasattr(comment, "author"):
            return False

        author_name = comment.author.name if hasattr(comment.author, "name") else None
        text = comment.body if hasattr(comment, "body") else None
        date = comment.created_utc if hasattr(comment, "created_utc") else None

        if author_name is None or text is None or date is None:
            return False

        return True

    def _create_comment(self, comment: RComment, post_title: str) -> Optional[Comment]:
        if not self._is_comment_valid(comment):
            return None

        filtered_text = re.sub(r"```.*?```", "", comment.body, flags=re.DOTALL)

        return Comment(
            comment.author.name,
            filtered_text,
            self._format_date(comment.created_utc),
            post_title,
        )

    def _format_date(self, date: str) -> str:
        return datetime.fromtimestamp(date).strftime("%Y-%m-%d %H:%M:%S")

    def _get_subreddit(self, subreddit_name: str) -> Optional[Subreddit]:
        try:
            subreddit = self._client.subreddit(subreddit_name)
            self._client.subreddit(subreddit_name).id
            return subreddit
        except Exception as e:
            print(
                f"Exception occurred while getting subreddit: {subreddit_name} \n {e}"
            )
            return None


RedditClient = RedditClientSingleton()
