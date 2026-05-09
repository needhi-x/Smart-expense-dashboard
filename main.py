import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Create folders
os.makedirs("data", exist_ok=True)
os.makedirs("images", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# ----------------------------
# 1. GENERATE DATA
# ----------------------------
np.random.seed(42)

dates = pd.date_range(start="2024-01-01", end="2024-03-31")

data = {
    "date": np.random.choice(dates, 150),
    "category": np.random.choice(
        ["Food", "Transport", "Shopping", "Bills", "Entertainment"], 150
    ),
    "amount": np.random.randint(100, 2000, 150),
    "payment_method": np.random.choice(
        ["Cash", "UPI", "Card"], 150
    ),
    "notes": ["Expense"] * 150,
}

df = pd.DataFrame(data)

# Save dataset
df.to_csv("data/expenses.csv", index=False)

# ----------------------------
# 2. CLEANING
# ----------------------------
df["date"] = pd.to_datetime(df["date"])
df["month"] = df["date"].dt.to_period("M")

# ----------------------------
# 3. ANALYSIS
# ----------------------------
category_expense = df.groupby("category")["amount"].sum().reset_index()
monthly_expense = df.groupby("month")["amount"].sum().reset_index()
payment_expense = df.groupby("payment_method")["amount"].sum()
daily_expense = df.groupby("date")["amount"].sum()

# ----------------------------
# 4. INSIGHTS
# ----------------------------
highest_category = category_expense.loc[category_expense["amount"].idxmax(), "category"]
total_spending = df["amount"].sum()
average_daily = daily_expense.mean()

# ----------------------------
# 5. VISUALIZATION
# ----------------------------
category_expense.plot(x="category", y="amount", kind="bar", title="Category-wise Spending")
plt.tight_layout()
plt.savefig("images/category_bar.png")
plt.close()

monthly_expense.plot(x="month", y="amount", kind="line", marker="o", title="Monthly Spending Trend")
plt.tight_layout()
plt.savefig("images/monthly_line.png")
plt.close()

payment_expense.plot(kind="pie", autopct="%1.1f%%", title="Payment Methods")
plt.ylabel("")
plt.tight_layout()
plt.savefig("images/payment_pie.png")
plt.close()

daily_expense.plot(title="Daily Spending Trend")
plt.tight_layout()
plt.savefig("images/daily_trend.png")
plt.close()

# ----------------------------
# 6. REPORTS (UPGRADED ✅)
# ----------------------------

# 1. Summary Report
summary_report = pd.DataFrame({
    "Metric": ["Total Spending", "Highest Category", "Average Daily Spending"],
    "Value": [total_spending, highest_category, round(average_daily, 2)]
})

summary_report.to_csv("outputs/summary_report.csv", index=False)

# 2. Category Report
category_expense.to_csv("outputs/category_report.csv", index=False)

# 3. Monthly Report
monthly_expense.to_csv("outputs/monthly_report.csv", index=False)

print("\n✅ Multiple Reports Generated Successfully!")