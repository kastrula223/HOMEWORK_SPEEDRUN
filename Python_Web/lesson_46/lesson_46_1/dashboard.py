import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE_URL = "https://jsonplaceholder.typicode.com"
REQUEST_TIMEOUT = 5  # секунд на один запит


def _fetch_json(url: str):
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def fetch_user_dashboard(user_id: int) -> dict:
    start_time = time.perf_counter()

    endpoints = {
        "profile": f"{BASE_URL}/users/{user_id}",
        "posts": f"{BASE_URL}/users/{user_id}/posts",
        "albums": f"{BASE_URL}/users/{user_id}/albums",
        "photos": f"{BASE_URL}/photos?userId={user_id}&_limit=10",
    }

    results = {}

    with ThreadPoolExecutor(max_workers=len(endpoints)) as executor:
        future_to_key = {
            executor.submit(_fetch_json, url): key
            for key, url in endpoints.items()
        }

        for future in as_completed(future_to_key):
            key = future_to_key[future]
            results[key] = future.result()

    elapsed = time.perf_counter() - start_time

    profile = results.get("profile")
    posts = results.get("posts")
    albums = results.get("albums")
    photos = results.get("photos")

    return {
        "user_id": user_id,
        "profile": profile,
        "posts": posts,
        "albums": albums,
        "photos": photos,
        "stats": {
            "posts_count": len(posts) if posts is not None else None,
            "albums_count": len(albums) if albums is not None else None,
            "photos_count": len(photos) if photos is not None else None,
            "profile_available": profile is not None,
        },
        "sources_status": {
            key: "ok" if value is not None else "unavailable"
            for key, value in results.items()
        },
        "execution_time_seconds": round(elapsed, 4),
    }