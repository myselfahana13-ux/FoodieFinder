"""
food_img.py — Auto Food Image Fetcher for FoodieFinder
=======================================================
Zero manual work. Fetches images automatically using:
  1. Unsplash (free, high quality food photos)
  2. DuckDuckGo image search (fallback)
  3. Picsum placeholder (final fallback, always works)

Usage in app.py:
    from food_img import get_food_image
    image_url = get_food_image("Dosa")
"""

import requests
import re

# ── Cache so we don't re-fetch the same food twice per session ──
_image_cache: dict = {}

# ── Unsplash Access Key ─────────────────────────────────────────
# Get a FREE key at https://unsplash.com/developers (takes 2 min)
# Create an app → copy "Access Key" → paste below
UNSPLASH_ACCESS_KEY = "YOUR_UNSPLASH_ACCESS_KEY"   # 🔑 replace this

# ── Fallback placeholder style ──────────────────────────────────
# Uses food name as seed so each food gets a consistent image
def _placeholder(food_name: str) -> str:
    safe = food_name.strip().replace(" ", "_")
    return f"https://picsum.photos/seed/{safe}/300/300"


# ── Source 1: Unsplash ──────────────────────────────────────────
def _fetch_unsplash(food_name: str) -> str | None:
    if UNSPLASH_ACCESS_KEY == "YOUR_UNSPLASH_ACCESS_KEY":
        return None  # key not set, skip
    try:
        query = f"{food_name} indian food"
        url   = "https://api.unsplash.com/search/photos"
        resp  = requests.get(url, params={
            "query":       query,
            "per_page":    1,
            "orientation": "squarish",
            "client_id":   UNSPLASH_ACCESS_KEY,
        }, timeout=4)
        data = resp.json()
        results = data.get("results", [])
        if results:
            return results[0]["urls"]["small"]
    except Exception:
        pass
    return None


# ── Source 2: DuckDuckGo image search (no API key needed) ───────
def _fetch_duckduckgo(food_name: str) -> str | None:
    try:
        query   = f"{food_name} indian food dish"
        headers = {"User-Agent": "Mozilla/5.0"}
        # Step 1: get vqd token
        resp = requests.get(
            "https://duckduckgo.com/",
            params={"q": query},
            headers=headers,
            timeout=4
        )
        vqd_match = re.search(r'vqd=([\d-]+)', resp.text)
        if not vqd_match:
            return None
        vqd = vqd_match.group(1)

        # Step 2: fetch image results
        img_resp = requests.get(
            "https://duckduckgo.com/i.js",
            params={"l": "us-en", "o": "json", "q": query, "vqd": vqd, "f": ",,,,,"},
            headers=headers,
            timeout=4
        )
        results = img_resp.json().get("results", [])
        if results:
            return results[0].get("image")
    except Exception:
        pass
    return None


# ── Main function — use this in app.py ──────────────────────────
def get_food_image(food_name: str) -> str:
    """
    Returns an image URL for a food name.
    Tries Unsplash → DuckDuckGo → Picsum placeholder.
    Results are cached in memory for the session.
    """
    food_name = food_name.strip()

    # Return from cache if already fetched
    if food_name in _image_cache:
        return _image_cache[food_name]

    # Try each source in order
    url = (
        _fetch_unsplash(food_name) or
        _fetch_duckduckgo(food_name) or
        _placeholder(food_name)
    )

    _image_cache[food_name] = url
    return url


# ── Optional: pre-warm cache for all foods at startup ───────────
def prewarm_cache(food_names: list, show_progress: bool = False) -> None:
    """
    Call this once at app startup to pre-fetch all images.
    Speeds up the UI so images don't load lazily.

    Usage in app.py:
        from food_img import get_food_image, prewarm_cache
        prewarm_cache(foodie['name'].tolist())
    """
    for i, name in enumerate(food_names):
        if name not in _image_cache:
            get_food_image(name)
        if show_progress and i % 20 == 0:
            print(f"  Pre-warmed {i}/{len(food_names)} images...")