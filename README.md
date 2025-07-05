# Meal Planner

A simple Streamlit application for planning meals and generating shopping lists.

## Features

- **Add Meals**: Create new meals with their ingredients and quantities
- **Generate Shopping Lists**: Select multiple meals and get an aggregated shopping list
- **View Meals**: Browse all stored meals and their ingredients
- **Data Persistence**: Uses DuckDB for local data storage

## Installation

This project uses `uv` for package management. Make sure you have `uv` installed.

```bash
# Clone the repository
git clone <repository-url>
cd meal-planner

# Install dependencies (if not already done)
uv sync
```

## Usage

Run the Streamlit application:

```bash
uv run streamlit run app.py
```

The application will be available at `http://localhost:8501`.

## Database

The application uses DuckDB to store data locally in a file called `meal_planner.db`. This file will be created automatically when you first run the application.

## How to Use

1. **Add Meal**: 
   - Navigate to the "Add Meal" page
   - Enter a meal name and optional description
   - Add ingredients one by one with their quantities and units
   - Save the meal

2. **Generate Shopping List**:
   - Navigate to the "Generate Shopping List" page
   - Select one or more meals from the list
   - View the aggregated shopping list
   - Download the shopping list as a CSV file

3. **View Meals**:
   - Navigate to the "View Meals" page
   - Browse all stored meals and their ingredients

## Database Schema

The application uses three tables:
- `meals`: Stores meal information (id, name, description)
- `ingredients`: Stores ingredient information (id, name, unit)
- `meal_ingredients`: Links meals to ingredients with quantities

## Requirements

- Python 3.13
- Streamlit
- DuckDB
- Pandas
