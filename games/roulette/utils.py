from dataclasses import dataclass
from typing import Literal

import json
import random


Color = Literal["red", "black", "green"]


class Tiles(dict[str, Color]):

    path = "./tiles.json"

    @classmethod
    def load(cls):
        with open(cls.path) as f:
            x: dict[str, Color] = json.load(f)

        return cls(x)

    @classmethod
    def load_color(cls, color: Color):
        x = cls.load()
        for k, v in x.items():
            if (v != color):
                del x[k]
        return list(x.keys())

    @classmethod
    def get_color(cls, num: int | str) -> Color:
        with open(cls.path) as f:
            x: dict[str, Color] = json.load(f)

        return x[str(num)]


@dataclass
class Entry:
    number: str
    color: Color

    def __eq__(self, __o: object):
        return isinstance(__o, self.__class__) and __o.number == self.number and __o.color == self.color

    @classmethod
    def random(cls):
        tiles = Tiles.load()
        couple = random.choice(tuple(tiles.items()))
        return cls(*couple)
