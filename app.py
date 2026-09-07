from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
from flask import send_from_directory

# ================= IMPORT PROJECT MODULES =================

from file_handler import upload_csv, validate_csv_format
from data_cleaning import clean_dataset
from data_analysis import detect_trend
from chart_generation import (
    plot_bar_chart,
    plot_line_chart,
    plot_pie_chart,
    plot_histogram,
    plot_scatter
)
from analysis_text import (
    generate_trend_text,
    generate_comparison_text,
    apply_privacy_rules,
    generate_human_summary
)
from export import generate_report, check_system_requirements

# ================= APP CONFIG =================

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
IMAGE_FOLDER = "static/images"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# =========================================================
# ================= FRONTEND ROUTES ========================
# =========================================================

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/overview.html")
def overview():
    return render_template("overview.html")


@app.route("/visua.html")
def visualizations():
    return render_template("visua.html")


@app.route("/help.html")
def help_page():
    return render_template("help.html")

@app.route("/downloads/<filename>")
def download_file(filename):
    return send_from_directory("uploads", filename, as_attachment=True)


# =========================================================
# ================= FILE UPLOAD API ========================
# =========================================================

@app.route("/api/upload", methods=["POST"])
def api_upload():

    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    df = upload_csv(filepath)

    if isinstance(df, tuple):
        df = df[0]

    if not validate_csv_format(df):
        return jsonify({"error": "Invalid CSV file"}), 400

    return jsonify({
        "filepath": filepath,
        "rows": int(df.shape[0]),
        "columns": list(df.columns)
    })


# =========================================================
# ================= DATA ANALYSIS API ======================
# =========================================================

@app.route("/api/analyze", methods=["POST"])
def api_analyze():

    data = request.json

    filepath = data.get("filepath")
    analysis_type = data.get("analysis_type")
    num_col = data.get("num_col")
    cat_col = data.get("cat_col")
    date_col = data.get("date_col")

    df = pd.read_csv(filepath)

    df = clean_dataset(df)
    df = apply_privacy_rules(df)

    if num_col not in df.columns:
        return jsonify({"error": f"Column '{num_col}' not found"})

    if cat_col and cat_col not in df.columns:
        return jsonify({"error": f"Column '{cat_col}' not found"})

    try:

        # ================= MEAN =================
        if analysis_type == "mean":

            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

            if df[num_col].dropna().empty:
                return jsonify({"error": "Column has no numeric values"})

            mean_val = float(df[num_col].mean())

            return jsonify({
                "mean": mean_val,
                "text": f"Mean value is {mean_val}"
            })


        # ================= MODE =================
        elif analysis_type == "mode":

            mode_val = df[num_col].mode()

            if mode_val.empty:
                return jsonify({"error": "No mode found"})

            mode_result = str(mode_val.iloc[0])

            return jsonify({
                "mode": mode_result,
                "text": f"Mode value is {mode_result}"
            })


        # ================= MIN-MAX =================
        elif analysis_type == "minmax":

            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

            max_val = float(df[num_col].max())
            min_val = float(df[num_col].min())

            return jsonify({
                "max": max_val,
                "min": min_val,
                "text": f"Maximum is {max_val} and minimum is {min_val}"
            })


        # ================= COMPARISON =================
        elif analysis_type == "comparison":

            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

            grouped = df.groupby(cat_col)[num_col].sum()

            top = grouped.idxmax()
            low = grouped.idxmin()
            diff = float(grouped[top] - grouped[low])

            comp_text = generate_comparison_text(top, low, diff)

            return jsonify({
                "top_category": str(top),
                "lowest_category": str(low),
                "difference": diff,
                "text": comp_text
            })


        # ================= DESCRIBE =================
        elif analysis_type == "describe":

            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

            desc = df[num_col].describe().to_dict()
            desc = {k: float(v) for k, v in desc.items()}

            return jsonify(desc)


        # ================= TREND =================
        elif analysis_type == "trend":

            trend = detect_trend(df, num_col, date_col)

            if trend is None:
                return jsonify({"error": "Trend detection failed"})

            start = df[num_col].iloc[0]
            end = df[num_col].iloc[-1]

            trend_text = generate_trend_text(trend, start, end)

            return jsonify({
                "trend": trend,
                "text": trend_text
            })


        else:
            return jsonify({"error": "Invalid analysis type"})


    except Exception as e:
        return jsonify({"error": str(e)})


