import pandas as pd
import plotly.express as px

# 1. Load data
df = pd.read_csv("fire_perimeters.csv").copy()

# 2. Keep only columns we need
cols = ["Year", "Unit ID", "GIS Calculated Acres", "DECADES"]
df = df[cols].copy()

# Clean up Year and drop rows with missing key values
df["Year"] = df["Year"].astype("Int64")
df = df.dropna(subset=["Year", "GIS Calculated Acres", "DECADES"])

# 3. Focus on more recent history and Glendale-area units
df = df[df["Year"] >= 1950]

focus_units = ["LAC", "VNC", "ANF"]
df = df[df["Unit ID"].isin(focus_units)]

# 4. Aggregate
agg = (
    df.groupby(["DECADES", "Unit ID"])["GIS Calculated Acres"]
      .sum()
      .reset_index(name="Total Burned Acres")
)

# 5. Chronological decade order
decade_order = [
    "1950-1959",
    "1960-1969",
    "1970-1979",
    "1980-1989",
    "1990-1999",
    "2000-2009",
    "2010-2019",
    "2020-January 2025"
]

# Remove unexpected decade labels
agg = agg[agg["DECADES"].isin(decade_order)].copy()

# 6. Set categorical order
agg["DECADES"] = pd.Categorical(agg["DECADES"], categories=decade_order, ordered=True)

# 7. Sort dataframe
agg = agg.sort_values("DECADES")

# 8. Build interactive chart with forced category order
fig = px.bar(
    agg,
    x="DECADES",
    y="Total Burned Acres",
    color="Unit ID",
    barmode="group",
    title="Total Wildfire Burned Acres per Decade near Glendale (by Fire Unit)",
    labels={
        "DECADES": "Decade",
        "Total Burned Acres": "Total Burned Area (acres)",
        "Unit ID": "Fire Unit"
    },
)

fig.update_xaxes(categoryorder="array", categoryarray=decade_order)

fig.update_layout(
    xaxis_title="Decade",
    yaxis_title="Total Burned Area (acres)",
)

fig.show()
