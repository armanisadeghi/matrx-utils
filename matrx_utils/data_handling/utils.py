import random


def get_random_text_entry():
    words = [
        "apple", "banana", "cherry", "dragon", "elephant",
        "forest", "garden", "horizon", "infinite", "journey",
        "knowledge", "lemon", "mountain", "notebook", "ocean",
        "puzzle", "quality", "rainbow", "sunshine", "technology",
        "umbrella", "victory", "whisper", "xylophone", "yesterday",
        "zebra"
    ]

    return random.choice(words)