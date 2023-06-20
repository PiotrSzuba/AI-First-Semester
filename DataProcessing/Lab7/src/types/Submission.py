from datetime import datetime, timedelta
from praw.models import Submission as RSubmission


class Submission:
    def __init__(self, submission: RSubmission) -> None:
        self.id = submission.id
        self.title = submission.title
        self.date = self._format_date(submission.created_utc)
        self.dead = self._is_dead(submission)
        submission.comments.replace_more(limit=None)
        self.comment_count = len(submission.comments.list())

    def _format_date(self, date: str) -> str:
        return datetime.fromtimestamp(date).strftime("%Y-%m-%d %H:%M:%S")

    def _is_dead(self, submission: RSubmission) -> bool:
        comments = submission.comments
        if not comments:
            return False
        last_comment_date = datetime.utcfromtimestamp(
            max(comments, key=lambda comment: comment.created_utc).created_utc
        )
        submission_date = datetime.utcfromtimestamp(submission.created_utc)
        time_difference = last_comment_date - submission_date
        return time_difference > timedelta(hours=24)
