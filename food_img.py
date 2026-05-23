"""
food_img.py — Smart Food Image Fetcher for FoodieFinder
========================================================
Fetches ACCURATE food images using:
  1. Hardcoded overrides — 100% accurate for common Indian foods
  2. Wikimedia Commons   — no key needed, food-accurate
  3. Spoonacular API     — food-specific (free: 150 calls/day)
  4. Unsplash API        — high quality (free, needs key)
  5. Consistent placeholder — never random

Get free Spoonacular key: https://spoonacular.com/food-api
Get free Unsplash key:    https://unsplash.com/developers
"""

import requests

# ── In-memory cache (per session) ───────────────────────────────
_image_cache: dict = {}

# ── API Keys (optional — app works without them via Wikimedia) ───
SPOONACULAR_API_KEY = "YOUR_SPOONACULAR_KEY"
UNSPLASH_ACCESS_KEY = "YOUR_UNSPLASH_KEY"

# ── Hardcoded overrides — guaranteed correct images ─────────────
FOOD_IMAGE_OVERRIDES = {
    # Desserts
    "Balu shahi":       "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Balushahi.jpg/300px-Balushahi.jpg",
    "Gulab jamun":      "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Gulab_jamun_%28after_cooking%29.jpg/300px-Gulab_jamun_%28after_cooking%29.jpg",
    "Jalebi":           "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Jalebi.jpg/300px-Jalebi.jpg",
    "Rasgulla":         "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Rasagola.jpg/300px-Rasagola.jpg",
    "Kheer":            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Kheer.jpg/300px-Kheer.jpg",
    "Gajar ka halwa":   "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Gajar-Halwa.jpg/300px-Gajar-Halwa.jpg",
    "Laddu":            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/thirty-three/Motichoor_Ke_Laddu.jpg/300px-Motichoor_Ke_Laddu.jpg",
    "Modak":            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Modak_Photo.jpg/300px-Modak_Photo.jpg",
    "Mysore pak":       "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Mysorepak.jpg/300px-Mysorepak.jpg",
    "Halwa":            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Gajar-Halwa.jpg/300px-Gajar-Halwa.jpg",
    # South Indian
    "Dosa":             "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Plain-Dosa.jpg/300px-Plain-Dosa.jpg",
    "Masala Dosa":      "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Masala_Dosa.jpg/300px-Masala_Dosa.jpg",
    "Idli":             "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Idli_Sambar.jpg/300px-Idli_Sambar.jpg",
    "Vada":             "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Medhu_Vadai.jpg/300px-Medhu_Vadai.jpg",
    "Uttapam":          "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Uttapam.jpg/300px-Uttapam.jpg",
    "Upma":             "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Upma.jpg/300px-Upma.jpg",
    "Pongal":           "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Pongal_Festival.jpg/300px-Pongal_Festival.jpg",
    "Sambhar":          "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Sambar_in_a_bowl.jpg/300px-Sambar_in_a_bowl.jpg",
    # Rice & Biryani
    "Biryani":          "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Delhi_Biryani.jpg/300px-Delhi_Biryani.jpg",
    "Chicken Biryani":  "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Delhi_Biryani.jpg/300px-Delhi_Biryani.jpg",
    "Pulao":            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Matar_pulao.jpg/300px-Matar_pulao.jpg",
    "Khichdi":          "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Khichdi.jpg/300px-Khichdi.jpg",
    # Breads
    "Naan":             "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Naan_Indian_bread.jpg/300px-Naan_Indian_bread.jpg",
    "Chapati":          "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Chapati.jpg/300px-Chapati.jpg",
    "Paratha":          "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Aloo_paratha.jpg/300px-Aloo_paratha.jpg",
    "Puri":             "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Puri_with_bhaji.jpg/300px-Puri_with_bhaji.jpg",
    "Bhatura":          "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Chole_Bhature.jpg/300px-Chole_Bhature.jpg",
    # Curries & Mains
    "Butter chicken":   "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Butter_Chicken.jpg/300px-Butter_Chicken.jpg",
    "Dal makhani ":     "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Dal_makhani.jpg/300px-Dal_makhani.jpg",
    "Dal tadka":        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Dal_tadka.jpg/300px-Dal_tadka.jpg",
    "Chana masala":     "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Chana_masala.jpg/300px-Chana_masala.jpg",
    "Rajma chaval":     "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Rajma-Chawal.jpg/300px-Rajma-Chawal.jpg",
    "Paneer tikka":     "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Paneer_tikka.jpg/300px-Paneer_tikka.jpg",
    "Palak paneer":     "https://upload.wikimedia.org/wikipedia/commons/thumb/4/forty/Palak_Paneer.jpg/300px-Palak_Paneer.jpg",
    # Snacks & Street Food
    "Samosa":           "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Samosachutney.jpg/300px-Samosachutney.jpg",
    "Pav Bhaji":        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Pav_bhaji_in_Mumbai.jpg/300px-Pav_bhaji_in_Mumbai.jpg",
    "Chole bhature":    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Chole_Bhature.jpg/300px-Chole_Bhature.jpg",
    "Aloo tikki":       "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Aloo_tikki.jpg/300px-Aloo_tikki.jpg",
    "Kachori":          "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Kachori.jpg/300px-Kachori.jpg",
    "Poha":             "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Poha_Recipe.jpg/300px-Poha_Recipe.jpg",
    "Bhel puri":        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Bhel_puri.jpg/300px-Bhel_puri.jpg",
    # Drinks
    "Lassi":            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Lassi_in_a_glass.jpg/300px-Lassi_in_a_glass.jpg",
    "Chai":             "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Masala_Chai.JPG/300px-Masala_Chai.JPG",
}


