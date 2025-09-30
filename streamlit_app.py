# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# App UI
st.title("🥤 Customize your smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# Input for name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Query fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col('SEARCH_ON'))
st.dataframe(data=my_dataframe, use_container_width = True)
st.stop()   

pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()

# Convert Snowpark DataFrame to list of fruit names
fruit_options = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Ingredient selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=fruit_options,
    max_selections=5
)

# If user selected ingredients
if ingredients_list:
    
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen )
        sf_df = st.dataframe(data = smoothiefroot_response.json(), use_container_width = True)

    # Prepare SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.code(my_insert_stmt)  # Show the SQL for transparency

    # Button to submit order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered! ✅')


smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
sf_df = st.dataframe(data = smoothiefroot_response.json(), use_container_width = True)
