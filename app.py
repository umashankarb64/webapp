# Replace the problematic part of your code with this:
import streamlit as st
from google.cloud import bigquery
import pandas as pd
import plotly.express as px
import folium
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import os
import tempfile

# Create a temporary file with the credentials
credentials_path = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
with open(credentials_path.name, 'w') as f:
    json.dump(dict(st.secrets["gcp_credentials"]), f)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path.name


# Initialize BigQuery client
client = bigquery.Client()

# Load data from BigQuery
@st.cache_data
def load_data():
    QUERY = """
    SELECT Final_Incident_Type, Priority, Street_Name
    FROM `golden-photon-448607-m7.incident_data.incident_calls`
    """  # Using `incident_calls` now
    return client.query(QUERY).to_dataframe()

# Streamlit UI
st.title("San Jose Incident Analysis")

# Load and display data
df = load_data()

# Sidebar filters
incident_types = st.sidebar.multiselect("Select Incident Types", df["Final_Incident_Type"].unique(), default=df["Final_Incident_Type"].unique())
priority_levels = st.sidebar.multiselect("Select Priority Levels", sorted(df["Priority"].unique()), default=sorted(df["Priority"].unique()))

# Apply filters
filtered_df = df[df["Final_Incident_Type"].isin(incident_types) & df["Priority"].isin(priority_levels)]

# 📊 **1️⃣ Top 10 Most Common Incident Types**
st.subheader("Top 10 Most Common Incident Types")
top_incidents = filtered_df["Final_Incident_Type"].value_counts().head(10)
fig1, ax1 = plt.subplots(figsize=(10, 6))
top_incidents.plot(kind='bar', color='skyblue', ax=ax1)
ax1.set_title("Top 10 Most Common Incident Types")
ax1.set_xticklabels(top_incidents.index, rotation=45)
st.pyplot(fig1)

# 📈 **2️⃣ Distribution of Incident Priority Levels**
st.subheader("Distribution of Incident Priority Levels")
fig2, ax2 = plt.subplots(figsize=(8, 5))
sns.histplot(filtered_df["Priority"], bins=10, kde=True, ax=ax2)
ax2.set_title("Distribution of Incident Priority Levels")
st.pyplot(fig2)

# 🌍 **3️⃣ Heatmap of Incidents Across Different Streets**
st.subheader("Incident Concentration Heatmap")

# Create base map centered in San Jose
m = folium.Map(location=[37.3382, -121.8863], zoom_start=12)

# Generate random offsets for street locations
np.random.seed(42)  
street_locations = {street: [37.3382 + np.random.uniform(-0.05, 0.05),
                             -121.8863 + np.random.uniform(-0.05, 0.05)]
                    for street in filtered_df['Street_Name'].dropna().unique()}

# Convert DataFrame to list of fake coordinates
heat_data = [street_locations[street] for street in filtered_df['Street_Name'].dropna() if street in street_locations]

# Add heatmap
HeatMap(heat_data).add_to(m)

# Display the map in Streamlit
folium_static(m)

# Display filtered table
st.write("Filtered Data:", filtered_df)
