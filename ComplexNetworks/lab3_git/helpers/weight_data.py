import os

import pandas as pd
from typing import List


def print_progress(index: int, max_iters: int):
    progress = 100 * (index + 1) / max_iters
    print(f" Processing {progress:.2f}%   ", end="\r")


def check_if_row_exists(dataFrame: pd.DataFrame, row: pd.Series) -> bool:
    return not dataFrame[
        (dataFrame["name"] == row["name"])
        & (dataFrame["title"] == row["title"])
        & (dataFrame["year"] == row["year"])
    ].empty


def get_authors_from_row(row: pd.Series) -> List[str]:
    return eval(row["pwr_authors"])


def add_missing_people(dataFrame: pd.DataFrame, min_year=2019) -> pd.DataFrame:
    name_list = list(dataFrame["name"].unique())

    dataFrame = dataFrame.drop(columns=["id"])
    new_dataFrame = dataFrame.copy().reset_index(drop=True)

    for index, row in dataFrame.iterrows():
        if row["year"] < min_year:
            continue

        print_progress(index, len(dataFrame))

        pwr_authors = get_authors_from_row(row)

        for author in pwr_authors:
            if author in name_list:
                continue

            new_row = row.copy()
            new_row["name"] = author
            
            if len(author.split(" ")) > 2 and len(author.split(" ").pop()) == 1:
                # pojedyncza literka zamiast drugiego imienia
                pass

            if check_if_row_exists(new_dataFrame, new_row):
                continue

            new_dataFrame = new_dataFrame.append(new_row, ignore_index=True)

    new_dataFrame = new_dataFrame.sort_values(by="name")
    grouped = new_dataFrame.groupby("name")
    new_dataFrame.insert(0, "id", grouped.ngroup())

    return new_dataFrame.reset_index(drop=True)


def remove_name_from_pwr_authors(row: pd.Series) -> pd.Series:
    authors = get_authors_from_row(row)

    name = row["name"]

    authors = [author for author in authors if author != name]

    row["pwr_authors"] = str(authors)

    return row


def remove_old_workers(names: List[str], authors: List[str]) -> List[str]:
    return [author for author in authors if author in names]


def prepare_dataFrame_for_weighting(dataFrame: pd.DataFrame) -> pd.DataFrame:
    new_df = pd.DataFrame(columns=["source", "target", "source_label", "target_label", "score"])

    name_id_tuples = list(
        dataFrame.groupby("name")
        .agg({"id": "first"})
        .reset_index()
        .itertuples(index=False, name=None)
    )
    
    names = [t[0] for t in name_id_tuples]
    
    for index, row in dataFrame.iterrows():
        print_progress(index, len(dataFrame))   
        row = remove_name_from_pwr_authors(row)

        authors = get_authors_from_row(row)

        authors = remove_old_workers(names, authors)

        for author in authors:
            if author not in names:
                raise ValueError(f"{author} does not have an id. row_index: {index}")

            source = row["id"]
            source_label = row["name"]
            target, target_label = [
                (t[1], t[0]) for t in name_id_tuples if t[0] == author
            ][0]
            score = row["score"]

            new_row = {
                "source": source,
                "target": target,
                "source_label": source_label,
                "target_label": target_label,
                "score": score,
            }
            new_df = new_df.append(new_row, ignore_index=True)

    return new_df


def weight_data(dataFrame: pd.DataFrame) -> pd.DataFrame:
    sent_count = dataFrame.groupby(["source", "target"]).size()
    all_sent_count = dataFrame.groupby("source").size()

    columns = dataFrame.columns.tolist()
    columns.append("weight")

    weighted_df = pd.DataFrame(columns=columns)

    items = sent_count.items()
    index = 0
    for (source, target), count in items:
        index += 1
        print_progress(index, len(sent_count))

        weight = count / all_sent_count[source]

        temp_df = (
            dataFrame[(dataFrame["source"] == source) & (dataFrame["target"] == target)]
            .copy()
            .reset_index(drop=True)
        )

        temp_df.loc[:, "weight"] = weight
        temp_df.loc[:, "source"] = (temp_df["source"].astype(int) + 1).astype(str)
        temp_df.loc[:, "target"] = (temp_df["target"].astype(int) + 1).astype(str)
        unique = temp_df.nlargest(1, "weight")

        weighted_df = pd.concat([weighted_df, unique])
    
    weighted_df.drop('score', axis=1, inplace=True)
    return weighted_df


def main(faculty_name: str):
    input_path = f"clean_data/{faculty_name}/{faculty_name}_data_with_faculty.csv"
    # input_path = f"clean_data/{faculty_name}/{faculty_name}_data_pre_weight.csv"
    dataFrame = pd.read_csv(input_path)

    dataFrame = add_missing_people(dataFrame)
    # dataFrame.to_csv(
    #     f"clean_data/{faculty_name}/{faculty_name}_data_faculty_expanded.csv", index=False
    # )

    dataFrame = prepare_dataFrame_for_weighting(dataFrame)
    dataFrame.to_csv(
        f"clean_data/{faculty_name}/{faculty_name}_with_faculty_data_faculty_pre_weight.csv", index=False
    )

    dataFrame = weight_data(dataFrame)
    dataFrame.to_csv(
        f"clean_data/{faculty_name}/{faculty_name}_weighted.csv", index=False
    )


if __name__ == "__main__":
    os.chdir("../")
    faculty_name = "all"
    main(faculty_name)
