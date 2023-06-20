import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys


def analyze_data(df):
    pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python data_analysis.py <input_path>")
        sys.exit(1)

    input_path = sys.argv[1]

    df = pd.read_csv(input_path)
    analyze_data(df)
