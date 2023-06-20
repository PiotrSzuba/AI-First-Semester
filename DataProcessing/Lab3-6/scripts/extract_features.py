import re
import sys
import ast
import yaml
import numpy as np
import pandas as pd
from typing import List, Tuple
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from gensim.models import Word2Vec


class Word2VecVectorizer:
    def __init__(self, max_features=1000):
        self.max_features = max_features
        self.model = None

    def _sentence_vector(self, words):
        vector_sum = np.zeros(self.max_features)
        word_count = 0

        for word in words:
            if word in self.model.wv:
                vector_sum += self.model.wv[word]
                word_count += 1

        return vector_sum / word_count if word_count > 0 else vector_sum

    def fit(self, X):
        tokenized_sentences = [sentence.split() for sentence in X]
        self.model = Word2Vec(
            tokenized_sentences, vector_size=self.max_features, min_count=1, workers=4
        )
        return self

    def transform(self, X):
        tokenized_sentences = [sentence.split() for sentence in X]

        def average_word_vectors(sentence):
            vectors = [
                self.model.wv[word] for word in sentence if word in self.model.wv
            ]
            if len(vectors) == 0:
                return np.zeros(self.max_features)
            return np.mean(vectors, axis=0)

        return np.array(
            [average_word_vectors(sentence) for sentence in tokenized_sentences]
        )


def code_categorical_data(df: pd.DataFrame, columns: List[str]):
    if len(columns) == 0:
        return df, []

    original_columns = set(df.columns)
    df = pd.get_dummies(df, columns=columns)
    new_columns = set(df.columns)
    added_columns = new_columns - original_columns
    return df, list(added_columns)


def convert_cell(series: pd.Series):
    converted = pd.to_numeric(series, errors="coerce", downcast="float")
    converted = converted.replace([np.inf, -np.inf], np.nan)
    converted = converted.fillna(np.nan)
    return converted


