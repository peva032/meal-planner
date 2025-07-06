from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy import func
from typing import List, Optional
from .models import Ingredient, Meal, MealIngredient, Unit, Category


class DbClient:
    """Database client for meal planner application using SQLModel and SQLite"""
    
    def __init__(self, db_path: str = "meal_planner.db"):
        self.db_path = db_path
        # Create SQLite engine with proper file path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.init_database()
    
    def init_database(self):
        """Initialize the database with SQLModel tables"""
        # Create all tables defined in the models
        SQLModel.metadata.create_all(self.engine)
    
    def add_meal(self, name: str, description: Optional[str] = None,
                 recipe_link: Optional[str] = None, notes: Optional[str] = None,
                 ingredients: Optional[List[tuple]] = None) -> int:
        """Add a new meal with optional ingredients, returns meal ID"""
        with Session(self.engine) as session:
            # Check if meal already exists (case-insensitive)
            existing_meal = session.exec(
                select(Meal).where(func.lower(Meal.name) == func.lower(name))
            ).first()
            
            if existing_meal:
                print(f"Meal '{name}' already exists (ID: {existing_meal.id}), skipping...")
                return existing_meal.id
            
            # Create and add meal
            meal = Meal(
                name=name, 
                description=description,
                recipe_link=recipe_link,
                notes=notes
            )
            session.add(meal)
            session.commit()
            session.refresh(meal)
            meal_id = meal.id
            
            # Add ingredients if provided
            if ingredients:
                for ingredient_tuple in ingredients:
                    # Handle both 3-tuple (name, quantity, unit) and 4-tuple (name, quantity, unit, category)
                    if len(ingredient_tuple) == 3:
                        ingredient_name, quantity, unit = ingredient_tuple
                        category = None
                    elif len(ingredient_tuple) == 4:
                        ingredient_name, quantity, unit, category = ingredient_tuple
                    else:
                        raise ValueError(f"Invalid ingredient tuple: {ingredient_tuple}")
                    
                    # Find or create ingredient (case-insensitive)
                    ingredient = session.exec(
                        select(Ingredient).where(func.lower(Ingredient.name) == func.lower(ingredient_name))
                    ).first()
                    
                    if not ingredient:
                        ingredient = Ingredient(
                            name=ingredient_name,
                            category=category if category else "NOT_SURE"
                        )
                        session.add(ingredient)
                        session.commit()
                        session.refresh(ingredient)
                    
                    # Check if this meal-ingredient relationship already exists
                    existing_relationship = session.exec(
                        select(MealIngredient).where(
                            MealIngredient.meal_id == meal.id,
                            MealIngredient.ingredient_id == ingredient.id
                        )
                    ).first()
                    
                    if existing_relationship:
                        print(f"Ingredient '{ingredient_name}' already linked to meal '{name}', skipping...")
                        continue
                    
                    # Create meal-ingredient relationship
                    # Convert unit to string if it's an enum
                    if isinstance(unit, Unit):
                        unit_str = unit.value
                    else:
                        unit_str = unit
                    
                    meal_ingredient = MealIngredient(
                        meal_id=meal.id,
                        ingredient_id=ingredient.id,
                        quantity=quantity,
                        unit=unit_str
                    )
                    session.add(meal_ingredient)
                
                session.commit()
            
            return meal_id
    
    def get_all_meals(self) -> List[Meal]:
        """Get all meals from the database"""
        with Session(self.engine) as session:
            statement = select(Meal).order_by(Meal.name)
            meals = session.exec(statement).all()
            return list(meals)
    
    def get_meal_by_id(self, meal_id: int) -> Optional[dict]:
        """Get a specific meal by ID"""
        with Session(self.engine) as session:
            meal = session.get(Meal, meal_id)
            if meal:
                return {
                    'id': meal.id,
                    'name': meal.name,
                    'description': meal.description,
                    'recipe_link': meal.recipe_link,
                    'notes': meal.notes,
                    'created_at': meal.created_at,
                    'updated_at': meal.updated_at
                }
            return None
    
    def get_meal_ingredients(self, meal_id: int) -> List[MealIngredient]:
        """Get ingredients for a specific meal with ingredient details"""
        with Session(self.engine) as session:
            statement = (
                select(MealIngredient)
                .join(Ingredient)
                .where(MealIngredient.meal_id == meal_id)
                .order_by(MealIngredient.id)
            )
            meal_ingredients = session.exec(statement).all()
            
            # Force loading of ingredient relationships
            result = []
            for mi in meal_ingredients:
                # Create a detached copy with ingredient name loaded
                ingredient_name = mi.ingredient.name
                result.append({
                    'id': mi.id,
                    'quantity': mi.quantity,
                    'unit': mi.unit,
                    'notes': mi.notes,
                    'ingredient_name': ingredient_name
                })
            
            return result
    
    def delete_meal(self, meal_id: int) -> bool:
        """Delete a meal and its ingredient associations"""
        with Session(self.engine) as session:
            meal = session.get(Meal, meal_id)
            if not meal:
                return False
            
            # Delete meal ingredients first
            meal_ingredients = session.exec(
                select(MealIngredient).where(MealIngredient.meal_id == meal_id)
            ).all()
            
            for meal_ingredient in meal_ingredients:
                session.delete(meal_ingredient)
            
            # Delete the meal
            session.delete(meal)
            session.commit()
            return True
    
    def get_all_ingredients(self) -> List[Ingredient]:
        """Get all ingredients from the database"""
        with Session(self.engine) as session:
            statement = select(Ingredient).order_by(Ingredient.name)
            return list(session.exec(statement).all())
    
    def update_meal(self, meal_id: int, name: str, description: Optional[str] = None,
                   recipe_link: Optional[str] = None, notes: Optional[str] = None,
                   ingredients: Optional[List[tuple]] = None) -> bool:
        """Update an existing meal"""
        with Session(self.engine) as session:
            meal = session.get(Meal, meal_id)
            if not meal:
                return False
            
            # Update meal details
            meal.name = name
            meal.description = description
            meal.recipe_link = recipe_link
            meal.notes = notes
            
            # Delete existing meal ingredients
            existing_ingredients = session.exec(
                select(MealIngredient).where(MealIngredient.meal_id == meal_id)
            ).all()
            
            for meal_ingredient in existing_ingredients:
                session.delete(meal_ingredient)
            
            # Add updated ingredients
            if ingredients:
                for ingredient_tuple in ingredients:
                    # Handle both 3-tuple (name, quantity, unit) and 4-tuple (name, quantity, unit, category)
                    if len(ingredient_tuple) == 3:
                        ingredient_name, quantity, unit = ingredient_tuple
                        category = None
                    elif len(ingredient_tuple) == 4:
                        ingredient_name, quantity, unit, category = ingredient_tuple
                    else:
                        raise ValueError(f"Invalid ingredient tuple: {ingredient_tuple}")
                    
                    # Find or create ingredient (case-insensitive)
                    ingredient = session.exec(
                        select(Ingredient).where(func.lower(Ingredient.name) == func.lower(ingredient_name))
                    ).first()
                    
                    if not ingredient:
                        ingredient = Ingredient(
                            name=ingredient_name,
                            category=category if category else "NOT_SURE"
                        )
                        session.add(ingredient)
                        session.commit()
                        session.refresh(ingredient)
                    
                    # Create meal-ingredient relationship
                    # Convert unit to string if it's an enum
                    if isinstance(unit, Unit):
                        unit_str = unit.value
                    else:
                        unit_str = unit
                    
                    meal_ingredient = MealIngredient(
                        meal_id=meal.id,
                        ingredient_id=ingredient.id,
                        quantity=quantity,
                        unit=unit_str
                    )
                    session.add(meal_ingredient)
            
            session.commit()
            return True
    
    def cleanup_unused_ingredients(self) -> int:
        """Remove ingredients that are not used in any meals"""
        with Session(self.engine) as session:
            # Find ingredients not referenced in meal_ingredients
            statement = (
                select(Ingredient)
                .where(
                    Ingredient.id.notin_(
                        select(MealIngredient.ingredient_id).distinct()
                    )
                )
            )
            
            unused_ingredients = session.exec(statement).all()
            count = len(unused_ingredients)
            
            for ingredient in unused_ingredients:
                session.delete(ingredient)
            
            session.commit()
            return count
    
    def generate_shopping_list(self, meal_ids: List[int]) -> List[tuple]:
        """Generate an aggregated shopping list for selected meals with category information"""
        if not meal_ids:
            return []
        
        with Session(self.engine) as session:
            # Get all meal ingredients for the selected meals with ingredient details
            statement = (
                select(MealIngredient, Ingredient)
                .join(Ingredient, MealIngredient.ingredient_id == Ingredient.id)
                .where(MealIngredient.meal_id.in_(meal_ids))
            )
            
            results = session.exec(statement).all()
            
            # Aggregate ingredients by name, unit, and category
            ingredient_totals = {}
            
            for meal_ingredient, ingredient in results:
                key = (ingredient.name, meal_ingredient.unit, ingredient.category)
                if key in ingredient_totals:
                    ingredient_totals[key] += meal_ingredient.quantity
                else:
                    ingredient_totals[key] = meal_ingredient.quantity
            
            # Convert to list of tuples with category information
            shopping_list = [
                (name, quantity, unit, category)
                for (name, unit, category), quantity in ingredient_totals.items()
            ]
            
            # Sort by category enum value, then by ingredient name
            def get_category_order(item):
                name, quantity, unit, category_str = item
                try:
                    category = Category.from_string(category_str)
                    return (category.value, name.lower())
                except:
                    return (Category.NOT_SURE.value, name.lower())
            
            shopping_list.sort(key=get_category_order)
            
            return shopping_list
