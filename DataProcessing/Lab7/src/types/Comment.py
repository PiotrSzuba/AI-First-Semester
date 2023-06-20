class Comment:
    def __init__(
        self, username: str, text: str, date: str, submission_title: str
    ) -> None:
        self.username: str = username
        self.text: str = text
        self.date: str = date
        self.submission_title: str = submission_title
