import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# ---------------- Database Connection ----------------
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'recipe_recommender')
    )

# ---------------- Initialize DB ----------------
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_recipes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            recipe_id INT NOT NULL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (recipe_id) REFERENCES recipes(id)
        )
    ''')

    # Insert sample recipes if none exist
    cursor.execute('SELECT COUNT(*) FROM recipes')
    if cursor.fetchone()[0] == 0:
        sample_recipes = [
            {
                'title': 'Tomato Chicken Stir Fry',
                'ingredients': 'chicken, tomato, garlic, oil, soy sauce',
                'instructions': 'Chop chicken and tomato, sauté with garlic in oil, add soy sauce, cook 10 min.'
            },
            {
                'title': 'Garlic Chicken Pasta',
                'ingredients': 'chicken, garlic, pasta, cream, cheese',
                'instructions': 'Cook pasta. Sauté chicken with garlic, add cream and cheese, mix with pasta.'
            },
            {
                'title': 'Spicy Chicken Curry',
                'ingredients': 'chicken, onion, tomato, curry powder, oil',
                'instructions': 'Sauté onion and spices, add chicken and tomato, cook until done.'
            },
            {
                'title': 'Chicken Salad',
                'ingredients': 'chicken, lettuce, tomato, cucumber, olive oil',
                'instructions': 'Mix all ingredients in a bowl and serve chilled.'
            },
            {
                'title': 'Veggie Salad',
                'ingredients': 'lettuce, tomato, cucumber, olive oil',
                'instructions': 'Mix all veggies and drizzle olive oil.'
            },
            {
                'title': 'Simple Soup',
                'ingredients': 'carrot, onion, celery, broth, herbs',
                'instructions': 'Simmer all ingredients in broth for 20 min.'
            }
        ]
        for r in sample_recipes:
            cursor.execute(
                'INSERT INTO recipes (title, ingredients, instructions) VALUES (%s, %s, %s)',
                (r['title'], r['ingredients'], r['instructions'])
            )

    conn.commit()
    cursor.close()
    conn.close()



# ---------------- Search Recipes ----------------
def get_recipe_by_ingredients(ingredients):
    if not ingredients:
        return []

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Clean ingredients
    ingredients = [ing.strip().lower() for ing in ingredients if ing.strip()]
    if not ingredients:
        return []

    # Build SQL query to match any ingredient (OR) and order by number of matched ingredients
    like_patterns = [f"%{ing}%" for ing in ingredients]
    query = """
        SELECT *, 
               (""" + " + ".join([f"(LOWER(ingredients) LIKE %s)" for _ in ingredients]) + """) AS match_count
        FROM recipes
        WHERE """ + " OR ".join(["LOWER(ingredients) LIKE %s" for _ in ingredients]) + """
        ORDER BY match_count DESC
        LIMIT 10
    """

    try:
        # Use each pattern twice: once for SELECT match_count, once for WHERE
        cursor.execute(query, like_patterns * 2)
        recipes = cursor.fetchall()

        # Convert ingredients string to list
        for recipe in recipes:
            recipe['ingredients'] = [ing.strip() for ing in recipe['ingredients'].split(',')]

        return recipes
    except Exception as e:
        print(f"Error in get_recipe_by_ingredients: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


# ---------------- Save User Recipe ----------------
def save_user_recipe(user_id, recipe_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'INSERT INTO user_recipes (user_id, recipe_id) VALUES (%s, %s)',
        (user_id, recipe_id)
    )

    conn.commit()
    cursor.close()
    conn.close()
