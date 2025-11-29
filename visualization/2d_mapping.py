import geopandas as gpd
import plotly.express as px
from pyproj import CRS

# -------------------------------
# 1. Load and reproject GeoJSON
# -------------------------------
gdf = gpd.read_file("buildings_glendale.geojson")

# EPSG:6424 → WGS84
gdf = gdf.to_crs(epsg=4326)

# -------------------------------
# 2. Create the main Plotly figure
# -------------------------------
fig = px.choropleth_mapbox(
    gdf,
    geojson=gdf.geometry,
    locations=gdf.index,
    color="Fire Risk",
    color_continuous_scale=[
        "#ffffb2",  # 1
        "#fecc5c",  # 2
        "#fd8d3c",  # 3
        "#f03b20",  # 4
        "#bd0026",  # 5
    ],
    mapbox_style="carto-positron",
    zoom=12.4,
    center={"lat": gdf.geometry.centroid.y.mean(),
            "lon": gdf.geometry.centroid.x.mean()},
    opacity=0.9,
    hover_data={
        "Fire Risk": True,
        "Height": True,
        "Elevation": True,
        "fid": True
    }
)

# -------------------------------
# 3. Make it clean & professional
# -------------------------------
fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(
        title="Fire Risk",
        tickvals=[1,2,3,4,5]
    ),
)

# -------------------------------
# 4. Export HTML
# -------------------------------
fig.write_html("fire_risk_2d_map.html", include_plotlyjs="cdn")