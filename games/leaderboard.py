from typing import Any

import json

class Leaderboard:

    path = "games/_/leaderboard.json"

    cache: Any

    def __init__(self, game: str):
        self.path.replace("_", game)

    @classmethod
    def load(cls, game: str):
        path = cls.path.replace("_", game)
        with open(path) as f:
            return json.load(f)

    def __enter__(self):
        with open(self.path) as f:
            self.cache = json.load(f)

        return self.cache

    def __exit__(self, *_):
        with open(self.cache, "w") as f:
            json.dump(self.cache, f, indent=4)