def impute_data(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    columns: List[str],
    stategy: str = "median",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    train_df[columns] = train_df[columns].apply(lambda x: convert_cell(x))
    test_df[columns] = test_df[columns].apply(lambda x: convert_cell(x))

    imputer = SimpleImputer(missing_values=np.nan, strategy=stategy)
    train_df[columns] = imputer.fit_transform(train_df[columns])
    test_df[columns] = imputer.transform(test_df[columns])

    return train_df, test_df


def scale_numeric_features(
    train_df: pd.DataFrame, test_df: pd.DataFrame, columns: List[str]
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    scaler = StandardScaler()

    for column in columns:
        if train_df[column].dtype == object:
            train_df[column] = pd.to_numeric(
                train_df[column].str.replace(",", ""), errors="coerce"
            )
        if test_df[column].dtype == object:
            test_df[column] = pd.to_numeric(
                test_df[column].str.replace(",", ""), errors="coerce"
            )

    train_df, test_df = impute_data(train_df, test_df, columns)

    train_df[columns] = normalize(train_df[columns])
    test_df[columns] = normalize(test_df[columns])

    train_df[columns] = scaler.fit_transform(train_df[columns])
    test_df[columns] = scaler.transform(test_df[columns])

    return train_df, test_df, columns


def clean_text(text):
    if text is None or isinstance(text, float) and np.isnan(text):
        return ""

    text = re.sub(r"[^a-zA-Z\s]", "", text)
    text = text.lower()

    return text


def fit_vectorizers(
    train_df: pd.DataFrame,
    text_col_name: str,
    feautures: int,
    vectorizer_class=CountVectorizer,
):
    train_df[text_col_name] = train_df[text_col_name].apply(clean_text)

    vectorizer = vectorizer_class(max_features=feautures)

    vectorizer.fit(train_df[text_col_name])

    return vectorizer


def get_vectorizer_class(vectorizer_method: str):
    if vectorizer_method == "bag-of-words":
        return CountVectorizer
    elif vectorizer_method == "tf-idf":
        return TfidfVectorizer
    elif vectorizer_method == "word2vec":
        return Word2VecVectorizer
    else:
        raise ValueError(f"Vectorizer method '{vectorizer_method}' not found.")


def get_vectorizers(
    train_df: pd.DataFrame,
    text_cols: List[str],
    max_words: int = 1000,
    vectorizer_method: str = "bag-of-words",
) -> List[Tuple[CountVectorizer, str]]:
    vectorizers: List[Tuple[CountVectorizer, str]] = []

    max_words_per_col = int(max_words / len(text_cols))

    for text_col in text_cols:
        vectorizer = fit_vectorizers(
            train_df,
            text_col,
            max_words_per_col,
            get_vectorizer_class(vectorizer_method),
        )
        vectorizers.append((vectorizer, text_col))

    return vectorizers


def vectorize_text(
    dataFrame: pd.DataFrame, vectorizer: CountVectorizer, column_name: str
) -> Tuple[pd.DataFrame, List[str]]:
    dataFrame[column_name] = dataFrame[column_name].apply(clean_text)

    text_vectors = vectorizer.transform(dataFrame[column_name])

    if hasattr(vectorizer, "get_feature_names_out"):
        columns = [f"{column_name}_{col}" for col in vectorizer.get_feature_names_out()]
        text_vectors_df = pd.DataFrame(text_vectors.toarray(), columns=columns)
    else:
        columns = [f"{column_name}_{i}" for i in range(text_vectors.shape[1])]
        text_vectors_df = pd.DataFrame(text_vectors, columns=columns)

    text_vectors_df.reset_index(drop=True, inplace=True)

    dataFrame = pd.concat([dataFrame, text_vectors_df], axis=1)

    dataFrame = dataFrame.drop(columns=[column_name])

    return dataFrame, list(columns)


def vectorize_text_columns(
    dataFrame: pd.DataFrame, vectorizers: List[Tuple[CountVectorizer, str]]
) -> Tuple[pd.DataFrame, List[str]]:
    if len(vectorizers) == 0:
        return dataFrame, []

    new_cols: List[str] = []

    for vectorizer, column in vectorizers:
        dataFrame, vectorized_cols = vectorize_text(dataFrame, vectorizer, column)
        new_cols += vectorized_cols

    return dataFrame, new_cols


def convert_cols(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    text_cols: List[str],
    categorical_features: List[str],
    vectorizer_method: str = "bag-of-words",
    vectorizer_lenght: int = 1000,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    train_df, categorical_columns = code_categorical_data(
        train_df, categorical_features
    )
    test_df, _ = code_categorical_data(test_df, categorical_features)

    vectorizers = get_vectorizers(
        train_df, text_cols, vectorizer_lenght, vectorizer_method
    )

    train_df, vectorized_columns = vectorize_text_columns(train_df, vectorizers)
    test_df, _ = vectorize_text_columns(test_df, vectorizers)

    return train_df, test_df, categorical_columns + vectorized_columns


def extract_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_feature: str,
    vectorizer_method: str = "bag-of-words",
    vectorizer_length: int = 1000,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    numerical_columns, categorical_columns, text_columns = get_cols_types(
        train_df, target_feature
    )

    train_df, test_df, converted_cols = convert_cols(
        train_df,
        test_df,
        text_columns,
        categorical_columns,
        vectorizer_method,
        vectorizer_length,
    )
    train_df, test_df, scaled_cols = scale_numeric_features(
        train_df, test_df, numerical_columns + converted_cols
    )

    train_df = train_df.drop(
        columns=[
            col for col in train_df.columns if col not in [target_feature] + scaled_cols
        ]
    )

    test_df = test_df.drop(
        columns=[
            col for col in test_df.columns if col not in [target_feature] + scaled_cols
        ]
    )

    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


def save_results(output_path: str, dataFrame: pd.DataFrame, keep_cols: List[str]):
    dataFrame.to_csv(output_path, index=False)


def get_numeric_columns(df: pd.DataFrame):
    for column in list(df.columns):
        numeric_vote = pd.to_numeric(df[column], errors="coerce")
        is_numeric = numeric_vote.notna()
        num_numeric = is_numeric.sum()
        pct_numeric = num_numeric / len(df) * 100
        if pct_numeric >= 80:
            if is_numeric.all():
                df["vote"] = numeric_vote.astype(int)
            else:
                df["vote"] = numeric_vote.astype(float)

    numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]

    return list(df.select_dtypes(include=numerics).columns)


def get_categorical_columns(df: pd.DataFrame):
    categorical_cols = []

    for column in df.columns:
        unique_ratio = df[column].nunique() / len(df[column])
        if unique_ratio < 0.01:
            categorical_cols.append(column)

    return categorical_cols


def eval_list(cell):
    try:
        return ast.literal_eval(cell)
    except (ValueError, SyntaxError):
        return cell


def get_cols_types(df: pd.DataFrame, target_feature: str):
    non_target_df = df.drop(columns=[target_feature])

    array_df = non_target_df.applymap(eval_list)
    array_cols = [
        c
        for c in array_df.columns
        if array_df[c].apply(lambda x: isinstance(x, list)).all()
    ]
    non_array_df = non_target_df.drop(columns=array_cols)

    numerical_columns = get_numeric_columns(non_array_df)
    non_num_df = non_array_df.drop(columns=numerical_columns)

    categorical_columns = get_categorical_columns(non_num_df)
    non_cat_df = non_num_df.drop(columns=categorical_columns)

    text_columns = (
        non_cat_df.select_dtypes(include=["object"])
        .applymap(lambda x: not isinstance(x, list) and len(str(x)) > 50)
        .any()
        .loc[lambda x: x]
        .index
    )

    return numerical_columns, categorical_columns, list(text_columns)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: python extract_features.py <train_input_path> <test_input_path> <train_output_path> <test_output_path>"
        )
        sys.exit(1)

    with open("params.yaml") as f:
        params = yaml.safe_load(f)

    train_input_path = sys.argv[1]
    test_input_path = sys.argv[2]
    train_output_path = sys.argv[3]
    test_output_path = sys.argv[4]

    train_df = pd.read_csv(train_input_path)
    test_df = pd.read_csv(test_input_path)

    train_df, test_df = extract_features(train_df, test_df, params["target_column"])

    train_df.to_csv(train_output_path, index=False)
    test_df.to_csv(test_output_path, index=False)
