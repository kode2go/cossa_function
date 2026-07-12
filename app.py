import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(
    page_title="COSSA 80th Function Food Tracker",
    page_icon="🍽️",
    layout="centered"
)

TABLE_NAME = "contributions"

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
    "Coffee Tin 500g": 4,
    "Tea boxes (100 pack)": 2,
    "Milk 2L": 10,
    "Drinks 2L": 10,
    "Water 2L": 10,
    "Flora Margarine 500g": 2,
    "Serviettes": 500,
    "Refresher Towel Sachets": 500,
    "Paper Plates": 250,
    "Paper Cups": 250,
    "White Plastic Sheets (m)": 20, 
}

decimal_items = {
    "Cheese kg",
    "Spice beef kg",
    "Tomatoes kg",
}

@st.dialog("Contribution Recorded")
def show_success_modal(name, item, quantity):
    qty_display = f"{quantity:.2f}" if item in decimal_items else str(int(quantity))

    st.markdown(f"""
### ✅ Thank you!

**Name:** {name}  
**Item:** {item}  
**Quantity:** {qty_display}
""")

    if st.button("Close"):
        st.rerun()

st.title("COSSA 80th Function 🍽️ Food Tracker v1.1")

# Load contributions
response = supabase.table(TABLE_NAME).select("*").order("created_at", desc=True).execute()
rows = response.data
df = pd.DataFrame(rows)

# Summary table
summary = []

for item_name, needed in items_needed.items():
    received = 0.0

    if not df.empty:
        item_rows = df[df["item"] == item_name].copy()
        if not item_rows.empty:
            received = pd.to_numeric(item_rows["quantity"], errors="coerce").fillna(0).sum()

    received = float(received)
    remaining = max(float(needed) - received, 0)

    if item_name in decimal_items:
        display_needed = f"{float(needed):.2f}"
        display_received = f"{received:.2f}"
        display_remaining = f"{remaining:.2f}"
    else:
        display_needed = str(int(float(needed)))
        display_received = str(int(received))
        display_remaining = str(int(remaining))

    summary.append({
        "Item": item_name,
        "Needed": display_needed,
        "Received": display_received,
        "Remaining": display_remaining,
    })

summary_df = pd.DataFrame(summary)

st.subheader("📊 Summary")
st.dataframe(summary_df, hide_index=True, use_container_width=True)

# Select item outside the form to avoid stale form values
item = st.selectbox("What are you contributing?", list(items_needed.keys()))

with st.form("contribution_form"):
    name = st.text_input("Your name")

    qty_default = "1.00" if item in decimal_items else "1"
    qty_text = st.text_input("Quantity", value=qty_default, key=f"qty_{item}")

    note = st.text_input("Note optional")

    submitted = st.form_submit_button("Submit contribution")

    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
            st.stop()

        try:
            quantity = float(qty_text)
        except ValueError:
            st.error("Please enter a valid quantity.")
            st.stop()

        if quantity <= 0:
            st.error("Quantity must be greater than 0.")
            st.stop()

        if item not in decimal_items and quantity != int(quantity):
            st.error(f"{item} only allows whole numbers, no decimals.")
            st.stop()

        supabase.table(TABLE_NAME).insert({
            "name": name.strip(),
            "item": item,
            "quantity": float(quantity),
            "note": note.strip()
        }).execute()


        show_success_modal(name, item, quantity)



st.subheader("📝 Contributions")

if df.empty:
    st.info("No contributions yet.")
else:
    display_df = df.copy()

    def format_qty(row):
        if row["item"] in decimal_items:
            return f'{float(row["quantity"]):.2f}'
        return str(int(float(row["quantity"])))

    display_df["quantity"] = display_df.apply(format_qty, axis=1)

    st.dataframe(
        display_df[["name", "item", "quantity", "note", "created_at"]],
        hide_index=True,
        use_container_width=True
    )
