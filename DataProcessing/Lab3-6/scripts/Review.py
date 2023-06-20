from typing import List


class Review:
    target_feature = "overall"
    text_columns = ["reviewText", "summary"]
    categorical_columns = ["category", "verified", "hasImage"]
    numeric_columns = [
        "vote",
        "unixReviewTime",
        "textToSummaryRatio",
        "reviewAge",
        "imageCount",
        "uniqueWordRatio",
        "questionCount",
    ]

    def __init__(
        self,
        overall: float,
        vote: int,
        image: List[str],
        verified: bool,
        reviewTime: str,
        reviewerID: str,
        asin: str,
        reviewerName: str,
        reviewText: str,
        summary: str,
        unixReviewTime: int,
        category: str,
        textToSummaryRatio: float,
        reviewAge: int,
        hasImage: bool,
        imageCount: int,
        uniqueWordRatio: int,
        questionCount: int,
    ):
        self.overall = overall
        self.vote = vote
        self.image = image
        self.verified = verified
        self.reviewTime = reviewTime
        self.reviewerID = reviewerID
        self.asin = asin
        self.reviewerName = reviewerName
        self.reviewText = reviewText
        self.summary = summary
        self.unixReviewTime = unixReviewTime
        self.category = category
        self.textToSummaryRatio = textToSummaryRatio
        self.reviewAge = reviewAge
        self.hasImage = hasImage
        self.imageCount = imageCount
        self.uniqueWordRatio = uniqueWordRatio
        self.questionCount = questionCount

    def to_dict(self):
        return {
            "overall": self.overall,
            "vote": self.vote,
            "image": self.image,
            "verified": self.verified,
            "reviewTime": self.reviewTime,
            "reviewerID": self.reviewerID,
            "asin": self.asin,
            "reviewerName": self.reviewerName,
            "reviewText": self.reviewText,
            "summary": self.summary,
            "unixReviewTime": self.unixReviewTime,
            "category": self.category,
            "textToSummaryRatio": self.textToSummaryRatio,
            "reviewAge": self.reviewAge,
            "hasImage": self.hasImage,
            "imageCount": self.imageCount,
            "uniqueWordRatio": self.uniqueWordRatio,
            "questionCount": self.questionCount,
        }
