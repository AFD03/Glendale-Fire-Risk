import pandas as pd
import plotly.express as px

df = pd.read_csv("fire_perimeters.csv").copy()

# Clean year
df["Year"] = df["Year"].astype("Int64")
df = df.dropna(subset=["Year"])

# ---- focus on recent years only (e.g. 1950+) ----
df = df[df["Year"] >= 1950]

focus_units = ["LAC", "ANF", "VNC"]  # change if your legend shows others you care about
df["Unit ID"] = df["Unit ID"].fillna("Unknown")
df = df[df["Unit ID"].isin(focus_units)]

# Aggregate
counts = (
    df.groupby(["Year", "Unit ID"])
      .size()
      .reset_index(name="Fire Count")
)

fig = px.line(
    counts,
    x="Year",
    y="Fire Count",
    color="Unit ID",
    title="Historic Wildfire Counts Near Glendale (by Unit)",
    markers=True,
)

fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Number of Fires"
)

fig.show()
