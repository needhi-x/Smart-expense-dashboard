import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

# ---------------- DATABASE ----------------
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    category TEXT,
    amount REAL,
    payment_method TEXT,
    notes TEXT
)
""")
conn.commit()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Fintech Dashboard", layout="wide")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
    .main {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("💳 Smart Expense Dashboard")

# ---------------- ADD EXPENSE ----------------
st.sidebar.header("➕ Add Expense")

with st.sidebar.form("expense_form", clear_on_submit=True):
    date = st.date_input("Date", datetime.today())
    category = st.selectbox("Category", ["Food", "Shopping", "Bills", "Transport", "Entertainment"])
    amount = st.number_input("Amount", min_value=0)
    payment = st.selectbox("Payment Method", ["UPI", "Card", "Cash"])
    notes = st.text_input("Notes")

    submitted = st.form_submit_button("Add Expense")

    if submitted:
        cursor.execute(
            "INSERT INTO expenses (date, category, amount, payment_method, notes) VALUES (?, ?, ?, ?, ?)",
            (str(date), category, amount, payment, notes)
        )
        conn.commit()
        st.sidebar.success("✅ Expense Added!")

# ---------------- LOAD DATA ----------------
df = pd.read_sql_query("SELECT * FROM expenses", conn)

if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # ---------------- EDIT / DELETE TABLE ----------------
    st.subheader("📋 Manage Expenses")

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True
    )

    colA, colB = st.columns(2)

    # -------- UPDATE BUTTON --------
    with colA:
        if st.button("💾 Save Changes"):
            for i, row in edited_df.iterrows():
                cursor.execute("""
                    UPDATE expenses
                    SET date=?, category=?, amount=?, payment_method=?, notes=?
                    WHERE id=?
                """, (
                    str(row["date"]),
                    row["category"],
                    row["amount"],
                    row["payment_method"],
                    row["notes"],
                    row["id"]
                ))
            conn.commit()
            st.success("✅ Changes Saved!")
            st.rerun()

    # -------- DELETE BUTTON --------
    with colB:
        delete_id = st.number_input("Enter ID to delete", min_value=1, step=1)
        if st.button("🗑️ Delete Expense"):
            cursor.execute("DELETE FROM expenses WHERE id=?", (delete_id,))
            conn.commit()
            st.warning("🗑️ Expense Deleted!")
            st.rerun()

    # ---------------- FILTERS ----------------
    st.sidebar.header("🔍 Filters")

    category_filter = st.sidebar.multiselect(
        "Category", df["category"].unique(),
        default=df["category"].unique()
    )

    payment_filter = st.sidebar.multiselect(
        "Payment Method", df["payment_method"].unique(),
        default=df["payment_method"].unique()
    )

    budget = st.sidebar.number_input("💰 Monthly Budget", value=10000)

    filtered_df = df[
        (df["category"].isin(category_filter)) &
        (df["payment_method"].isin(payment_filter))
    ]

    # ---------------- KPIs ----------------
    total = filtered_df["amount"].sum()
    avg = filtered_df["amount"].mean()

    top_category = "N/A"
    if not filtered_df.empty:
        top_category = filtered_df.groupby("category")["amount"].sum().idxmax()

    c1, c2, c3 = st.columns(3)
    c1.metric("💸 Total Spending", f"₹{int(total)}")
    c2.metric("📊 Average Spending", f"₹{round(avg,2)}")
    c3.metric("🏆 Top Category", top_category)

    # ---------------- BUDGET ALERT ----------------
    st.subheader("🚨 Budget Status")

    if total > budget:
        st.error(f"⚠️ Over budget by ₹{int(total - budget)}")
    elif total > 0.8 * budget:
        st.warning("⚠️ Close to budget limit")
    else:
        st.success("✅ Within budget")

    # ---------------- AI INSIGHTS ----------------
    st.subheader("🤖 AI Insights")

    if not filtered_df.empty:
        cat_spend = filtered_df.groupby("category")["amount"].sum()

        if cat_spend.max() > 0.4 * total:
            st.info(f"💡 You are spending most on {cat_spend.idxmax()}")

        if avg > 500:
            st.info("💡 Your average spending is high")

    # ---------------- CHARTS ----------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Category Spending")
        fig1 = px.bar(
            filtered_df.groupby("category")["amount"].sum().reset_index(),
            x="category", y="amount", color="category"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("🥧 Payment Distribution")
        fig2 = px.pie(filtered_df, names="payment_method", values="amount")
        st.plotly_chart(fig2, use_container_width=True)

    # ---------------- TREND ----------------
    st.subheader("📈 Daily Trend")

    daily = filtered_df.groupby("date")["amount"].sum().reset_index()
    fig3 = px.line(daily, x="date", y="amount", markers=True)
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.info("No data yet. Add expenses from sidebar 👈")