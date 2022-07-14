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
        self._categories = self._load_categories()

    def _load_categories(self) -> List[Category]:
        """Return a dictionary of expenses categories from DB"""
        categories = db.fetch_all(
            'category', 'codename name is_base_expense aliases'.split()
        )
        return self._fill_aliases(categories)

    def _fill_aliases(self, categories: List[Dict]) -> List[Category]:
        """Fill in aliases on each of the category"""
        categories_result = []
        for category in categories:
            aliases = category['aliases'].split(',')
            aliases = list(filter(None, map(str.strip, aliases)))
            aliases.append(category['codename'])
            aliases.append(category['name'])
            categories_result.append(Category(
                codename=category['codename'],
                name=category['name'],
                is_base_expense=category['is_base_expense'],
                aliases=aliases
            ))

        return categories_result

    def get_all_categories(self) -> List[Dict]:
        """Returns a dictionary of categories"""
        return self._categories

    def get_category(self, category_name: str) -> Category:
        """Returns a category by one of its aliases"""
        found = None
        another_category = None
        for category in self._categories:
            if category.codename == 'other':
                another_category = category
            for alias in category.aliases:
                if category_name in alias:
                    found = category
        if not found:
            found = another_category

        return found
