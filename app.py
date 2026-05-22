import streamlit as st
import pandas as pd
import pickle
import os
import requests
from food_img import FOOD_IMAGE_MAP

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="FoodieFinder",
    page_icon="🍕",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
base_dir = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_data():
    food_dict = pickle.load(open(os.path.join(base_dir, 'models', 'food_dict.pkl'), 'rb'))
    similarity = pickle.load(open(os.path.join(base_dir, 'models', 'similarity.pkl'), 'rb'))
    foodie = pd.DataFrame(food_dict)
    # ✅ FIXED PATH
    recipes_df = pd.read_csv(os.path.join(base_dir, 'Food_data', 'food_csv', 'new_df.csv'))
    return foodie, similarity, recipes_df

foodie, similarity, recipes_df = load_data()

# ---------------- IMAGE FUNCTION ----------------
@st.cache_data
def get_food_image(food_name):
    # ✅ First try img_url from CSV, then FOOD_IMAGE_MAP, then fallback
    row = recipes_df[recipes_df['name'] == food_name]
    if not row.empty and 'img_url' in row.columns:
        url = row.iloc[0]['img_url']
        if pd.notna(url) and str(url).startswith('http'):
            return url
    return FOOD_IMAGE_MAP.get(
        food_name,
        f"https://picsum.photos/seed/{food_name}/300/300"
    )

# ---------------- RECOMMEND FUNCTION ----------------
def recommend(food_name):
    food_idx = foodie[foodie['name'] == food_name].index[0]
    dist = similarity[food_idx]
    food_list = sorted(
        list(enumerate(dist)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]
    results = []
    for i in food_list:
        name = foodie.iloc[i[0]]['name']
        row = recipes_df[recipes_df['name'] == name]
        ingredients = row.iloc[0]['ingredients'] if not row.empty and 'ingredients' in row.columns else "Not available"
        cook_time   = row.iloc[0]['cook_time']   if not row.empty and 'cook_time'   in row.columns else "Not available"
        results.append({
            'name':        name,
            'ingredients': ingredients,
            'cook_time':   cook_time
        })
    return results

# ---------------- AI RECIPE FUNCTION ----------------
def get_ai_recipe(food_name, ingredients):
    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type":    "application/json",
                "x-api-key":       api_key,          # ✅ FIXED: API key header added
                "anthropic-version": "2023-06-01"    # ✅ FIXED: required version header
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [{
                    "role": "user",
                    "content": f"""Give me a simple home recipe for {food_name}.
Ingredients available: {ingredients}
Format your response exactly like this:
🍳 RECIPE: {food_name}
⏱ Time: [time]
👥 Serves: [number]

📝 INGREDIENTS:
- [ingredient 1]
- [ingredient 2]

👨‍🍳 STEPS:
1. [step 1]
2. [step 2]
3. [step 3]

💡 TIP: [one quick tip]

Keep it short, simple and friendly!"""
                }]
            }
        )
        data = response.json()
        return data['content'][0]['text']
    except Exception as e:
        return f"Could not generate recipe: {e}"

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Nunito:wght@300;400;600;700&family=Satisfy&display=swap');

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background-color: #E8D5B0;
    background-image:
        radial-gradient(circle at 15% 25%, #DFC49A 0%, transparent 45%),
        radial-gradient(circle at 85% 75%, #D4AF85 0%, transparent 45%);
    font-family: 'Nunito', sans-serif;
    overflow-x: hidden;
}

.floating-foods {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.food-float {
    position: absolute;
    animation: wave 4s ease-in-out infinite;
    opacity: 0.55;
    filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.15));
}