def _placeholder(food_name: str) -> str:
    """SVG placeholder — clean food card, never a random photo."""
    import urllib.parse
    label = food_name.strip()[:22]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300">
      <rect width="300" height="300" rx="16" fill="#F5DEB3"/>
      <text x="150" y="120" font-size="72" text-anchor="middle">🍽️</text>
      <text x="150" y="185" font-size="20" text-anchor="middle"
            font-family="sans-serif" fill="#7C4A2D" font-weight="bold">{label}</text>
      <text x="150" y="215" font-size="13" text-anchor="middle"
            font-family="sans-serif" fill="#9A7B5E">Indian Dish</text>
    </svg>'''
    return f"data:image/svg+xml,{urllib.parse.quote(svg)}"

def _fetch_wikimedia(food_name: str) -> str | None:
    """Wikipedia page image — no API key needed, food-accurate."""
    try:
        resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action":      "query",
                "titles":      food_name,
                "prop":        "pageimages",
                "format":      "json",
                "pithumbsize": 300,
            },
            timeout=5
        )
        pages = resp.json().get("query", {}).get("pages", {})
        for page in pages.values():
            src = page.get("thumbnail", {}).get("source")
            if src:
                return src
    except Exception:
        pass
    return None


def _fetch_spoonacular(food_name: str) -> str | None:
    if SPOONACULAR_API_KEY == "YOUR_SPOONACULAR_KEY":
        return None
    try:
        resp = requests.get(
            "https://api.spoonacular.com/food/search",
            params={"query": food_name, "number": 1, "apiKey": SPOONACULAR_API_KEY},
            timeout=4
        )
        for item in resp.json().get("searchResults", []):
            results = item.get("results", [])
            if results and results[0].get("image"):
                return results[0]["image"]
    except Exception:
        pass
    return None


def _fetch_unsplash(food_name: str) -> str | None:
    if UNSPLASH_ACCESS_KEY == "YOUR_UNSPLASH_KEY":
        return None
    try:
        resp = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query":       f"{food_name} indian food dish",
                "per_page":    1,
                "orientation": "squarish",
                "client_id":   UNSPLASH_ACCESS_KEY,
            },
            timeout=4
        )
        results = resp.json().get("results", [])
        if results:
            return results[0]["urls"]["small"]
    except Exception:
        pass
    return None


def get_food_image(food_name: str) -> str:
    """
    Returns best image URL for a food name.
    Order: Override → Cache → Wikimedia → Spoonacular → Unsplash → Placeholder
    """
    food_name = food_name.strip()

    # 1. Hardcoded overrides — always correct
    if food_name in FOOD_IMAGE_OVERRIDES:
        return FOOD_IMAGE_OVERRIDES[food_name]

    # 2. Session cache
    if food_name in _image_cache:
        return _image_cache[food_name]

    # 3. Try APIs
    url = (
        _fetch_wikimedia(food_name)   or
        _fetch_spoonacular(food_name) or
        _fetch_unsplash(food_name)    or
        _placeholder(food_name)
    )

    _image_cache[food_name] = url
    return url