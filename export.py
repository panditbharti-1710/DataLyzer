import os


def export_cleaned_data(df, file_name="cleaned_dataset.csv"):

    if df is None:
        return False, "No data available"

    try:
        df.to_csv(file_name, index=False)
        return True, file_name
    except Exception as e:
        return False, str(e)


def export_anonymized_data(df, file_name="anonymized_dataset.csv"):

    if df is None:
        return False, "No data available"

    try:
        df.to_csv(file_name, index=False)
        return True, file_name
    except Exception as e:
        return False, str(e)


def generate_report(charts=None, summary=None, file_name="auto_report.txt"):

    try:
        with open(file_name, "w") as f:

            f.write("=== DATA ANALYSIS REPORT ===\n\n")

            if summary:
                f.write("SUMMARY:\n")
                if isinstance(summary, list):
                    for part in summary:
                        f.write(part + "\n\n")
                else:
                    f.write(summary + "\n\n")

            if charts:
                f.write("CHARTS:\n")
                for chart in charts:
                    f.write(f"- {chart}\n")

        return True, file_name

    except Exception as e:
        return False, str(e)


def log_user_action(action):

    try:
        with open("system_log.txt", "a") as f:
            f.write(action + "\n")
    except:
        pass


def handle_errors(error):

    return {"error": str(error)}


def check_system_requirements():

    required = ["pandas", "matplotlib"]

    missing = []

    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            missing.append(lib)

    if missing:
        return False, missing

    return True, []
