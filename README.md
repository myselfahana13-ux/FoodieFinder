# 🍽 FoodieFinder

> *Because choosing food should be delicious.*

FoodieFinder is a content-based food recommendation web app built with **Streamlit** and **Python**. Tell it what you're craving, and it suggests similar dishes — complete with cook times, ingredient previews, match scores, and a direct link to find nearby restaurants on Google Maps.

---

## ✨ Features

- **Smart Recommendations** — Enter any dish and get up to 5 similar food suggestions ranked by a similarity score, with a family-match bonus (e.g. dal dishes stay with dal dishes).
- **Veg / Non-Veg Awareness** — Recommendations always respect dietary type; vegetarian dishes will never suggest non-veg alternatives and vice versa.
- **Mood Filter** — Filter the food list by mood: Spicy 🌶️, Sweet 🍬, Dessert 🍮, Main Course 🍛, Vegetarian 🥗, or Non-Veg 🍗.
- **Food of the Day** — A daily featured dish seeded by the current date, so it changes every day automatically.
- **Surprise Me!** — Not sure what to pick? Hit the random button and let FoodieFinder decide.
- **Recently Viewed** — Keeps track of the last 5 dishes you explored in the current session.
- **Find a Restaurant** — Each recommendation card links directly to Google Maps to find nearby places serving that dish.
- **Fun Food Facts** — A rotating banner of Indian food trivia to enjoy while you browse.

---

## 🗂 Project Structure

```
FoodieFinder/
│
├── app.py                  # Main Streamlit application
├── food_img.py             # Food name → image URL mapping
├── requirements.txt        # Python dependencies
├── runtime.txt             # Python runtime version
│
├── Food_data/
│   └── food_csv/
│       └── new_df.csv      # Dataset with food names, ingredients, cook times, tags
│
└── models/
    ├── food_dict.pkl       # Serialized food name list (used for similarity lookup)
    └── similarity.pkl      # Precomputed cosine similarity matrix
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/myselfahana13-ux/FoodieFinder.git
   cd FoodieFinder
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**

   ```bash
   streamlit run app.py
   ```

   The app will open in your browser at `http://localhost:8501`.

---

## 🧠 How It Works

FoodieFinder uses a **content-based filtering** approach:

1. Food data (ingredients, tags, cook time) is preprocessed and vectorized.
2. A **cosine similarity matrix** is computed across all dishes and saved as `similarity.pkl`.
3. When a user selects a food, the app looks up its row in the similarity matrix and retrieves the top candidates.
4. Candidates are filtered by dietary type (veg/non-veg) and boosted if they belong to the same dish family (e.g. biryani stays close to other rice dishes).
5. Final results are ranked by a blended score: `similarity score + family bonus`.

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web app framework |
| `pandas` | Data loading and manipulation |
| `numpy` | Numerical operations |
| `scikit-learn` | Similarity computation |
| `requests` | HTTP requests (image fetching) |

---

## 🍛 Dataset

The food dataset (`new_df.csv`) contains Indian dishes with the following fields:

- `name` — dish name
- `ingredients` — ingredient list
- `cook_time` — preparation time in minutes
- `tags` — cuisine type, dietary category, flavour profile

---

## 🙋‍♀️ Author

Made with 🤍 by [Ahana](https://github.com/myselfahana13-ux)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
