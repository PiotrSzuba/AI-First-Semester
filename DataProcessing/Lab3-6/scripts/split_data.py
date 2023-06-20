import pandas as pd
from sklearn.model_selection import train_test_split
import yaml
import sys
from typing import Tuple


def split_data(
    dataFrame,
    target_column,
    test_size=0.3,
    random_seed=42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    train_data, test_data = train_test_split(
        dataFrame,
        test_size=test_size,
        random_state=random_seed,
        stratify=dataFrame[target_column],
    )

    return train_data.reset_index(drop=True), test_data.reset_index(drop=True)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python split_data.py <input_path> <train_output_path> <test_output_path>"
        )
        sys.exit(1)

    with open("params.yaml") as f:
        params = yaml.safe_load(f)

    input_path = sys.argv[1]
    train_output_path = sys.argv[2]
    test_output_path = sys.argv[3]

    dataFrame = pd.read_csv(input_path)

    train_df, test_df = split_data(
        dataFrame,
        params["target_column"],
        params["split_ratio"],
        params["random_seed"],
    )

    train_df.to_csv(train_output_path, index=False)
    test_df.to_csv(test_output_path, index=False)
