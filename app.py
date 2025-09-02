from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from db import init_db, get_db_connection, get_recipe_by_ingredients, save_user_recipe

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# ---------------- Serve index.html at root ----------------
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# Initialize database
init_db()

# -------------------- AUTH ROUTES --------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name', 'Anonymous')

    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM users WHERE email=%s', (email,))
    user = cursor.fetchone()

    if user:
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        message = f'Logged in as {user["name"]}'
    else:
        cursor.execute('INSERT INTO users (name, email) VALUES (%s, %s)', (name, email))
        conn.commit()
        user_id = cursor.lastrowid
        session['user_id'] = user_id
        session['user_name'] = name
        message = f'User {name} created and logged in'

    cursor.close()
    conn.close()
    return jsonify({'success': True, 'message': message})


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


# -------------------- RECIPE ROUTES --------------------
@app.route('/get-recipes', methods=['POST'])
def get_recipes():
    try:
        data = request.get_json()
        ingredients = data.get('ingredients', [])
        if not ingredients:
            return jsonify({'error': 'No ingredients provided'}), 400

        recipes = get_recipe_by_ingredients(ingredients)
        return jsonify({'recipes': recipes})
    except Exception as e:
        print(f"Error fetching recipes: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/save-recipe', methods=['POST'])
def save_recipe_to_user():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login required'}), 401

    data = request.get_json()
    recipe_id = data.get('recipe_id')
    if not recipe_id:
        return jsonify({'success': False, 'message': 'Recipe ID required'}), 400

    try:
        save_user_recipe(session['user_id'], recipe_id)
        return jsonify({'success': True, 'message': 'Recipe saved successfully'})
    except Exception as e:
        print(f"Error saving recipe: {e}")
        return jsonify({'success': False, 'message': 'Failed to save recipe'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
