import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be", name_on_order)

# Connection from Streamlit Community Cloud Secrets
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

fruit_options = [
    row["FRUIT_NAME"]
    for row in my_dataframe.collect()
]

ingredients_list = st.multiselect(
    "Choose Up to 5 Ingredients:",
    fruit_options,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/watermelon"
        )

        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        my_insert_stmt = f"""
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS
            (INGREDIENTS, NAME_ON_ORDER)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """

        session.sql(my_insert_stmt).collect()

        st.success(
            f"Your Smoothie is Ordered, {name_on_order}!",
            icon="✅"
        )
