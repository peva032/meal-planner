from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, String, Text, UniqueConstraint, func
from .category import Category
from .units import Unit


class Ingredient(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint('name', name='uq_ingredient_name_case_insensitive'),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String, nullable=False, index=True))
    category: str = Field(default=Category.NOT_SURE.name)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    meal_ingredients: List["MealIngredient"] = Relationship(back_populates="ingredient")


class Meal(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint('name', name='uq_meal_name_case_insensitive'),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String, nullable=False, index=True))
    description: Optional[str] = None
    recipe_link: Optional[str] = None
    notes: Optional[str] = Field(sa_column=Column(Text), default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    meal_ingredients: List["MealIngredient"] = Relationship(back_populates="meal")


class MealIngredient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    meal_id: int = Field(foreign_key="meal.id")
    ingredient_id: int = Field(foreign_key="ingredient.id")
    quantity: float
    unit: str = Field(default=Unit.ITEM.value)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    meal: Meal = Relationship(back_populates="meal_ingredients")
    ingredient: Ingredient = Relationship(back_populates="meal_ingredients")
