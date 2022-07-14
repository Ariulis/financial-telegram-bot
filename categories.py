from typing import Dict, List, NamedTuple

import db


class Category(NamedTuple):
    """Category structure"""
    codename: str
    name: str
    is_base_expense: bool
    aliases: List[str]


class Categories:
    def __init__(self) -> None:
        self.categories = self._load_categories()

    def _load_categories(self) -> List[Category]:
        """Return a dictionary of expenses categories from DB"""
        categories = ''
