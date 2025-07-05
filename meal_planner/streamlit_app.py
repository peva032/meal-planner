import streamlit as st
import pandas as pd
from typing import List, Dict, Tuple
import os
from .db import DbClient
from .units import Unit

# Initialize database client
@st.cache_resource
def get_db_client():
    """Get cached database client instance"""
    return DbClient()

def main():
    st.title("🍽️ Meal Planner")
    st.markdown("Plan your meals and generate shopping lists!")
    
    # Get database client
    db = get_db_client()
    
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
        col1, col2, col3, col4 = st.columns([3, 1, 1.5, 1])
        with col1:
            ingredient_name = st.text_input("Ingredient Name", key="ingredient_name")
        with col2:
            quantity = st.number_input("Quantity", min_value=0.0, step=0.1, key="quantity")
        with col3:
            # Get unit options for selectbox
            unit_options = Unit.get_display_options()
            unit_display_names = [option[0] for option in unit_options]
            unit_values = [option[1] for option in unit_options]
            
            # Default to "Gram (g)"
            default_index = unit_values.index(Unit.GRAM.value) if Unit.GRAM.value in unit_values else 0
            
            selected_unit_display = st.selectbox(
                "Unit", 
                options=unit_display_names,
                index=default_index,
                key="unit_select"
            )
            
            # Get the actual unit value from the display name
            selected_index = unit_display_names.index(selected_unit_display)
            unit = unit_values[selected_index]
            
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
                try:
                    if db.add_meal(meal_name, meal_description, st.session_state.ingredients):
                        st.success("Meal added successfully!")
                        st.session_state.ingredients = []
                        st.rerun()
                except Exception as e:
                    st.error(f"Error adding meal: {str(e)}")
            else:
                st.error("Please provide a meal name and at least one ingredient.")
    
    elif page == "Generate Shopping List":
        st.header("Generate Shopping List")
        
        # Get all meals
        meals = db.get_all_meals()
        
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
            shopping_list = db.generate_shopping_list(selected_meal_ids)
            
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
        
        meals = db.get_all_meals()
        
        if not meals:
            st.info("No meals found. Please add some meals first.")
            return
        
        # Display meals
        for meal_id, name, description in meals:
            with st.expander(f"🍽️ {name}"):
                if description:
                    st.markdown(f"**Description:** {description}")
                
                # Get ingredients
                ingredients = db.get_meal_ingredients(meal_id)
                
                if ingredients:
                    st.markdown("**Ingredients:**")
                    for ingredient_name, quantity, unit in ingredients:
                        st.write(f"• {ingredient_name}: {quantity} {unit}")
                else:
                    st.write("No ingredients found.")

if __name__ == "__main__":
    main()
