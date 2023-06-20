import os
import re
import pandas as pd
from typing import List


def merge_csvs(input_directory: str) -> pd.DataFrame:
    dataFrame_list = []

    for filename in os.listdir(input_directory):
        if not filename.endswith(".csv"):
            continue

        file_path = os.path.join(input_directory, filename)
        dataFrame = pd.read_csv(file_path)

        name = filename.replace("_", " ").replace(".csv", "")

        dataFrame.insert(0, "name", name)

        dataFrame_list.append(dataFrame)

    merged_dataFrame = pd.concat(dataFrame_list, axis=0, ignore_index=True)

    return merged_dataFrame


def clear_name_list(names: str):
    if names == None or names == "":
        return []
    
    people = names.split(";")

    formatted_names = []
    for person in people:
        if "," in person:
            surname, name = person.split(",")
            formatted_name = f"{surname} {name}"
        else:
            formatted_name = person

        if formatted_name.endswith("."):
            formatted_name = formatted_name[:-1]

        formatted_name = formatted_name.replace("  ", " ")

        words = formatted_name.split(" ")
        if len(words) == 3 and len(words[-1]) == 1:
            formatted_name = ' '.join(words[:-1]) + words[-1]
            formatted_name = formatted_name[:-1]
        
        formatted_names.append(formatted_name)

    return formatted_names


def clear_score(score: str):
    score = str(score)
    if score == "0":
        return score
    
    if score.startswith('00') and len(score) == 3:
        return score[2:]
    
    if score.startswith('0') and len(score) == 3:
        return score[1:]
    
    if '.' in score and ';' not in score:
        return int(float(score))
    
    if bool(re.search(r'^\d+$', score)):
        return score
    
    scores = score.split(";")
    
    if len(scores) <= 1:
        raise ValueError(f"Could not convert {score}") 
    
    new_scores = []
    for x in scores:
        if len(x) != 3:
            continue
        
        if x.startswith('00'):
            new_scores.append(x[2:])
            continue
        
        if x.startswith('0'):
            new_scores.append(x[1:])
            continue
    
    scores = [int(x) for x in new_scores]
    
    return max(scores)


def clear_title(title: str):
    return title[:-1] if title.endswith('/') else title


def clear_final_csv(dataFrame: pd.DataFrame, faculty_name: str) -> pd.DataFrame:
    keep_cols = [
        "name",
        "Wydział główny",
        "Jednostka główna",
        "Rodzaj pracy",
        "Rok zaliczenia",
        "Autorzy PWr",
        "Tytuł pracy",
        "Punktacja czasopisma na wykazie MEiN",
    ]

    cleaned_dataFrame = dataFrame.drop(
        columns=[col for col in dataFrame.columns if col not in keep_cols]
    )

    new_names = {
        "Wydział główny": "faculty",
        "Jednostka główna": "department",
        "Rodzaj pracy": "work_type",
        "Rok zaliczenia": "year",
        "Autorzy PWr": "pwr_authors",
        "Tytuł pracy": "title",
        "Punktacja czasopisma na wykazie MEiN": "score",
    }

    cleaned_dataFrame = cleaned_dataFrame.rename(columns=new_names)
    cleaned_dataFrame = cleaned_dataFrame.dropna(subset=["pwr_authors"])
    cleaned_dataFrame["score"].fillna(value=0, inplace=True)
    cleaned_dataFrame["score"] = cleaned_dataFrame["score"].apply(
        clear_score
    )
    
    cleaned_dataFrame["title"] = cleaned_dataFrame["title"].apply(
        clear_title
    )

    cleaned_dataFrame["faculty"] = faculty_name
    cleaned_dataFrame["pwr_authors"] = cleaned_dataFrame["pwr_authors"].apply(
        clear_name_list
    )

    cleaned_dataFrame = cleaned_dataFrame.drop(
        cleaned_dataFrame.loc[(cleaned_dataFrame["pwr_authors"].apply(len) == 1)].index
    )

    for index, row in cleaned_dataFrame.iterrows():
        if row['name'] in row['pwr_authors']:
            row['pwr_authors'].remove(row['name'])

    cleaned_dataFrame["u_name"] = cleaned_dataFrame["name"] + " " + faculty_name
    
    grouped = cleaned_dataFrame.groupby("u_name")
    cleaned_dataFrame.insert(0, "id", grouped.ngroup())

    return cleaned_dataFrame


def clear_data(faculty_name: str):
    input_directory = f"raw_data_cache/{faculty_name}_workers"
    output_path = f"clean_data/{faculty_name}/{faculty_name}_data.csv"
    
    dataFrame = merge_csvs(input_directory)

    dataFrame = clear_final_csv(dataFrame, faculty_name)

    dataFrame["faculty"] = faculty_name

    if not os.path.exists(f"clean_data/{faculty_name}"):
        os.makedirs(f"clean_data/{faculty_name}")

    dataFrame.to_csv(output_path, index=False)

    return dataFrame


def concat_dataframes(dataFrames: List[pd.DataFrame]):
    dataFrame = pd.concat(dataFrames, ignore_index=True)
    dataFrame.drop('id', axis=1, inplace=True)
    grouped = dataFrame.groupby("u_name")
    dataFrame.insert(0, "id", grouped.ngroup())
    dataFrame = dataFrame.sort_values('id')
    
    if not os.path.exists("clean_data/all"):
        os.makedirs("clean_data/all")
    
    dataFrame.to_csv("clean_data/all/all_data_with_faculty.csv", index=False)
    
    return dataFrame


if __name__ == "__main__":
    os.chdir("../")
    faculties = ["W02", "W03", "W04", "W05", "W06", "W07", "W08", "W09", "W10", "W11", "W12", "W13"]
    dataFrames = [clear_data(faculty_name) for faculty_name in faculties]
    concat_dataframes(dataFrames)