.f1  { top: 5%;  left: 2%;   animation-delay: 0s;    font-size: 58px; }
.f2  { top: 18%; left: 91%;  animation-delay: 0.5s;  font-size: 50px; }
.f3  { top: 35%; left: 3%;   animation-delay: 1s;    font-size: 46px; }
.f4  { top: 50%; left: 93%;  animation-delay: 1.5s;  font-size: 54px; }
.f5  { top: 68%; left: 1%;   animation-delay: 2s;    font-size: 48px; }
.f6  { top: 80%; left: 90%;  animation-delay: 2.5s;  font-size: 52px; }
.f7  { top: 90%; left: 8%;   animation-delay: 0.8s;  font-size: 44px; }
.f8  { top: 8%;  left: 85%;  animation-delay: 1.2s;  font-size: 56px; }
.f9  { top: 60%; left: 6%;   animation-delay: 1.8s;  font-size: 50px; }
.f10 { top: 42%; left: 88%;  animation-delay: 0.3s;  font-size: 46px; }
.f11 { top: 75%; left: 45%;  animation-delay: 2.2s;  font-size: 42px; opacity: 0.3; }
.f12 { top: 12%; left: 48%;  animation-delay: 1.6s;  font-size: 40px; opacity: 0.25; }

@keyframes wave {
    0%   { transform: translateX(0px) rotate(0deg); }
    25%  { transform: translateX(12px) rotate(3deg); }
    50%  { transform: translateX(0px) rotate(0deg); }
    75%  { transform: translateX(-12px) rotate(-3deg); }
    100% { transform: translateX(0px) rotate(0deg); }
}

.stSelectbox label {
    color: #5C3D2E !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    font-family: 'Nunito', sans-serif !important;
}

.stSelectbox > div > div {
    background-color: #FFF3E0 !important;
    border: 2px solid #C4956A !important;
    border-radius: 14px !important;
    color: #3B2A1A !important;
    font-family: 'Nunito', sans-serif !important;
}

