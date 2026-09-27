from datetime import timedelta, date as date_type
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

def get_rolling_average(user_id, days=7):
    """Calculate the rolling average of calories/protein/fat/carbs over the last `days` days."""
    assert days > 0 and isinstance(days, int) # Ensure days is a positive integer
    
    today = date_type.today()
    start_date = today - timedelta(days=days - 1)
    daily_totals = []
    for single_date in (start_date + timedelta(n) for n in range(days)):
        daily_totals.append(get_daily_totals(user_id, single_date))
    
    if not daily_totals:
        return {'calories': 0, 'protein_g': 0, 'carbs_g': 0, 'fat_g': 0}
    
    averages = {
        'calories': sum(day['calories'] for day in daily_totals) / days,
        'protein_g': sum(day['protein_g'] for day in daily_totals) / days,
        'carbs_g': sum(day['carbs_g'] for day in daily_totals) / days,
        'fat_g': sum(day['fat_g'] for day in daily_totals) / days,
    }

    return averages