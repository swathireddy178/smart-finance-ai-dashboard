import pandas as pd

def load_data(path):
    df = pd.read_csv(path)
    df["trans_date_trans_time"] = pd.to_datetime(df["trans_date_trans_time"])
    return df

def get_user_data(df, card):
    return df[df["cc_num"] == card]

def monthly_spending(user_df):
    return user_df.resample("M", on="trans_date_trans_time")["amt"].sum().reset_index()

def spending_metrics(user_df):
    return {
        "total": user_df["amt"].sum(),
        "avg": user_df["amt"].mean(),
        "max": user_df["amt"].max()
    }

def category_spending(user_df):
    return user_df.groupby("category")["amt"].sum().reset_index()