.food-card {
    background: linear-gradient(145deg, #FFF8F0, #FDEFD8);
    border: 1.5px solid #D4B896;
    padding: 14px;
    border-radius: 18px;
    text-align: center;
    color: #3B2A1A;
    transition: 0.3s ease;
    box-shadow: 0px 4px 14px rgba(92, 61, 46, 0.12);
    margin-top: 10px;
}
.food-card:hover {
    transform: scale(1.03) translateY(-3px);
    box-shadow: 0px 10px 24px rgba(92, 61, 46, 0.2);
}
.food-card h3 {
    font-size: 14px;
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    color: #3B2A1A;
    margin: 0; padding: 0;
}

.info-pill {
    display: inline-block;
    background: #F5DEB3;
    color: #5C3D2E;
    border-radius: 99px;
    padding: 3px 10px;
    font-size: 11px;
    font-family: 'Nunito', sans-serif;
    margin-top: 6px;
    border: 1px solid #D4B896;
}

.restaurant-btn {
    display: block;
    background: linear-gradient(135deg, #2E7D32, #388E3C);
    color: white !important;
    text-decoration: none !important;
    border-radius: 10px;
    padding: 7px 14px;
    font-size: 12px;
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    text-align: center;
    margin-top: 8px;
    transition: 0.2s;
}
.restaurant-btn:hover {
    background: linear-gradient(135deg, #1B5E20, #2E7D32);
    transform: translateY(-1px);
}

.stButton > button {
    background: linear-gradient(135deg, #7C4A2D, #5C3D2E);
    color: #FFF8F0;
    border-radius: 14px;
    height: 52px;
    width: 230px;
    font-size: 16px;
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    border: none;
    display: block;
    margin: 0 auto;
    transition: 0.25s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #5C3D2E, #3B2A1A);
    color: #FFF8F0;
    border: none;
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(92, 61, 46, 0.35);
}

.stImage img {
    border-radius: 16px !important;
    border: 2px solid #D4B896 !important;
}

.recipe-box {
    background: #FFF8F0;
    border: 1.5px solid #D4B896;
    border-radius: 14px;
    padding: 16px;
    font-family: 'Nunito', sans-serif;
    color: #3B2A1A;
    font-size: 14px;
    line-height: 1.7;
    white-space: pre-wrap;
}

hr {
    border: none;
    border-top: 1.5px solid #C4A882;
    margin: 16px auto;
    width: 50%;
    opacity: 0.6;
}
</style>

<div class="floating-foods">
    <div class="food-float f1">🍛</div>
    <div class="food-float f2">🧆</div>
    <div class="food-float f3">🍟</div>
    <div class="food-float f4">🍮</div>
    <div class="food-float f5">🥘</div>
    <div class="food-float f6">🍔</div>
    <div class="food-float f7">🍱</div>
    <div class="food-float f8">🌭</div>
    <div class="food-float f9">🥗</div>
    <div class="food-float f10">🍭</div>
    <div class="food-float f11">🥂</div>
    <div class="food-float f12">🍜</div>
    <div class="food-float f13">🍕</div>
    <div class="food-float f14">🧁</div>
    <div class="food-float f15">🫐</div>
    <div class="food-float f16">🥪</div>
    <div class="food-float f17">🌮</div>
    <div class="food-float f12">🌽</div>
    <div class="food-float f13">🥐</div>
    <div class="food-float f14">🥨</div>
    <div class="food-float f15">🎂</div>
    <div class="food-float f16">🥙</div>
    <div class="food-float f17">🍥</div>
    <div class="food-float f12">🍽️</div>
    <div class="food-float f13">🥑</div>
    <div class="food-float f14">🍫</div>
    <div class="food-float f15">🍳</div>
    <div class="food-float f16">🥬</div>
    <div class="food-float f17">🍩</div>
</div>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown(
    "<h1 style='text-align:center; color:#3B1F0E; font-family:Playfair Display,serif; font-size:56px; margin-top:30px; letter-spacing:-1px; position:relative; z-index:1;'>🍽 FoodieFinder</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center; color:#7A4F2E; font-family:Satisfy,cursive; font-size:24px; margin-top:4px; position:relative; z-index:1;'>Because choosing food should be delicious.</p>",
    unsafe_allow_html=True
)
st.markdown("<hr>", unsafe_allow_html=True)
st.write("")

# ---------------- SELECT BOX ----------------
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    selected_food_name = st.selectbox(
        "🍕 What are you craving today?",
        foodie['name'].values
    )

st.write("")

# ---------------- BUTTON ----------------
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    recommend_clicked = st.button('✨ Find Similar Foods')

# ---------------- RESULTS ----------------
if recommend_clicked:
    try:
        recommendations = recommend(selected_food_name)

        st.write("")
        st.markdown(
            "<h2 style='color:#3B1F0E; text-align:center; font-family:Playfair Display,serif; margin-top:20px;'>Recommended for you 🌿</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<p style='text-align:center; color:#9A7B5E; font-size:15px; font-family:Nunito,sans-serif;'>Because you liked <strong>{selected_food_name}</strong></p>",
            unsafe_allow_html=True
        )
        st.write("")

        cols = st.columns(5)
        for idx, food_data in enumerate(recommendations):
            food      = food_data['name']
            ingr      = food_data['ingredients']
            cook_time = food_data['cook_time']
            image_url = get_food_image(food)

            maps_url = f"https://www.google.com/maps/search/{food.replace(' ', '+')}+restaurant+near+me"

            with cols[idx]:
                st.image(image_url, use_container_width=True)

                st.markdown(f"""
                <div class="food-card">
                    <h3>{food}</h3>
                    <span class="info-pill">⏱ {cook_time}</span>
                    <p style="color:#9A7B5E; font-size:11px; margin-top:8px;">
                        🧂 {str(ingr)[:60]}{'...' if len(str(ingr)) > 60 else ''}
                    </p>
                    <a href="{maps_url}" target="_blank" class="restaurant-btn">
                        📍 Find Restaurant
                    </a>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("📖 Get AI Recipe"):
                    if st.button(f"Generate Recipe for {food}", key=f"recipe_{idx}"):
                        with st.spinner("🍳 Cooking up a recipe..."):
                            recipe = get_ai_recipe(food, ingr)
                            st.markdown(
                                f"<div class='recipe-box'>{recipe}</div>",
                                unsafe_allow_html=True
                            )

        st.write("")
        st.markdown("""
        <div style='text-align:center; font-size:28px; margin-top:10px; letter-spacing:6px; opacity:0.5;'>
            🥘 &nbsp; 🍱 &nbsp; 🥗 &nbsp; 🍲 &nbsp; 🧆
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Something went wrong: {e}. Please try another food.")

# ---------------- FOOTER ----------------
st.write("")
st.markdown("""
<p style='text-align:center; color:#B8906A; font-size:13px; font-family:Satisfy,cursive; margin-top:50px;'>
    Made with 🤍 · FoodieFinder © 2025
</p>
""", unsafe_allow_html=True)