import os

import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from torch import nn
from torch.nn.functional import normalize as normalize_emb
from torchvision import transforms as T
from torchvision.io.image import read_image, ImageReadMode
from torchvision import models as tv_models
from tqdm import tqdm


def load_raw_data(root_dir: str, num_samples: int, seed: int) -> pd.DataFrame:
    data = pd.read_csv(
        filepath_or_buffer=os.path.join(root_dir, "labels.csv"),
        index_col=0,
    )
    data = data.drop(columns=["text_ocr"])
    data = data.dropna()

    # Some of the files are malformed or they are GIFs
    data = data[~data["image_name"].isin([
        "image_1567.jpg",
        "image_3925.jpg",
        "image_4924.jpg",
        "image_5119.png",
        "image_5250.jpg",
        "image_5580.png",
        "image_6357.jpg",
        "image_6882.png",
    ])]

    data["humour"] = data["humour"].map({
        "hilarious": 0,
        "very_funny": 1,
        "funny": 2,
        "not_funny": 3,
    })
    data["sarcasm"] = data["sarcasm"].map({
        "very_twisted": 0,
        "twisted_meaning": 1,
        "general": 2,
        "not_sarcastic": 3,
    })
    data["offensive"] = data["offensive"].map({
        "hateful_offensive": 0,
        "very_offensive": 1,
        "slight": 2,
        "not_offensive": 3,
    })
    data["motivational"] = data["motivational"].map({
        "motivational": 0,
        "not_motivational": 1,
    })
    data["overall_sentiment"] = data["overall_sentiment"].map({
        "very_positive": 0,
        "positive": 1,
        "neutral": 2,
        "negative": 3,
        "very_negative": 4,
    })

    data = data.sample(n=num_samples, random_state=seed)

    return data


def get_image_feature_extractor() -> tv_models.ResNet:
    """For images use the ResNet50 model"""
    resnet = tv_models.resnet50(pretrained=True)
    resnet.eval()
    resnet.fc = nn.Identity()

    return resnet


def get_text_feature_extractor() -> SentenceTransformer:
    miniLM = SentenceTransformer("all-MiniLM-L6-v2")

    return miniLM


def preprocess(
    root_dir: str,
    num_samples: int,
    seed: int
) -> pd.DataFrame:
    resize = T.Resize((224, 224))
    normalize = T.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    )

    resnet18 = get_image_feature_extractor()
    miniLM = get_text_feature_extractor()

    metadata = load_raw_data(root_dir, num_samples, seed)
    imgs_dir = os.path.join(root_dir, "images/")

    out = []

    for _, row in tqdm(
        iterable=metadata.iterrows(),
        total=metadata.shape[0],
        desc="Processing",
    ):
        try:
            original_img = read_image(
                path=os.path.join(imgs_dir, row["image_name"]),
                mode=ImageReadMode.RGB,
            ).float()
        except Exception as e:
            print(row)
            continue

        resized_img = resize(original_img)
        normalized_img = normalize(resized_img)

        with torch.no_grad():
            img_emb = resnet18(normalized_img.unsqueeze(dim=0))
            text_emb = miniLM.encode(
                sentences=row["text_corrected"],
                convert_to_tensor=True,
            )

        out.append({
            "img_emb": normalize_emb(img_emb[0], dim=0),
            "text_emb": normalize_emb(text_emb, dim=0),

            "image": resized_img,
            "text": row["text_corrected"],

            "label_humour": row["humour"],
            "label_sarcasm": row["sarcasm"],
            "label_offensive": row["offensive"],
            "label_motivational": row["motivational"],
            "label_sentiment": row["overall_sentiment"],
        })

    return pd.DataFrame.from_records(out)


def main():
    all_data = preprocess(
        root_dir="./data/memotion/",
        num_samples=1_000,
        seed=42,
    )

    all_data.to_pickle("data/processed.pkl")


if __name__ == "__main__":
    main()
