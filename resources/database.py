from typing import overload

import json
import sqlite3 as sql



class Movies:

    def __init__(self):
        self.connection = sql.connect("database/movies/movies.sqlite")

    def __enter__(self):
        return self.connection.cursor()

    def __exit__(self, *args):
        self.connection.commit()
        self.connection.close()


class WatchList:

    path = "database/movies/watchlist.json"

    cache: dict[str, list[str]]

    @classmethod
    def load(cls) -> dict[str, list[str]]:
        with open(cls.path) as f:
            return json.load(f)

    def __enter__(self) -> dict[str, list[str]]:
        with open(self.path) as f:
            self.cache = json.load(f)
            return self.cache

    def __exit__(self, *args):
        with open(self.path, "w") as f:
            json.dump(self.cache, f, indent=4)

class Commands:

    path = "database/commands.json"

    cache: dict[str, bool]

    @classmethod
    def load(cls) -> dict[str, bool]:
        with open(cls.path) as f:
            return json.load(f)

    def __enter__(self) -> dict[str, bool]:
        with open(self.path) as f:
            self.cache = json.load(f)
            return self.cache

    def __exit__(self, *_):
        with open(self.path, "w") as f:
            json.dump(self.cache, f, indent=4)

class Settings:

    path = "database/settings.json"

    cache: dict[str, bool]

    @overload
    @classmethod
    def load(cls, entry: str) -> bool:
        ...
    
    @overload
    @classmethod
    def load(cls, entry: None = None) -> dict[str, bool]:
        ...

    @classmethod
    def load(cls, entry: str | None = None):
        with open(cls.path) as f:
            if not entry:
                return json.load(f)
            
            return json.load(f)[entry]
            

    def __enter__(self) -> dict[str, bool]:
        with open(self.path) as f:
            self.cache = json.load(f)
            return self.cache

    def __exit__(self, *_):
        with open(self.path, "w") as f:
            json.dump(self.cache, f, indent=4)

class Friendship:

    path = "database/friendship.json"

    cache: dict[str, float]

    @overload
    @classmethod
    def load(cls, user_id: str) -> float:
        ...

    @overload
    @classmethod
    def load(cls, user_id: None = None) -> dict[str, float]:
        ...

    @classmethod
    def load(cls, user_id: str | None = None):
        with open(cls.path) as f:
            fs = json.load(f)

            if (not user_id):
                return fs

            if (user_id not in fs):
                return 0
            
            return fs[user_id]


    def __enter__(self) -> dict[str, float]:
        with open(self.path) as f:
            self.cache = json.load(f)
        return self.cache

    def __exit__(self, *_):
        with open(self.path, "w") as f:
            json.dump(self.cache, f, indent=4)

class Triggers:

    path = "database/triggers.json"

    cache: list[str]

    @classmethod
    def load(cls) -> list[str]:
        with open(cls.path) as f:
            return json.load(f)

    def __enter__(self) -> list[str]:
        with open(self.path) as f:
            self.cache = json.load(f)
        return self.cache

    def __exit__(self, *_):
        with open(self.path, "w") as f:
            json.dump(self.cache, f, indent=4)
