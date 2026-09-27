from datetime import date as date_type
from models import MealLog

def get_daily_totals(user_id, log_date = None):
    """Sum calories/protein/fat/carbs across all foods logged by a user on a given date"""
    log_date = log_date or date_type.today()
    meal_log = MealLog.query.filter_by(user_id=user_id, date=log_date).first()
    totals = {'calories': 0, 'protein_g': 0, 'carbs_g': 0, 'fat_g': 0}

    if meal_log is None:
        return totals
    
    for item in meal_log.items:
        totals['calories'] += item.calories or 0
        totals['protein_g'] += item.protein_g or 0
        totals['carbs_g'] += item.carbs_g or 0
        totals['fat_g'] += item.fat_g or 0
    
    return totals