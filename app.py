import streamlit as st
import pandas as pd
import pickle

# Page config
st.set_page_config(
    page_title="FoodieFinder",
    page_icon="🍩",
    layout="wide"
)

# Load data
food_dict = pickle.load(open('food_dict.pkl', 'rb'))
foodie = pd.DataFrame(food_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# Recommendation function
def recommend(food_name):

    food_idx = foodie[foodie['name'] == food_name].index[0]

    dist = similarity[food_idx]

    food_list = sorted(
        list(enumerate(dist)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_food = []

    for i in food_list:
        recommended_food.append(
            foodie.iloc[i[0]]['name']
        )

    return recommended_food


# Title
st.markdown(
    "<h1 style='text-align:center; color:#ff4b4b;'>🍕Food Recommender System</h1>",
    unsafe_allow_html=True
)

st.write("### Discover food similar to your favorites 🍿")


# Select Box
selected_food_name = st.selectbox(
    "Choose a food",
    foodie['name'].values
)


# Recommendation Button
if st.button('Recommend'):

    recommendations = recommend(selected_food_name)

    st.write("## Recommended Food")

    cols = st.columns(5)

    for idx, food in enumerate(recommendations):

        with cols[idx]:
            st.markdown(
                f"""
                <div style="
                    background-color:#262730;
                    padding:20px;
                    border-radius:15px;
                    text-align:center;
                    color:white;
                    height:150px;
                ">
                    <h4>{food}</h4>
                </div>
                """,
                unsafe_allow_html=True
            )