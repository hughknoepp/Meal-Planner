import os
import requests

API_KEY = os.environ.get('USDA_API_KEY')
BASE_URL = 'https://api.nal.usda.gov/fdc/v1'

def search_food(query, page_size=10):
    r = requests.get(f'{BASE_URL}/foods/search', params={
        'api_key': API_KEY,
        'query': query,
        'pageSize': page_size,
    }, timeout=10)
    r.raise_for_status()
    return r.json()['foods']

def get_food_details(fdc_id):
    r = requests.get(f'{BASE_URL}/food/{fdc_id}', params={
        'api_key': API_KEY,
    }, timeout=10)
    r.raise_for_status()
    return r.json()