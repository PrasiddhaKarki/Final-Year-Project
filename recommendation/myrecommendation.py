import streamlit as st 
import pandas as pd
import pickle 



def recommend(food):
    food_index = foods[foods['title'] == food].index[0]
    distances = similarity[food_index]
    food_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])
   
    recommended_food = []
    for i in food_list:
        recommended_food.append(foods.iloc[i[0]].title)
    return recommended_food


st.header('Food Recommender System')
food_dict = pickle.load(open('food_dict.pkl','rb'))
foods = pd.DataFrame(food_dict)
similarity = pickle.load(open('similarity.pkl','rb'))

selected_food_name = st.selectbox( 
    "Type or select a food from the dropdown", foods['title'].values
    )

if st.button('Show Recommendation'):
    recommendations = recommend(selected_food_name)
    for i in recommendations:
      st.write(i)
