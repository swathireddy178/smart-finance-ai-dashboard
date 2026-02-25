import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)

def ask_finance_ai(question, monthly_df, category_df):

    monthly_text = monthly_df.to_string(index=False)
    category_text = category_df.to_string(index=False)

    prompt = f"""
You are FinSight AI financial advisor.

Monthly Spending Data:
{monthly_text}

Category Spending Data:
{category_text}

Question:
{question}

Give clear answer using data.
"""

    res = client.chat.completions.create(
        model="meta/llama3-8b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=400
    )

    return res.choices[0].message.content