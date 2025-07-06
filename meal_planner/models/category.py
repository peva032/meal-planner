from enum import Enum


class Category(Enum):
    """
    Enum for ingredient categories with their shopping order values.
    Lower order values appear first in shopping lists.
    """
    VEGETABLES = 1
    BAKERY = 2
    FRIDGE = 3
    DRY_FOOD = 4
    ASIAN = 5
    CANS = 6
    SPICES = 7
    TREATS = 8
    NOT_SURE = 9
    BAKING = 10
    FROZEN = 11
    ORGANIC_STORE = 12
    MEAT_FRIDGE = 14
    ALCOHOL = 15
    OTHER = 16

    @classmethod
    def from_string(cls, category_str: str) -> "Category":
        """Convert a category string to the corresponding Category enum."""
        if not category_str or category_str.strip() == "":
            return cls.NOT_SURE
        
        # Normalize the string (lowercase, replace spaces with underscores)
        normalized = category_str.strip().upper().replace(" ", "_")
        
        # Handle special cases
        if normalized == "MEAT_FRIDGE":
            return cls.MEAT_FRIDGE
        elif normalized == "DRY_FOOD":
            return cls.DRY_FOOD
        elif normalized == "NOT_SURE":
            return cls.NOT_SURE
        elif normalized == "ORGANIC_STORE":
            return cls.ORGANIC_STORE
        
        # Try to match directly
        try:
            return cls[normalized]
        except KeyError:
            # If no match found, default to NOT_SURE
            return cls.NOT_SURE

    @property
    def display_name(self) -> str:
        """Get the display name for the category."""
        return self.name.replace("_", " ").title()
