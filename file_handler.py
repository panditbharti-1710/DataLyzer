import pandas as pd


def upload_csv(file_path):

    if not file_path:
        return None, "No file provided"

    if not file_path.endswith(".csv"):
        return None, "Only CSV files allowed"

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return None, str(e)

    if df.empty:
        return None, "File is empty"

    return df, None


def validate_csv_format(df):

    if df is None:
        return False

    if df.shape[0] == 0 or df.shape[1] == 0:
        return False

    return True


def reset_session():
    return True
