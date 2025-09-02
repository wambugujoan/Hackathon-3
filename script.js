document.addEventListener('DOMContentLoaded', function() {
    const ingredientInput = document.getElementById('ingredient-input');
    const addIngredientBtn = document.getElementById('add-ingredient');
    const ingredientList = document.getElementById('ingredient-list');
    const findRecipesBtn = document.getElementById('find-recipes');
    const recipeResults = document.getElementById('recipe-results');
    const loading = document.getElementById('loading');

    let selectedIngredients = [];
    let loggedInUser = null;

    const loginBtn = document.getElementById('login-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const registerBtn = document.getElementById('register-btn'); // Move here
    const loginMessage = document.getElementById('login-message');

    // ------------------ Ingredient Handling ------------------
    addIngredientBtn.addEventListener('click', () => {
        const ingredient = ingredientInput.value.trim();
        if (ingredient && !selectedIngredients.includes(ingredient)) {
            selectedIngredients.push(ingredient);
            updateIngredientList();
            ingredientInput.value = '';
        }
    });

    ingredientInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addIngredientBtn.click();
    });

    function updateIngredientList() {
        ingredientList.innerHTML = '';
        selectedIngredients.forEach(ingredient => {
            const chip = document.createElement('div');
            chip.className = 'ingredient-chip';
            chip.innerHTML = `${ingredient} <i class="fas fa-times"></i>`;
            ingredientList.appendChild(chip);

            chip.querySelector('i').addEventListener('click', () => {
                selectedIngredients = selectedIngredients.filter(i => i !== ingredient);
                updateIngredientList();
            });
        });
    }

    // ------------------ Recipe Fetching ------------------
    findRecipesBtn.addEventListener('click', () => {
        if (selectedIngredients.length === 0) {
            alert('Please add at least one ingredient');
            return;
        }

        loading.classList.add('show');
        recipeResults.innerHTML = '';

        fetch('/get-recipes', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ ingredients: selectedIngredients })
        })
        .then(res => res.json())
        .then(data => {
            loading.classList.remove('show');
            if (data.error) {
                recipeResults.innerHTML = `<p>${data.error}</p>`;
            } else {
                displayRecipes(data.recipes);
            }
        })
        .catch(err => {
            loading.classList.remove('show');
            console.error(err);
            recipeResults.innerHTML = '<p>Sorry, an error occurred while fetching recipes.</p>';
        });
    });

    function displayRecipes(recipes) {
        if (!recipes || recipes.length === 0) {
            recipeResults.innerHTML = '<p>No recipes found. Try different ingredients.</p>';
            return;
        }

        recipeResults.innerHTML = '';
        recipes.forEach(recipe => {
            const recipeCard = document.createElement('div');
            recipeCard.className = 'recipe-card';

            const colors = ['#4CAF50','#FF9800','#F44336','#2196F3','#9C27B0'];
            const color = colors[Math.floor(Math.random() * colors.length)];

            recipeCard.innerHTML = `
                <div class="recipe-image" style="background: linear-gradient(45deg, ${color}, ${lightenColor(color, 25)})">
                    🍽️
                </div>
                <div class="recipe-content">
                    <h3 class="recipe-title">${recipe.title}</h3>
                    <p class="recipe-ingredients"><strong>Ingredients:</strong> ${recipe.ingredients.join(', ')}</p>
                    <p class="recipe-instructions"><strong>Instructions:</strong> ${recipe.instructions}</p>
                    <div class="recipe-actions">
                        <button class="save-recipe" data-id="${recipe.id}">
                            <i class="fas fa-bookmark"></i> Save
                        </button>
                    </div>
                </div>
            `;

            recipeResults.appendChild(recipeCard);

            recipeCard.querySelector('.save-recipe').addEventListener('click', () => {
                if (!loggedInUser) {
                    alert('Please login to save recipes.');
                } else {
                    saveRecipe(recipe.id);
                }
            });
        });
    }

    function lightenColor(color, percent) {
        const num = parseInt(color.slice(1),16);
        const amt = Math.round(2.55*percent);
        const R = Math.min(255, Math.max(0, (num>>16)+amt));
        const G = Math.min(255, Math.max(0, ((num>>8)&0x00FF)+amt));
        const B = Math.min(255, Math.max(0, (num&0x0000FF)+amt));
        return '#' + ((1<<24)+(R<<16)+(G<<8)+B).toString(16).slice(1);
    }

    function saveRecipe(id) {
        fetch('/save-recipe', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({recipe_id: id})
        })
        .then(res => res.json())
        .then(data => alert(data.success ? 'Recipe saved!' : 'Failed to save.'))
        .catch(err => { console.error(err); alert('Failed to save recipe.'); });
    }

    // ------------------ LOGIN HANDLING ------------------
    loginBtn.addEventListener('click', () => {
        const name = document.getElementById('login-name').value.trim() || 'Anonymous';
        const email = document.getElementById('login-email').value.trim();
        if (!email) {
            loginMessage.textContent = 'Please enter your email';
            return;
        }

        fetch('/login', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({name, email})
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                loggedInUser = { name, email };
                loginMessage.textContent = data.message;
                loginBtn.classList.add('hidden');
                registerBtn.classList.add('hidden');
                logoutBtn.classList.remove('hidden');
            } else {
                loginMessage.textContent = data.message;
            }
        })
        .catch(err => console.error(err));
    });

    logoutBtn.addEventListener('click', () => {
        fetch('/logout', {method:'POST'})
        .then(res => res.json())
        .then(data => {
            loggedInUser = null;
            loginMessage.textContent = data.message;
            loginBtn.classList.remove('hidden');
            registerBtn.classList.remove('hidden');
            logoutBtn.classList.add('hidden');
        })
        .catch(err => console.error(err));
    });

    // ------------------ REGISTER HANDLING ------------------
    registerBtn.addEventListener('click', () => {
        const name = document.getElementById('login-name').value.trim() || 'Anonymous';
        const email = document.getElementById('login-email').value.trim();
        if (!email) {
            loginMessage.textContent = 'Please enter your email';
            return;
        }

        fetch('/register', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({name, email})
        })
        .then(res => res.json())
        .then(data => {
            loginMessage.textContent = data.message;
            if (data.success) {
                loggedInUser = { name, email };
                loginBtn.classList.add('hidden');
                registerBtn.classList.add('hidden');
                logoutBtn.classList.remove('hidden');
            }
        })
        .catch(err => console.error(err));
    });

});
