# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be", name_on_order)

session = get_active_session()

my_dataframe = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

ingredients_list = st.multiselect(
    "Choose Up to 5 Ingredients:",
    my_dataframe,
    max_selections=5
)

if ingredients_list:

    ingredients_string = ""

    for fruits_chosen in ingredients_list:
        ingredients_string += fruits_chosen + " "

    my_insert_stmt = """
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS
        (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('""" + ingredients_string + """', '""" + name_on_order + """')
    """

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(
            f"Your Smoothie is Ordered, {name_on_order}!",
            icon="✅"
        )
