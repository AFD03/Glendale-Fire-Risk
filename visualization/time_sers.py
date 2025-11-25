import plotly.express as px
import pandas as pd
df = pd.read_csv("time_series_data.csv") # reading in csv file
df["Incident Start Date"] = pd.to_datetime(df["Incident Start Date"]) # initialize a data frame for year
df["Year"] = df["Incident Start Date"].dt.year # create year column
fire_year = df.groupby("Year").size().reset_index(name = "Fire Frequency") # sums up the number of fires per year

fig = px.line(fire_year, x = "Year", y = "Fire Frequency", title = "Los Angeles County Fire Time Series", color_discrete_sequence = ['red'], markers = True) # line characteristics
fig.show() # produce the line
