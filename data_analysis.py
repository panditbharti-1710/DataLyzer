import pandas as pd


def get_basic_statistics(df):

    if df is None:
        return None

    return df.describe(include="all")


def find_max_min(df, column):

    if column not in df.columns:
        return None, None

    return df[column].max(), df[column].min()


def find_mean_mode(df, column):

    if column not in df.columns:
        return None, None

    mean_val = df[column].mean()

    mode_val = df[column].mode()
    mode_val = mode_val.iloc[0] if not mode_val.empty else None

    return mean_val, mode_val


def grouped_by_category(df, cat_col, num_col):

    if cat_col not in df.columns or num_col not in df.columns:
        return None

    return df.groupby(cat_col)[num_col].sum()


def compare_categories(grouped_data):

    if grouped_data is None or grouped_data.empty:
        return None, None

    highest = grouped_data.idxmax()
    lowest = grouped_data.idxmin()

    return highest, lowest


def detect_trend(df, num_col, date_col):

    if date_col not in df.columns or num_col not in df.columns:
        return None

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    if df[date_col].isnull().all():
        return None

    df = df.sort_values(by=date_col)

    start = df[num_col].iloc[0]
    end = df[num_col].iloc[-1]

    if end > start:
        return "increasing"
    elif end < start:
        return "decreasing"
    else:
        return "stable"
