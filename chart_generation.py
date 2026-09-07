import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os


def save_chart(fig_name, folder="static/images"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, fig_name)

    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight", dpi=120)
    plt.close()

    return path


# ---------- BAR CHART ----------
def plot_bar_chart(df, x_col, y_col):

    data = df.groupby(x_col)[y_col].sum()

    plt.figure(figsize=(8, 4.5))
    plt.bar(data.index, data.values)

    plt.title(f"{y_col} by {x_col}")
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.ylabel(y_col)

    return save_chart("bar_chart.png")


# ---------- LINE CHART ----------
def plot_line_chart(df, x_col, y_col):

    data = df.sort_values(by=x_col)

    plt.figure(figsize=(8, 4.5))
    plt.plot(data[x_col], data[y_col], marker="o")

    plt.title(f"{y_col} over {x_col}")
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.ylabel(y_col)

    return save_chart("line_chart.png")


# ---------- PIE CHART ----------
def plot_pie_chart(df, cat_col, num_col):

    data = df.groupby(cat_col)[num_col].sum()

    plt.figure(figsize=(4.5, 4.5))
    plt.pie(data, labels=data.index, autopct="%1.1f%%", startangle=90)

    plt.title(f"{num_col} Distribution")

    return save_chart("pie_chart.png")


# ---------- HISTOGRAM ----------
def plot_histogram(df, num_col):

    plt.figure(figsize=(7, 4))
    plt.hist(df[num_col].dropna(), bins=12)

    plt.title(f"Distribution of {num_col}")
    plt.xlabel(num_col)

    return save_chart("histogram.png")


# ---------- SCATTER ----------
def plot_scatter(df, x_col, y_col):

    plt.figure(figsize=(7, 4))
    plt.scatter(df[x_col], df[y_col])

    plt.title(f"{y_col} vs {x_col}")
    plt.xlabel(x_col)
    plt.ylabel(y_col)

    return save_chart("scatter.png")