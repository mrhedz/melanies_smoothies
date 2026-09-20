import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be", name_on_order)

# Connect to Snowflake from Streamlit Community Cloud
cnx = st.connection("snowflake")
session = cnx.session()

# Get both the display name and the API search value
my_dataframe = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(
        col("FRUIT_NAME"),
        col("SEARCH_ON")
    )
)

fruit_rows = my_dataframe.collect()

# Values shown to the user in the multiselect
fruit_options = [
    row["FRUIT_NAME"]
    for row in fruit_rows
]

# Map GUI name -> API search value
search_map = {
    row["FRUIT_NAME"]: row["SEARCH_ON"]
    for row in fruit_rows
}

ingredients_list = st.multiselect(
    "Choose Up to 5 Ingredients:",
    fruit_options,
    max_selections=5
)

if ingredients_list:

    ingredients_string = " ".join(ingredients_list)

    for fruit_chosen in ingredients_list:

        # Get the API-compatible value for the chosen fruit
        search_on = search_map[fruit_chosen]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{requests.utils.quote(search_on)}",
            timeout=10
        )

        if smoothiefroot_response.ok:
            st.dataframe(
                data=smoothiefroot_response.json(),
                use_container_width=True
            )
        else:
            st.warning(
                f"No nutrition information was found for {fruit_chosen}."
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
