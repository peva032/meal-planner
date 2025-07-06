# Meal Planner

A comprehensive Streamlit web application for planning meals and generating shopping lists with robust data management.

## Features

- **Add & Edit Meals**: Create and modify meals with ingredients, quantities, and optional recipe links and notes
- **Standardized Units**: Uses predefined metric units with comprehensive unit system
- **Ingredient Categories**: Organize ingredients by shopping categories for efficient grocery trips
- **Generate Shopping Lists**: Select multiple meals and get aggregated shopping lists with category organization
- **View & Browse Meals**: Browse all stored meals with expandable ingredient details
- **Data Import**: Import existing meal data from CSV files
- **Data Persistence**: Uses SQLite for reliable local data storage
- **Duplicate Prevention**: Case-insensitive uniqueness constraints prevent duplicate meals and ingredients

## Installation

This project uses `uv` for package management. Make sure you have `uv` installed.

```bash
# Clone the repository
git clone <repository-url>
cd meal-planner

# Install dependencies
uv sync
```

## Usage

### Web Application

Run the Streamlit web application:

```bash
# Start the web application
uv run streamlit run app.py
```

The application will be available at `http://localhost:8501`.

### Data Import

Import existing meal data from CSV files:

```bash
# Import meals from CSV
uv run python import_meals_from_csv.py
```

## Database

The application uses SQLite to store data locally in a file called `meal_planner.db`. This file will be created automatically when you first run the application.

### Database Features
- **Case-insensitive uniqueness**: Prevents duplicate meals and ingredients regardless of capitalization
- **Relational integrity**: Proper foreign key relationships between meals and ingredients
- **Automatic timestamps**: Tracks creation and update times for all records

## How to Use

1. **Add Meal**: 
   - Navigate to the "Add Meal" page
   - Enter a meal name and optional description, recipe link, and notes
   - Add ingredients one by one with their quantities and units
   - Save the meal

2. **Edit Meal**:
   - Navigate to the "Add Meal" page and select "Edit Existing Meal"
   - Choose a meal from the dropdown
   - Modify the meal details and ingredients
   - Update or delete the meal

3. **Generate Shopping List**:
   - Navigate to the "Generate Shopping List" page
   - Select one or more meals from the list
   - View the aggregated shopping list
   - Download the shopping list as a CSV file

4. **View Meals**:
   - Navigate to the "View Meals" page
   - Browse all stored meals and their ingredients
   - Expand meal cards to see ingredient details

## Database Schema

The application uses three tables:
- `meals`: Stores meal information (id, name, description)
- `ingredients`: Stores ingredient information (id, name, unit)
- `meal_ingredients`: Links meals to ingredients with quantities

## Project Structure

```
meal-planner/
├── meal_planner/              # Main Python package
│   ├── __init__.py           # Package initialization
│   ├── __main__.py           # Module entry point
│   ├── cli.py                # Command-line interface
│   ├── db.py                 # Database client class
│   ├── units.py              # Unit enum with standardized units
│   └── streamlit_app.py      # Streamlit web application
├── app.py                    # Entry point for Streamlit app
├── example_usage.py          # Example script demonstrating usage
├── pyproject.toml            # Package configuration
├── README.md                 # This file
└── meal_planner.db           # DuckDB database (created automatically)
```

## DbClient Class

The database operations are encapsulated in the `DbClient` class in `db.py`. Key methods include:

- `add_meal(name, description, ingredients)`: Add a new meal
- `get_all_meals()`: Retrieve all meals
- `get_meal_ingredients(meal_id)`: Get ingredients for a specific meal
- `generate_shopping_list(meal_ids)`: Generate aggregated shopping list
- `delete_meal(meal_id)`: Delete a meal
- `update_meal(meal_id, name, description, ingredients)`: Update an existing meal

## Units

The application uses standardized metric units defined in the `Unit` enum:

**Weight/Mass:** gram (g), kilogram (kg)  
**Volume - Liquid:** millilitre (ml), litre (l)  
**Volume - Cooking:** teaspoon (tsp), tablespoon (tbsp), cup  
**Count:** piece, pieces, clove, cloves  
**Length:** centimetre (cm)  
**Special:** pinch, dash  
**Containers:** can, jar, bottle, packet, bag  
**Fresh Produce:** head, bunch, stalk, leaf, leaves  


## Requirements

- Python 3.13
- Streamlit
- DuckDB
- Pandas
