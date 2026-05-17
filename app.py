import streamlit as st
import pandas as pd
import pickle
import requests

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="FoodieFinder",
    page_icon="🍕",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
food_dict = pickle.load(open('food_dict.pkl', 'rb'))
foodie = pd.DataFrame(food_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# ---------------- FOOD IMAGE API (TMDB STYLE) ----------------
@st.cache_data
def get_food_image(food_name):

    try:
        # Wikipedia API (acts like TMDB poster lookup)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{food_name}"
        response = requests.get(url, timeout=5)
        data = response.json()

        if "thumbnail" in data:
            return data["thumbnail"]["source"]

    except:
        pass

    # fallback (always works)
    return f"https://picsum.photos/seed/{food_name}/300/300"

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

.main {
    background: linear-gradient(to right, #141e30, #243b55);
}

.food-card {
    background-color: #1f2937;
    padding: 20px;
    border-radius: 20px;
    text-align: center;
    color: white;
    transition: 0.3s;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    height: 100%;
}

.food-card:hover {
    transform: scale(1.05);
    background-color: #374151;
}

.food-img {
    border-radius: 15px;
    width: 100%;
    height: 180px;
    object-fit: cover;
}

.stButton>button {
    background-color: #ff4b4b;
    color: white;
    border-radius: 10px;
    height: 50px;
    width: 200px;
    font-size: 18px;
    border: none;
}

.stButton>button:hover {
    background-color: #ff1e1e;
}

</style>
""", unsafe_allow_html=True)

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

# ---------------- BUTTON ----------------
if st.button('🍽 Recommend Foods'):

    recommendations = recommend(selected_food_name)

    st.markdown(
        "<h2 style='color:white;'>Recommended Foods For You 😍</h2>",
        unsafe_allow_html=True
    )

    cols = st.columns(5)

    for idx, food in enumerate(recommendations):

        image_url = get_food_image(food)

        with cols[idx]:

            st.markdown(
                f"""
                <div class="food-card">

                    <img class="food-img" src="{image_url}">

                    <h3 style="margin-top:15px;">{food}</h3>

                    <p style="color:gray; font-size:12px;">
                        TMDB-style recommendation engine 🍴
                    </p>

                </div>
                """,
                unsafe_allow_html=True
            )