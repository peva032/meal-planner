from enum import Enum


class Unit(Enum):
    """Standard metric units for meal planning ingredients"""
    
    # Weight/Mass
    GRAM = "g"
    KILOGRAM = "kg"
    
    # Volume - Liquid
    MILLILITRE = "ml"
    LITRE = "l"
    
    # Volume - Cooking measurements
    TEASPOON = "tsp"
    TABLESPOON = "tbsp"
    CUP = "cup"
    
    # Count/Pieces
    PIECE = "piece"
    PIECES = "pieces"
    CLOVE = "clove"
    CLOVES = "cloves"
    
    # Length (for things like pasta, vegetables)
    CENTIMETRE = "cm"
    
    # Special cooking units
    PINCH = "pinch"
    DASH = "dash"
    
    # Package/Container units
    CAN = "can"
    JAR = "jar"
    BOTTLE = "bottle"
    PACKET = "packet"
    BAG = "bag"
    
    # Fresh produce units
    HEAD = "head"  # lettuce, cabbage
    BUNCH = "bunch"  # herbs, green onions
    STALK = "stalk"  # celery
    LEAF = "leaf"  # bay leaves
    LEAVES = "leaves"
    
    def __str__(self):
        return self.value
    
    @classmethod
    def get_display_options(cls):
        """Get a list of (display_name, value) tuples for UI display"""
        return [
            # Weight/Mass
            ("Gram (g)", cls.GRAM.value),
            ("Kilogram (kg)", cls.KILOGRAM.value),
            
            # Volume - Liquid
            ("Millilitre (ml)", cls.MILLILITRE.value),
            ("Litre (l)", cls.LITRE.value),
            
            # Volume - Cooking
            ("Teaspoon (tsp)", cls.TEASPOON.value),
            ("Tablespoon (tbsp)", cls.TABLESPOON.value),
            ("Cup", cls.CUP.value),
            
            # Count/Pieces
            ("Piece", cls.PIECE.value),
            ("Pieces", cls.PIECES.value),
            ("Clove", cls.CLOVE.value),
            ("Cloves", cls.CLOVES.value),
            
            # Length
            ("Centimetre (cm)", cls.CENTIMETRE.value),
            
            # Special
            ("Pinch", cls.PINCH.value),
            ("Dash", cls.DASH.value),
            
            # Containers
            ("Can", cls.CAN.value),
            ("Jar", cls.JAR.value),
            ("Bottle", cls.BOTTLE.value),
            ("Packet", cls.PACKET.value),
            ("Bag", cls.BAG.value),
            
            # Fresh produce
            ("Head", cls.HEAD.value),
            ("Bunch", cls.BUNCH.value),
            ("Stalk", cls.STALK.value),
            ("Leaf", cls.LEAF.value),
            ("Leaves", cls.LEAVES.value),
        ]
    
    @classmethod
    def get_values_list(cls):
        """Get a simple list of all unit values"""
        return [unit.value for unit in cls]
