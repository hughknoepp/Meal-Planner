from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from config import Config
from models import db, User, MealLog, MealItem
from usda import search_food, get_food_details
from datetime import date as date_type

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/log/search')
@login_required
def food_search():
    query = request.get('q', '')
    results = search_food(query) if query else []
    return render_template('food_search.html', results=results)

NUTRIENT_MAP = {
    'calories': ('Energy', 'KCAL'),
    'protein_g': ('Protein', 'G'),
    'carbs_g': ('Carbohydrate, by difference', 'G'),
    'fat_g': ('Total lipid (fat)', 'G'),
}

def extract_nutrients(food_detail):
    """Pull the four tracked nutrients (per 100g) out of a USDA food record."""
    values = {}
    for field, (name, unit) in NUTRIENT_MAP.items():
        values[field] = None
        for n in food_detail.get('foodNutrients', []):
            nutrient = n.get('nutrient', {})
            if nutrient.get('name') == name and nutrient.get('unitName', '').upper() == unit:
                values[field] = n.get('amount')
                break
    return values

@app.route('/log/add/<int:fdc_id>', methods=['POST'])
@login_required
def add_food(fdc_id):
    try:
        quantity_g = float(request.form['quantity_g'])
    except (KeyError, ValueError):
        flash('Enter a valid quantity in grams')
        return redirect(url_for('food_search'))
    
    if quantity_g <= 0:
        flash('Quantity must be greater than zero')
        return redirect(url_for('food_search'))
    
    food = get_food_details(fdc_id)
    per_100g = extract_nutrients(food)
    scale = quantity_g / 100

    meal_log = MealLog.query.filter_by(
        user_id=current_user.id, date=date_type.today()
    ).first()
    if meal_log is None:
        meal_log = MealLog(user_id=current_user.id, date=date_type.today())
        db.session.add(meal_log)
        db.session.flush()
    
    item = MealItem(
        meal_log_id = meal_log.id,
        food_name = food.get('description', 'Unknown food'),
        fdc_id = fdc_id,
        quantity_g = quantity_g,
        calories = (per_100g['calories'] or 0) * scale,
        protein_g = (per_100g['protein_g'] or 0) * scale,
        carbs_g = (per_100g['carbs_g'] or 0) * scale,
        fat_g = (per_100g['fat_g'] or 0) * scale,
    )
    db.session.add(item)
    db.session.commit()

    flash(f"Added {item.food_name} to today's log")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5050)