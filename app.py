import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="COSSA 80th Function Food Tracker", page_icon="🍽️", layout="centered")

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

items_needed = {
    "Pies": 400,
    "Samoosas": 400,
    "Pizza": 250,
    "Koeksisters": 150,
    "Bolaas": 150,
    "Bread loaves": 4,
    "Cheese kg": 1.0,
    "Spice beef kg": 2.0,
    "Tomatoes kg": 2.0,
    "Lettuce g": 500,
    "Coffee boxes": 2,
    "Tea boxes": 2,
    "Milk 2L": 10,
    "Drinks 2L": 10,
    "Water 2L": 10,
    "Flora Margarine 500g": 2,
    "Serviettes": 500,
    "Refresher Towel Sachets": 500,
    "Paper Plates": 250,
    "Paper Cups": 250,
}

decimal_items = {
    "Cheese kg",
    "Spice beef kg",
    "Tomatoes kg",
}

st.title("COSSA 80th Function 🍽️ Food Tracker")

response = supabase.table("contributions").select("*").order("created_at", desc=True).execute()
rows = response.data

df = pd.DataFrame(rows)

summary = []

for item, needed in items_needed.items():
    received = 0.0

    if not df.empty:
        received = df[df["item"] == item]["quantity"].sum()

    received = float(received)
    remaining = max(float(needed) - received, 0)

    summary.append({
        "Item": item,
        "Needed": needed,
        "Received": round(received, 2) if item in decimal_items else int(received),
        "Remaining": round(remaining, 2) if item in decimal_items else int(remaining),
    })

summary_df = pd.DataFrame(summary)

st.subheader("📊 Summary")
st.dataframe(summary_df, hide_index=True, use_container_width=True)

with st.form("contribution_form"):
    name = st.text_input("Your name")
    item = st.selectbox("What are you contributing?", list(items_needed.keys()))

    if item in decimal_items:
        quantity = st.number_input("Quantity", min_value=0.1, step=0.1, format="%.2f")
    else:
        quantity = st.number_input("Quantity", min_value=1, step=1)

    note = st.text_input("Note optional")

    submitted = st.form_submit_button("Submit contribution")

    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
        else:
            supabase.table("contributions").insert({
                "name": name.strip(),
                "item": item,
                "quantity": float(quantity) if item in decimal_items else int(quantity),
                "note": note.strip()
            }).execute()

            st.success("Contribution saved successfully.")
            st.rerun()

st.subheader("📝 Contributions")
if df.empty:
    st.info("No contributions yet.")
else:
    st.dataframe(
        df[["name", "item", "quantity", "note", "created_at"]],
        hide_index=True,
        use_container_width=True
    )
