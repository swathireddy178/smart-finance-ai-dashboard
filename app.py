import streamlit as st
import plotly.express as px
import pandas as pd

from auth import create_users_table, login_user, signup_user
from analysis import load_data, get_user_data, monthly_spending, spending_metrics, category_spending
from ai_advisor import ask_finance_ai

# ================= PAGE CONFIG =================
st.set_page_config(layout="wide")

# ================= SESSION STATE =================
if "user" not in st.session_state:
    st.session_state.user = None

if "show_ai_sidebar" not in st.session_state:
    st.session_state.show_ai_sidebar = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ================= DB INIT =================
create_users_table()

# ================= DARK WHITE PREMIUM CSS =================
st.markdown("""
<style>
.stApp { background:#020617; color:white; }
section[data-testid="stSidebar"] { background:#020617; }
section[data-testid="stSidebar"] * { color:white !important; }
h1,h2,h3,h4,h5,h6,label,p,span,div { color:white !important; }
input,textarea { background:#020617 !important; color:white !important; border:1px solid rgba(255,255,255,0.15) !important; }
div[data-baseweb="select"] > div { background:#020617 !important; color:white !important; border:1px solid rgba(255,255,255,0.15) !important; }
div[data-baseweb="popover"] * { background:#020617 !important; color:white !important; }
.stButton button { background: linear-gradient(135deg,#6366F1,#06B6D4); border:none; color:white; border-radius:10px; }
[data-testid="stMetric"] { background: rgba(15,23,42,0.8); padding:20px; border-radius:16px; border:1px solid rgba(255,255,255,0.06); }
</style>
""", unsafe_allow_html=True)

# ================= NAVBAR =================
st.markdown("### 💳 Smart Finance AI Dashboard")

# ================= LOGIN UI =================
if st.session_state.user is None:

    st.sidebar.title("Navigation")
    nav = st.sidebar.radio("", ["Login","Create Account","Reset Password"])

    if nav == "Login":
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(email,pwd)=="success":
                st.session_state.user=email
                st.rerun()
            else:
                st.error("Invalid login")

    if nav == "Create Account":
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Create Account"):
            signup_user(email,email,pwd)
            st.success("Account created")

    if nav == "Reset Password":
        st.text_input("Email")
        st.text_input("Temporary Password")
        st.text_input("New Password", type="password")
        st.text_input("Confirm Password", type="password")
        st.button("Reset Password")

    st.stop()

# ================= LOAD DATA =================
df = load_data("data/credit_card_transactions.csv")
df["year"] = pd.to_datetime(df["trans_date_trans_time"]).dt.year

# ================= SIDEBAR ANALYTICS OPTIONS =================
st.sidebar.title(f"Welcome {st.session_state.user}")

card = st.sidebar.selectbox("Select Card", df["cc_num"].unique())

analysis_mode = st.sidebar.selectbox(
    "Select Analysis View",
    [
        "Dashboard Overview",
        "Yearly Spend Analysis",
        "Highest Spending Category",
        "Product / Category Deep Dive"
    ]
)

user_df = get_user_data(df, card)
user_df["year"] = pd.to_datetime(user_df["trans_date_trans_time"]).dt.year

# ================= DEFAULT METRICS =================
monthly = monthly_spending(user_df)
monthly["month"] = monthly["trans_date_trans_time"].dt.strftime("%b %Y")

cat = category_spending(user_df)
metrics = spending_metrics(user_df)

# ================= VIEW 1: DASHBOARD =================
if analysis_mode == "Dashboard Overview":

    st.title("📊 Financial Dashboard")

    k1,k2,k3 = st.columns(3)
    k1.metric("Total Spend", f"${metrics['total']:,.0f}")
    k2.metric("Avg Spend", f"${metrics['avg']:,.0f}")
    k3.metric("Max Spend", f"${metrics['max']:,.0f}")

    chart_type = st.selectbox("Select Chart Type",
        ["Monthly Trend (Line)","Category (Bar)","Monthly Distribution (Pie)"])

    if chart_type == "Monthly Trend (Line)":
        st.plotly_chart(px.line(monthly,x="month",y="amt"), use_container_width=True)

    if chart_type == "Category (Bar)":
        st.plotly_chart(px.bar(cat,x="category",y="amt"), use_container_width=True)

    if chart_type == "Monthly Distribution (Pie)":
        st.plotly_chart(px.pie(monthly,names="month",values="amt", title="Monthly Spend Distribution"), use_container_width=True)

# ================= VIEW 2: YEARLY SPEND =================
if analysis_mode == "Yearly Spend Analysis":

    st.title("📅 Yearly Spending Analysis")

    yearly = user_df.groupby("year")["amt"].sum().reset_index()

    st.metric("Total Years Tracked", len(yearly))
    st.metric("Highest Year Spend", f"${yearly['amt'].max():,.0f}")

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(px.bar(yearly, x="year", y="amt", title="Yearly Spending"), use_container_width=True)

    with col2:
        st.plotly_chart(px.pie(yearly, names="year", values="amt", title="Yearly Spend Distribution"), use_container_width=True)

# ================= VIEW 3: HIGHEST CATEGORY =================
if analysis_mode == "Highest Spending Category":

    st.title("🏆 Highest Spending Category")

    top_cat = cat.sort_values("amt", ascending=False).iloc[0]

    st.metric("Top Category", top_cat["category"])
    st.metric("Amount Spent", f"${top_cat['amt']:,.2f}")

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(px.bar(cat.sort_values("amt", ascending=False), x="category", y="amt", title="Category Ranking"), use_container_width=True)

    with col2:
        st.plotly_chart(px.pie(cat, names="category", values="amt", title="Category Spend Distribution"), use_container_width=True)

# ================= VIEW 4: DEEP DIVE =================
if analysis_mode == "Product / Category Deep Dive":

    st.title("🔍 Category Deep Dive")

    selected_cat = st.selectbox("Select Category", user_df["category"].unique())

    cat_df = user_df[user_df["category"] == selected_cat]

    st.metric("Total Spend In Category", f"${cat_df['amt'].sum():,.2f}")
    st.metric("Transactions Count", len(cat_df))

    cat_month = cat_df.groupby(cat_df["trans_date_trans_time"].dt.to_period("M"))["amt"].sum().reset_index()
    cat_month["trans_date_trans_time"] = cat_month["trans_date_trans_time"].astype(str)

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(px.line(cat_month, x="trans_date_trans_time", y="amt", title="Category Monthly Trend"), use_container_width=True)

    with col2:
        cat_total = cat_df.groupby("category")["amt"].sum().reset_index()
        st.plotly_chart(px.pie(cat_total, names="category", values="amt", title="Category Share"), use_container_width=True)

# ================= AI =================
if st.button("🤖 AI Assistant"):
    st.session_state.show_ai_sidebar = not st.session_state.show_ai_sidebar

if st.session_state.show_ai_sidebar:

    st.sidebar.markdown("## AI Financial Assistant")

    for msg in st.session_state.chat_history:
        if msg["role"]=="user":
            st.sidebar.markdown(f"**You:** {msg['text']}")
        else:
            st.sidebar.markdown(f"**AI:** {msg['text']}")

    q = st.sidebar.text_input("Ask finance question")

    if q:
        st.session_state.chat_history.append({"role":"user","text":q})
        reply = ask_finance_ai(q, monthly, cat)
        st.session_state.chat_history.append({"role":"ai","text":reply})
        st.rerun()