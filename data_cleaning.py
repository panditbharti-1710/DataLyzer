import pandas as pd


# =========================================================
# FIX DATA TYPES FIRST
# =========================================================

def correct_data_types(df):

    if df is None:
        return None

    for col in df.columns:

        # Try numeric conversion
        converted_numeric = pd.to_numeric(df[col], errors="coerce")

        # If many values became numbers → use it
        if converted_numeric.notna().sum() > 0:
            df[col] = converted_numeric
            continue

        # Try datetime conversion
        converted_date = pd.to_datetime(df[col], errors="coerce")

        if converted_date.notna().sum() > 0:
            df[col] = converted_date

    return df


# =========================================================
# HANDLE MISSING VALUES SAFELY
# =========================================================

def handle_missing_values(df):

    if df is None:
        return None

    for col in df.columns:

        if pd.api.types.is_numeric_dtype(df[col]):
            median_val = df[col].median()

            if pd.notna(median_val):
                df[col] = df[col].fillna(median_val)
            else:
                df[col] = df[col].fillna(0)

        else:
            df[col] = df[col].fillna("Unknown")

    return df


# =========================================================
# REMOVE DUPLICATES
# =========================================================

def remove_duplicates(df):

    if df is None:
        return None

    return df.drop_duplicates()


# =========================================================
# MAIN CLEAN PIPELINE
# =========================================================

def clean_dataset(df):

    if df is None:
        return None

    # ⭐ Correct order is VERY IMPORTANT
    df = correct_data_types(df)
    df = handle_missing_values(df)
    df = remove_duplicates(df)

    return df

def prepare_clean_dataset(df):
    df = clean_dataset(df)
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
