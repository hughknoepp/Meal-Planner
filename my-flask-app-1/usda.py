import os
from datetime import timedelta

import requests_cache

API_KEY = os.environ.get('USDA_API_KEY')
BASE_URL = 'https://api.nal.usda.gov/fdc/v1'

CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'usda_cache')

# All USDA GETs go through this session. Only 200 responses are cached (errors never are),
# and if the API is down or rate-limited we fall back to a stale cached copy.
session = requests_cache.CachedSession(
    CACHE_PATH,
    backend='sqlite',
    expire_after=timedelta(hours=1),
    urls_expire_after={
        # Search rankings can shift, so keep these relatively fresh
        f'{BASE_URL}/foods/search*': timedelta(hours=6),
        # A food's nutrient record for a given fdcId is effectively static
        f'{BASE_URL}/food/*': timedelta(days=30),
    },
    # Keep the API key out of the cache key and out of the stored request URL,
    # so it never lands in the cache file
    ignored_parameters=['api_key'],
    stale_if_error=True,
)

def search_food(query, page_size=10):
    # Normalise so "Apple", "apple " and "APPLE" share one cache entry
    query = query.strip().lower()
    r = session.get(f'{BASE_URL}/foods/search', params={
        'api_key': API_KEY,
        'query': query,
        'pageSize': page_size,
    }, timeout=10)
    r.raise_for_status()
    return r.json()['foods']

def get_food_details(fdc_id):
    r = session.get(f'{BASE_URL}/food/{fdc_id}', params={
        'api_key': API_KEY,
    }, timeout=10)
    r.raise_for_status()
    return r.json()
