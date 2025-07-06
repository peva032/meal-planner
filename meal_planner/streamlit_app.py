import streamlit as st
import pandas as pd
from typing import List, Dict, Tuple
import os
from .db import DbClient
from .models import Unit, Category

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
        st.header("Add/Edit Meal")
        
        # Mode selection
        mode = st.radio(
            "Choose action:",
            ["Add New Meal", "Edit Existing Meal"],
            horizontal=True
        )
        
        # Initialize variables
        selected_meal_id = None
        meal_name = ""
        meal_description = ""
        meal_recipe_link = ""
        meal_notes = ""
        
        if mode == "Edit Existing Meal":
            # Get all meals for selection
            meals = db.get_all_meals()
            if meals:
                meal_options = {meal.name: meal.id for meal in meals}
                selected_meal_name = st.selectbox(
                    "Select meal to edit:",
                    options=list(meal_options.keys())
                )
                
                if selected_meal_name:
                    selected_meal_id = meal_options[selected_meal_name]
                    # Get meal details
                    meal_data = db.get_meal_by_id(selected_meal_id)
                    if meal_data:
                        meal_name = meal_data['name']
                        meal_description = meal_data['description'] or ""
                        meal_recipe_link = meal_data['recipe_link'] or ""
                        meal_notes = meal_data['notes'] or ""
                        
                        # Load existing ingredients into session state
                        if 'editing_meal_id' not in st.session_state or st.session_state.editing_meal_id != selected_meal_id:
                            st.session_state.editing_meal_id = selected_meal_id
                            existing_ingredients = db.get_meal_ingredients(selected_meal_id)
                            # Load ingredients with category information
                            st.session_state.ingredients = []
                            for ing in existing_ingredients:
                                # Get ingredient from database to fetch category
                                all_ingredients = db.get_all_ingredients()
                                ingredient_category = None
                                for db_ing in all_ingredients:
                                    if db_ing.name.lower() == ing['ingredient_name'].lower():
                                        ingredient_category = db_ing.category
                                        break
                                
                                if ingredient_category:
                                    st.session_state.ingredients.append((
                                        ing['ingredient_name'], 
                                        float(ing['quantity']), 
                                        ing['unit'],
                                        ingredient_category
                                    ))
                                else:
                                    # Fallback for ingredients without category
                                    st.session_state.ingredients.append((
                                        ing['ingredient_name'], 
                                        float(ing['quantity']), 
                                        ing['unit'],
                                        Category.NOT_SURE.name
                                    ))
            else:
                st.info("No meals found. Please add a meal first.")
                st.stop()
        else:
            # Reset editing state when switching to add mode
            if 'editing_meal_id' in st.session_state:
                del st.session_state.editing_meal_id
                st.session_state.ingredients = []
        
        # Meal details form
        st.subheader("Meal Details")
        meal_name = st.text_input("Meal Name", value=meal_name)
        meal_description = st.text_area("Description (optional)", value=meal_description)
        meal_recipe_link = st.text_input("Recipe Link (optional)", value=meal_recipe_link, placeholder="https://...")
        meal_notes = st.text_area("Notes (optional)", value=meal_notes, placeholder="Personal notes, modifications, etc.")
        
        st.subheader("Ingredients")
        
        # Initialize session state for ingredients
        if 'ingredients' not in st.session_state:
            st.session_state.ingredients = []
        
        # Add ingredient form
        col1, col2, col3, col4, col5 = st.columns([2.5, 1, 1.2, 1.5, 0.8])
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
            # Category selection
            category_options = [(cat.display_name, cat.name) for cat in Category]
            category_display_names = [option[0] for option in category_options]
            category_values = [option[1] for option in category_options]
            
            # Default to "Not Sure"
            default_cat_index = category_values.index(Category.NOT_SURE.name) if Category.NOT_SURE.name in category_values else 0
            
            selected_category_display = st.selectbox(
                "Category",
                options=category_display_names,
                index=default_cat_index,
                key="category_select"
            )
            
            # Get the actual category value
            selected_cat_index = category_display_names.index(selected_category_display)
            category = category_values[selected_cat_index]
            
        with col5:
            if st.button("Add Ingredient"):
                if ingredient_name and quantity > 0:
                    st.session_state.ingredients.append((ingredient_name, quantity, unit, category))
                    st.rerun()
        
        # Display current ingredients
        if st.session_state.ingredients:
            st.subheader("Current Ingredients")
            for i, ingredient_tuple in enumerate(st.session_state.ingredients):
                # Handle both 3-tuple and 4-tuple formats
                if len(ingredient_tuple) == 3:
                    name, qty, unit = ingredient_tuple
                    category_display = ""
                elif len(ingredient_tuple) == 4:
                    name, qty, unit, category = ingredient_tuple
                    try:
                        cat_enum = Category[category] if hasattr(Category, category) else Category.from_string(category)
                        category_display = f" ({cat_enum.display_name})"
                    except:
                        category_display = f" ({category})"
                else:
                    continue  # Skip malformed entries
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"{name}: {qty} {unit}{category_display}")
                with col2:
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.ingredients.pop(i)
                        st.rerun()
        
        # Save and Delete buttons
        if mode == "Edit Existing Meal":
            col1, col2 = st.columns([3, 1])
            with col1:
                save_button = st.button("Update Meal", type="primary")
            with col2:
                delete_button = st.button("Delete Meal", type="secondary")
        else:
            save_button = st.button("Save Meal", type="primary")
            delete_button = False
        
        # Handle save button
        if save_button:
            if meal_name and st.session_state.ingredients:
                try:
                    if mode == "Edit Existing Meal" and selected_meal_id:
                        # Update existing meal
                        if db.update_meal(
                            selected_meal_id, 
                            meal_name, 
                            meal_description, 
                            meal_recipe_link, 
                            meal_notes,
                            st.session_state.ingredients
                        ):
                            st.success("Meal updated successfully!")
                            # Clear editing state
                            if 'editing_meal_id' in st.session_state:
                                del st.session_state.editing_meal_id
                            st.session_state.ingredients = []
                            st.rerun()
                    else:
                        # Add new meal
                        meal_id = db.add_meal(
                            meal_name, 
                            meal_description, 
                            meal_recipe_link, 
                            meal_notes,
                            st.session_state.ingredients
                        )
                        if meal_id:
                            st.success("Meal added successfully!")
                            st.session_state.ingredients = []
                            st.rerun()
                except Exception as e:
                    action = "updating" if mode == "Edit Existing Meal" else "adding"
                    st.error(f"Error {action} meal: {str(e)}")
            else:
                st.error("Please provide a meal name and at least one ingredient.")
        
        # Handle delete button
        if delete_button and selected_meal_id:
            # Show confirmation dialog
            if st.button("⚠️ Confirm Delete", key="confirm_delete"):
                try:
                    if db.delete_meal(selected_meal_id):
                        st.success("Meal deleted successfully!")
                        # Clear editing state
                        if 'editing_meal_id' in st.session_state:
                            del st.session_state.editing_meal_id
                        st.session_state.ingredients = []
                        st.rerun()
                    else:
                        st.error("Failed to delete meal.")
                except Exception as e:
                    st.error(f"Error deleting meal: {str(e)}")
            else:
                st.warning(f"Click 'Confirm Delete' to permanently delete '{meal_name}'. This action cannot be undone.")
    
    elif page == "Generate Shopping List":
        st.header("Generate Shopping List")
        
        # Get all meals
        meals = db.get_all_meals()
        
        if not meals:
            st.info("No meals found. Please add some meals first.")
            return
        
        # Meal selection
        meal_options = {meal.name: meal.id for meal in meals}
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
                df = pd.DataFrame(shopping_list, columns=['Ingredient', 'Quantity', 'Unit', 'Category'])
                # Convert Decimal to float for proper display
                df['Quantity'] = pd.to_numeric(df['Quantity']).round(2)
                
                # Display the shopping list table
                st.dataframe(df, use_container_width=True)
                
                # Create formatted text for copying
                def format_shopping_list_text(shopping_list):
                    """Format shopping list as text with category display names."""
                    formatted_lines = []
                    for name, quantity, unit, category_str in shopping_list:
                        # Get category display name
                        try:
                            category = Category.from_string(category_str)
                            category_display = category.display_name
                        except:
                            category_display = "Not Sure"
                        
                        # Format quantity to remove unnecessary decimals
                        if float(quantity) == int(float(quantity)):
                            qty_str = str(int(float(quantity)))
                        else:
                            qty_str = str(float(quantity))
                        
                        formatted_lines.append(f"{name} - {qty_str} {unit} ({category_display})")
                    
                    return "\n".join(formatted_lines)
                
                # Generate formatted text
                formatted_text = format_shopping_list_text(shopping_list)
                
                # Two-column layout for export options
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # Download as CSV
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name=f"shopping_list_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    # Download as text
                    st.download_button(
                        label="📄 Download as Text",
                        data=formatted_text,
                        file_name=f"shopping_list_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                # Text area for copying
                st.subheader("Copy Shopping List")
                st.text_area(
                    "Shopping list formatted for copying:",
                    value=formatted_text,
                    height=300,
                    help="Select all text (Ctrl+A / Cmd+A) and copy (Ctrl+C / Cmd+C) to use elsewhere"
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
        for meal in meals:
            with st.expander(f"🍽️ {meal.name}"):
                # Get meal details for full information
                meal_data = db.get_meal_by_id(meal.id)
                
                if meal_data:
                    # Description
                    if meal_data.get('description'):
                        st.markdown(f"**Description:** {meal_data['description']}")
                    
                    # Recipe link
                    if meal_data.get('recipe_link'):
                        st.markdown(f"**Recipe Link:** [View Recipe]({meal_data['recipe_link']})")
                    
                    # Notes
                    if meal_data.get('notes'):
                        st.markdown(f"**Notes:** {meal_data['notes']}")
                    
                    # Separator if we have any details
                    if meal_data.get('description') or meal_data.get('recipe_link') or meal_data.get('notes'):
                        st.markdown("---")
                
                # Get ingredients with category information
                ingredients = db.get_meal_ingredients(meal.id)
                all_ingredients = db.get_all_ingredients()
                
                if ingredients:
                    st.markdown("**Ingredients:**")
                    for ingredient in ingredients:
                        # Find category for this ingredient
                        ingredient_category = "Not Sure"
                        for db_ing in all_ingredients:
                            if db_ing.name.lower() == ingredient['ingredient_name'].lower():
                                try:
                                    cat_enum = Category.from_string(db_ing.category)
                                    ingredient_category = cat_enum.display_name
                                except:
                                    ingredient_category = db_ing.category
                                break
                        
                        st.write(f"• {ingredient['ingredient_name']}: {ingredient['quantity']} {ingredient['unit']} ({ingredient_category})")
                else:
                    st.write("No ingredients found.")

if __name__ == "__main__":
    main()
