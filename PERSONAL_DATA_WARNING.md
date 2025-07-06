# Personal Data and Repository Management

## ⚠️ CRITICAL: Personal Data Files

The following files contain personal data and should **NEVER** be committed to version control:

### Database Files
- `meal_planner.db` - SQLite database with your imported meals and ingredients
- `*.db`, `*.sqlite`, `*.sqlite3` - Any other database files

### CSV Data Files  
- `Meal Planner - Ingredients.csv` - Your personal meal planning data
- Any other `*.csv` files containing meal/ingredient data

### Other Personal Data
- Any exported shopping lists
- Personal configuration files
- Any files with your specific meal preferences or dietary data

## ✅ Safe to Commit (Application Code)

The following are part of the application and should be committed:

### Core Application
- `meal_planner/` - All Python modules and packages
- `pyproject.toml` - Project configuration
- `uv.lock` - Dependency lock file
- `README.md` - Documentation
- `app.py` - Streamlit application entry point

### Scripts and Tools
- `import_meals_from_csv.py` - CSV import utility (code only, not data)

### Configuration
- `.gitignore` - Git ignore rules
- `.python-version` - Python version specification

## 🛡️ Current Protection

The `.gitignore` file has been configured to automatically exclude:

```gitignore
# Database files (personal data)
*.db
*.duckdb
*.sqlite
*.sqlite3

# Personal meal data
*.csv
Meal Planner*.csv

# Streamlit config
.streamlit/

# Package build artifacts
*.egg-info/
```

## 🚨 Before Each Commit

Always run `git status` and verify that no personal data files are being added:

```bash
git status
```

Look for files like:
- `*.csv` files
- `*.db` files  
- Any files with your personal meal data

## 📋 Safe Commit Checklist

Before committing, ensure:
- [ ] No `.csv` files are being committed
- [ ] No `.db` files are being committed  
- [ ] No personal meal/ingredient data
- [ ] Only application code and documentation
- [ ] Run `git status` to double-check

## 🔄 Sharing the Application

When sharing this repository:
1. Only the application code will be shared
2. No personal meal data will be included
3. Users can import their own CSV data using the import script
4. Each user will have their own local database

This ensures your personal meal planning data remains private while allowing others to use the application.
