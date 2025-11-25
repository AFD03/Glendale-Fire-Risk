import pandas as pd
import plotly.express as px

df = pd.read_csv("drought_risk_csv.csv") # reading in csv file
risk_colors = {
    "High":"powderblue",
    "Medium":"royalblue",
    "Low":"midnightblue"
    } # identifying risk colors, the darker the blue, the less drought risk
df["risk_color"] = df["CVA Drought Risk"].map(risk_colors)

fig = px.scatter_mapbox(df, lat = "latitude", lon = "longitude",
                        color = "CVA Drought Risk", color_discrete_map=risk_colors,
                        category_orders = {"CVA Drought Risk": ["High", "Medium", "Low"]}, hover_name = "CVA Drought Risk", zoom = 8,
                        center = {"lat": 34.0522, "lon": -118.2437},
                        title = "Los Angeles County Drought Risk Map")      # creates the map based on longitude and latitude of the water systems in slos anegeles county
fig.update_layout(mapbox_style= "carto-positron")
fig.show()

