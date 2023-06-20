import json
import glob
import os
import sys
import pandas as pd
from typing import List
from datetime import datetime
from Review import Review

decoder = json.JSONDecoder()


def get_review(line: str, category: str):
    obj = json.loads(line)
    obj.pop("style", None)
    obj.setdefault("image", [])
    obj.setdefault("vote", 0)
    obj.setdefault("reviewText", "")
    obj.setdefault("summary", "")
    obj.setdefault("reviewerName", "")
    obj["category"] = category

    if obj["summary"]:
        text_word_count = len(obj["reviewText"].split())
        summary_word_count = len(obj["summary"].split())
        obj["textToSummaryRatio"] = text_word_count / summary_word_count
    else:
        obj["textToSummaryRatio"] = 0

    review_date = datetime.strptime(obj["reviewTime"], "%m %d, %Y")
    current_date = datetime.now()
    obj["reviewAge"] = (current_date - review_date).days

    obj["hasImage"] = bool(len(obj["image"]))
    obj["imageCount"] = len(obj["image"])

    obj["uniqueWordRatio"] = (
        len(set(obj["reviewText"].split())) / len(obj["reviewText"].split())
        if len(obj["reviewText"].split()) > 0
        else 0
    )

    obj["questionCount"] = obj["reviewText"].count("?")

    return Review(**obj)


def get_list_of_reviews_from_file(filename: str) -> List[Review]:
    category = os.path.splitext(os.path.basename(filename))[0][:-2]

    return [get_review(line, category) for line in open(filename)]

class Movie:
    def __init__(self, text: str, sentiment: str):
        self.text = text
        self.sentiment = sentiment

    def to_dict(self):
        return {
            "text": self.text,
            "sentiment": self.sentiment
        }


def get_movie(line: str, category: str) -> Review:
    return Movie(line.strip(), category)


def get_list_of_movie_reviews_from_file(filename: str) -> List[Movie]:
    sentiment = "positive" if "pos" in filename else "negative"

    with open(filename, encoding='ISO-8859-1') as file:
        return [get_movie(line, sentiment) for line in file]


def get_list_of_all_data(files: List[str]) -> List[Movie]:
    return [
        review
        for filename in files
        for review in get_list_of_movie_reviews_from_file(filename)
    ]


def get_data_frame_from_files(files: List[str]) -> pd.DataFrame:
    return pd.DataFrame([review.to_dict() for review in get_list_of_all_data(files)])


def preprocess_data(files: List[str]):
    reviews_df = get_data_frame_from_files(files)
    #reviews_df.dropna(subset=["overall", "reviewText", "reviewerName"], inplace=True)

    return reviews_df.reset_index(drop=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python preprocess_data.py <file_path>")
        sys.exit(1)

    output_path = sys.argv[1]

    files = glob.glob("./data/movie_input/*")

    reviews_df = preprocess_data(files)

    reviews_df.to_csv(output_path, index=False)
