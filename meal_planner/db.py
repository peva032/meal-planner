import duckdb
from typing import List, Tuple, Optional
import os
from .units import Unit


class DbClient:
    """Database client for meal planner application using DuckDB"""
    
    def __init__(self, db_path: str = "meal_planner.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get a connection to the database"""
        return duckdb.connect(self.db_path)
    
    def init_database(self):
        """Initialize the DuckDB database with required tables"""
        conn = self.get_connection()
        
        try:
            # Create sequences
            conn.execute("CREATE SEQUENCE IF NOT EXISTS meals_id_seq START 1")
            conn.execute("CREATE SEQUENCE IF NOT EXISTS ingredients_id_seq START 1")
            
            # Create meals table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS meals (
                    id INTEGER PRIMARY KEY DEFAULT nextval('meals_id_seq'),
                    name VARCHAR UNIQUE NOT NULL,
                    description TEXT
                )
            """)
            
            # Create ingredients table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ingredients (
                    id INTEGER PRIMARY KEY DEFAULT nextval('ingredients_id_seq'),
                    name VARCHAR UNIQUE NOT NULL,
                    unit VARCHAR NOT NULL DEFAULT 'piece'
                )
            """)
            
            # Create meal_ingredients junction table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS meal_ingredients (
                    meal_id INTEGER,
                    ingredient_id INTEGER,
                    quantity DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (meal_id) REFERENCES meals(id),
                    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
                    PRIMARY KEY (meal_id, ingredient_id)
                )
            """)
        finally:
            conn.close()
    
    def add_meal(self, name: str, description: str, ingredients: List[Tuple[str, float, str]]) -> bool:
        """Add a new meal with its ingredients"""
        conn = self.get_connection()
        
        try:
            conn.execute("BEGIN TRANSACTION")
            
            # Insert meal and get the ID
            result = conn.execute("INSERT INTO meals (name, description) VALUES (?, ?) RETURNING id", 
                        (name, description))
            meal_id = result.fetchone()[0]
            
            # Insert ingredients and link to meal
            for ingredient_name, quantity, unit in ingredients:
                # Insert ingredient if it doesn't exist
                conn.execute("""
                    INSERT INTO ingredients (name, unit) 
                    VALUES (?, ?) 
                    ON CONFLICT (name) DO UPDATE SET unit = EXCLUDED.unit
                """, (ingredient_name, unit))
                
                # Get ingredient ID
                ingredient_id = conn.execute(
                    "SELECT id FROM ingredients WHERE name = ?", 
                    (ingredient_name,)
                ).fetchone()[0]
                
                # Link meal and ingredient
                conn.execute("""
                    INSERT INTO meal_ingredients (meal_id, ingredient_id, quantity)
                    VALUES (?, ?, ?)
                """, (meal_id, ingredient_id, quantity))
            
            conn.execute("COMMIT")
            return True
            
        except Exception as e:
            conn.execute("ROLLBACK")
            raise e
        finally:
            conn.close()
    
    def get_all_meals(self) -> List[Tuple[int, str, str]]:
        """Get all meals from the database"""
        conn = self.get_connection()
        try:
            result = conn.execute("SELECT id, name, description FROM meals ORDER BY name").fetchall()
            return result
        finally:
            conn.close()
    
    def get_meal_by_id(self, meal_id: int) -> Optional[Tuple[int, str, str]]:
        """Get a specific meal by ID"""
        conn = self.get_connection()
        try:
            result = conn.execute(
                "SELECT id, name, description FROM meals WHERE id = ?", 
                (meal_id,)
            ).fetchone()
            return result
        finally:
            conn.close()
    
    def get_meal_ingredients(self, meal_id: int) -> List[Tuple[str, float, str]]:
        """Get ingredients for a specific meal"""
        conn = self.get_connection()
        try:
            result = conn.execute("""
                SELECT i.name, mi.quantity, i.unit
                FROM meal_ingredients mi
                JOIN ingredients i ON mi.ingredient_id = i.id
                WHERE mi.meal_id = ?
                ORDER BY i.name
            """, (meal_id,)).fetchall()
            return result
        finally:
            conn.close()
    
    def generate_shopping_list(self, meal_ids: List[int]) -> List[Tuple[str, float, str]]:
        """Generate an aggregated shopping list for selected meals"""
        if not meal_ids:
            return []
        
        conn = self.get_connection()
        try:
            # Get aggregated ingredients
            result = conn.execute("""
                SELECT i.name, SUM(mi.quantity) as total_quantity, i.unit
                FROM meal_ingredients mi
                JOIN ingredients i ON mi.ingredient_id = i.id
                WHERE mi.meal_id IN ({})
                GROUP BY i.name, i.unit
                ORDER BY i.name
            """.format(','.join('?' * len(meal_ids))), meal_ids).fetchall()
            
            return result
        finally:
            conn.close()
    
    def delete_meal(self, meal_id: int) -> bool:
        """Delete a meal and its ingredient associations"""
        conn = self.get_connection()
        try:
            conn.execute("BEGIN TRANSACTION")
            
            # Delete meal ingredients first (foreign key constraint)
            conn.execute("DELETE FROM meal_ingredients WHERE meal_id = ?", (meal_id,))
            
            # Delete the meal
            result = conn.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
            
            conn.execute("COMMIT")
            return result.rowcount > 0
            
        except Exception as e:
            conn.execute("ROLLBACK")
            raise e
        finally:
            conn.close()
    
    def update_meal(self, meal_id: int, name: str, description: str, 
                   ingredients: List[Tuple[str, float, str]]) -> bool:
        """Update an existing meal"""
        conn = self.get_connection()
        try:
            conn.execute("BEGIN TRANSACTION")
            
            # Update meal details
            conn.execute(
                "UPDATE meals SET name = ?, description = ? WHERE id = ?",
                (name, description, meal_id)
            )
            
            # Delete existing meal ingredients
            conn.execute("DELETE FROM meal_ingredients WHERE meal_id = ?", (meal_id,))
            
            # Insert updated ingredients
            for ingredient_name, quantity, unit in ingredients:
                # Insert ingredient if it doesn't exist
                conn.execute("""
                    INSERT INTO ingredients (name, unit) 
                    VALUES (?, ?) 
                    ON CONFLICT (name) DO UPDATE SET unit = EXCLUDED.unit
                """, (ingredient_name, unit))
                
                # Get ingredient ID
                ingredient_id = conn.execute(
                    "SELECT id FROM ingredients WHERE name = ?", 
                    (ingredient_name,)
                ).fetchone()[0]
                
                # Link meal and ingredient
                conn.execute("""
                    INSERT INTO meal_ingredients (meal_id, ingredient_id, quantity)
                    VALUES (?, ?, ?)
                """, (meal_id, ingredient_id, quantity))
            
            conn.execute("COMMIT")
            return True
            
        except Exception as e:
            conn.execute("ROLLBACK")
            raise e
        finally:
            conn.close()
    
    def get_all_ingredients(self) -> List[Tuple[int, str, str]]:
        """Get all ingredients from the database"""
        conn = self.get_connection()
        try:
            result = conn.execute("SELECT id, name, unit FROM ingredients ORDER BY name").fetchall()
            return result
        finally:
            conn.close()
    
    def cleanup_unused_ingredients(self):
        """Remove ingredients that are not used in any meals"""
        conn = self.get_connection()
        try:
            conn.execute("""
                DELETE FROM ingredients 
                WHERE id NOT IN (
                    SELECT DISTINCT ingredient_id 
                    FROM meal_ingredients
                )
            """)
            return conn.rowcount
        finally:
            conn.close()
