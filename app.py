import streamlit as st
import pandas as pd
import pickle
import os
from food_img import FOOD_IMAGE_MAP

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="FoodieFinder",
    page_icon="🍕",
    layout="wide"
)

# ---------------- LOAD DATA (fixed paths) ----------------
base_dir = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_data():
    food_dict = pickle.load(open(os.path.join(base_dir, 'models', 'food_dict.pkl'), 'rb'))
    similarity = pickle.load(open(os.path.join(base_dir, 'models', 'similarity.pkl'), 'rb'))
    foodie = pd.DataFrame(food_dict)
    return foodie, similarity

foodie, similarity = load_data()

# ---------------- IMAGE FUNCTION ----------------
@st.cache_data
def get_food_image(food_name):
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
    return [foodie.iloc[i[0]]['name'] for i in food_list]

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
/* Hide Streamlit default header/footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Page background */
.stApp {
    background: linear-gradient(135deg, #141e30 0%, #243b55 100%);
}

/* Selectbox label */
.stSelectbox label {
    color: white !important;
    font-size: 16px !important;
}

/* Food card */
.food-card {
    background-color: #1f2937;
    padding: 15px;
    border-radius: 15px;
    text-align: center;
    color: white;
    transition: 0.3s;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    margin-top: 10px;
}
.food-card:hover {
    transform: scale(1.05);
    background-color: #374151;
}
.food-card h3 {
    font-size: 14px;
    margin: 0;
    padding: 0;
}

/* Recommend button */
.stButton > button {
    background-color: #ff4b4b;
    color: white;
    border-radius: 10px;
    height: 50px;
    width: 200px;
    font-size: 18px;
    border: none;
    display: block;
    margin: 0 auto;
}
.stButton > button:hover {
    background-color: #ff1e1e;
    color: white;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown(
    "<h1 style='text-align:center; color:#ff4b4b;'>🍔 FoodieFinder 🍟</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h4 style='text-align:center; color:white;'>Find foods similar to your favorites 😋</h4>",
    unsafe_allow_html=True
)
st.write("")

# ---------------- SELECT BOX ----------------
selected_food_name = st.selectbox(
    "🍕 Choose Your Favorite Food",
    foodie['name'].values
)
st.write("")

# ---------------- BUTTON + RESULTS ----------------
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    recommend_clicked = st.button('🍽 Recommend Foods')

if recommend_clicked:
    try:
        recommendations = recommend(selected_food_name)

        st.markdown(
            "<h2 style='color:white; text-align:center; margin-top:30px;'>Recommended Foods For You 😍</h2>",
            unsafe_allow_html=True
        )

        cols = st.columns(5)
        for idx, food in enumerate(recommendations):
            image_url = get_food_image(food)
            with cols[idx]:
                st.image(image_url, use_container_width=True)
                st.markdown(
                    f"""
                    <div class="food-card">
                        <h3>{food}</h3>
                        <p style="color:#9ca3af; font-size:12px; margin-top:6px;">
                            Similar to {selected_food_name} 🍴
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    except Exception as e:
        st.error(f"Something went wrong: {e}. Please try another food.")