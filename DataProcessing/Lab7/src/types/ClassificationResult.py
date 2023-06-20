class ClassificationResult:
    def __init__(self, prediction) -> None:
        self.anger: float = None
        self.fear: float = None
        self.joy: float = None
        self.sadness: float = None
        self.love: float = None
        self.surprise: float = None

        for item in prediction[0]:
            label = item["label"].lower()
            score = item["score"]
            if label == "anger":
                self.anger = score
            elif label == "fear":
                self.fear = score
            elif label == "joy":
                self.joy = score
            elif label == "sadness":
                self.sadness = score
            elif label == "love":
                self.love = score
            elif label == "surprise":
                self.surprise = score
            else:
                raise ValueError(f"{label} not handled")