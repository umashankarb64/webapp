import streamlit as st
from google.cloud import bigquery
import pandas as pd
import plotly.express as px
import folium
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import os
import json
import tempfile

# Include service account credentials directly (for development only)
service_account_info = {
  "type": "service_account",
  "project_id": "golden-photon-448607-m7",
  "private_key_id": "a42f9ac64c5d527d65f0e487ffd1ba5ecab4fbef",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDD8ADQ8gKwKXSu\nGYTkMu/wP/oFV2gre5SGdsCQg6LZTcxN9Sh/tmAj0TsVesr1tJ+B/IOTYyY7AcIo\nv2ZcMaC0YC3HVaBz+5z/7SjUzXsd1hfX+PeCgSaJUb2I4BXeF150B7PXo2MU13DY\nMbmDSk580Ome0s+63w0FRJHUtS+YdWNO4OraRrVy5gn512XfNO162seoKfE0Qjyl\n+W0+imaAFNNCYHSiDcWoGiOVl5rE9GKTi1T5LvV0Wf2zS8skmM4D5vsgYlUvrifh\nfPhvBgbr12bHXnvqaLvjQHKF5PDabwg5SWA9vuoypbJYQQ3OoGzXc/XDYELKWhrp\nxkOJXOVTAgMBAAECggEAJBivdc7X6u9ANSCzaDzwEhEfNOO056nVI252LElr81+P\nP19mThzhmked/GeKQ3i6l/5WmQz/iohY5hvYtixYYFKFrH7cV/GnK0jcKFQQld8O\ntnWB15OGb27VHYW20Zr5hiOzIItTog/MlK+YbxT936W3HFDW/yS/Z9SJjyev9IR8\nv8vK5lW3KBHFzQP7IsbdhdWNOB3L9OI6Mv+CRDULpWyNKRbfDwhsm0VlQrvIJIhs\nLG2LTwoWIpHmjmH27Ilb6rHQBFsSqyi6bZe+nlrzDQmvlqsl6KvBGVIEGPc63kjW\nOcM8PCppnD0DmgHtHDlpk6SerGhWxHBE8CmXpH8hZQKBgQD5T9EPbmdJx3BXaZbi\nI5IES3xp2fdwejQTgyZiqOxp36XgWwhFHvF/KTrMnu9le13bRqsKKj9wdiCn0UkR\nOok2AFuooAhmdhRwMG2PovuaVLe3edpax+rnjd2GmCh+EG6aMAFltNNx+b8Q90zH\n7l225fGzDOQc+ryJ2y9fuFB5FwKBgQDJMaGdvODMitb4nRWw5A+NEq3C/Bzv94fm\nCyK9UzY9y9J0dDATe7NAbWEoP+Hfo9bS2fWYwCCR7IH50m+vL3F4UEObkJ+AJN73\nWSWgSMzqOJq0X55uQWyFjO0rfzzpwDOKYhe67+mZDXk8CUxpyp85w57QoISVPWq2\ndhqkSgTjJQKBgQCvUkDbUDFUgervnbJcbtU1Lfxc18oZD+blPdpVkSNHxN36ayni\nqcL8QHs4ACCrxdiX5hdLu7AHHxsRyKxQcFCjaBcM+xVNMIZo6rVxSBUVT7QuU4OJ\nSYNYuLvq9b+r/1Q4G8AvzLzRLub9QFt/UZIXl5aj6lHUS0Mg0sF617vHmwKBgDKH\nJ2qhA+f6unBnqwnozMsGNONyQ6Y0iUnJ5CieHFI6vRkIEQbjmyoEDlF4cbajxBDi\nMl7xaXycZCwkoG3jwWCQ79nC4XviRqjiF6QAhI4SNzAzj2trPODxeqLg6qBd59PK\nPOFy3TzV+GuOfkVXYNO2AE2u8n00lndKg/hcqouNAoGBAIIX59SkQHlwmpWmoB53\nuEjEEkFLQHFwKwh9trkc/hH6b+oXGWSyoKTcdSrEEbd8wDGVwaelLH2Gp2IiekuX\ncsADBBRf6xTLO1+wgc8Xy0YZUt5JZNRQxcQSA2HE2C7YKnnLS55i9yi2Ua6vgJGS\nwrOuZb1XVw4jrWYW7LOBvqLo\n-----END PRIVATE KEY-----\n",
  "client_email": "bigquery-access@golden-photon-448607-m7.iam.gserviceaccount.com",
  "client_id": "108061918927749029180",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bigquery-access%40golden-photon-448607-m7.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Write the credentials to a temporary file
credentials_path = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
with open(credentials_path.name, 'w') as f:
    json.dump(service_account_info, f)

# Set environment variable to point to the credentials file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path.name

# Initialize BigQuery client
client = bigquery.Client()

# Load data from BigQuery
@st.cache_data
def load_data():
    QUERY = """
    SELECT Final_Incident_Type, Priority, Street_Name
    FROM `golden-photon-448607-m7.incident_data.incident_calls`
    """
    return client.query(QUERY).to_dataframe()

# Rest of your Streamlit app code remains the same
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
