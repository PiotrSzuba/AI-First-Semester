import os
from typing import Union
from difflib import SequenceMatcher

import pandas as pd

VALID_FACULTIES = ["W02", "W03", "W04", "W05", "W06", "W07", "W08", "W09", "W10", "W11", "W12", "W13"]


def similarity_rating(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def load_workers(faculty: str) -> pd.DataFrame:
    return pd.read_csv(f"raw_data_cache/{faculty}_workers.csv")


def load_people_from_edge_list(filepath: Union[str, os.PathLike]) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df = df[["source", "source_label"]]
    df.columns = ["node_id", "node_label"]
    df = df.drop_duplicates()
    return df


def main(working_dir: Union[str, os.PathLike], faculties: list[str]):
    os.chdir(working_dir)

    people_df = load_people_from_edge_list("clean_data/all/all_weighted.csv")
    people_df["faculty"] = pd.NA

    for faculty in faculties:
        df = load_workers(faculty)
        names_set = set(df["name"])
        people_df = populate_faculty(people_df, names_set, faculty)

    unassigned = people_df[pd.isnull(people_df["faculty"])]
    count_unassigned = len(unassigned)

    if count_unassigned > 10:
        raise ValueError(f"{count_unassigned} are left unassigned")
    else:
        print("Please annotate rows:")
        print(unassigned)
        people_df.to_csv("clean_data/all/names.csv", index=False)


def populate_faculty(people_df: pd.DataFrame, faculty_name_set: set[str], faculty_name: str) -> pd.DataFrame:
    def infer_faculty_by_name(row):
        full_name = row["node_label"]
        if pd.isnull(row["faculty"]) and full_name in faculty_name_set:
            return faculty_name
        else:
            return row["faculty"]

    people_df["faculty"] = people_df.apply(infer_faculty_by_name, axis=1)

    return people_df


if __name__ == "__main__":
    faculties = ["W02", "W03", "W04", "W05", "W06", "W07", "W08", "W09", "W10", "W11", "W12", "W13"]
    main("../", faculties)
