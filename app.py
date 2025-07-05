import streamlit as st
import duckdb
import pandas as pd
from typing import List, Dict, Tuple
import os

# Initialize database
DB_PATH = "meal_planner.db"

def init_database():
    """Initialize the DuckDB database with required tables"""
    conn = duckdb.connect(DB_PATH)
    
    # Create meals table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL,
            description TEXT
        )
    """)
    
    # Create ingredients table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL,
            unit VARCHAR NOT NULL DEFAULT 'unit'
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
    
    conn.close()

def get_connection():
    """Get a connection to the database"""
    return duckdb.connect(DB_PATH)

def add_meal(name: str, description: str, ingredients: List[Tuple[str, float, str]]):
    """Add a new meal with its ingredients"""
    conn = get_connection()
    
    try:
        conn.execute("BEGIN TRANSACTION")
        
        # Insert meal
        conn.execute("INSERT INTO meals (name, description) VALUES (?, ?)", 
                    (name, description))
        meal_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        
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
        st.error(f"Error adding meal: {str(e)}")
        return False
    finally:
        conn.close()

def get_all_meals():
    """Get all meals from the database"""
    conn = get_connection()
    result = conn.execute("SELECT id, name, description FROM meals ORDER BY name").fetchall()
    conn.close()
    return result

def get_meal_ingredients(meal_id: int):
    """Get ingredients for a specific meal"""
    conn = get_connection()
    result = conn.execute("""
        SELECT i.name, mi.quantity, i.unit
        FROM meal_ingredients mi
        JOIN ingredients i ON mi.ingredient_id = i.id
        WHERE mi.meal_id = ?
        ORDER BY i.name
    """, (meal_id,)).fetchall()
    conn.close()
    return result

def generate_shopping_list(meal_ids: List[int]):
    """Generate an aggregated shopping list for selected meals"""
    conn = get_connection()
    
    # Get aggregated ingredients
    result = conn.execute("""
        SELECT i.name, SUM(mi.quantity) as total_quantity, i.unit
        FROM meal_ingredients mi
        JOIN ingredients i ON mi.ingredient_id = i.id
        WHERE mi.meal_id IN ({})
        GROUP BY i.name, i.unit
        ORDER BY i.name
    """.format(','.join('?' * len(meal_ids))), meal_ids).fetchall()
    
    conn.close()
    return result

def main():
    st.title("🍽️ Meal Planner")
    st.markdown("Plan your meals and generate shopping lists!")
    
    # Initialize database
    init_database()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Add Meal", "Generate Shopping List", "View Meals"])
    
    if page == "Add Meal":
        st.header("Add New Meal")
        
        # Meal details
        meal_name = st.text_input("Meal Name")
        meal_description = st.text_area("Description (optional)")
        
        st.subheader("Ingredients")
        
        # Initialize session state for ingredients
        if 'ingredients' not in st.session_state:
            st.session_state.ingredients = []
        
        # Add ingredient form
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            ingredient_name = st.text_input("Ingredient Name", key="ingredient_name")
        with col2:
            quantity = st.number_input("Quantity", min_value=0.0, step=0.1, key="quantity")
        with col3:
            unit = st.text_input("Unit", value="unit", key="unit")
        with col4:
            if st.button("Add Ingredient"):
                if ingredient_name and quantity > 0:
                    st.session_state.ingredients.append((ingredient_name, quantity, unit))
                    st.rerun()
        
        # Display current ingredients
        if st.session_state.ingredients:
            st.subheader("Current Ingredients")
            for i, (name, qty, unit) in enumerate(st.session_state.ingredients):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"{name}: {qty} {unit}")
                with col2:
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.ingredients.pop(i)
                        st.rerun()
        
        # Save meal
        if st.button("Save Meal"):
            if meal_name and st.session_state.ingredients:
                if add_meal(meal_name, meal_description, st.session_state.ingredients):
                    st.success("Meal added successfully!")
                    st.session_state.ingredients = []
                    st.rerun()
            else:
                st.error("Please provide a meal name and at least one ingredient.")
    
    elif page == "Generate Shopping List":
        st.header("Generate Shopping List")
        
        # Get all meals
        meals = get_all_meals()
        
        if not meals:
            st.info("No meals found. Please add some meals first.")
            return
        
        # Meal selection
        meal_options = {f"{meal[1]}": meal[0] for meal in meals}
        selected_meals = st.multiselect(
            "Select meals for your shopping list",
            options=list(meal_options.keys()),
            default=[]
        )
        
        if selected_meals:
            selected_meal_ids = [meal_options[meal] for meal in selected_meals]
            
            # Generate shopping list
            shopping_list = generate_shopping_list(selected_meal_ids)
            
            if shopping_list:
                st.subheader("Shopping List")
                
                # Create DataFrame for better display
                df = pd.DataFrame(shopping_list, columns=['Ingredient', 'Quantity', 'Unit'])
                df['Quantity'] = df['Quantity'].round(2)
                
                st.dataframe(df, use_container_width=True)
                
                # Download as CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Shopping List as CSV",
                    data=csv,
                    file_name=f"shopping_list_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No ingredients found for selected meals.")
    
    elif page == "View Meals":
        st.header("All Meals")
        
        meals = get_all_meals()
        
        if not meals:
            st.info("No meals found. Please add some meals first.")
            return
        
        # Display meals
        for meal_id, name, description in meals:
            with st.expander(f"🍽️ {name}"):
                if description:
                    st.markdown(f"**Description:** {description}")
                
                # Get ingredients
                ingredients = get_meal_ingredients(meal_id)
                
                if ingredients:
                    st.markdown("**Ingredients:**")
                    for ingredient_name, quantity, unit in ingredients:
                        st.write(f"• {ingredient_name}: {quantity} {unit}")
                else:
                    st.write("No ingredients found.")

if __name__ == "__main__":
    main()
