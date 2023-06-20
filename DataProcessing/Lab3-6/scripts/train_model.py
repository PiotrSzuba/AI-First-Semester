import os
import sys
import yaml
import json
import mlflow
import warnings
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Tuple
from sklearn.svm import SVC
from datetime import datetime
from sklearn.decomposition import PCA
from sklearn.dummy import DummyClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import f1_score, confusion_matrix
from sklearn.feature_selection import SelectKBest, f_classif

warnings.filterwarnings(
    "ignore", category=UserWarning, message="Features .* are constant."
)
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, message="invalid value encountered in divide"
)


def cross_val_metrics(classifier, X, y, cv=5):
    f1_scores = cross_val_score(classifier, X, y, cv=cv, scoring="f1_weighted")
    mlflow.log_metric("cross_val mean F1 score", np.mean(f1_scores))
    mlflow.log_metric("cross_val Standard Deviation", np.std(f1_scores))


def mlflow_setup(experiment_name: str):
    mlflow_tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
    mlflow.set_tracking_uri(mlflow_tracking_uri)

    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        mlflow.create_experiment(experiment_name)

    mlflow.set_experiment(experiment_name)


def split_data(train_data: pd.DataFrame, test_data: pd.DataFrame, target_feature: str):
    X_train = train_data[[col for col in train_data.columns if col != target_feature]]
    y_train = train_data[target_feature]
    X_test = test_data[[col for col in test_data.columns if col != target_feature]]
    y_test = test_data[target_feature]

    return X_train, y_train, X_test, y_test


def apply_fueature_selection(
    X_train: np.ndarray, X_test: np.ndarray, y_train: np.ndarray, features: int = 200
) -> Tuple[np.ndarray, np.ndarray]:
    n_features = X_train.shape[1]
    k_best = min(features, n_features)
    selector = SelectKBest(f_classif, k=k_best)
    X_train_selected = selector.fit_transform(X_train, y_train)
    X_test_selected = selector.transform(X_test)

    return X_train_selected, X_test_selected


def apply_pca(
    X_train: np.ndarray, X_test: np.ndarray, components: int = 50
) -> Tuple[np.ndarray, np.ndarray]:
    n_features = X_train.shape[1]
    n_components = min(components, n_features)
    pca = PCA(n_components=n_components)
    X_train_pca = pca.fit_transform(X_train)
    X_test_pca = pca.transform(X_test)

    return X_train_pca, X_test_pca


def plot_confusion_matrix(conf_matrix, title):
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues")
    plt.title(title)
    plt.xlabel("Predicted label")
    plt.ylabel("True label")
    return plt


def log_metrics(
    y_train,
    y_pred_train,
    y_test,
    y_pred_test,
    metrics_output_path,
    random_seed,
    strategy,
):
    f1_train = f1_score(y_train, y_pred_train, average="weighted")
    f1_test = f1_score(y_test, y_pred_test, average="weighted")

    with open(metrics_output_path, "w") as f:
        json.dump({"f1_score": f1_test}, f)

    mlflow.log_param("random_seed", random_seed)
    mlflow.log_param("strategy", strategy)

    mlflow.log_metric("f1_score_train", f1_train)
    mlflow.log_metric("f1_score_test", f1_test)

    mlflow.log_artifact(metrics_output_path)


def plot_and_save_confusion_matrices(
    y_train, y_pred_train, y_test, y_pred_test, classifier
):
    conf_matrix_train = confusion_matrix(y_train, y_pred_train)
    conf_matrix_test = confusion_matrix(y_test, y_pred_test)

    conf_matrix_train_plt = plot_confusion_matrix(
        conf_matrix_train, "Train Confusion Matrix"
    )
    conf_matrix_test_plt = plot_confusion_matrix(
        conf_matrix_test, "Test Confusion Matrix"
    )

    conf_name = f"./data/output/{classifier.__class__.__name__}_conf_matrix_train.png"
    conf_matrix_train_plt.savefig(conf_name)
    mlflow.log_artifact(conf_name)

    conf_name = f"./data/output/{classifier.__class__.__name__}_conf_matrix_test.png"
    conf_matrix_test_plt.savefig(conf_name)
    mlflow.log_artifact(conf_name)


def train(
    classifier,
    train_data: pd.DataFrame,
    test_data: pd.DataFrame,
    target_feature: str,
    n_best_features: int = 200,
    n_pca_comps: int = 50,
):
    X_train, y_train, X_test, y_test = split_data(train_data, test_data, target_feature)

    X_train_selected, X_test_selected = apply_fueature_selection(
        X_train, X_test, y_train, n_best_features
    )

    X_train_pca, X_test_pca = apply_pca(X_train_selected, X_test_selected, n_pca_comps)

    cross_val_metrics(classifier, X_train_pca, y_train)

    clf = classifier
    clf.fit(X_train_pca, y_train)

    y_pred_train = clf.predict(X_train_pca)
    y_pred_test = clf.predict(X_test_pca)

    return y_pred_train, y_pred_test, y_train, y_test


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python train_model.py <train_features> <test_features> <output_path>"
        )
        sys.exit(1)

    with open("params.yaml") as f:
        params = yaml.safe_load(f)

    train_input_path = sys.argv[1]
    test_input_path = sys.argv[2]
    metrics_output_path = sys.argv[3]

    experiments = ["bag-of-words", "tf-idf", "word2vec"]

    classifiers = [
        DummyClassifier(
            strategy=params["strategy"], random_state=params["random_seed"]
        ),
        SVC(random_state=params["random_seed"]),
        RandomForestClassifier(random_state=params["random_seed"]),
    ]

    for classifier in classifiers:
        features_to_use = "all"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        mlflow_setup(features_to_use)
        with mlflow.start_run(
            run_name=f"{classifier.__class__.__name__} - {features_to_use} - {timestamp}"
        ):
            train_data = pd.read_csv(train_input_path)
            test_data = pd.read_csv(test_input_path)

            y_pred_train, y_pred_test, y_train, y_test = train(
                classifier, train_data, test_data, params["target_column"]
            )

            log_metrics(
                y_train,
                y_pred_train,
                y_test,
                y_pred_test,
                metrics_output_path,
                params["random_seed"],
                params["strategy"],
            )

            plot_and_save_confusion_matrices(
                y_train, y_pred_train, y_test, y_pred_test, classifier
            )
