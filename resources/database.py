from discord.utils import MISSING
from typing import Any, Generic
from typing import TypeVar, TypedDict
from typing import overload

import json
import sqlite3 as sql

# from models.database import Commands as CommandEntry


T = TypeVar("T")


class Movies:

    def __init__(self):
        self.connection = sql.connect("database/movies/movies.sqlite")

    def __enter__(self):
        return self.connection.cursor()

    def __exit__(self, *_):
        self.connection.commit()
        self.connection.close()



class JSONContextManager(Generic[T]):

    path = "database/"
    file: str

    cache: T

    @classmethod
    def load(cls) -> T:
        with open(cls.path + cls.file) as f:
            return json.load(f)

    def __enter__(self) -> T:
        with open(self.path + self.file) as f:
            self.cache = json.load(f)
            return self.cache

    def __exit__(self, *_) -> None:
        with open(self.path + self.file, "w") as f:
            json.dump(self.cache, f, indent=4)



class WatchList(JSONContextManager[dict[str, list[str]]]):

    file = "movies/watchlist.json"

    @classmethod
    @overload
    def load(cls, requester: int) -> list[str]:
        ...

    @classmethod
    @overload
    def load(cls) -> dict[str, list[str]]:
        ...

    @classmethod
    def load(cls, requester: int = MISSING) -> Any:
        data = super().load()
        if requester is not MISSING:
            return data.get(str(requester), [])
        return data



class CommandEntry(TypedDict):
    command: str
    active: str

class Commands(JSONContextManager[CommandEntry]):

    file = "commands.json"



class Settings(JSONContextManager[dict[str, bool]]):

    file = "settings.json"

    @overload
    @classmethod
    def load(cls, entry: str) -> bool:
        ...
    
    @overload
    @classmethod
    def load(cls, entry: None = None) -> dict[str, bool]:
        ...

    @classmethod
    def load(cls, entry: str | None = None) -> Any:
        with open(cls.path + cls.file) as f:
            if not entry:
                return json.load(f)
            
            return json.load(f)[entry]



class Friendship(JSONContextManager[dict[str, float]]):

    file = "friendship.json"

    @overload
    @classmethod
    def load(cls, user_id: str) -> float:
        ...

    @overload
    @classmethod
    def load(cls, user_id: None = None) -> dict[str, float]:
        ...

    @classmethod
    def load(cls, user_id: str | None = None) -> Any:
        with open(cls.path + cls.file) as f:
            fs = json.load(f)

            if (not user_id):
                return fs

            if (user_id not in fs):
                return 0
            
            return fs[user_id]



class Triggers(JSONContextManager[list[str]]):

    file = "triggers.json"


def monke(monke: str):
    with open("database/monkes.json") as f:
        data = json.load(f)
    return data[monke]