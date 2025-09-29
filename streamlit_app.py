# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Get the Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title("🥤 Customize your smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# Get name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Let user pick ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=[row["FRUIT_NAME"] for row in my_dataframe.collect()],
    max_selections=5
)

# If user selected ingredients
if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    # Prepare insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.write("Your order SQL statement:")
    st.code(my_insert_stmt)

    # Submit button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered! ✅')
