import pandas as pd
from transformers import pipeline


_model = None


def load_nlp_model():

    global _model

    if _model is None:
        _model = pipeline(
            "summarization",
            model="sshleifer/distilbart-cnn-12-6"
        )

    return _model


def generate_trend_text(trend, start, end):

    if trend is None:
        return None

    pct = ((end - start) / start * 100) if start != 0 else 0
    pct = round(pct, 2)

    if trend == "increasing":
        return f"Values increased from {start} to {end} ({pct}%)."

    elif trend == "decreasing":
        return f"Values decreased from {start} to {end} ({abs(pct)}%)."

    else:
        return f"Values remained stable between {start} and {end}."


def generate_comparison_text(top, low, diff):

    if top is None or low is None:
        return None

    if diff > 0:
        return f"{top} performed best while {low} performed worst. Difference is {diff}."

    return "Both categories performed equally."


def build_analysis_text(insights):

    text = ""

    for value in insights.values():
        if value:
            text += value + " "

    return text.strip()


def generate_human_summary(text):

    if not text:
        return None

    model = load_nlp_model()

    try:
        result = model(text, max_length=120, min_length=30)
        return result[0]["summary_text"]
    except:
        return text


def detect_sensitive_columns(df):

    sensitive_keywords = [
        "name",
        "email",
        "phone",
        "mobile",
        "aadhaar",
        "pan",
        "account",
        "password",
        "address"
    ]

    # Columns NOT to mask even if they contain "name"
    allowed_name_columns = [
        "product_name",
        "brand_name",
        "company_name",
        "category_name", 
        "customer_name", 
        "customers_name"
    ]

    for col in df.columns:

        col_lower = col.lower()

        # Skip allowed columns
        if col_lower in allowed_name_columns:
            continue

        # Mask if sensitive keyword found
        if any(key in col_lower for key in sensitive_keywords) or \
           ("name" in col_lower and "product" not in col_lower):

            df[col] = df[col].astype(str).apply(
                lambda x: x[:2] + "***" if len(x) > 2 else "***"
            )

    return df


def mask_sensitive_data(df, columns):

    for col in columns:
        df[col] = df[col].apply(
            lambda x: "*" * len(str(x)) if pd.notnull(x) else x
        )

    return df


def apply_privacy_rules(df):

    sensitive_keywords = [
        "email", "phone", "mobile",
        "aadhaar", "pan", "address"
    ]

    cols_to_mask = []

    for col in df.columns:
        for key in sensitive_keywords:
            if key.lower() in col.lower():
                cols_to_mask.append(col)
                break

    # ⭐ SAFE CHECK
    if len(cols_to_mask) > 0:
        for col in cols_to_mask:
            df[col] = "***MASKED***"

    return df