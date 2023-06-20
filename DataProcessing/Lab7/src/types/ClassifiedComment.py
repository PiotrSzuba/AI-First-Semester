import re
from src.types.Classifier import Classifier
from src.types.Comment import Comment


class ClassifiedComment:
    def __init__(self, comment: Comment, subreddit_name: str) -> None:
        self.username: str = comment.username
        self.text: str = self._clean_text(comment.text)
        self.date: str = comment.date
        self.submission_title: str = comment.submission_title
        self.subreddit_name: str = subreddit_name

        result = Classifier.analize(self.text)

        self.anger: float = result.anger
        self.fear: float = result.fear
        self.joy: float = result.joy
        self.sadness: float = result.sadness
        self.love: float = result.love
        self.surprise: float = result.surprise

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"http\S+", "", text)  # URLs
        text = re.sub(r"@\w+", "", text)  # user mentions
        text = re.sub(r"[^a-zA-Z\s]", "", text)  # special characters, digits
        text = re.sub(r"\s{2,}", " ", text)  # extra spaces

        return text.strip()
