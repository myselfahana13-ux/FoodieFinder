import pandas as pd
import requests
import os
import time

df = pd.read_csv('Food_data/new_df.csv')

def get_info(food_name):
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Content-Type": "application/json",
            "x-api-key": "YOUR_API_KEY_HERE",
            "anthropic-version": "2023-06-01"
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 200,
            "messages": [{
                "role": "user",
                "content": f"""For the Indian food '{food_name}', give me:
1. Main ingredients (comma separated, max 6)
2. Cook time (e.g. 30 mins)

Reply in exactly this format only, nothing else:
INGREDIENTS: ingredient1, ingredient2, ingredient3
COOK_TIME: XX mins"""
            }]
        }
    )
    text = response.json()['content'][0]['text']
    ingredients = text.split('INGREDIENTS:')[1].split('\n')[0].strip()
    cook_time = text.split('COOK_TIME:')[1].strip()
    return ingredients, cook_time

ingredients_list = []
cook_time_list = []

for idx, row in df.iterrows():
    print(f"Processing {row['name']}...")
    try:
        ing, ct = get_info(row['name'])
        ingredients_list.append(ing)
        cook_time_list.append(ct)
        time.sleep(0.5)  # avoid rate limit
    except:
        ingredients_list.append("Not available")
        cook_time_list.append("Not available")

df['ingredients'] = ingredients_list
df['cook_time'] = cook_time_list
df.to_csv('Food_data/new_df.csv', index=False)
print("Done! CSV updated.")