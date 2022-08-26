import json
import sqlite3 as sql



COMMANDS_PATH = 'database/commands.json'
FRIENDSHIP_PATH = 'database/friendship.json'
SETTINGS_PATH = 'database/settings.json'

TRIGGERS_PATH = 'database/triggers.json'


class Movies:

    def __init__(self):
        self.connection = sql.connect('database/movies/movies.sqlite')

    def __enter__(self):
        return self.connection.cursor()

    def __exit__(self, *args):
        self.connection.commit()
        self.connection.close()


class WatchList:

    path = 'database/movies/watchlist.json'

    cache: dict[int, list[str]]


    def __enter__(self) -> dict[int, list[str]]:
        with open(self.path) as f:
            self.cache = json.load(f)
            return self.cache

    def __exit__(self, *args):
        with open(self.path, 'w') as f:
            json.dump(self.cache, f, indent=4)



def commands() -> dict[str, bool]:
    with open(COMMANDS_PATH) as f:
        c = json.load(f)
    return c

def edit_commands(obj: dict[str, bool]) -> None:
    with open(COMMANDS_PATH, 'w') as f:
        json.dump(obj, f, indent=4)

def settings() -> dict[str, bool]:
    with open(SETTINGS_PATH) as f:
        s = json.load(f)
    return s

def edit_settings(obj: dict[str, bool]) -> None:
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(obj, f, indent=4)

def friendship() -> dict[str, float]:
    with open(FRIENDSHIP_PATH) as fd:
        f = json.load(fd)
    return f

def edit_friendship(obj: dict[str, float]) -> None:
    with open(FRIENDSHIP_PATH, 'w') as f:
        json.dump(obj, f, indent=4)


def triggers() -> list[str]:
    with open(TRIGGERS_PATH) as f:
        t = json.load(f)
    return t

def edit_trigger(obj: dict[str, int]) -> None:
    with open(TRIGGERS_PATH, 'w') as f:
        json.dump(obj, f, indent=4)