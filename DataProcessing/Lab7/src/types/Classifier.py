from transformers import pipeline, AutoTokenizer
from src.types.ClassificationResult import ClassificationResult


class ClassifierSingleton:
    emotions = [
        "anger",
        "fear",
        "joy",
        "sadness",
        "love",
        "surprise"
    ]
    
    def __init__(self) -> None:
        self._model = "bhadresh-savani/albert-base-v2-emotion"
        self.classifier = pipeline(
            "text-classification",
            model=self._model,
            top_k=None,
        )
        self._tokenizer = AutoTokenizer.from_pretrained(self._model)
        self._max_length = 512

    def analize(self, text: str) -> ClassificationResult:
        tokens = self._tokenizer.tokenize(text)
        truncated_tokens = tokens[: self._max_length - 2]
        truncated_text = self._tokenizer.convert_tokens_to_string(truncated_tokens)
        prediction = self.classifier(truncated_text)
        return ClassificationResult(prediction)


Classifier = ClassifierSingleton()