# =========================================================
# ================= CHART GENERATION API ===================
# =========================================================

@app.route("/api/chart", methods=["POST"])
def api_chart():

    data = request.json

    filepath = data.get("filepath")
    chart_type = data.get("chart_type")
    x_col = data.get("x_col")
    y_col = data.get("y_col")

    df = pd.read_csv(filepath)

    try:

        if chart_type == "bar":
            path = plot_bar_chart(df, x_col, y_col)

        elif chart_type == "line":
            path = plot_line_chart(df, x_col, y_col)

        elif chart_type == "pie":
            path = plot_pie_chart(df, x_col, y_col)

        elif chart_type == "hist":
            path = plot_histogram(df, y_col)

        elif chart_type == "scatter":
            path = plot_scatter(df, x_col, y_col)

        else:
            return jsonify({"error": "Invalid chart type"}), 400

        return jsonify({"chart_url": "/" + path})

    except Exception as e:
        return jsonify({"error": str(e)})


# ================= NLP ANALYSIS TEXT API =================

@app.route("/api/analyze-text", methods=["POST"])
def api_analyze_text():

    data = request.json

    filepath = data.get("filepath")
    x_col = data.get("x_col")
    y_col = data.get("y_col")

    try:
        df = pd.read_csv(filepath)

        # Ensure numeric
        df[y_col] = pd.to_numeric(df[y_col], errors="coerce")

        grouped = df.groupby(x_col)[y_col].sum()

        top_cat = grouped.idxmax()
        low_cat = grouped.idxmin()

        max_val = grouped.max()
        min_val = grouped.min()
        avg_val = grouped.mean()

        # ⭐ HUMAN-FRIENDLY TEXT
        base_text = (
            f"The highest {y_col} is for '{top_cat}' with value {max_val:.2f}. "
            f"The lowest is '{low_cat}' with {min_val:.2f}. "
            f"The average across all {x_col} categories is {avg_val:.2f}. "
            f"This indicates that '{top_cat}' contributes the most to overall {y_col}."
        )

        # Optional NLP polishing
        try:
            text = generate_human_summary(base_text)
        except:
            text = base_text

        return jsonify({"text": text})

    except Exception:
        return jsonify({"text": "Analysis generated but details unavailable."})
    
# =========================================================
# ================= EXPORT REPORT API ======================
# =========================================================

@app.route("/api/export", methods=["POST"])
def api_export():

    data = request.json

    summary = data.get("summary")

    success, report_file = generate_report(
        charts=["Generated Charts"],
        summary=summary
    )

    if success:
        return jsonify({"report": report_file})
    else:
        return jsonify({"error": report_file})
    

@app.route("/api/overview", methods=["POST"])
def api_overview():

    data = request.json
    filepath = data.get("filepath")

    df = pd.read_csv(filepath)

    overview = {
        "columns": list(df.columns),
        "missing": df.isnull().sum().to_dict(),
        "duplicates": int(df.duplicated().sum()),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "preview": df.head().to_dict(orient="records")
    }

    return jsonify(overview)

@app.route("/api/download-cleaned", methods=["POST"])
def download_cleaned():

    data = request.json
    filepath = data.get("filepath")

    df = pd.read_csv(filepath)

    from data_cleaning import prepare_clean_dataset
    from analysis_text import apply_privacy_rules

    df = prepare_clean_dataset(df)
    df = apply_privacy_rules(df)

    filename="cleaned_dataset.csv"
    clean_path = os.path.join("uploads","cleaned_dataset.csv")
    
    df.to_csv(clean_path, index=False)

    return jsonify({
        "file": "/downloads/cleaned_dataset.csv"
    })


# =========================================================
# ================= SYSTEM CHECK API =======================
# =========================================================

@app.route("/api/system-check")
def system_check():

    ok, missing = check_system_requirements()

    if ok:
        return jsonify({"status": "System ready"})
    else:
        return jsonify({"missing_libraries": missing})


# =========================================================
# ================= RUN SERVER =============================
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)
