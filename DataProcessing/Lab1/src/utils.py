import random


def generate_name():
    syllables = [
        "ka",
        "ki",
        "ku",
        "ke",
        "ko",
        "sa",
        "shi",
        "su",
        "se",
        "so",
        "ta",
        "chi",
        "tsu",
        "te",
        "to",
        "na",
        "ni",
        "nu",
        "ne",
        "no",
        "ha",
        "hi",
        "fu",
        "he",
        "ho",
        "ma",
        "mi",
        "mu",
        "me",
        "mo",
        "ya",
        "yu",
        "yo",
        "wa",
        "ra",
        "ri",
        "ru",
        "re",
        "ro",
    ]

    number_of_syllables = random.randint(2, 5)

    name = ""
    for _ in range(number_of_syllables):
        name += syllables[random.randint(0, len(syllables) - 1)]
    return name
